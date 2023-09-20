#!/usr/bin/env python3

# Este Script tem como objetivo fazer backup da configuracao dos equipamentos Cisco
# Eh necessario instalar algumas dependencias como:
## pip install netmiko
## pip install schedule
# Criar uma pasta para armazenar os backups, exemplo "C:\Filezilla\Backups\device\"
# Criar um arquivo com os ips dos Cisco na pasta com o nome "device-backup-schedule-devices"
# Criado por Vagner Silva - vagner.araujo@msn.com
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
    IP_LIST = open('cisco-backup-schedule-devices')
    for IP in IP_LIST:
        device = {
            'device_type': 'cisco_ios',
            'ip':   IP,
            'username': 'admin',
            'password': 'C1sco12345',
        }

        print ('\n Conectando no dispositivo ' + IP.strip() + ' \n')
        try:
            net_connect = ConnectHandler(**device)
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
        'show run',
        'show version',
    ]
        output = net_connect.send_config_set(config_commands)
        
        # Salvando o arquivo no Windows
        IP = IP.rstrip("\n")
        IP = IP.rstrip("'")
        device_BACKUP_FILE = "C:/Filezilla/Backups/device/" + "%a-%a-device-backup-file.txt" % (IP, FILETIME)
        SAVE_FILE = open(device_BACKUP_FILE, 'w')
        SAVE_FILE.write(output)
        SAVE_FILE.close
        print('Backup finalizado')
        net_connect.disconnect()
        print('Sessao ssh encerrada')

schedule.every().minute.at(":00").do(BACKUP)
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