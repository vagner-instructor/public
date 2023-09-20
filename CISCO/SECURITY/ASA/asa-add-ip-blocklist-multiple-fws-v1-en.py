#!/usr/bin/env python3

# The purpose of this Script it Add a IP Address in multiple ASA Firewalls
# It's necessary install some dependencies like:
## pip install netmiko
#
#
# Customized by Vagner Silva - vagner.instructor@gmail.com
# Github - https://github.com/vagner-instructor
#
# Thanks to RaceFPV (https://gist.github.com/RaceFPV)

# import all the modules we need
import sys
import os
import netmiko
import getpass
from netmiko import ConnectHandler
print('imported modules')

# Firewalls list to add objetcs to BLOCKLIST
list_asa = ['198.18.133.254', '198.18.133.254', '198.18.133.254']
print ("Number of Firewalls in the list = ", len(list_asa))
print ("Firewalls: ")
for asa in list_asa:
    print (asa)
    

# Parametro 1 deve ser sempre o IP que gostaria de bloquear
# Checar se temos o parametro necessario
if len(sys.argv) < 2:
    sys.exit('ERROR: Please include a parameter to include the IP in the BLOCKLIST in Multiple Firewalls. \nExample: python asa-add-ip-blocklist-multiple-fws-v1.py 1.1.1.1')
    
param_1 = sys.argv[1]
print('Checking parameter... param_1: ' + param_1)

##### There are a few ways to get the username and password:
## Way - 1
## Collect the username/password from Local's environment variables
#username = os.environ.get('CISCOUSERNAME', 'None')
#password = os.environ.get('CISCOPASSWORD', 'None')

## Way - 2
# Specify in the code
#username = 'admin'
#password = 'C1sco12345'

## Way - 3
# Ask user to type it
username = input("Please insert the username:\n")
print('Please insert the password:')
password = getpass.getpass()

secret = password
print('Getting access with the supplied credentials')

# It checks if the parameters for Environment Variables it's been set
if (username == 'None') or (password == 'None'):
        sys.exit('ERROR: Login username/password not set in environment variables')


# Looping to send news objets to all Firewalls listed 
for asa in list_asa:

    # It creates the SSH using NETMIKO
    print('Criando a conexao ssh para ' + asa)
    device = ConnectHandler(device_type='cisco_asa', ip=asa, username=username, password=password, secret=secret)
    print('Conexao estabelecida no equipamento ' + asa)

    # Lista de comandos
    config_commands = [
#        'conf t',
#        'terminal width 300',
        'object network talos_ip_blocklist-' + param_1,
        'host ' + param_1,
        'object-group network grp_talos_blocklist',
        'network-object object talos_ip_blocklist-' + param_1
    ]
    print('Enviando a lista de comandos no ' + asa)
    # Envia os comandos Cisco especificos e guarda a saida em uma variavel
    output = device.send_config_set(config_commands)
    print('sent ASA command to ' + asa)

    # Printar a saida de comandos executados
    print(output)

    # Fecha a conexao ssh do equipamento
    device.disconnect()
    print('closed ssh session')

print('Terminou em todos os equipamentos')