from datetime import datetime
from decouple import config
from os.path import exists
from requests import get
import requests
import pathlib
import time
import json
import sys
import os


# Cloud Flare
CF_API_KEY = config('CF_API_KEY', default=False)
RECORD_ID = config('RECORD_ID', default=False)
ZONE_ID = config('ZONE_ID', default=False)
CF_EMAIL = config('CF_EMAIL', default='your-email-cloudflare')
CF_DOMAIN = config('CF_DOMAIN', default='your-record-domain')
CF_TYPE = config('CF_TYPE', default='A')
STATUS = config('STATUS', default=False)
# Telegram
BOT_ID = config('BOT_ID', default=False)
CHAT_ID = config('CHAT_ID', default=False)
FLARE = '\n Dominio: ' + CF_DOMAIN + '\n Atualizado com sucesso!'
url = 'https://api.telegram.org/{}/sendmessage'.format(BOT_ID)
# https://api.telegram.org/bot5561402281:AAHpIpMbgFJDj6QVYg8Z7lG3i6FCr3Nfm7o/getUpdates

localDir = str(pathlib.Path(__file__).parent.resolve())
filetxt = localDir + '/ip.txt'
filerec = localDir + '/dnsrec.txt'
domain_update = False
newIp = False
found = False

# Inicio
ip = get('https://ip.tarcisio.me').text
file_exists = exists(filetxt)
newfile = False

ip = json.loads(ip)
ip = ip.get('ip')

def sendMsg(ip):
    params = (
            ('chat_id', CHAT_ID),
            ('text', 'Novo ip: ' + ip + FLARE),
        )
    response = requests.get(url, params=params)

if file_exists == False:
    print('File não existe!')
    with open(filetxt,'w') as file:
        file.write('Arquivo criado com sucesso!')
        file.close()
    newfile = True

with open(filetxt, 'r+', encoding = 'utf-8') as file:
    myip = file.read()
    file.close()

if myip != ip:
    with open(filetxt,'r') as file:
        myip = file.read()
        newIp = True

# CloudFlare
if newIp:
    resp = requests.get(
        'https://api.cloudflare.com/client/v4/zones/{}/dns_records'.format(ZONE_ID),
        headers={
            'X-Auth-Email': CF_EMAIL,
            'X-Auth-Key': CF_API_KEY,
            'Content-Type': 'application/json'
        })
    dump = json.dumps(resp.json(), indent=4, sort_keys=True)
    print('Dumps', dump, '\n', '--------------------------')
    result = json.loads(json.dumps(resp.json()))


    # Get Records
    records = []
    # TODO - Verificar aqui
    for domain in result['result']:
        records.append([domain.get('type'), domain.get('name'), domain.get('id')])

    if records != []:
        print('records', records)
        # Pegando os 2 primeiros itens da lista e igualando, depois vamos pegar o record_id
        for dm in records:
            # TODO - Verificar se o dominio continua com o mesmo nome, teste do cu.
            if ([CF_TYPE,CF_DOMAIN]) == dm[0:2]:
                RECORD_ID = dm[2]
                found = True
    print('-------------------------------------------------')

# Send new IP for cloudflare
if found == True and newIp:
    try:
        resp = requests.put(
            'https://api.cloudflare.com/client/v4/zones/{}/dns_records/{}'.format(
                ZONE_ID, \
                RECORD_ID),
            headers={
                'X-Auth-Key': CF_API_KEY,
                'X-Auth-Email': CF_EMAIL,
                'Content-Type': 'application/json'
            },
            json={
                'type': CF_TYPE,
                'name': CF_DOMAIN,
                'content': ip,
                'ttl': 60,
                'proxied': False
            })
        dump = json.dumps(resp.json(), indent=4, sort_keys=True)
        check_status = json.loads(dump)['success']

        if resp.status_code == 200:
            STATUS = True
        
        if check_status == True:
            domain_update = True

    except:
        print('Verificar se o update está correto')
        sys.exit(1)

if (myip != ip or newfile == True) and STATUS == True:
    with open(filetxt,'w') as file:
        file.write(ip)
    sendMsg(ip)

if newIp == True and STATUS == True and domain_update == True:
    MSG=f"""
----------------------
DATA: 14/09/2022 10:42
OLD IP: {myip}
NEW IP: {ip}
DOMAIN: {CF_DOMAIN}
----------------------
"""
    print(MSG)
elif STATUS == False and domain_update == False:
    print('Verificar API CF :', datetime.today().strftime('%d/%m/%Y %H:%M'))
else:
    print('Sem alterações :', datetime.today().strftime('%d/%m/%Y %H:%M'))
