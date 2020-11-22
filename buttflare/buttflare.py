#!/usr/bin/env python3

# todo: allow for multiple IP lookup endpoints with retry
# - http://ipv4.icanhazip.com
# - https://www.ipify.org/
# - https://seeip.org/

# Also test with https

import requests
import sys

from buttflare.api import CfApiError, CloudFlare, Zone
from buttflare.config import Config

config = Config()

cf = CloudFlare(config.email, config.api_key)
zone = Zone(cf, config.zone_name)

def set_record(addr_type):
    if addr_type == 'v4':
        host = config.v4_host
        check_url = config.v4_check_url
        record_type = 'A'
    elif addr_type == 'v6':
        host = config.v6_host
        check_url = config.v6_check_url
        record_type = 'AAAA'
    else:
        raise ValueError("arg 1 to addr_type() must be 'v4' or 'v6'")

    fqdn = '.'.join((host, config.zone_name))
    # fetch actual address
    actual_addr = requests.get(check_url).text.strip()
    # fetch current record from cloudflare
    cf_result = zone.get_dns_records(type=record_type, name=fqdn)
    # if there's no record in cloudflare, create one
    if not cf_result:
        try:
            zone.create_dns_record(record_type, host, actual_addr)
        except CfApiError as e:
            print(e.msg, file=sys.stderr)
            print(e.errors, file=sys.stderr)
            sys.exit(1)
        else:
            print('Record created: {} {} {}'.format(fqdn, record_type,
                actual_addr))
            return
    cf_addr = cf_result[0]['content']
    # if actual and cloudflare don't agree, update cloudflare
    if actual_addr != cf_addr:
        cf_id = cf_result[0]['id']
        try:
            zone.update_dns_record(cf_id, record_type, host, actual_addr)
        except CfApiError as e:
            print(e.msg, file=sys.stderr)
            print(e.errors, file=sys.stderr)
            sys.exit(1)
        else:
            print('Record updated: {} {} {}'.format(fqdn, record_type,
                actual_addr))
            return


def main():
    if config.v4_host:
        set_record('v4')
    if config.v6_host:
        set_record('v6')
    if not (config.v4_host or config.v6_host):
        print('No ddns config found.', file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
