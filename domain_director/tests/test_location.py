import unittest

from domain_director.location import get_location


class TestLocationModule(unittest.TestCase):

    def test_location_inaccurate(self):
        lat, lon, accuracy = get_location([{
            "macAddress": "82:2a:a8:88:24:fb"
        }], "test")

        self.assertGreater(accuracy, 1000)
