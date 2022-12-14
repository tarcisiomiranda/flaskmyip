from lib.cloudflare import TMCloudflare
from lib.telegram import TMTelegram
from lib.getpubip import Getpubip
from lib.ssh_cmd import SshNodes
from lib.home_ip import HomeIP
from lib.api_do import API_DO
from datetime import datetime
from decouple import config
from os.path import exists
import subprocess
import requests
import pathlib
import socket
import time
import json
import sys
import os


class Flaskmyip:
    def __init__(self, args=None):
        # Cloud Flare
        self.STATUS = config('STATUS', default=False)
        self.ZONE_ID = config('ZONE_ID', default=False)
        self.RECORD_ID = config('RECORD_ID', default=False)
        self.CF_API_KEY = config('CF_API_KEY', default=False)
        self.CF_EMAIL = config('CF_EMAIL', default='your-email-cloudflare')
        # Telegram
        self.BOT_ID = config('BOT_ID', default=False)
        self.CHAT_ID = config('CHAT_ID', default=False)
        # Dir log
        self.DIR_LOG = config('DIR_LOG', default='/var/log/ip_update/')
        # Dir log and File log
        if args == None:
            self.rec_log = False
        elif args:
            self.rec_log = True
        self.local_dir = str(pathlib.Path(__file__).parent.resolve())
        self.filelog = self.DIR_LOG + 'update.log'
        self.filetxt = self.local_dir + '/ip.txt'
        self.filerec = self.local_dir + '/domains.txt'
        self.filedte = self.local_dir + '/date_renew_ip.txt'
        self.fserver = self.local_dir + '/servers.txt'
        self.fwl_do = config('FWL_DO', default=False)
        # print('SYS ARG :', self.rec_log)

    def get_result(self):
        key_cf = {
            'ZONE_ID': self.ZONE_ID,
            'CF_EMAIL': self.CF_EMAIL,
            'CF_API_KEY': self.CF_API_KEY
        }

        cf = TMCloudflare()
        res = cf.get_records(**key_cf)

        if res is None:
            MSG = 'Error when querying the CloudFlare'
            er_data = {
                'CHAT_ID': self.CHAT_ID,
                'BOT_ID': self.BOT_ID,
                'MSG': MSG
            }
            TMTelegram().send_msg(**er_data)
            print(MSG)
            sys.exit(1)

        return res

    def public_ipv4(self):
        # Get ipv4 public
        gp = Getpubip()
        pub_ipv4 = gp.getipv4().get('ip')
        
        return pub_ipv4

    def ipv4_file(self):
        file_exists = exists(self.filetxt)
        if file_exists == False:
            print('File n??o existe!')
            with open(self.filetxt,'w') as file:
                file.write('Arquivo criado com sucesso!')
                file.close()

            return 'Novo Arquivo!'
        else:
            with open(self.filetxt, 'r+', encoding = 'utf-8') as file:
                myip = file.read()
                file.close()

            return myip

    def read_domain(self):
        try:
            with open(self.filerec, 'r+', encoding = 'utf-8') as file:
                my_domains = file.read()
                file.close()

            count = 0
            domains = []
            for d in my_domains.splitlines():
                domains.append(d.split(';'))

            return domains

        except Exception as err:
            return {
                'status': False,
                'message': 'Error when getting ipv4 - {}'.format(err)
            }

    def write_ip(self, ip=None):
        try:
            with open(self.filetxt,'w') as file:
                file.write(ip)

            return True

        except Exception as err:
            return {
            'status': 'Error',
            'message': 'Error when getting ipv4 - {}'.format(err)
        }

    def send_check(self, **kwargs):
        if len(kwargs) > 1:
            res_telegram = TMTelegram().send_msg(**kwargs)
            return res_telegram

    def check_install(self):
        # Check directory and file
        dir_log = os.path.exists(self.DIR_LOG)
        if dir_log == False:
            os.mkdir(self.DIR_LOG)

        fil_log = exists(self.filelog)
        if fil_log == False:
            with open(self.filelog,'w') as file:
                file.write('Arquivo de log criado com sucesso!')
                file.close()

        fil_dte = exists(self.filedte)
        if fil_dte == False:
            with open(self.filedte,'w') as file:
                file.write('Arquivo de data criado com sucesso!')
                file.close()

        fil_srv = exists(self.fserver)
        if fil_srv == False:
            with open(self.fserver,'w') as file:
                file.write('Arquivo de servidores criado com sucesso!')
                file.close()

        if dir_log and fil_log and fil_dte and fil_srv:
            res_check_install = True
        else:
            res_check_install = False

        return res_check_install

    def update_rules(self, aws=False, do=False, oci=False):
        pub_ipv4 = self.public_ipv4()
        retorno = API_DO().update_fw(ipv4=pub_ipv4, fwl=self.fwl_do)

        if bool(retorno):
            return retorno

        else:
            return False

    def check_ipv4(self):
        # Check dir and log file
        ci = self.check_install()
        if ci == False:
            retry = self.check_install()
            if retry == False:
                raise Exception({
                    'status': 'Error',
                    'message': 'Error when create dir log or file log'
                })

        pub_ipv4 = self.public_ipv4()
        file_ipv4 = self.ipv4_file()

        if pub_ipv4 != file_ipv4:
            file_domains = self.read_domain()
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
            result = self.get_result()
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
                'CF_EMAIL': self.CF_EMAIL,
                'CF_API_KEY': self.CF_API_KEY,
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

            # update fwl_do
            update_fwl_do = self.update_rules()
            data_res = {
                'BOT_ID': self.BOT_ID,
                'CHAT_ID': self.CHAT_ID,
                'Domains Success': res_compose_ok,
                'Domains Error': res_compose_er,
                'NEW_IP': pub_ipv4,
                'OLD_IP': file_ipv4,
                'FWL_DO': update_fwl_do
            }

            if len(res_compose_ok) > 1:
                self.write_ip(ip=pub_ipv4)
                res = self.send_check(**data_res)
                data_res.update(res)

            if self.rec_log:
                with open(self.filelog,'a') as file:
                    file.write(str(data_res.get('MSG')))
                    file.close()

            return data_res

        # No changes IPV4 - All Ok
        sys.exit(0)

    def restart_salt(self):
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
                'CHAT_ID': self.CHAT_ID,
                'BOT_ID': self.BOT_ID,
                'IC_RESTART': socket.gethostname(),
                'OTHER': True
            }
            self.send_check(**res_data)
            return True

        else:
            return False

    def restart_via_ssh_salt(self):

        pub_ipv4 = self.public_ipv4()
        # reiniciar servidores que possuem salt
        with open(self.fserver, 'r') as file:
            srv = file.read()
            file.close()

        servers_ok = []
        servers_er = []
        for s in srv.split('\n'):
            server = s.split(';')
            try:
                if len(server) > 1:
                    print('SERVER >', server)
                    if server[0] == 'LNX':
                        res_ssh = SshNodes().connect(host=server[1], port=server[2], username=server[3], pkey=server[4], passphrase=server[5])

                        if pub_ipv4 != res_ssh[0]:
                            res_salt = SshNodes().connect(host=server[1], port=server[2], username=server[3], pkey=server[4], passphrase=server[5], \
                                cmmd='systemctl restart salt-minion && sleep 0.4 && systemctl status salt-minion | grep "Active:"')
                            print('IP4_DIFF', res_salt)
                            if res_salt == 'restart':
                                servers_ok.append(server[1])
                            elif res_salt == 're-error':
                                servers_er.append(server[1])

            except Exception as err:
                servers_er.append(server[1])
                print(str(err))

        if servers_ok != []:
            res_data = {
            'CHAT_ID': self.CHAT_ID,
            'BOT_ID': self.BOT_ID,
            'IC_RESTART': servers_ok,
            'IC_ERROR': servers_er,
            'OTHER': True
            }
            self.send_check(**res_data)
            return True

        else:
            return False



def run_and_install():
    act_log = False
    re_salt = False
    if len(sys.argv) == 1:
        print('put arg --log or --restart_salt')
        sys.exit(1)

    for arg in sys.argv:
        if arg == '--log':
            act_log = True
        if arg == '--restart_salt':
            re_salt = True

    if re_salt:
        Flaskmyip().restart_salt()
    elif act_log:
        Flaskmyip(args=True).check_ipv4()
        Flaskmyip().restart_via_ssh_salt()

    # Exemples test
    # Flaskmyip().get_result()
    # Flaskmyip().ipv4_file()
    # Flaskmyip().read_domain()
    # Flaskmyip().check_install()
    # Flaskmyip().check_ipv4()
    # Flaskmyip(args=True).restart_salt()

run_and_install()
# Flaskmyip().update_rules()
