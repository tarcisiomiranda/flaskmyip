from requests import get
import json


class Getpubip:
    def __init__(self):
        self.url = 'https://ip.tarcisio.me'

    def getipv4(self):
        try:
            ip = get(self.url, timeout=10).text
            ip = json.loads(ip)
            return ip

        except Exception as err:
            return {
                'status': 500,
                'message': 'Error when getting ipv4 - {}'.format(err)
            }
