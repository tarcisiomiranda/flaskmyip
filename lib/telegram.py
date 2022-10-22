import requests
import sys

class TMTelegram:
    def __init__(self):
        self.url = 'https://api.telegram.org/'

    def send_msg(self, **kwargs):
        if kwargs.get('OTHER'):
            MSG=f"""
ICHOST: {kwargs.get('IC_HOST')}
STATUS: Salt restarted
"""

        elif len(kwargs) > 3:
            domain_update = []
            if len(kwargs.get('Domains Success')) >= 1:
                for d in kwargs.get('Domains Success'):
                    if bool(d.get('result')):
                        do_su = d.get('result')
                        do_su = do_su.get('name')
                        domain_update.append(do_su)

            MSG=f"""
OLD IP: {kwargs.get('Old IP')}
NEW IP: {kwargs.get('New IP')}
DOMAIN: {domain_update}
"""

        # continue script
        if kwargs.get('MSG'):
            MSG = kwargs.get('MSG')

        try:
            if kwargs.get('CHAT_ID') is None or kwargs.get('BOT_ID') is None:
                raise Exception({
                    'status': 500,
                    'message': 'Error when send message',
                    'MSG': MSG
                })

            else:
                params = (
                    ('chat_id', kwargs.get('CHAT_ID')),
                    ('text', MSG),
                )

                new_url = '{}{}/sendmessage'.format(self.url, kwargs.get('BOT_ID'))
                res = requests.get(new_url, params=params)
                
                if res.status_code == 200:
                    return {
                        'status': 200,
                        'message': 'message sent',
                        'MSG': MSG
                    }

        except Exception as err:
            return {
                'status': 500,
                'message': 'Error when send message - {}'.format(err),
                'MSG': MSG
            }
