#!/usr/bin/env python3

# Logoff user from multiple Cisco ASA Firewalls
# Dependencies:
## pip install netmiko
#
# Created by Vagner Silva - vagner.instructor@gmail.com
# Github - https://github.com/vagner-instructor
#
# Thanks to RaceFPV (https://gist.github.com/RaceFPV)

# Importar os modulos necessarios
import sys
import os
import netmiko
import getpass
from netmiko import ConnectHandler
print('Modulos Importados')

# Lista dos equipamentos para fazer backup
lista_asa = ['198.18.133.254', '198.18.133.254']

# Parametro 1 pega um argumento para adicionar como nome do usuario para derrubar a sessao da vpn
# Checa se temos o parametro necessario para continuarr
# Tive que corrigir para 2 aqui, antes estava 1
if len(sys.argv) < 2:
    sys.exit('ERRO: Por favor inclua um parametro apos o script, exemplo * python asa-logoff-user-v1.py nomedousuario')
    
# Tive que mudar para 0 pois com o numero 1 estava com erro
param_1 = sys.argv[1]
print('Checando o parametro fornecido de data... param_1: ' + param_1)

##### Existem Algumas Formas de pegar as senhas:
## Forma 1
## Pegar o username/password das variaveis de ambiente locais
#username = os.environ.get('CISCOUSERNAME', 'None')
#password = os.environ.get('CISCOPASSWORD', 'None')

## Forma 2
## E possivel especificar no Codigo as senhas mas tem um risco de cair em maos erradas, se for subir em docker seria necessario
# username = 'admin'
# password = 'C1sco12345'

## Forma 3
## Pedir para o administrator digitar
#Primeiro dos Firewalls
username = input("ASAs - Por favor insira o usuario de serviço para executar o comando no asa:\n")
print('Por favor insira a senha desse usuario:')
password = getpass.getpass()

#Podemos adicionar o nome do usuário aqui em vez do parametro no comando
#vpn_user = input("ASA - Por favor insira o nome do usuario da VPN com comportamento anômalo:\n")

secret = password
print('Obtendo acesso com as credenciais fornecidas')

# Aqui é o looping principal que vai rodar todos os equipamentos especificados e fazer backup
for asa in lista_asa:

    # Cria a sessao SSH utilizando o netmiko
    print('Criando a conexao ssh para ' + asa)
    device = ConnectHandler(device_type='cisco_asa', ip=asa, username=username, password=password, secret=secret)
    print('Conexao estabelecida no equipamento ' + asa)

    # Pegar a lista de comandos e jogar dentro de um Array
    print('Enviando a lista de comandos no ' + asa + ' para o usuario ' + param_1)
#
    config_commands = [
        'end',
        'vpn-sessiondb logoff name ' + param_1 + ' noconfirm',
    ]
    # Enviar os comandos para o dispositivo e armazenar a saida em uma variavel
    output = device.send_config_set(config_commands)
    print('Comandos enviados para o ' + asa)

    #print the output
    print(output)
    print('Logoff OK')

    #close the ssh session cleanly
    device.disconnect()
    print('Sessao ssh encerrada')

print('Terminou em todos os equipamentos')


# Criado por Vagner Silva - vagner.araujo@msn.com
# Github - https://github.com/vagner-instructor