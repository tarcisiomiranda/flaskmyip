import sys
import time
import requests
import boto3
from botocore.exceptions import ClientError


# class api_aws:
    # def __init__(self):
        
GROUP_ID = 'sg-xxxxxxxxxxxxxxxxxx'
RULE_DESCRIPTION = 'Rule Description'
NEW_IP = requests.get('http://checkip.amazonaws.com').text[:-1] + '/32'
OLD_IP = ''

'''
client = boto3.client(
    's3',
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    aws_session_token=SESSION_TOKEN
)
'''
print('NEW_IP \n', NEW_IP)

ec2 = boto3.client('ec2')

try:
    response = ec2.describe_security_groups(GroupIds=[GROUP_ID])
except ClientError as e:
    print(e)

sg = response['SecurityGroups']


def revoke_rule(ip_permission=None):
    if ip_permission != None:
        print('|---------------> ')
        print(ip_permission)
        print('|---------------> ')
        try:
            # print('__REVOKE__ -- CHEGOU AQUI ', ip_permission)
            d = ec2.revoke_security_group_ingress(
                GroupId = GROUP_ID,
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
            print('Ingress successfully removed {}'.format(d), '\n')
            print('REMOVEU -- 30 Segundos')
            # time.sleep(30)
            return True

        except ClientError as e:
            print('error revoke ', e)
            return e

    else:
        return False

def authorize_rule(ip_permission=None):
    if ip_permission != None:
        try:
            # print('AUTHORIZED -- CHEGOU AQUI ', ip_permission)
            d = ec2.authorize_security_group_ingress(
                GroupId = GROUP_ID,
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
            print('Ingress successfully set {}'.format(d), '\n')
            print('INSERIU -- 30 Segundos')
            # time.sleep(30)
        except ClientError as e:
            print('error revoke ', e)
            return e

    else:
        return False

def remove_misc(data=None, update=False):
    if data != None:
        data.pop('Ipv6Ranges')
        data.pop('PrefixListIds')
        data.pop('UserIdGroupPairs')

        # TODO
        if update:
            pass
            # if revoke_rule(ip_permission=[old_fp_22_other]):
                # authorize_rule(ip_permission=[fp_22_other])
        else:
            print('Removeu numa boa!')
            return data

    else:
        return None


if sg[0].get('GroupName') == 'main_linux':
    # acessando o ipermission(regras individuais)
    for fp in sg[0].get('IpPermissions'):
        if fp.get('FromPort') == 22:
            old_fp_22_other = fp.copy()
            fp_22_other = fp.copy()
            new_fp_22_other = []

            for rule_range in fp_22_other.get('IpRanges'):
                if rule_range.get('Description') == 'api_ssh_home':
                    new_fp_22_other.append({'CidrIp': NEW_IP, 'Description': 'api_ssh_home'})
                if rule_range.get('Description') != 'api_ssh_home':
                    new_fp_22_other.append(rule_range)

            # tratando o revoke antes de enviar
            old_fp_22_other = remove_misc(data=old_fp_22_other)
            if revoke_rule(ip_permission=[old_fp_22_other]):
                '''
                    Verificar o pq depois de eu fazer um list compre, a varivel old_fp_22_other muda
                    mesmo se eu usar um copy() em cima na linha 126
                    tive que colocar o if com append aqui depois de revoke
                '''
                if len(fp_22_other.get('IpRanges')) > 1:
                    fp_22_other['IpRanges'].clear()
                    [fp_22_other['IpRanges'].append(x) for x in new_fp_22_other]
                    fp_22_other = remove_misc(data=fp_22_other)
                # enviando a nova regra
                authorize_rule(ip_permission=[fp_22_other])

        # regras comuns
        if fp.get('FromPort') == 9090 and fp.get('IpRanges')[0].get('Description') == 'api_federate':
            fp_9090_prometheus = fp.copy()
            fp_9090_prometheus = remove_misc(data=fp_9090_prometheus)
            if revoke_rule(ip_permission=[fp_9090_prometheus]):
                fp_9090_prometheus['IpRanges'][0].update({'CidrIp': NEW_IP})
                authorize_rule(ip_permission=[fp_9090_prometheus])

        if fp.get('FromPort') == 1624 and fp.get('IpRanges')[0].get('Description') == 'iw4x-admin':
            fp_1624_iw4x_admin = fp.copy()
            fp_1624_iw4x_admin = remove_misc(data=fp_1624_iw4x_admin)
            if revoke_rule(ip_permission=[fp_1624_iw4x_admin]):
                fp_1624_iw4x_admin['IpRanges'][0].update({'CidrIp': NEW_IP})
                authorize_rule(ip_permission=[fp_1624_iw4x_admin])

        if fp.get('FromPort') == 3389 and fp.get('IpRanges')[0].get('Description') == 'api_rdp':
            fp_3389_rdp = fp.copy()
            fp_3389_rdp = remove_misc(data=fp_3389_rdp)
            if revoke_rule(ip_permission=[fp_3389_rdp]):
                fp_3389_rdp['IpRanges'][0].update({'CidrIp': NEW_IP})
                authorize_rule(ip_permission=[fp_3389_rdp])

        if fp.get('FromPort') == 9109 and fp.get('IpRanges')[0].get('Description') == 'api_prometheus':
            fp_9109_node = fp.copy()
            fp_9109_node = remove_misc(data=fp_9109_node)
            print('API PROMETHEUS \n', fp_9109_node)

            if revoke_rule(ip_permission=[fp_9109_node]):
                fp_9109_node['IpRanges'][0].update({'CidrIp': NEW_IP})
                authorize_rule(ip_permission=[fp_9109_node])
