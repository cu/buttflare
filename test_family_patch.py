import ipaddress
import socket

from buttflare import buttflare


family = lambda: socket.AF_INET
expected_type = ipaddress.IPv4Address
IP = buttflare.get_actual_addr(family, expected_type, 'https://ipv4.icanhazip.com')
print(f'v4: {IP}')

family = lambda: socket.AF_INET6
expected_type = ipaddress.IPv6Address
IP = buttflare.get_actual_addr(family, expected_type, 'https://ipv4.icanhazip.com')
print(f'v6: {IP}')
