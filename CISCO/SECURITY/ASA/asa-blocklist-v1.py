#!/usr/bin/env python3

# Este Script tem como objetivo adicionar IP em diversos equipamentos
# Eh necessario instalar algumas dependencias como:
## pip install netmiko
#
# Personalizado por Vagner Silva - vagner.araujo@msn.com
# Github - https://github.com/vagner-instructor
#
# Agradecimentos para RaceFPV (https://gist.github.com/RaceFPV)

#import all the modules we need
import sys
import os
import netmiko
import getpass
from netmiko import ConnectHandler
print('imported modules')

# Lista dos Firewalls para adicionar o objeto na Blocklist
lista_asa = ['198.18.133.254', '198.18.133.254', '198.18.133.254']
#print('Temos os seguintes Equipamentos ' + lista_asa)

# Parametro 1 deve ser sempre o IP que gostaria de bloquear
# Checar se temos o parametro necessario
if len(sys.argv) < 2:
    sys.exit('ERRO: Por favor inclua um parametro de endereço de IP para adicionar na BLOCKLIST')
    
param_1 = sys.argv[1]
print('Checando parametros... param_1: ' + param_1)

##### Existem Algumas Formas de pegar as senhas:
## Forma 1
## Pegar o username/password das variaveis de ambiente locais
#username = os.environ.get('CISCOUSERNAME', 'None')
#password = os.environ.get('CISCOPASSWORD', 'None')

##Forma 2
# Eh possivel especificar no Codigo tambem
#username = 'admin'
#password = 'C1sco12345'

##Forma 3
#Ou pedir para digitar
username = input("Por favor insira o usuario:\n")
#password = input("Por favor insira a senha:\n")
print('Por favor insira a senha:')
password = getpass.getpass()

secret = password
print('Obtendo acesso com as credenciais fornecidas')

#check that we have all of the environment variables we need
if (username == 'None') or (password == 'None'):
        sys.exit('ERROR: Login username/password not set in environment variables')


#start the main loop
for asa in lista_asa:

    #create the ssh session using netmiko
    print('Criando a conexao ssh para ' + asa)
    device = ConnectHandler(device_type='cisco_asa', ip=asa, username=username, password=password, secret=secret)
    print('Conexao estabelecida no equipamento ' + asa)

    #preload our config changes into a single array
    config_commands = [
#        'conf t',
#        'terminal width 300',
        'object network talos_ip_blocklist-' + param_1,
        'host ' + param_1,
        'object-group network grp_talos_blocklist',
        'network-object object talos_ip_blocklist-' + param_1
    ]
    print('Enviando a lista de comandos no ' + asa)
#######################
# Para testar
#    config_commands = [
#        'show version'
#    ]
    #send our Cisco-specific commands and dump the output to a variable
    output = device.send_config_set(config_commands)
    print('sent ASA command to ' + asa)

    #print the output
    print(output)

    #close the ssh session cleanly
    device.disconnect()
    print('closed ssh session')

print('finished on all firewall devices')