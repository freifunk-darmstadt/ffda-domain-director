import json
import unittest

from domain_director.kml_converter import convert_kml_to_geojson


class TestKMLConverterModule(unittest.TestCase):
    def test_kml_geojson_conversion(self):
        with open("domains/sample_domains.kml") as fh:
            geojson_kml = json.loads(convert_kml_to_geojson(fh.read().encode()))
        with open("domains/sample_domains.geojson") as fh:
            geojson_reference = json.loads(fh.read().encode())

        self.assertEqual(geojson_kml, geojson_reference)
