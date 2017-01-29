import json

import requests

"""
Currently, this class implements only enough of the CloudFlare v4 API to
fetch and update DNS records. Written because the author found the official
CloudFlare Python API to be seriously lacking in terms of fundamental
design (read: not very Pythonic). Also, buttflare seemed like a better name.
https://github.com/panicsteve/cloud-to-butt
"""

ENDPOINT = 'https://api.cloudflare.com/client/v4/'

class CfApiError(Exception):
    def __init__(self, msg, errors):
        self.msg = msg
        self.errors = errors

class CloudFlare():
    """
    Create a CloudFlare API instance. Parameters are the email address of
    the account and the API key.
    """
    def __init__(self, email, api_key):
        self.headers = {'X-Auth-Email': email, 'X-Auth-Key': api_key,
            'Content-type': 'application/json'}
        pass


class Zone():
    """
    DNS zone instance. Pass in a CloudFlare object and the name of the zone
    (typically the name of the domain managed by CloudFlare.
    """
    def __init__(self, cf, name):
        self.cf = cf
        params = {'name': name}
        zone_resp = requests.get(ENDPOINT + 'zones', headers=self.cf.headers,
            params=params)
        self.id = json.loads(zone_resp.text)['result'][0]['id']

    def get_dns_records(self, **kwargs):
        """
        Fetch the DNS records for this zone.
        Filter via optional parameters (kwargs) as described here:
        https://api.cloudflare.com/#dns-records-for-a-zone-list-dns-records
        Return a list of records as dicts.
        """
        rec_resp = requests.get(ENDPOINT + 'zones/' + self.id + '/dns_records',
            headers=self.cf.headers, params=kwargs)
        return json.loads(rec_resp.text)['result']

    def create_dns_record(self, type, name, content, **kwargs):
        """
        Create a DNS record for this zone.
        'type', 'name', and 'content' args are required.
        Return True if successful. False if not.
        """
        data = {'type': type, 'name': name, 'content': content}
        data = {**data, **kwargs}
        create_resp = requests.post(ENDPOINT + 'zones/' + self.id +
            '/dns_records', headers=self.cf.headers, json=data)
        create_resp_py = json.loads(create_resp.text)
        if not create_resp_py['success']:
            raise CfApiError('Could not create record: {}'.format(data),
                create_resp_py['errors'])

    # xxx code duplication (well, some)
    def update_dns_record(self, id, type, name, content, **kwargs):
        """
        Update a DNS record for this zone.
        'type', 'name', and 'content' args are required.
        Return True if successful. False if not.
        """
        data = {'type': type, 'name': name, 'content': content}
        data = {**data, **kwargs}
        update_resp = requests.put(ENDPOINT + 'zones/' + self.id +
            '/dns_records/' + id, headers=self.cf.headers, json=data)
        update_resp_py = json.loads(update_resp.text)
        if not update_resp_py['success']:
            raise CfApiError('Could not update record: {}'.format(data),
                update_resp_py['errors'])
