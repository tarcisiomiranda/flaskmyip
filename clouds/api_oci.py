import oci
import sys
import os

# Dict
# https://stackoverflow.com/questions/61517/python-dictionary-from-an-objects-fields
# Folder
# https://stackoverflow.com/questions/65453576/diference-between-os-getcwd-and-os-path-dirname-file
# os.getcwd()
# Set up config
# config = oci.config.from_file(
#     "~/.oci/config",
#     "DEFAULT"
#     )

class API_OCI:
    def __init__(self):\
        # TODO - Melhorar isso pelo amor de Deus
        # self.localdir = os.path.abspath(os.path.dirname(__file__))
        # Pega a pasta base do projeto e nao o local do arquivo como acima
        self.localdir = os.getcwd()
        print('__file__', __file__)
        with open('{}/.env'.format(self.localdir), 'r') as file:
            envs = file.read()

        # config
        credentials = {}
        key_mapping = {
            'FWL_OCI_USER': 'user',
            'FWL_OCI_KEY': 'key_file',
            'FWL_OCI_FINGER': 'fingerprint',
            'FWL_OCI_TENANCY': 'tenancy',
            'FWL_OCI_REGION': 'region'
        }

        for env in envs.split('\n'):
            parts = env.split('=')
            key = parts[0]
            value = parts[1].replace('\'', '') if len(parts) > 1 else None

            if 'FWL_OCI' in key:
                if key == 'FWL_OCI_SECURITY_LIST_ID':
                    self.security_list_id = value
                elif key == 'FWL_OCI_KEY':
                    credentials['key_file'] = '{}/keys_gpg/key_oci/{}'.format(self.localdir, value)
                elif key in key_mapping:
                    credentials[key_mapping[key]] = value

        # config credentials
        self.config = credentials

    def current_rules(self):
        identity_client = oci.identity.IdentityClient(self.config)
        # print('IDENTIFICACAO DO CLIENTE: ', identity_client)
        core_client = oci.core.VirtualNetworkClient(self.config)
        security_list = core_client.get_security_list(security_list_id=self.security_list_id).data
        current_rules = security_list.ingress_security_rules

        return {'core_client': core_client, 'current_rules': current_rules}

        '''
        list_compartments_response = identity_client.list_compartments(
        compartment_id=self.config['tenancy'],
        lifecycle_state="ACTIVE")
        print('|TUDO SOBRE O COMPARTIMENTO| === > ', list_compartments_response.data)
        '''

    def update_rules(self, ipv4=None):
        if ipv4 is not None:
            ipv4 = '{}/32'.format(ipv4)
            try:
                current_rules = self.current_rules()['current_rules']
                network_client = self.current_rules()['core_client']
                for rule in current_rules:
                    if rule.description is not None and 'home' in rule.description:
                        rule.source = ipv4

                # Update the security list with the modified rule
                update_security_list_details = oci.core.models.UpdateSecurityListDetails(
                    ingress_security_rules = current_rules
                )
                network_client.update_security_list(
                    security_list_id = self.security_list_id,
                    update_security_list_details = update_security_list_details
                )

                print("IngressSecurityRule updated successfully.")
                return True

            except Exception as e:
                print('Erro no update das regras {}'.format(e))
                return False

        else:
            return False


if __name__ == '__main__':
    API_OCI().update_rules(ipv4='192.168.29.11')
