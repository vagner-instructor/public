#!/usr/bin/env python3

# Este Script tem como objetivo fazer backup da configuração dos equipamentos ASAs
# Eh necessario instalar algumas dependencias como:
## pip install netmiko
#
# Personalizado por Vagner Silva - vagner.araujo@msn.com
# Github - https://github.com/vagner-instructor
#
# Agradecimentos para RaceFPV (https://gist.github.com/RaceFPV), inspiração para esse Script "Maroto", o original tinha um objetivo diferente


# Importar os modulos necessarios
import sys
import os
import netmiko
import getpass
from netmiko import ConnectHandler
print('Modulos Importados')

# Lista dos equipamentos para fazer backup
asa_list = ['198.19.10.27', '198.19.10.27', '198.19.10.27']
#Adicionando as variaveis dos Firewalls de Costa Carvalho e de Ponte Pequena (CC-10.7.222.60 e PP-10.36.162.10)
#asa_list = ['10.7.222.60, 10.36.162.10']

#print('Temos os seguintes Equipamentos ' + asa_list)

#############################################################################################
# MALUQUICE MINHA - VAGNER SILVA - Desconsiderar
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

# Parametro 1 pega um argumento para adicionar como nome do arquivo de backup que sera gravado
# Checa se temos o parametro necessario para continuarr
#Tive que corrigir para 2 aqui, antes estava 1
if len(sys.argv) < 2:
    sys.exit('ERRO: Por favor inclua um parametro apos o script, exemplo * python asa-logoff-user-v1.py nomedousuario)
    
# Tive que mudar para 0 pois com o numero 1 estava com erro
param_1 = sys.argv[1]
print('Checando o parametro fornecido de data... param_1: ' + param_1)

##### Existem 3 Formas de pegar as senhas:
## Forma 1
## Pegar o username/password das variaveis de ambiente locais
#username = os.environ.get('CISCOUSERNAME', 'None')
#password = os.environ.get('CISCOPASSWORD', 'None')

## Forma 2
## É possivel especificar no Codigo as senhas mas tem um risco de cair em maos erradas, se for subir em docker seria necessario
#username = 'admin'
#password = 'C1sco12345'

## Forma 3
## Pedir para o administrator digitar
#Primeiro dos Firewalls
username = input("ASAs - Por favor insira o usuario de serviço para executar o comando no asa:\n")
print('Por favor insira a senha desse usuario:')
password = getpass.getpass()

#Agora o IP Opcionalmente posso colocar o nome do usuário aqui em vez do parametro no comando
#vpn_user = input("ASA - Por favor insira o nome do uaurio da VPN com comportamento anomalo:\n")

secret = password
print('Obtendo acesso com as credenciais fornecidas')

# Checar se nos temos todas as variveis necessarias de ambiente caso sendo utilizadas
if (username == 'None') or (password == 'None'):
        sys.exit('ERROR: Login username/password not set in environment variables')


# Aqui é o looping principal que vai rodar todos os equipamentos especificados e fazer backup
for asa in asa_list:

    # Cria a sessao SSH utilizando o netmiko
    print('Criando a conexao ssh para ' + asa)
    device = ConnectHandler(device_type='cisco_asa', ip=asa, username=username, password=password, secret=secret)
    print('Conexao estabelecida no equipamento ' + asa)

    # Pegar a lista de comandos e jogar dentro de um Array
    print('Enviando a lista de comandos no ' + asa + ' para o usuario ' + param_1)
#
    config_commands = [
        'vpnsessiondb logoff name' + param_1, 
    ]
    #send our Cisco-specific commands and dump the output to a variable
    output = device.send_config_set(config_commands)
    print('Comandos enviados para o ' + asa)

    #print the output
    print(output)
    print('Logoff OK')

    #close the ssh session cleanly
    device.disconnect()
    print('Sessao ssh encerrada')

print('Terminou em todos os equipamentos')