#!/usr/bin/env python3

# Este Script tem como objetivo fazer backup da configuracao dos equipamentos ASAs
# Eh necessario instalar algumas dependencias como:
## pip install netmiko
## pip install schedule
# Criar uma pasta para armazenar os backups, exemplo "C:\Filezilla\Backups\ASA\"
# Criar um arquivo com os ips dos ASAs na pasta com o nome "asa-backup-schedule-devices"
# Criado por Vagner Silva - vagner.instructor@gmail.com
# Github - https://github.com/vagner-instructor
#
# Agradecimentos para NetworkEvolution em https://www.youtube.com/watch?v=Xb-8_GvsTfs 
# Agradecimentos para Datacamp em https://www.datacamp.com/community/tutorials/reading-writing-files-python

from netmiko import ConnectHandler
from netmiko.ssh_exception import NetMikoTimeoutException
from netmiko.ssh_exception import NetMikoAuthenticationException
from paramiko.ssh_exception import SSHException
import time
import datetime
import schedule

def BACKUP():
    FILETIME = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M')
    TNOW = datetime.datetime.now().replace(microsecond=0)
    IP_LIST = open('asa-backup-schedule-devices')
    for IP in IP_LIST:
        ASA = {
            'device_type': 'cisco_asa',
            'ip':   IP,
            'username': 'admin',
            'password': 'C1sco12345',
        }

        print ('\n Conectando no dispositivo ' + IP.strip() + ' \n')
        try:
            net_connect = ConnectHandler(**ASA)
        except NetMikoTimeoutException:
            print ('Dispositivo não pode ser alcançado' )
            continue

        except NetMikoAuthenticationException:
            print ('Falha na autenticação' )
            continue

        except SSHException:
            print ('Tenha certeza que o SSH está habilitado' )
            continue

        print(' Inicializando o backup às ' + str(TNOW))
        
        #Enviando os comandos para backup e versão
        config_commands = [
        'terminal pager 0',
        'terminal width 300',
        'end',
        'more system:running-config', 
        'show run',
        'show version',
    ]
        output = net_connect.send_config_set(config_commands)
        
        # Salvando o arquivo no Windows
        IP = IP.rstrip("\n")
        IP = IP.rstrip("'")
        ASA_BACKUP_FILE = "C:/Filezilla/Backups/ASA/" + "%a-%a-asa-backup-file.txt" % (IP, FILETIME)
        SAVE_FILE = open(ASA_BACKUP_FILE, 'w')
        SAVE_FILE.write(output)
        SAVE_FILE.close
        print('Backup finalizado')
        net_connect.disconnect()
        print('Sessao ssh encerrada')

schedule.every().day.at("10:30").do(BACKUP)
#Cada empresa tem uma janela diferente e um requisito em particular, exemplos abaixo
#schedule.every(10).minutes.do(BACKUP)
#schedule.every().hour.do(BACKUP)
#schedule.every().day.at("10:30").do(BACKUP)
#schedule.every().monday.do(BACKUP)
#schedule.every().wednesday.at("13:15").do(BACKUP)
#schedule.every().minute.at(":00").do(BACKUP)
while True:
    schedule.run_pending()
    time.sleep(1)