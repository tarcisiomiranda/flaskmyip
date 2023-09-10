import requests
import sys

class TMTelegram:
    def __init__(self):
        self.url = 'https://api.telegram.org/'

    def organize(self, domains):
        domain_dict = {}

        for subdomain in domains:
            parts = subdomain.split('.')
            sub = parts[0]
            domain = '.'.join(parts[1:])

            if domain in domain_dict:
                domain_dict[domain].append(sub)
            else:
                domain_dict[domain] = [sub]

        return domain_dict

    def send_msg(self, **kwargs):
        if kwargs.get('UPDATE'):
            domain_update = [item['result']['name'] for item in kwargs['UPDATE']['Domains Success']]
            _organize_sub = self.organize(domain_update)

            MSG = f'''\
OLD_IP4: {kwargs['UPDATE'].get('OLD_IP', None)}
NEW_IP4: {kwargs['UPDATE'].get('NEW_IP', None)}
FWL_DOC: {kwargs['UPDATE'].get('FWL_DIO', None)}
FWL_AWS: {kwargs['UPDATE'].get('FWL_AWS', None)}
FWL_LIN: {kwargs['UPDATE'].get('FWL_LIN', None)}
FWL_OCI: {kwargs['UPDATE'].get('FWL_OCI', None)}
DOMAINS: {_organize_sub}
DETAILS: http://192.168.29.2:3002/domains
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
