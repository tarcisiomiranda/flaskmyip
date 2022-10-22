from decouple import config
import requests
import sys

class HomeIP:
    def __init__(self):
        self.url = config('HOME_URL_CHECK', False)

    def get_home_ip(self):
        try:
            if bool(self.url):
                params = (
                    ('g_ip', config('PASSWD')),
                )

                res = requests.get(self.url, params=params)
                new_ip = res.text

            if res.status_code == 200:
                return new_ip

        except Exception as err:
            return {
                'status': 500,
                'message': 'Error when send message - {}'.format(err),
            }
