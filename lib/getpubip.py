from requests import get
import json
import re
import urllib3
urllib3.disable_warnings()


class Getpubip:
    def __init__(self):
        self.url = 'https://ip.tarcisio.me'

    def validade(self, ip):
        pattern = re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')
        return bool(pattern.match(ip))

    def getipv4(self):
        try:
            ip = get(self.url, timeout=6, verify=False).text
            ip = json.loads(ip)
            return ip  if self.validade(ip['ip']) else None

        except Exception as err:
            return None


if __name__ == '__main__':
    print('Meu IP: ', Getpubip().getipv4())
