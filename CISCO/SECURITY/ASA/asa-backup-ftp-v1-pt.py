#!/usr/bin/env python3

# Objetivo:
# Fazer backup da configuração dos equipamentos ASAs e enviar para o seu servidor FTP
#
# Dependências:
## pip install netmiko
## Subir servidor ftp
#
# Criado por Vagner Silva - vagner.instructor@gmail.com
# Github - https://github.com/vagner-instructor
#
# Agradecimentos para RaceFPV (https://gist.github.com/RaceFPV)


# Importar os modulos necessarios
import sys
import os
import netmiko
import getpass
from netmiko import ConnectHandler
print('Modulos Importados')

# Lista dos equipamentos para fazer backup
lista_asa = ['198.18.133.254', '198.18.133.254', '198.18.133.254']

# Parametro 1 pega um argumento para adicionar como nome do arquivo de backup que sera gravado
# Checa se temos o parametro necessario para continuar
if len(sys.argv) < 2:
    sys.exit('ERRO: Por favor inclua um parametro apos o script para adicionar no nome do backup, exemplo * python asa-backup-v1.py 2020-12-25 *')
    
param_1 = sys.argv[1]
print('Checando o parametro fornecido ... param_1: ' + param_1)

##### Existem Algumas Formas de pegar as senhas:
## Forma 1
## Pegar o username/password das variaveis de ambiente locais
#username = os.environ.get('CISCOUSERNAME', 'None')
#password = os.environ.get('CISCOPASSWORD', 'None')

##Forma 2
# Eh possivel especificar no Codigo tambem
#username = 'admin'
#password = 'C1sco12345'
#username_2 = 'vagner.silva'
#password_2 = 'C1sco12345'
#servidor_ftp = '10.16.3.177'

## Forma 3
## Pedir para o administrator digitar
# Credenciais dos Firewalls
username = input("ASAs - Por favor insira o usuario de backup:\n")
print('Por favor insira a senha do usuario de backup do ASA:')
password = getpass.getpass()

# Usuario/Senha do FTP
username_2 = input("FTP - Por favor insira o usuario do FTP:\n")
print('Por favor insira a senha do usuario do FTP:')
password_2 = getpass.getpass()

# IP do servidor de FTP
servidor_ftp = input("FTP - Por favor insira o IP do FTP:\n")

secret = password
print('Obtendo acesso com as credenciais fornecidas')

# Checa se nao ha usuario como None se nao ha setado variaveis do ambiente
if (username == 'None') or (password == 'None'):
        sys.exit('ERRO: Login username/password nao configurado nas variveis do ambiente')


# Looping que vai rodar todos os equipamentos especificados e fazer backup para o servidor FTP
for asa in lista_asa:

    # Cria a sessao SSH utilizando o netmiko
    print('Criando a conexao ssh para ' + asa)
    device = ConnectHandler(device_type='cisco_asa', ip=asa, username=username, password=password, secret=secret)
    print('Conexao estabelecida no equipamento ' + asa)

    # Lista de comandos
    print('Enviando a lista de comandos no ' + asa + '_' + param_1)
#
    config_commands = [
        'conf t',
        'terminal width 300',
        'copy /noconfirm running-config ftp://' + username_2 + ':' + password_2 + '@' + servidor_ftp + '/' + asa + '_' + param_1, 
    ]
    # Envia os comandos Cisco especificos e guarda a saida em uma variavel
    output = device.send_config_set(config_commands)
    print('Comandos enviados para o ' + asa)

    # Printar a saida de comandos executados
    print(output)
    print('Backup OK')

    # Fecha a conexao ssh do equipamento
    device.disconnect()
    print('Sessao ssh encerrada')

print('Terminou em todos os equipamentos')
