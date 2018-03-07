import re
from ipaddress import IPv6Address


def ipv6_to_mac(ip):
    ip = IPv6Address(ip)
    binary = ip.packed
    nodeid = ["{:02x}".format(binary[8] - 2), "{:02x}".format(binary[9]), "{:02x}".format(binary[10]),
              "{:02x}".format(binary[13]), "{:02x}".format(binary[14]), "{:02x}".format(binary[15])]
    return ":".join(nodeid)


def is_bssid(bssid):
    pattern = re.compile("^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$")
    return pattern.match(bssid)
