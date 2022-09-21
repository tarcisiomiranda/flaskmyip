from requests import get
import requests
import json
import sys


class TMCloudflare:
    def __init__(self, **kwargs):
        self.url = 'https://api.cloudflare.com/'
        self.ZONE_ID = None

    def get_records(self, **kwargs):
        if kwargs:
            resp = requests.get(
                '{}client/v4/zones/{}/dns_records'.format(self.url, kwargs.get('ZONE_ID')),
                headers={
                    'X-Auth-Email': kwargs.get('CF_EMAIL'),
                    'X-Auth-Key': kwargs.get('CF_API_KEY'),
                    'Content-Type': 'application/json'
                })
            dump = json.dumps(resp.json(), indent=4, sort_keys=True)
            result = json.loads(json.dumps(resp.json()))
            return result

        else:
            return None
    
    def update_record(self, *args, **kwargs):
        CF_TYPE   = args[0][0]
        CF_DOMAIN = args[0][1]
        RECORD_ID = args[0][2]
        ZONE_ID   = args[0][3]
        # print(CF_TYPE)
        # print(CF_DOMAIN)
        # print(RECORD_ID)
        # print(ZONE_ID)
        # print(kwargs.get('CF_API_KEY'))
        # print(kwargs.get('CF_EMAIL'))
        # print(kwargs.get('NEW_IPV4'))
        # sys.exit(1)

        try:
            resp = requests.put(
                '{}client/v4/zones/{}/dns_records/{}'.format(
                    self.url,
                    ZONE_ID,
                    RECORD_ID
                    ),
                headers={
                    'X-Auth-Key': kwargs.get('CF_API_KEY'),
                    'X-Auth-Email': kwargs.get('CF_EMAIL'),
                    'Content-Type': 'application/json'
                },
                json={
                    'type': CF_TYPE,
                    'name': CF_DOMAIN,
                    'content': kwargs.get('NEW_IPV4'),
                    'ttl': 60,
                    'proxied': False
                })
            dump = json.dumps(resp.json(), indent=4, sort_keys=True)
            dump_dict = json.loads(json.dumps(resp.json()))

            if bool(dump_dict.get('success')) == False:
                raise Exception({
                    'status': 500,
                    'domain': CF_DOMAIN,
                    'message': 'Error when update records'
                })

            dump_dict.update({'status': 200})
            return dump_dict
        except Exception as err:
            return {
                'status': 500,
                'domain': CF_DOMAIN,
                'message': 'Error when update records - {}'.format(err)
            }

if __name__ == '__main__':
    pass
    # print(Cloudflare().get_records())
