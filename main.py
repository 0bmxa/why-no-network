#!/usr/bin/env python3

import subprocess
import http.client
# import requests


def main():

    # IP / DHCP
    ip = getIPv4()
    print('IP:           %s' % ip)
    if ip.startswith('169.'):
        print('No DHCP')
        return

    # Gateway
    gatewayIP = getGatewayIP()
    if gatewayIP is None:
        print('Gateway:      NONE')
    else:
        print('Gateway:      %s' % gatewayIP)
        print('Gateway ping: %s' % ping(gatewayIP))

    # sendHTTPRequest(gatewayIP)
    # return

    # Teh Internets
    googleDNSPing = ping('8.8.8.8')
    print('8.8.8.8 ping: %s' % googleDNSPing)

    # if googleDNSPing != 'Down':
    #     return

    # NOTE: algo5 does not respond to pings
    # vpnHostPing = ping('138.197.186.179')
    # print('VPN ping:     %s' % vpnHostPing)

    print('\nTrying to find captive portal... [ALPHA]\r')
    """
    curl('http://captive.apple.com')
    captiveResponse = sendHTTPRequest('captive.apple.com')
    if '<HTML><HEAD><TITLE>Success</TITLE></HEAD><BODY>Success</BODY></HTML>' in captiveResponse:  # noqa
        print('Captive:      No portal')
    else:
        print('Captive:\n\t%s' % captiveResponse)
    """

    gatewayRedirect = getRedirectLocation('http://%s/' % gatewayIP)
    if gatewayRedirect:
        print('Gateway redirects to: %s' % gatewayRedirect)

    # # captivePortalAddress = captivePortalAddress()
    # captiveIP = resolve('WIFIonICE.de', gatewayIP)
    # curl('http://%s/' % gatewayIP)


def getIPv4():
    (stdout, stderr) = _exec("ifconfig en0")
    result = stdout.split("\n")
    inetLine = [line for line in result if "inet " in line][0]
    IPv4 = inetLine.split(" ")[1]
    return IPv4


def getGatewayIP():
    (stdout, stderr) = _exec("route -n get default")
    result = stdout.split("\n")
    gatewayLines = [line for line in result if "gateway" in line]
    if len(gatewayLines) == 0:
        return None
    gatewayIP = gatewayLines[0].split(': ')[1]
    return gatewayIP


def getRedirectLocation(url):
    cmd = 'curl -s -D - -m 5 "%s"' % url
    print(cmd)
    (stdout, stderr) = _exec('curl -s -D - -m 5 "%s"' % url)
    result = stdout.split("\n")
    print('---')
    print(stdout)
    print('---')
    print(stderr)
    print('---')
    locationLines = [line for line in result if "Location: " in line]
    if len(locationLines) == 0:
        return None
    redirectLocation = locationLines[0].split(': ')[1]
    return redirectLocation


def ping(IP):
    (stdout, stderr) = _exec("ping -q -c2 -t2 %s" % IP)
    result = stdout.split("\n")
    packetLossLine = [line for line in result if "packet loss" in line][0]
    packetLoss = packetLossLine.split(' ')[6]

    if packetLoss == '0.0%':
        return 'OK'
    if packetLoss == '100.0%':
        return 'Down'
    return "%s packet loss" % packetLoss

# def curl(url, host=None):
#     try:
#         r = requests.get(url)
#     except:
#         return None
#     location = r.headers['location'] if 'location' in r.headers else None
#     print('location: %s' % location)
#     print(r.text)


def sendHTTPRequest(host, method='GET', path='/', headers={}, body=None):

    try:
        connection = http.client.HTTPSConnection(host)
        connection.request(method, path, body, headers)
    except OSError as e:
        return e

    #  Get response
    response = connection.getresponse()
    data = response.read()
    result = data.decode("utf-8")
    return result


def resolve(hostname, dnsIP=None):
    digCommand = ''
    if dnsIP is None:
        digCommand = "dig -t A %s" % hostname
    else:
        digCommand = "dig -t A @%s %s" % (dnsIP, hostname)
    (stdout, stderr) = _exec(digCommand)

    result = stdout.split("\n")
    dnsARecordLines = [line for line in result if "IN\tA\t" in line]
    if len(dnsARecordLines) == 0:
        return None

    """
    foo = [line[line.find("IN\tA\t")+5:] for line in result if line.find("IN\tA\t") != -1]  # noqa
    foo = [line[index+5:] for (index,line) in ((line.find("IN\tA\t"), line) for line in result)if i != -1]  # noqa
    """

    IPv4s = [line[line.find("IN\tA\t")+5:] for line in dnsARecordLines]
    if len(IPv4s) == 0:
        return None

    return IPv4s[0]


def _exec(command):
    tokens = command.split(' ')
    process = subprocess.Popen(
            tokens, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdoutBytes, stderrBytes) = process.communicate()
    stdout = stdoutBytes.decode('utf-8')
    stderr = stderrBytes.decode('utf-8')
    return (stdout, stderr)


"""
def captivePortalAddress(networkName):
    switch(networkName):
        case 'WIFIonICE':
            captiveAddress = _exec
"""


if __name__ == '__main__':
    main()
