#!/usr/bin/env python3

#This script assumes there is a network object-group on all Cisco ASAs called 'grp_talos_blocklist', and that the group is attached to the correct ACL/interface
#pip install netmiko


#import all the modules we need
import sys
import os
import netmiko
import getpass
from netmiko import ConnectHandler
print('imported modules')

#list of firewall devices to add the talos_blocklist ip to
#exemplo 
#asa_list = ['10.1.1.1', '10.2.2.2', '10.3.3.3']
asa_list = ['198.18.133.254', '198.18.133.254', '198.18.133.254']
#print('Temos os seguintes Equipamentos ' + asa_list)

#############################################################################################
# MALUQUICE MINHA - VAGNER
#for i in asa_list:
# net_connect = ConnectHandler(**i)
# # get the prompt as a string
# output=net_connect.send_command_expect('show version | grep %')
# print("--------------------------------------------------------------------------------------------------------")
# print(output)
#
#
#
##############################################################################################

#Parameter 1 should always be the ip of the address to block (talos_blocklist)
#check that we have enough parameters to continue (the ip addresses we need)
#Tive que corrigir para 2 aqui, antes estava 1
if len(sys.argv) < 2:
    sys.exit('ERROR: Please include parameters for the talos_blocklist IP address')
    
# Tive que mudar para 0 pois com o numero 1 estava com erro
param_1 = sys.argv[1]
print('checking params... param_1: ' + param_1)

#####3 Formas de pegar as senhas:
##Forma 1
#get the username/password information from local system environment variables
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
for asa in asa_list:

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