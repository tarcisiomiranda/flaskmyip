from requests import get
import json
import urllib3
urllib3.disable_warnings()


class Getpubip:
    def __init__(self):
        self.url = 'https://ip.tarcisio.me'

    def getipv4(self):
        try:
            ip = get(self.url, timeout=10, verify=False).text
            ip = json.loads(ip)
            return ip

        except Exception as err:
            return {
                'status': 500,
                'message': 'Error when getting ipv4 - {}'.format(err)
            }

if __name__ == '__main__':
  print('Meu IP: ', Getpubip().getipv4())

