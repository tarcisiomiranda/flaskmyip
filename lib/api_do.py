import os
import sys
import json
import yaml
import requests


class API_DO:
    def __init__(self):
        basedir = os.path.abspath(os.path.dirname(__file__))
        with open('{}/../keys_gpg/do_key.txt'.format(basedir), 'r') as f:
            DIGITALOCEAN_TOKEN = f.read()
            f.close()
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {DIGITALOCEAN_TOKEN}',
        }

    def verify_none(self, data=False):
        # print('DATA ', type(data), data, bool(data))
        if bool(data):
            if data == None:
                return True
            else:
                return False

        else:
            return None

    def get_fw(self):
        response = requests.get('https://api.digitalocean.com/v2/firewalls', headers=self.headers)
        res = response.text
        json_decode = json.loads(res)
        json_encode = json.dumps(res, sort_keys=True, indent=4)

        return json_decode

    def put_fw(self, data=None):
        if data != None:
            fw_id = data[0].get('id')
            data[0].pop('id')
            data[0].pop('status')
            data[0].pop('pending_changes')
            data[0].pop('created_at')

            response = requests.put(
                    'https://api.digitalocean.com/v2/firewalls/{}'.format(fw_id),
                    headers=self.headers,
                    json=data[0]
                )
            res = response.text
            json_res = json.loads(res)

            return json_res

        else:
            return None

    def update_fw(self, ipv4=None, fwl=None):
        if ipv4 != None and fwl != None:
            json_decode = self.get_fw()
            for ifw in json_decode:
                if ifw == 'firewalls':
                    if len(json_decode[ifw]) >= 2:
                        rule_update = [x for x in json_decode[ifw] if x.get('name') == fwl]
                        # colocando name
                        rule_update[0].update({'name': rule_update[0].get('name')})
                        # indentificando a regra
                        # print('NOME: ', rule_update[0].get('name'))
                        # print('__ID: ', rule_update[0].get('id'))

                        # Melhorar isso aqui meu Deus
                        inbound_rules = rule_update[0].get('inbound_rules').copy()
                        print('inbound_rules', inbound_rules)
                        for ports in inbound_rules:
                            if ports.get('ports') == '22':
                                if self.verify_none(data=ports.get('sources').get('addresses')):
                                    ports.get('sources')['addresses'].append(ipv4)
                                else:
                                    ports.get('sources').update({'addresses': [ipv4]})

                            if ports.get('ports') == '9109':
                                if self.verify_none(data=ports.get('sources').get('addresses')):
                                    ports.get('sources')['addresses'].append(ipv4)
                                else:
                                    ports.get('sources').update({'addresses': [ipv4]})
    
                        # limpando e adicionando os novos address
                        rule_update[0]['inbound_rules'].clear()
                        [rule_update[0]['inbound_rules'].append(x) for x in inbound_rules]

                        # TODO - mesmo metodo acima | outbound_rules
                        # if rule_update[0].get('outbound_rules')[0].get('protocol') == 'icmp':
                        #     if rule_update[0].get('outbound_rules')[0].get('destinations').get('addresses') == None:
                        #         rule_update[0].get('outbound_rules')[0].get('destinations').update({'addresses': [ipv4]})
                        #     else:
                        #         rule_update[0].get('outbound_rules')[0].get('destinations').get('addresses').append(ipv4)

                        # chamando a def de update
                        up_rule = self.put_fw(data=rule_update)
                        if bool(up_rule.get('firewall').get('status')):
                            return up_rule.get('firewall').get('status')

                        else:
                            return False

                else:
                    return None

        else:
            return False

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


# Call
if __name__ == '__main__':
    print('FIREWALLS: ', API_DO().get_fw())
    print('UPDATE_FW: ', API_DO().update_fw())
    # print(API_DO().get_dropelets())
    # print((json.dumps(API_DO().get_fw(), indent=1)))
    # print((yaml.dump(API_DO().get_fw(), default_flow_style=False)))
