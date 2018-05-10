#!/usr/bin/env python3

import subprocess
import http.client
# import requests


def main():

    # IP / DHCP
    ip = get_ipv4()
    print('IP:           %s' % ip)
    if ip.startswith('169.'):
        print('No DHCP')
        return

    # Gateway
    gateway_ip = get_gateway_ip()
    if gateway_ip is None:
        print('Gateway:      NONE')
    else:
        print('Gateway:      %s' % gateway_ip)
        print('Gateway ping: %s' % ping(gateway_ip))

    # send_http_request(gateway_ip)
    # return

    # Teh Internets
    google_dns_ping = ping('8.8.8.8')
    print('8.8.8.8 ping: %s' % google_dns_ping)

    # if google_dns_ping != 'Down':
    #     return

    # NOTE: algo5 does not respond to pings
    # vpnHostPing = ping('138.197.186.179')
    # print('VPN ping:     %s' % vpnHostPing)

    print('')
    print('Trying to find captive portal... [ALPHA]')
    print('')

    """
    curl('http://captive.apple.com')
    captiveResponse = send_http_request('captive.apple.com')
    if '<HTML><HEAD><TITLE>Success</TITLE></HEAD><BODY>Success</BODY></HTML>' in captiveResponse:  # noqa
        print('Captive:      No portal')
    else:
        print('Captive:\n\t%s' % captiveResponse)
    """

    gateway_redirect = get_redirection_location('http://%s/' % gateway_ip)
    if gateway_redirect:
        print('Gateway redirects to: %s' % gateway_redirect)

    # captivePortalAddress = captivePortalAddress()
    # captiveIP = resolve('WIFIonICE.de', gateway_ip)
    # curl('http://%s/' % gateway_ip)


def get_ipv4():
    (stdout, stderr) = _exec("ifconfig en0")
    result = stdout.split("\n")
    inet_line = [line for line in result if "inet " in line][0]
    ipv4 = inet_line.split(" ")[1]
    return ipv4


def get_gateway_ip():
    (stdout, stderr) = _exec("route -n get default")
    result = stdout.split("\n")
    gateway_lines = [line for line in result if "gateway" in line]
    if not gateway_lines:
        return None
    gateway_ip = gateway_lines[0].split(': ')[1]
    return gateway_ip


def get_redirection_location(url):
    cmd = 'curl -s -D - -m 5 "%s"' % url
    print(cmd)
    (stdout, stderr) = _exec('curl -s -D - -m 5 "%s"' % url)
    result = stdout.split("\n")
    print('---')
    print(stdout)
    print('---')
    print(stderr)
    print('---')
    location_lines = [line for line in result if "Location: " in line]
    if not location_lines:
        return None
    redirect_location = location_lines[0].split(': ')[1]
    return redirect_location


def ping(IP):
    (stdout, stderr) = _exec("ping -q -c2 -t2 %s" % IP)
    result = stdout.split("\n")
    packet_loss_line = [line for line in result if "packet loss" in line][0]
    packet_loss = packet_loss_line.split(' ')[6]

    if packet_loss == '0.0%':
        return 'OK'
    if packet_loss == '100.0%':
        return 'Down'
    return "%s packet loss" % packet_loss

# def curl(url, host=None):
#     try:
#         r = requests.get(url)
#     except:
#         return None
#     location = r.headers['location'] if 'location' in r.headers else None
#     print('location: %s' % location)
#     print(r.text)


def send_http_request(host, method='GET', path='/', headers={}, body=None):

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


def resolve(hostname, dns_ip=None):
    dig_command = ''
    if dns_ip is None:
        dig_command = "dig -t A %s" % hostname
    else:
        dig_command = "dig -t A @%s %s" % (dns_ip, hostname)
    (stdout, stderr) = _exec(dig_command)

    result = stdout.split("\n")
    dns_a_record_lines = [line for line in result if "IN\tA\t" in line]
    if not dns_a_record_lines:
        return None

    """
    foo = [line[line.find("IN\tA\t")+5:] for line in result if line.find("IN\tA\t") != -1]  # noqa
    foo = [line[index+5:] for (index,line) in ((line.find("IN\tA\t"), line) for line in result)if i != -1]  # noqa
    """

    ipv4s = [line[line.find("IN\tA\t")+5:] for line in dns_a_record_lines]
    if not ipv4s:
        return None

    return ipv4s[0]


def _exec(command):
    tokens = command.split(' ')
    process = subprocess.Popen(
            tokens, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdout_bytes, stderr_bytes) = process.communicate()
    stdout = stdout_bytes.decode('utf-8')
    stderr = stderr_bytes.decode('utf-8')
    return (stdout, stderr)


"""
def captivePortalAddress(networkName):
    switch(networkName):
        case 'WIFIonICE':
            captiveAddress = _exec
"""


if __name__ == '__main__':
    main()
