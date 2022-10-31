#!/usr/bin/python3
from datetime import datetime, timedelta
import paramiko
import pathlib
import sys
import os.path as path
from io import StringIO

class SshNodes():
    def __init__(self):
        self.locate = str(pathlib.Path(__file__).parent.resolve())
        self.two = path.abspath(path.join(__file__ ,"../../"))
        self.fserver = self.two + '/servers.txt'
        self.cmmd = 'getent hosts salt.tarcisio.me | awk "{ print $1 }"'

    def connect(self, host=None, port=22, username=None, pkey=None, passphrase=None, cmmd=None):
        if cmmd == None:
            cmmd = self.cmmd
        else:
            cmmd = cmmd

        ssh = paramiko.SSHClient()
        with open('{}/{}'.format(self.two, pkey), 'r') as file:
            pkey = file.read()
            file.close()

        private_key = StringIO(pkey)
        pk = paramiko.RSAKey.from_private_key(private_key)
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=host, port=port, username=username, pkey=pk, passphrase=passphrase, timeout=11)
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmmd)
        retorno = ssh_stdout.readlines()

        """
        print('OUT -->', type(ssh_stdout))
        print('OUT -->', type(ssh_stdin))
        print('OUT -->', bool(ssh_stderr))
        """

        ssh.close()

        if len(retorno) == 1:
            retorno = retorno[0].split()
            if len(retorno) == 2:
                return retorno
            elif len(retorno) == 10:
                if retorno[2] == '(running)':
                    return 'restart'
                else:
                    return 're-error'

            return retorno
        else:
            return False



if __name__ == '__main__':
    with open(SshNodes().fserver, 'r') as file:
            srv = file.read()
            file.close()

    for s in srv.split('\n'):
        server = s.split(';')
        if len(server) > 1:
            print('SERVER ==>', server)
            if server[0] == 'LNX':
                SshNodes().connect(host=server[1], port=server[2], username=server[3], pkey=server[4], passphrase=server[5])
