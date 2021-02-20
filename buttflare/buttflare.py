#!/usr/bin/env python3

import ipaddress
import random
import socket
import sys
import requests.packages.urllib3.util.connection as urllib3_cn

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from buttflare.api import CfApiError, CloudFlare, Zone
from buttflare.config import Config

config = Config()

cf = CloudFlare(config.email, config.api_key)
zone = Zone(cf, config.zone_name)

def get_actual_addr(family, expected_type, check_urls):
    """
    Returns a string containing the actual public IP address of the host,
    or throws an exception if all attempts to look up the IP have failed.
    """
    retry_strategy = Retry(
        total=3,
        status_forcelist=[429, 500, 502, 503, 504],
        backoff_factor=3 # retry after 3s, 6s, 12s
    )
    adapter = requests.adapters.HTTPAdapter(max_retries=retry_strategy)

    urls = check_urls.split()
    random.shuffle(urls)

    actual_addr = None

    urllib3_cn.allowed_gai_family = family

    for url in urls:
        #print(f'trying {url}')
        http = requests.Session()
        http.mount("https://", adapter)
        http.mount("http://", adapter)
        try:
            response = http.get(url, timeout=10)
        except:
            continue
        try:
            actual_addr = ipaddress.ip_address(response.text.strip())
        except ValueError:
            continue
        if actual_addr and type(actual_addr) == expected_type:
            #print(f"got: {actual_addr} from {url}")
            return str(actual_addr)

    if actual_addr is None:
        raise RuntimeError(f'Could not look up IP from any of: {urls}')

def set_record(addr_type):
    if addr_type == 'v4':
        host = config.v4_host
        check_urls = config.v4_check_urls
        record_type = 'A'
        family = lambda: socket.AF_INET
        expected_type = ipaddress.IPv4Address
    elif addr_type == 'v6':
        host = config.v6_host
        check_urls = config.v6_check_urls
        record_type = 'AAAA'
        family = lambda: socket.AF_INET6
        expected_type = ipaddress.IPv6Address
    else:
        raise ValueError("arg 1 to addr_type() must be 'v4' or 'v6'")

    fqdn = '.'.join((host, config.zone_name))
    # fetch actual address
    actual_addr = get_actual_addr(family, expected_type, check_urls)
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
