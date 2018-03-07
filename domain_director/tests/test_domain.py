import unittest

from domain_director.domain import load_domain_polygons, get_domain


class TestDomainModule(unittest.TestCase):

    def test_domains(self):
        with open("domains/sample_domains.geojson", "r") as f:
            polygons = load_domain_polygons(f.read())

        self.assertEqual(get_domain(49.843996, 8.700313, polygons), "domain1")
        self.assertEqual(get_domain(49.859322, 8.754904, polygons), "domain2")
        self.assertEqual(get_domain(49.797885, 8.754848, polygons), "domain3")
        self.assertEqual(get_domain(49.791845, 8.693972, polygons), None)
