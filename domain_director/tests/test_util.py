import unittest

from domain_director import ipv6_to_mac


class TestUtilModule(unittest.TestCase):
    def test_ipv6_to_mac(self):
        self.assertEqual(ipv6_to_mac("2001:67c:2ed8:6100:724f:57ff:fe45:5e50"), "70:4f:57:45:5e:50")

