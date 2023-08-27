import requests
import sys

class TMTelegram:
    def __init__(self):
        self.url = 'https://api.telegram.org/'


    def send_msg(self, **kwargs):
        # print('KWARGS ', kwargs)
        def get_value(data):
            print('DATA', data)
            return data.strip() if data is not None and not isinstance(data, bool) else None

        if kwargs.get('UPDATE'):
            domain_update = [item['result']['name'] for item in kwargs['UPDATE']['Domains Success']]
            MSG = f'''\
OLD_IP4: {get_value(kwargs['UPDATE'].get('OLD_IP'))}
NEW_IP4: {get_value(kwargs['UPDATE'].get('NEW_IP'))}
FWL_DOC: {get_value(kwargs['UPDATE'].get('FWL_DO'))}
FWL_AWS: {get_value(kwargs['UPDATE'].get('FWL_AWS'))}
FWL_LIN: {get_value(kwargs['UPDATE'].get('FWL_LIN'))}
FWL_OCI: {get_value(kwargs['UPDATE'].get('FWL_OCI'))}
DOMAINS: {domain_update}
'''
        elif kwargs.get('RESTART'):
            MSG = f'''\
Salt-Minion Restarted
OK: {kwargs['RESTART'].get('OK')}
ER: {kwargs['RESTART'].get('ER')}
'''
        elif kwargs.get('REQUEST'):
            MSG = f'''\
Request acess service
NOME: {kwargs['REQUEST'].get('name', '?')}
HOST: {kwargs['REQUEST'].get('host', '?')}
    '''
        else:
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
                    ('text', f'<code>{MSG}</code>'),
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
