from datetime import datetime, timedelta, date
from apscheduler.triggers.cron import CronTrigger
from flask_apscheduler import APScheduler
from flask import Flask, jsonify, current_app
from os.path import exists
from pytz import timezone
import subprocess
import threading
import argparse
import pathlib
import logging
import socket
import json
import sys
import os
# Others
import requests
from decouple import config
# Clouds
from clouds.api_linode import API_LINODE
from clouds.api_oci import API_OCI
from clouds.api_aws import API_AWS
from clouds.api_do import API_DO
# Firewalls
from lib.cloudflare import TMCloudflare
from lib.telegram import TMTelegram
from lib.getpubip import Getpubip
from lib.ssh_cmd import SshNodes
from lib.home_ip import HomeIP

''' Process Lock '''
processing_lock = threading.Lock()

''' Logging '''
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

''' Start Flask and Scheduler '''
app = Flask(__name__)
scheduler = APScheduler()
tz = timezone('America/Sao_Paulo')
class ConfigScheduler:
    SCHEDULER_API_ENABLED = True

''' Cron for jobs '''
trigger_check_ip = CronTrigger(minute='*', timezone=tz)
trigger_ssh_salt = CronTrigger(hour=1, minute=0, timezone=tz)

class Flaskmyip:
    def __init__(self, args=None):
        # Cloudflare
        self.STATUS = config('STATUS', default=False)
        self.ZONE_ID = config('ZONE_ID', default=False)
        self.RECORD_ID = config('RECORD_ID', default=False)
        self.CF_API_KEY = config('CF_API_KEY', default=False)
        self.CF_EMAIL = config('CF_EMAIL', default='your-email-cloudflare')
        # Telegram
        self.BOT_ID = config('BOT_ID', default=False)
        self.CHAT_ID = config('CHAT_ID', default=False)
        self.rec_log = False if args == None else True
        self.local_dir = str(pathlib.Path(__file__).parent.resolve())
        self.filelog  = self.local_dir + '/flaskmyip.log'
        self.filetxt  = self.local_dir + '/datasets/ip.txt'
        self.filerec  = self.local_dir + '/datasets/domains.txt'
        self.filedte  = self.local_dir + '/datasets/date_renew_ip.txt'
        self.fserver  = self.local_dir + '/datasets/servers.txt'
        # Firewall API
        self.fwl_do = config('FWL_DO', default=False)
        self.fwl_aws = config('FWL_AWS_GROUP_ID', default=False)
        # print('SYS ARG :', self.rec_log)

''' Instance Flaskmyip '''
_flaskmyip = Flaskmyip()

def create_response(data, status_code=200):
    with app.app_context():
        response = jsonify(data)
        if current_app.config["JSONIFY_PRETTYPRINT_REGULAR"] or current_app.debug:
            response = current_app.response_class(
                response=response.response,
                status=status_code,
                mimetype="application/json",
                content_type=response.content_type,
                headers=response.headers,
                direct_passthrough=True,
            )
    return response

@app.route('/', methods=['GET'])
def agora():
    current_time = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')
    horario = f' *\033[1m Horario atual:\033[0m {current_time}'
    print(horario)
    return current_time

def get_result():
    key_cf = {
        'ZONE_ID': _flaskmyip.ZONE_ID,
        'CF_EMAIL': _flaskmyip.CF_EMAIL,
        'CF_API_KEY': _flaskmyip.CF_API_KEY
    }

    cf = TMCloudflare()
    res = cf.get_records(**key_cf)

    if res is None:
        MSG = 'Error when querying the CloudFlare'
        er_data = {
            'CHAT_ID': _flaskmyip.CHAT_ID,
            'BOT_ID': _flaskmyip.BOT_ID,
            'MSG': MSG
        }
        TMTelegram().send_msg(**er_data)
        print(MSG)
        return jsonify({"error": f'Erro update CloudFlare'}, 500)

    return res

def public_ipv4():
    gp = Getpubip()
    pub_ipv4 = gp.getipv4().get('ip')

    return pub_ipv4

def ipv4_file():
    file_exists = exists(_flaskmyip.filetxt)
    if file_exists == False:
        print('File não existe!')
        with open(_flaskmyip.filetxt,'w') as file:
            file.write('Arquivo criado com sucesso!')
            file.close()

        return 'Novo Arquivo!'
    else:
        with open(_flaskmyip.filetxt, 'r+', encoding = 'utf-8') as file:
            myip = file.read()
            file.close()

        return myip

def read_domain():
    try:
        with open(_flaskmyip.filerec, 'r+', encoding = 'utf-8') as file:
            my_domains = file.read()
            file.close()

        domains = []
        for d in my_domains.splitlines():
            domains.append(d.split(';'))

        return domains

    except Exception as err:
        return {
            'status': False,
            'message': 'Error when getting ipv4 - {}'.format(err)
        }

def write_ip(ip=None):
    try:
        with open(_flaskmyip.filetxt,'w') as file:
            file.write(ip)

        return True

    except Exception as err:
        return {
        'status': 'Error',
        'message': 'Error when getting ipv4 - {}'.format(err)
    }

def send_check(**kwargs):
    if len(kwargs) > 1:
        res_telegram = TMTelegram().send_msg(**kwargs)
        return res_telegram

def check_install():
    # Check directory and file
    '''
    dir_log = os.path.exists(_flaskmyip.DIR_LOG)
    if dir_log == False:
        os.mkdir(_flaskmyip.DIR_LOG)
    '''

    fil_log = exists(_flaskmyip.filelog)
    if fil_log == False:
        with open(_flaskmyip.filelog,'w') as file:
            file.write('Arquivo de log criado com sucesso!')
            file.close()

    fil_dte = exists(_flaskmyip.filedte)
    if fil_dte == False:
        with open(_flaskmyip.filedte,'w') as file:
            file.write('Arquivo de data criado com sucesso!')
            file.close()

    fil_srv = exists(_flaskmyip.fserver)
    if fil_srv == False:
        with open(_flaskmyip.fserver,'w') as file:
            file.write('Arquivo de servidores criado com sucesso!')
            file.close()

    if fil_log and fil_dte and fil_srv:
        res_check_install = True
    else:
        res_check_install = False

    return res_check_install

def update_rules(_do=False, _aws=False, _oci=False, _lin=False):
    pub_ipv4 = public_ipv4()
    _cloud = ''
    try:
        if _do:
            _cloud = 'Digital Ocean'
            retorno = API_DO().update_fw(ipv4=pub_ipv4, fwl=_flaskmyip.fwl_do)
        elif _aws:
            _cloud = 'AWS'
            retorno = API_AWS(ipv4=pub_ipv4, gid=_flaskmyip.fwl_aws).update_rules()
        elif _oci:
            _cloud = 'OCI'
            retorno = API_OCI().update_rules(ipv4=pub_ipv4)
        elif _lin:
            _cloud = 'Linode'
            retorno = API_LINODE().replace_rule(ipv4=pub_ipv4, fwl_name='main_linux')
        else:
            return None

    except Exception as err:
        print('Update Rules, cloud {}: err: {}'.format(_cloud, str(err)))
        return False

    return retorno if retorno else False

@scheduler.task(id='check_ipv4', trigger=trigger_check_ip, misfire_grace_time=50)
@app.route('/check_ipv4', methods=['GET'])
def check_ipv4():
    with processing_lock:
        # Check dir and log file
        ci = check_install()
        if ci == False:
            retry = check_install()
            if retry == False:
                raise Exception({
                    'status': 'Error',
                    'message': 'Error when create dir log or file log'
                })

        pub_ipv4 = public_ipv4()
        file_ipv4 = ipv4_file()

        if pub_ipv4 != file_ipv4:
            file_domains = read_domain()
            params = (
                    ('n_ip', pub_ipv4),
                    ('pass', config('PASSWD')),
                )
            res = requests.get(config('HOME_URL_CHECK'), params=params)
            # TODO - melhorar a verificacao
            if res.status_code == 200:
                pass

            # records
            records = []
            result = get_result()
            for domain in result['result']:
                records.append([domain.get('type'),
                    domain.get('name'),
                    domain.get('id'),
                    domain.get('zone_id')]
                    )

            update_list = []
            for fd in file_domains:
                for rc in records:
                    if fd == rc[0:2]:
                        if rc not in update_list:
                            update_list.append(rc)

            key_cf = {
                'CF_EMAIL': _flaskmyip.CF_EMAIL,
                'CF_API_KEY': _flaskmyip.CF_API_KEY,
                'NEW_IPV4': pub_ipv4
            }

            res_compose_ok = []
            res_compose_er = []
            for compose in update_list:
                res = TMCloudflare().update_record(compose, **key_cf)
                if res.get('status') == 500:
                    res_compose_er.append(res)
                else:
                    res_compose_ok.append(res)

            # Update firewall
            print('| ------ START UPDATES FIREWALL ------ |')
            update_fwl_do =  update_rules(_do=True)
            update_fwl_aws = update_rules(_aws=False)
            update_fwl_lin = update_rules(_lin=True)
            update_fwl_oci = update_rules(_oci=True)
            print('| ------- END UPDATES FIREWALL ------- |')
            data_res = {
                'BOT_ID': _flaskmyip.BOT_ID,
                'CHAT_ID': _flaskmyip.CHAT_ID,
                'UPDATE': {
                    'Domains Success': res_compose_ok,
                    'Domains Error': res_compose_er,
                    'NEW_IP': pub_ipv4,
                    'OLD_IP': file_ipv4,
                    'FWL_DO': update_fwl_do,
                    'FWL_AWS': update_fwl_aws,
                    'FWL_LIN': update_fwl_lin,
                    'FWL_OCI': update_fwl_oci,
                }
            }

            if len(res_compose_ok) > 1:
                write_ip(ip=pub_ipv4)
                res = send_check(**data_res)
                data_res.update(res)

            if _flaskmyip.rec_log:
                with open(_flaskmyip.filelog,'a') as file:
                    file.write(str(data_res.get('MSG')))
                    file.close()

            return data_res

    # No changes IPV4 - All Ok
    response_data = {"message": "No changes detected in IPV4. All OK."}
    return create_response(response_data)

# Legacy function (ja implementei outra ideia melhor)
def restart_salt():
    salt_home_ip = HomeIP().get_home_ip()
    salt_url_ip = socket.gethostbyname(config('HOME_SALT_URL'))

    commd = 'sudo systemctl restart salt-minion'
    res = {}
    if salt_home_ip != salt_url_ip:
        proc = subprocess.Popen(commd, stdout=subprocess.PIPE, shell=True, \
        stderr=subprocess.PIPE, universal_newlines=True)
        out, err = proc.communicate()

        res = {
            'stdout': out.strip(),
            'stderr': err.strip(),
        }

    if res.get('stderr') == '':
        res_data = {
            'CHAT_ID': _flaskmyip.CHAT_ID,
            'BOT_ID': _flaskmyip.BOT_ID,
            'RESTART' :{
                'IC_RESTART': socket.gethostname(),
            }
        }
        send_check(**res_data)
        return True

    else:
        return False

@scheduler.task(id='restart_ssh_salt', trigger=trigger_ssh_salt, misfire_grace_time=50)
@app.route('/restart_ssh_salt', methods=['GET'])
def restart_ssh_salt():
    with processing_lock:
        pub_ipv4 = public_ipv4()
        # reiniciar servidores que possuem salt
        with open(_flaskmyip.fserver, 'r') as file:
            srv = file.read()
            file.close()

        servers_ok = []
        servers_er = []
        for s in srv.split('\n'):
            server = s.split(';')
            try:
                if len(server) > 1:
                    if server[0] == 'LNX':
                        # Verificar se o IP é o mesmo
                        res_ssh = SshNodes().connect(host=server[1], port=server[2], username=server[3], pkey=server[4], passphrase=server[5])
                        if pub_ipv4 == res_ssh[0]:
                            # Linux | systemd || init
                            if server[6].lower() == 'systemd':
                                cmmd_exe='systemctl restart salt-minion && sleep 0.4 && systemctl status salt-minion | grep "Active:"'
                            else:
                                cmmd_exe='''\
                            restart_salt=$({ service salt-minion restart && sleep 0.4 && service salt-minion status;} 2>&1 \
                            | grep -E 'running|status' ); echo "$restart_salt"
                                '''
                            # Full command ssh
                            res_salt = SshNodes().connect(host=server[1], port=server[2], username=server[3], pkey=server[4],\
                                    passphrase=server[5], cmmd=cmmd_exe, init_system=server[6])
                            if res_salt:
                                servers_ok.append(server[1])
                            elif not res_salt:
                                servers_er.append(server[1])

            except Exception as err:
                servers_er.append(server[1])
                print(str(err))

        if servers_ok != []:
            res_data = {
            'CHAT_ID': _flaskmyip.CHAT_ID,
            'BOT_ID': _flaskmyip.BOT_ID,
            'RESTART' :{
                'OK': servers_ok,
                'ER': servers_er,
                }
            }

            send_check(**res_data)
            return jsonify({"success": f'Restart with success salt cloud vms'}, 200)

        else:
            return jsonify({"error": f'Erro restart salt cloud vms'}, 500)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process some inputs.')
    parser.add_argument('--logging', action='store_true',
                        help='activate logging')
    parser.add_argument('--restart', action='store_true',
                        help='restart salt')

    ''' Args '''
    args = parser.parse_args()
    run_logging = args.logging
    run_restart = args.restart

    ''' Setup Scheduler '''
    app.config.from_object(ConfigScheduler())
    scheduler.init_app(app)
    scheduler.start()

    ''' Set Pretty Regular Flask '''
    app.config["JSONIFY_PRETTYPRINT_REGULAR"] = True
    # app.config['AUTH_REQUIRED'] = app_auth

    ''' Time Now '''
    agora()

    if run_logging:
        Flaskmyip(args=True)
        print(' * Basic Auth: Enabled')
        print(' * User: admin')

        print(' * Running: Flask Development...')
        app.run(debug=True, host='0.0.0.0', port=3002, use_reloader=True)

    if run_restart:
        print(' * Running:  Production...')
        app.run(debug=True, host='0.0.0.0', port=3002, use_reloader=True)

    else:
        print('Invalid app mode. Use "dev" or "prd".')
        print('Use --auth to request a authenticated route".')
