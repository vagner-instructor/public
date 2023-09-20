#!/usr/bin/env python3

# Main Function:
# Find computers trying to access an URL/DNS destination
#
# Dependencies:
## pip install requests
## pip install json
## Change API_KEY to your key
## Change API_SECRET to your secret
## Change ORG_ID to your ORG_ID

#
# Criado por Vagner Silva - vagner.instructor@gmail.com
# Github - https://github.com/vagner-instructor
#
# Thanks to Cisco "Implementing Automation for Cisco Security Solutions (SAUI) v1.0" Course


import sys

import requests
import json
from datetime import datetime

API_KEY = "123456"
API_SECRET = "123456"
ORG_ID = "123456"


if len(sys.argv) < 2:
    sys.exit('ERRO: Please insert a parameter after script, exemple * python destinations-top-identities-with-parameter-v1-en.py url')
    
param_1 = sys.argv[1]
print('Checking with the following URL provided: ' + param_1)

def getTopIdentities():
    url = 'https://reports.api.umbrella.com/v1/organizations/' + ORG_ID + '/destinations/' + param_1 + '/identities'

    # do GET request for the domain status and category
    req = requests.get(url, auth = (API_KEY, API_SECRET))

    # error handling if true then the request was HTTP 200, so successful
    if (req.status_code != 200):
        print("An error has ocurred with the following code %s" % req.status_code)
        sys.exit(0)

    output = req.json()

    print('{:^20}{:^20}{:^20}{:^20}'.format(
        "Origin ID",
        "Origin Type",
        "Origin Label",
        "Number of Requests"
    ))

    for item in output["identities"]:
        origin_id = item['originId']
        if item['originType']:
           origin_type = item['originType']
        else:
           origin_type = ""
 #      origin_type = item['originType']
        origin_label = item['originLabel']
        number_of_requests = item['numberOfRequests']

        print('{:^20}{:^20}{:^20}{:^20}'.format(
            origin_id,
            origin_type,
            origin_label,
            number_of_requests
        ))

def main():
    # Print the menu
    print("""
                 Umbrella - Retrieve Destinations: Top Identities Report
                             ACME Inc, IT Security Department
                   """)

    getTopIdentities()


if __name__ == '__main__':
    main()
