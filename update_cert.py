from datetime import datetime
import requests
import argparse
import urllib3
import base64
import yaml
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

'''
python3 update_cert.py --mode cert --token 633d9314dcd9e982adb2c724a8bce3d43297bf01 --path '/srv/nginx/etc/certs/'
'''

SALT_API_URL = 'https://192.168.29.40:8000'

def generate_salt_token(url, username, password, eauth='pam'):
    login_url = f"{url}/login"
    headers = {'Accept': 'application/x-yaml'}
    data = {
        'username': username,
        'password': password,
        'eauth': eauth
    }

    try:
        response = requests.post(login_url, headers=headers, data=data, verify=False)
        response.raise_for_status()

        token_info = yaml.safe_load(response.text)['return'][0]
        start_date = datetime.fromtimestamp(token_info['start'])
        expire_date = datetime.fromtimestamp(token_info['expire'])

        return {
            'token': token_info['token'],
            'start_date': start_date.strftime('%Y-%m-%d %H:%M:%S'),
            'expire_date': expire_date.strftime('%Y-%m-%d %H:%M:%S')
        }
    except requests.RequestException as e:
        print(f"Erro ao gerar o token: {e}")
        return None

def get_cert(token=None, cert_path='/etc/nginx/certs/'):
    headers = {
        "Accept": "application/x-yaml",
        "X-Auth-Token": token
    }

    # Cmmd
    pub_cmd = '''cat /srv/blog/acme.json | jq -r '(.Certificates[] | if .Domain.Main == "*.tarcisio.me" then .Certificate else empty end)\''''
    key_cmd = '''cat /srv/blog/acme.json | jq -r '(.Certificates[] | if .Domain.Main == "*.tarcisio.me" then .Key else empty end)\''''

    # Run
    pub_response = requests.post(
        SALT_API_URL,
        headers=headers,
        data={
            "client": "local",
            "tgt": "enc-linode",
            "fun": "cmd.run",
            "arg": pub_cmd
        },
        verify=False
    )

    key_response = requests.post(
        SALT_API_URL,
        headers=headers,
        data={
            "client": "local",
            "tgt": "enc-linode",
            "fun": "cmd.run",
            "arg": key_cmd
        },
        verify=False
    )

    if pub_response.status_code == 200 and key_response.status_code == 200:
        _pub = yaml.safe_load(pub_response.text)
        _key = yaml.safe_load(key_response.text)

        value_pub = list(_pub['return'][0].items())[0][1]
        value_key = list(_key['return'][0].items())[0][1]

        pub = base64.b64decode(value_pub).decode('utf-8')
        key = base64.b64decode(value_key).decode('utf-8')

        # Gravando os arquivos
        print('Generate pub file...')
        with open(f'{cert_path}certificate.crt', 'w') as file:
            file.write(pub)

        print('Generate key file...')
        with open(f'{cert_path}certificate.key', 'w') as file:
            file.write(key)
    else:
        print("Error while fetching certificate or key.")

def test_ping(token=None):
    headers = {
        "Accept": "application/x-yaml",
        "X-Auth-Token": TOKEN
    }

    data = {
        "client": "local",
        "tgt": "*",
        "fun": "test.ping"
    }

    response = requests.post(SALT_API_URL, headers=headers, data=data, verify=False)

    if response.status_code == 200:
        print("PING", response.text)
    else:
        print("Error:", response.status_code, response.text)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script para interagir com a API do SaltStack")
    parser.add_argument('--token', help="Token de autenticação para a API do SaltStack")
    parser.add_argument('--username', help="Nome de usuário para autenticação na API do SaltStack")
    parser.add_argument('--password', help="Senha para autenticação na API do SaltStack")
    parser.add_argument('--mode', default='ping', help='App mode: "dev" ou "prd"', required=True)
    parser.add_argument('--path', default='/etc/nginx/certs/', help="Caminho onde o certificado será gravado")

    args = parser.parse_args()
    TOKEN = args.token
    LOCAL = args.path
    if args.token:
        if args.mode.lower() == 'cert':
            print('Pegando o certificado ...')
            get_cert(TOKEN, LOCAL)
        else:
            print('Fazendo o test.ping ...')
            test_ping(TOKEN)

    elif args.username and args.password:
        token_info = generate_salt_token(SALT_API_URL, args.username, args.password)
        if token_info:
            TOKEN = token_info['token']
            print(f"Token gerado: {TOKEN}")
        else:
            print("Falha ao gerar o token. Verifique suas credenciais e tente novamente.")
            exit(1)
    else:
        print("Username e password são necessários para gerar um novo token.")
        exit(1)
