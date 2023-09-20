#!/usr/bin/env python3

# Este Script tem como objetivo listar os tipos de eventos no Cisco Endpoint Secure (AMP - Antimalware Protection)
# Eh necessario instalar algumas dependencias como:
## pip install requests
#
# Personalizado por Vagner Silva - vagner.araujo@msn.com
# Github - https://github.com/vagner-instructor
#
# Agradecimentos para Cisco Security - https://github.com/CiscoSecurity/amp-01-basics

import requests

amp_client_id = '123456'
amp_api_key = '12345678910-ABCDEFGHIJ'

def listEventTypes():
    url = 'https://api.amp.cisco.com/v1/event_types'

    request = requests.get(url, auth=(amp_client_id, amp_api_key))
    response = request.json()

    print('{:^20} {:^15}'.format('ID', 'Name', 'Description'))

    for item in response["data"]:
        print('{:^20} {:<15}'.format(item['id'], item['name']))

if __name__ == '__main__':
    print("""
               Advanced Malware Protection (AMP) - Cloud

                    Lista de Tipos de Eventos :
                    """)

    listEventTypes()