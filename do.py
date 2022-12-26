import os
import sys
import json
import yaml
import requests
# https://medium.com/@almirx101/pgp-key-pair-generation-and-encryption-and-decryption-examples-in-python-3-a72f56477c22


class DO:
    def __init__(self):
        with open('./pgp_keys/do_key.txt', 'r') as f:
            DIGITALOCEAN_TOKEN = f.read()
            f.close()
        # DIGITALOCEAN_TOKEN = os.getenv('DIGITALOCEAN_TOKEN')
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {DIGITALOCEAN_TOKEN}',
        }


    def get_fw(self):
        response = requests.get('https://api.digitalocean.com/v2/firewalls', headers=self.headers)
        res = response.text
        json_decode = json.loads(res)
        json_encode = json.dumps(res, sort_keys=True, indent=4)
        # print('json_decode', type(json_decode), len(json_decode))

        return json_decode

    def put_fw(self, data=None):
        print('ANTES DE ENVIAR ', data, '\n')

        if data != None:
            fw_id = data[0].get('id')
            data[0].pop('id')
            data[0].pop('status')
            data[0].pop('pending_changes')
            data[0].pop('created_at')
            print('fw_id', fw_id)
            print('DEPOIS  MUDANCA ', json.dumps(data), '\n')
            print('DEPOIS  MUDANCA ', data, '\n')
            print('URL ', 'https://api.digitalocean.com/v2/firewalls/{}'.format(fw_id))

            response = requests.put(
                    'https://api.digitalocean.com/v2/firewalls/{}'.format(fw_id),
                    headers=self.headers,
                    # json=json.dumps(data[0])
                    json=data[0]
                )
            res = response.text
            json_res = json.loads(res)

            return json_res

        else:
            return None


    def update_fw(self):
        json_decode = self.get_fw()
        count = 0
        print('Voltas: ', count)
        for ifw in json_decode:
            count += 1
            if ifw == 'firewalls':
                if len(json_decode[ifw]) >= 2:
                    rule_update = [x for x in json_decode[ifw] if x.get('name') == 'tarcisio.me']
                    if rule_update[0].get('inbound_rules')[0].get('ports') == '22':
                        print('NOME: ', rule_update[0].get('name'))
                        print('__ID: ', rule_update[0].get('id'))
                        # append do novo IP
                        rule_update[0].get('inbound_rules')[0].get('sources').get('addresses').append('192.168.29.29')
                        # colocando name
                        rule_update[0].update({'name': rule_update[0].get('name')})
                    # chamando a def de update
                    up_rule = self.put_fw(data=rule_update)
                    print('Retorno update: ', up_rule)

                else:
                    print('-- ELSE --')
                    pass

        '''
        print(json_decode)
        print('\n','---------')
        print(json_encode)
        print('\n','---------')
        print(yaml.dump(json_decode, default_flow_style=False))
        '''

    def get_dropelets(self):
        params = {
            'page': '1',
            'per_page': '9',
        }

        response = requests.get('https://api.digitalocean.com/v2/droplets', params=params, headers=self.headers)
        res = response.text
        json_decode = json.loads(res)
        
        for dl in json_decode:
            if dl == 'droplets':
                print('LEN > ', len(json_decode[dl]))
                if len(json_decode[dl]) >= 2:
                    for i in json_decode[dl]:
                        print('==>', i.get('name'))
                elif len(json_decode[dl]) == 1:
                    i = json_decode[dl][0]
                    print('==>', i.get('name'))

            print('-->', dl)

        return json_decode

    def send_data(self):
        pass

        response = requests.put('https://api.digitalocean.com/v2/firewalls/4fe14eae-7cc8-4e22-bf89-cc3413efa762', headers=headers, json=json_data)
        print('RESPONSE RESULT', response.text)




# Call
print(DO().update_fw())
# print(DO().get_dropelets())
# print((json.dumps(DO().get_fw(), indent=1)))
# print((yaml.dump(DO().get_fw(), default_flow_style=False)))

