from decouple import config
import requests
import sys

class TMTelegram:
    def __init__(self):
        self.url = 'https://api.telegram.org/'
        self.BOT_ID = config('BOT_ID', default=False)
        self.CHAT_ID = config('CHAT_ID', default=False)

    def send_msg(self, request_acess=None):
        if request_acess is not None:
            MSG=f"""\
<b>Request acess service</b>
<b>NOME:</b> {request_acess.get('name', '?')}
<b>HOST:</b> {request_acess.get('host', '?')}
"""

            try:
                if self.CHAT_ID is None or self.BOT_ID is None:
                    raise Exception({
                        'status': 500,
                        'message': 'Error when send message',
                        'MSG': MSG
                    })

                else:
                    params = (
                        ('chat_id', self.CHAT_ID),
                        ('text', MSG),
                        ('parse_mode', 'HTML')
                    )

                    new_url = '{}{}/sendmessage'.format(self.url, self.BOT_ID)
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

        else:
            return {
                'status': 500,
                'message': 'request_acess is empty!',
            }


if __name__ == '__main__':
    pass
