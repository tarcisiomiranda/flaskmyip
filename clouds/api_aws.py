import sys
import time
import requests
import boto3
from botocore.exceptions import ClientError


class API_AWS:
    def __init__(self, ipv4=None, gid=None):
        '''
        client = boto3.client(
            's3',
            aws_access_key_id=ACCESS_KEY,
            aws_secret_access_key=SECRET_KEY,
            aws_session_token=SESSION_TOKEN
        )
        '''
        if gid != None:
            self.GROUP_ID = gid
        else:
            print('Favor informar o GROUP_ID DA AWS')
            sys.exit(1)

        if ipv4 != None:
            self.NEW_IP = '{}/32'.format(ipv4)
        else:
            self.NEW_IP = requests.get('http://checkip.amazonaws.com').text[:-1] + '/32'

        self.ec2 = boto3.client('ec2')
        try:
            response = self.ec2.describe_security_groups(GroupIds=[self.GROUP_ID])
        except ClientError as e:
            print('Error em pegar informações de rede AWS {}'.format(e))

        self.sg = response['SecurityGroups']

    # funcoes de tratamento
    def revoke_rule(self, ip_permission=None):
        if ip_permission != None:
            try:
                # print('__REVOKE__ -- CHEGOU AQUI ', ip_permission)
                d = self.ec2.revoke_security_group_ingress(
                    GroupId = self.GROUP_ID,
                    IpPermissions = ip_permission
                    # IpPermissions=[
                    #     {
                    #         'FromPort': 3306,
                    #         'ToPort': 3306,
                    #         'IpProtocol': 'tcp',
                    #         'IpRanges': [
                    #             {
                    #                 'CidrIp': OLD_IP,
                    #                 'Description': RULE_DESCRIPTION
                    #             }
                    #         ]
                    #     }
                    # ]
                )
                # print('Ingress successfully removed {}'.format(d), '\n')
                return True

            except ClientError as e:
                print('error revoke ', e)
                return e

        else:
            return False

    def authorize_rule(self, ip_permission=None):
        if ip_permission != None:
            try:
                d = self.ec2.authorize_security_group_ingress(
                    GroupId = self.GROUP_ID,
                    IpPermissions = ip_permission
                    # IpPermissions=[
                    #     {
                    #         'FromPort': 3306,
                    #         'ToPort': 3306,
                    #         'IpProtocol': 'tcp',
                    #         'IpRanges': [
                    #             {
                    #                 'CidrIp': NEW_IP,
                    #                 'Description': RULE_DESCRIPTION
                    #             }
                    #         ]
                    #     }
                    # ]
                )
                # print('Ingress successfully set {}'.format(d), '\n')
                return True

            except ClientError as e:
                print('error revoke ', e)
                return e

        else:
            return False

    def remove_misc(self, data=None, update=False):
        if data != None:
            data.pop('Ipv6Ranges')
            data.pop('PrefixListIds')
            data.pop('UserIdGroupPairs')

            # TODO
            if update:
                pass
                # if self.revoke_rule(ip_permission=[old_fp_22_other]):
                    # self.authorize_rule(ip_permission=[fp_22_other])
            else:
                return data

        else:
            return None

    def update_rules(self):
        if self.sg[0].get('GroupName') == 'main_linux':
            # acessando o ipermission(regras individuais)
            for fp in self.sg[0].get('IpPermissions'):
                if fp.get('FromPort') == 22:
                    old_fp_22_other = fp.copy()
                    fp_22_other = fp.copy()
                    new_fp_22_other = []

                    for rule_range in fp_22_other.get('IpRanges'):
                        if rule_range.get('Description') == 'api_ssh_home':
                            new_fp_22_other.append({'CidrIp': self.NEW_IP, 'Description': 'api_ssh_home'})
                        if rule_range.get('Description') != 'api_ssh_home':
                            new_fp_22_other.append(rule_range)

                    # tratando o revoke antes de enviar
                    old_fp_22_other = self.remove_misc(data=old_fp_22_other)
                    if self.revoke_rule(ip_permission=[old_fp_22_other]):
                        '''
                            Verificar o pq depois de eu fazer um list compre, a varivel old_fp_22_other muda
                            mesmo se eu usar um copy() em cima na linha 126
                            tive que colocar o if com append aqui depois de revoke
                        '''
                        if len(fp_22_other.get('IpRanges')) > 1:
                            fp_22_other['IpRanges'].clear()
                            [fp_22_other['IpRanges'].append(x) for x in new_fp_22_other]
                            fp_22_other = self.remove_misc(data=fp_22_other)
                        # enviando a nova regra
                        self.authorize_rule(ip_permission=[fp_22_other])

                # regras comuns
                if fp.get('FromPort') == 9090 and fp.get('IpRanges')[0].get('Description') == 'api_federate':
                    fp_9090_prometheus = fp.copy()
                    fp_9090_prometheus = self.remove_misc(data=fp_9090_prometheus)
                    if self.revoke_rule(ip_permission=[fp_9090_prometheus]):
                        fp_9090_prometheus['IpRanges'][0].update({'CidrIp': self.NEW_IP})
                        self.authorize_rule(ip_permission=[fp_9090_prometheus])

                if fp.get('FromPort') == 1624 and fp.get('IpRanges')[0].get('Description') == 'iw4x-admin':
                    fp_1624_iw4x_admin = fp.copy()
                    fp_1624_iw4x_admin = self.remove_misc(data=fp_1624_iw4x_admin)
                    if self.revoke_rule(ip_permission=[fp_1624_iw4x_admin]):
                        fp_1624_iw4x_admin['IpRanges'][0].update({'CidrIp': self.NEW_IP})
                        self.authorize_rule(ip_permission=[fp_1624_iw4x_admin])

                if fp.get('FromPort') == 3389 and fp.get('IpRanges')[0].get('Description') == 'api_rdp':
                    fp_3389_rdp = fp.copy()
                    fp_3389_rdp = self.remove_misc(data=fp_3389_rdp)
                    if self.revoke_rule(ip_permission=[fp_3389_rdp]):
                        fp_3389_rdp['IpRanges'][0].update({'CidrIp': self.NEW_IP})
                        self.authorize_rule(ip_permission=[fp_3389_rdp])

                if fp.get('FromPort') == 9109 and fp.get('IpRanges')[0].get('Description') == 'api_prometheus':
                    fp_9109_node = fp.copy()
                    fp_9109_node = self.remove_misc(data=fp_9109_node)

                    if self.revoke_rule(ip_permission=[fp_9109_node]):
                        fp_9109_node['IpRanges'][0].update({'CidrIp': self.NEW_IP})
                        self.authorize_rule(ip_permission=[fp_9109_node])

            # fim do for
            return True

        else:
            return None

# Call
if __name__ == '__main__':
    api_aws().update_rules()
