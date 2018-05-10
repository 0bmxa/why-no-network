#!/bin/sh

Yellow='\033[1;33m'
LightBlue='\033[1;34m'
RESET='\033[0m'

DEBUG=1

function main {
    # Get gateway IP
    GATEWAY_IP=$(getGatewayIP)
    if [[ -z "$GATEWAY_IP" ]]; then
        printf "We don't even have a Gateway IP... aborting.\n\n"
        exit -1;
    fi
    echo "Gateway: ${GATEWAY_IP}"


    # Get REDIRECT from gateway
    GATEWAY_REDIRECT=$(getLocationFromURL "http://${GATEWAY_IP}/")
    # echo "${Yellow}Redirects to:${RESET}"
    # echo "${GATEWAY_REDIRECT}"
    echo "Redirects to: ${Yellow}${GATEWAY_REDIRECT}${RESET}"
    # [ ! -z "${GATEWAY_REDIRECT}" ] && safariAndExit "${GATEWAY_REDIRECT}"
    [ ! -z "${GATEWAY_REDIRECT}" ] && curlAndExit "${GATEWAY_REDIRECT}"

    # Get REDIRECT from captive.apple.com
    # CAPTIVE_REDIRECT=$(getLocationFromURL 'http://captive.apple.com')
    # printf "Redirects to: ${Yellow}>%s${RESET}\n" "${CAPTIVE_REDIRECT}"
    # [ ! -z "${CAPTIVE_REDIRECT}" ] && safariAndExit "${CAPTIVE_REDIRECT}"
    # [ ! -z "${CAPTIVE_REDIRECT}" ] && curlAndExit "${CAPTIVE_REDIRECT}"
}


function getGatewayIP {
    GATEWAY_IP=$(route -n get default | awk '/gateway:/ {print $2}')
    echo "${GATEWAY_IP}"
}


function getLocationFromURL {
    url=$1

    # printf "Connecting to ${LightBlue}%s${RESET}...\n" "${url}" >&2

    response=$(curl -s -D - -m 5 "${url}")
    if [[ -z "${response}" ]]; then
        echo ''
        # echo "Does Little Snitch allow connections to ${url} ?" >&2
        return
    fi

    # if [[ $DEBUG=1 ]]; then
    #     echo "---" >&2
    #     echo "${response}" >&2
    #     echo "---" >&2
    # fi

    # Getting redirect
    httpRedirectLocation=$(echo "$response" | awk '/Location:/ {print $2}' | sed "s/[[:space:]]//g")
    if [[ ! -z "${httpRedirectLocation}" ]]; then
        echo "${httpRedirectLocation}"
        return
    fi


    # Plain response
    # printf 'No REDIRECT found. Response:\n%s\n\n' "${response}"
}

# function safariAndExit {
#     url=$1
#
#     # Test url first
#     # response=$(curl -s -D - -m 2 "${url}")
#     # [ -z "${response}" ] && echo "ERROR: Couldn't call ${url}" >&2 && exit
#
#     # If test worked, open Safari
#     open -a 'Safari' "${url}"
#     exit 0
# }

function curlAndExit {
    url=$1

    # Test url first
    response=$(curl -s -D - -m 5 "${url}")
    if [ -z "${response}" ]; then
        echo "ERROR: Couldn't call ${url}" >&2
        curl "${url}" >&2
        exit -1
    fi

    echo "---"
    echo "${response}"
    echo "---"

    exit 0
}

main
