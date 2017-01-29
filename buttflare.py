#!/usr/bin/env python3

import requests
import sys

from api import CfApiError, CloudFlare, Zone
from config import Config

config = Config()

cf = CloudFlare(config.email, config.api_key)
zone = Zone(cf, config.zone_name)

if config.v4_host:
    v4_fqdn = '.'.join((config.v4_host, config.zone_name))
    # fetch address from ipv4.bityard.net
    actual_v4_addr = requests.get(config.v4_check_url).text
    # fetch current record from cloudflare
    cf_v4_result = zone.get_dns_records(type='A', name=v4_fqdn)
    # if there's no record in cloudflare, create one
    if not cf_v4_result:
        try:
            zone.create_dns_record('A', config.v4_host, actual_v4_addr)
        except CfApiError as e:
            print(e.msg, file=sys.stderr)
            print(e.errors, file=sys.stderr)
            sys.exit(1)
        else:
            print('Record created: {} A {}'.format(v4_fqdn, actual_v4_addr))
            sys.exit()
    cf_v4_addr = cf_v4_result[0]['content']
    # if actual and cloudflare don't agree, update cloudflare
    if actual_v4_addr != cf_v4_addr:
        cf_v4_id = cf_v4_result[0]['id']
        try:
            zone.update_dns_record(cf_v4_id, 'A', config.v4_host,
                actual_v4_addr)
        except CfApiError as e:
            print(e.msg, file=sys.stderr)
            print(e.errors, file=sys.stderr)
            sys.exit(1)
        else:
            print('Record updated: {} A {}'.format(v4_fqdn, actual_v4_addr))
            sys.exit()
