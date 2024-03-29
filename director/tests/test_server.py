import json
import os
import unittest

import yaml

from director.server import create_app


class TestServerModule(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        config_file = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                        "config/config0.yml")
        with open(config_file, 'r') as c:
            config = yaml.safe_load(c.read())
            app = create_app(dict(config), testing=True)
            cls.app = app.test_client()

    def test_empty_get_request(self):
        rv = self.app.get('/')
        self.assertEqual(rv.status_code, 400)
        rv = self.app.get('/get_domain')
        self.assertEqual(rv.status_code, 400)

    def test_empty_post_request(self):
        rv = self.app.post('/')
        self.assertEqual(rv.status_code, 400)
        rv = self.app.post('/get_domain')
        self.assertEqual(rv.status_code, 400)

    def test_correct_request(self):
        post_data = [{'signal': -58, 'bssid': '82:2A:A8:C2:AD:03'},
                     {'signal': -42, 'bssid': 'F2:9F:C2:F5:AE:2C'},
                     {'signal': -47, 'bssid': 'F0:9F:C2:F4:AE:2C'},
                     {'signal': -74, 'bssid': '80:2A:A8:C1:B3:FA'},
                     {'signal': -47, 'bssid': '80:2A:A8:C1:AD:03'},
                     {'signal': -74, 'bssid': '94:05:B6:5B:D9:E4'},
                     {'signal': -87, 'bssid': 'B4:30:52:38:C5:63'}]
        rv = self.app.post('/', data={'wifis': json.dumps(post_data)},
                           environ_base={'REMOTE_ADDR': '2001:67c:2ed8:6100:fc64:3ff:fecd:45dd'})
        self.assertEqual(rv.status_code, 200)

        rv = self.app.post('/get_domain', data={'wifis': json.dumps(post_data)},
                           environ_base={'REMOTE_ADDR': '2001:67c:2ed8:6100:fc64:3ff:fecd:45dd'})
        self.assertEqual(rv.status_code, 200)

    def test_admin_token(self):
        rv = self.app.patch('/mesh/1/?token=ujVw0wU0kHms8TRXO4Ji9H0nF4ZVYVWUIz41AdfBYKtFSI16SEWFroWQa0OlbD3n')
        self.assertNotEqual(401, rv.status_code)

        rv = self.app.patch('/mesh/1/?token=badbadbad')
        self.assertEqual(401, rv.status_code)

    def test_locator_invalid_request(self):
        rv = self.app.post('/get_location')
        self.assertEqual(400, rv.status_code)

        rv = self.app.post('/get_location', data="{")
        self.assertEqual(400, rv.status_code)

        rv = self.app.post('/get_location', data={"wifis": []})
        self.assertEqual(400, rv.status_code)

    def test_locator_valid_request(self):
        post_data = [{'signal': -58, 'bssid': '82:2A:A8:C2:AD:03'},
                     {'signal': -42, 'bssid': 'F2:9F:C2:F5:AE:2C'},
                     {'signal': -47, 'bssid': 'F0:9F:C2:F4:AE:2C'},
                     {'signal': -74, 'bssid': '80:2A:A8:C1:B3:FA'},
                     {'signal': -47, 'bssid': '80:2A:A8:C1:AD:03'},
                     {'signal': -74, 'bssid': '94:05:B6:5B:D9:E4'},
                     {'signal': -87, 'bssid': 'B4:30:52:38:C5:63'}]

        rv = self.app.post('/get_location',
                           data={'wifis': json.dumps(post_data)})
        self.assertEqual(200, rv.status_code)
