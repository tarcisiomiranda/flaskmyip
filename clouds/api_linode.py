import os
import sys
import json
import yaml
import requests


class API_LINODE:
    def __init__(self):
        basedir = os.path.abspath(os.path.dirname(__file__))
        with open('{}/../keys_gpg/linode_key.txt'.format(basedir), 'r') as f:
            TOKEN_API_LINODE = f.read().strip()

        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {TOKEN_API_LINODE}',
        }

    def getlist_rules(self):
        response = requests.get('https://api.linode.com/v4/networking/firewalls', headers=self.headers)
        res = response.text
        json_decode = json.loads(res)

        return json_decode

    def update_rules(self, rule=None, fw_id=None):
        response = requests.put(
            'https://api.linode.com/v4/networking/firewalls/{}/rules'.format(fw_id),
            headers=self.headers, json=rule)
        res = response.text

        if 'error' in res.lower():
            return False

        else:
            # print('RESULTADO_UPDATE ', res)
            return True

    def replace_rule(self, ipv4=None, fwl_name='teste_api'):
        firewall = self.getlist_rules()
        if ipv4 != None and firewall:
            update_ip = ['{}/32'.format(ipv4)]
            firewall_name = []
            for fw in firewall['data']:
                if fw['label'] == fwl_name:
                    firewall_id = fw['id']
                    if fw['rules'] not in firewall_name:
                        firewall_name.append(fw['rules'])

            inbound_rules = []
            rule_4_update = []
            firewall_copy = firewall_name.copy()
            for rule in firewall_name[0]['inbound']:
                if 'home' not in rule.get('label'):
                    if rule not in inbound_rules:
                        inbound_rules.append(rule)
                if 'home' in rule.get('label'):
                    if rule not in rule_4_update:
                        rule_4_update.append(rule)

            if len(inbound_rules) > 1 and len(rule_4_update) > 0:
                # limpando as rules e colocando as novas
                firewall_copy[0]['inbound'].clear()
                [firewall_copy[0]['inbound'].append(x) for x in inbound_rules]

                # trocando o addresses pelo ip novo e atualzando a lista de rules
                for add in rule_4_update:
                    add['addresses'].update({'ipv4': update_ip})
                [firewall_copy[0]['inbound'].append(x) for x in rule_4_update]

                # Call update_rule
                if self.update_rules(rule=firewall_copy[0], fw_id=firewall_id):
                    return True

                else:
                    return False

            else:
                return False

        else:
            return False


if __name__ == '__main__':
    API_LINODE().replace_rule(ipv4='192.168.29.11', fwl_name='teste_api')
