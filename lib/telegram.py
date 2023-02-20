import requests
import sys

class TMTelegram:
    def __init__(self):
        self.url = 'https://api.telegram.org/'

    def send_msg(self, **kwargs):
        if kwargs.get('OTHER'):
            MSG=f"""\
<b>____STATUS:</b> <b>Salt hosts Minion</b>
<b>IC_RESTART:</b> {kwargs.get('IC_RESTART')}
<b>IC___ERROR:</b> {kwargs.get('IC_ERROR')}
"""

        elif len(kwargs) > 3:
            domain_update = []
            if len(kwargs.get('Domains Success')) >= 1:
                for d in kwargs.get('Domains Success'):
                    if bool(d.get('result')):
                        do_su = d.get('result')
                        do_su = do_su.get('name')
                        domain_update.append(do_su)

            MSG=f"""\
<b>OLD_IP:</b> {kwargs.get('OLD_IP').strip()}
<b>NEW_IP:</b> {kwargs.get('NEW_IP').strip()}
<b>FWL_DO:</b> {kwargs.get('FWL_DO').strip()}
<b>FWL_AWS:</b> {kwargs.get('FWL_DO').strip()}
<b>FWL_LIN:</b> {kwargs.get('FWL_LIN').strip()}
<b>FWL_OCI:</b> {kwargs.get('FWL_OCI').strip()}
<b>DOMAIN:</b> {domain_update} 
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
                    ('parse_mode', 'HTML')
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


if __name__ == '__main__':
    pass
