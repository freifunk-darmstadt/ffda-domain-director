import unittest

from peewee import SqliteDatabase

from domain_director.db import create_tables, distribute_nodes_meshviewer_json
from domain_director.db.model import db, Node
from domain_director.domain import load_domain_polygons, get_domain, decide_node_domain, DecisionCriteria


class TestDomainModule(unittest.TestCase):

    def setUp(self):
        database = SqliteDatabase(':memory:')
        db.initialize(database)
        create_tables(database)

    def test_domains(self):
        with open("domains/sample_domains.geojson", "r") as f:
            polygons = load_domain_polygons(f.read())

        self.assertEqual(get_domain(49.843996, 8.700313, polygons), "domain1")
        self.assertEqual(get_domain(49.859322, 8.754904, polygons), "domain2")
        self.assertEqual(get_domain(49.797885, 8.754848, polygons), "domain3")
        self.assertEqual(get_domain(49.791845, 8.693972, polygons), None)

    def test_topology_update_no_bridging(self):
        # Test correct handling of topology update when bridging is not active
        with open("domains/sample_domains.geojson") as gj:
            polygons = load_domain_polygons(gj.read())
        with open("topologies/topology_independent.json", "r") as idp:
            distribute_nodes_meshviewer_json(idp.read(), True)
            idp.close()

        dom3 = decide_node_domain("daff61000302", lat=49.795449888, lon=8.754730225, accuracy=10,
                                  polygons=polygons, default_domain="default")  # Domain 3
        dom2 = decide_node_domain("daff61000402", lat=49.842410779, lon=8.750610352, accuracy=10,
                                  polygons=polygons, default_domain="default")  # Domain 2
        dom1 = decide_node_domain("c04a00dd692a", lat=49.840639497, lon=8.692588806, accuracy=10,
                                  polygons=polygons, default_domain="default")  # Domain 1
        domd = decide_node_domain("60e3272f92b2", lat=49.803427592, lon=8.670616150, accuracy=10,
                                  polygons=polygons, default_domain="default")  # Default

        with open("topologies/topology_fullmesh.json", "r") as idp:
            distribute_nodes_meshviewer_json(idp.read(), False)
            idp.close()

        self.assertEqual(decide_node_domain("daff61000302", lat=49.795449888, lon=8.754730225, accuracy=10,
                                            polygons=polygons, default_domain="default"), dom3)
        self.assertEqual(decide_node_domain("daff61000402", lat=49.842410779, lon=8.750610352, accuracy=10,
                                            polygons=polygons, default_domain="default"), dom2)
        self.assertEqual(decide_node_domain("c04a00dd692a", lat=49.840639497, lon=8.692588806, accuracy=10,
                                            polygons=polygons, default_domain="default"), dom1)
        self.assertEqual(decide_node_domain("60e3272f92b2", lat=49.803427592, lon=8.670616150, accuracy=10,
                                            polygons=polygons, default_domain="default"), domd)

    def test_topology_update_bridging(self):
        # Test correct handling of topology update when bridging is not active
        with open("domains/sample_domains.geojson") as gj:
            polygons = load_domain_polygons(gj.read())
        with open("topologies/topology_independent.json", "r") as idp:
            distribute_nodes_meshviewer_json(idp.read(), True)
            idp.close()

        dom3 = decide_node_domain("daff61000302", lat=49.795449888, lon=8.754730225, accuracy=10,
                                  polygons=polygons, default_domain="default")  # Domain 3
        dom2 = decide_node_domain("daff61000402", lat=49.842410779, lon=8.750610352, accuracy=10,
                                  polygons=polygons, default_domain="default")  # Domain 2
        dom1 = decide_node_domain("c04a00dd692a", lat=49.840639497, lon=8.692588806, accuracy=10,
                                  polygons=polygons, default_domain="default")  # Domain 1
        domd = decide_node_domain("60e3272f92b2", lat=49.803427592, lon=8.670616150, accuracy=10,
                                  polygons=polygons, default_domain="default")  # Default

        self.assertNotEqual(dom3, dom2)
        self.assertNotEqual(dom2, dom1)
        self.assertNotEqual(dom1, domd)
        with open("topologies/topology_fullmesh.json", "r") as idp:
            distribute_nodes_meshviewer_json(idp.read(), True)
            idp.close()

        dom3 = decide_node_domain("daff61000302", lat=49.795449888, lon=8.754730225, accuracy=10,
                                  polygons=polygons, default_domain="default")  # Domain 3
        dom2 = decide_node_domain("daff61000402", lat=49.842410779, lon=8.750610352, accuracy=10,
                                  polygons=polygons, default_domain="default")  # Domain 2
        dom1 = decide_node_domain("c04a00dd692a", lat=49.840639497, lon=8.692588806, accuracy=10,
                                  polygons=polygons, default_domain="default")  # Domain 1
        domd = decide_node_domain("60e3272f92b2", lat=49.803427592, lon=8.670616150, accuracy=10,
                                  polygons=polygons, default_domain="default")  # Default

        self.assertEqual(dom3, dom2)
        self.assertEqual(dom2, dom1)
        self.assertNotEqual(dom2, domd)

    def test_decision_criteria(self):
        with open("domains/sample_domains.geojson") as gj:
            polygons = load_domain_polygons(gj.read())
        with open("topologies/topology_independent.json", "r") as idp:
            distribute_nodes_meshviewer_json(idp.read(), True)
            idp.close()

        decide_node_domain("c04a00dd692a", lat=49.795449888, lon=8.754730225, accuracy=10000,
                           polygons=polygons, default_domain="default")
        decide_node_domain("60e3272f92b2", lat=49.842410779, lon=8.750610352, accuracy=10,
                           polygons=polygons, default_domain="default", max_accuracy=250)
        decide_node_domain("daff61000402", polygons=polygons, default_domain="default")

        self.assertEqual(Node.get(node_id="c04a00dd692a").mesh_id.decision_criteria,
                         int(DecisionCriteria.USER_LOCATION))
        self.assertEqual(Node.get(node_id="60e3272f92b2").mesh_id.decision_criteria,
                         int(DecisionCriteria.APPROX_LOCATION))
        self.assertEqual(Node.get(node_id="daff61000402").mesh_id.decision_criteria,
                         None)
