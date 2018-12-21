import unittest
from peewee import SqliteDatabase

from domain_director.db import create_tables, distribute_nodes_meshviewer_json
from domain_director.db.model import db, Node, Mesh
from domain_director.domain import load_domain_polygons, get_domain, get_node_domain, DecisionCriteria


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

    def test_domain_query_no_approx_location(self):
        with open("domains/sample_domains.geojson") as gj:
            polygons = load_domain_polygons(gj.read())
        with open("topologies/topology_independent.json", "r") as idp:
            distribute_nodes_meshviewer_json(idp.read(), True)
            idp.close()
        dom0, decision_criteria = get_node_domain("c04a00dd692a", polygons=polygons)
        self.assertEqual(dom0, "domain1")

    def test_topology_update_no_bridging(self):
        # Test correct handling of topology update when bridging is not active
        with open("domains/sample_domains.geojson") as gj:
            polygons = load_domain_polygons(gj.read())
        with open("topologies/topology_independent.json", "r") as idp:
            distribute_nodes_meshviewer_json(idp.read(), True)
            idp.close()

        dom3 = get_node_domain("daff61000302", lat=49.795449888, lon=8.754730225, accuracy=10,
                               polygons=polygons, default_domain="default")  # Domain 3
        dom2 = get_node_domain("daff61000402", lat=49.842410779, lon=8.750610352, accuracy=10,
                               polygons=polygons, default_domain="default")  # Domain 2
        dom1 = get_node_domain("c04a00dd692a", lat=49.840639497, lon=8.692588806, accuracy=10,
                               polygons=polygons, default_domain="default")  # Domain 1
        domd = get_node_domain("60e3272f92b2", lat=49.803427592, lon=8.670616150, accuracy=10,
                               polygons=polygons, default_domain="default")  # Default

        with open("topologies/topology_fullmesh.json", "r") as idp:
            distribute_nodes_meshviewer_json(idp.read(), False)
            idp.close()

        self.assertEqual(get_node_domain("daff61000302", lat=49.795449888, lon=8.754730225, accuracy=10,
                                         polygons=polygons, default_domain="default"), dom3)
        self.assertEqual(get_node_domain("daff61000402", lat=49.842410779, lon=8.750610352, accuracy=10,
                                         polygons=polygons, default_domain="default"), dom2)
        self.assertEqual(get_node_domain("c04a00dd692a", lat=49.840639497, lon=8.692588806, accuracy=10,
                                         polygons=polygons, default_domain="default"), dom1)
        self.assertEqual(get_node_domain("60e3272f92b2", lat=49.803427592, lon=8.670616150, accuracy=10,
                                         polygons=polygons, default_domain="default"), domd)

    def test_topology_update_bridging(self):
        # Test correct handling of topology update when bridging is not active
        with open("domains/sample_domains.geojson") as gj:
            polygons = load_domain_polygons(gj.read())
        with open("topologies/topology_independent.json", "r") as idp:
            distribute_nodes_meshviewer_json(idp.read(), True)
            idp.close()

        dom3 = get_node_domain("daff61000302", lat=49.795449888, lon=8.754730225, accuracy=10,
                               polygons=polygons, default_domain="default")  # Domain 3
        dom2 = get_node_domain("daff61000402", lat=49.842410779, lon=8.750610352, accuracy=10,
                               polygons=polygons, default_domain="default")  # Domain 2
        dom1 = get_node_domain("c04a00dd692a", lat=49.840639497, lon=8.692588806, accuracy=10,
                               polygons=polygons, default_domain="default")  # Domain 1
        domd = get_node_domain("60e3272f92b2", lat=49.803427592, lon=8.670616150, accuracy=10,
                               polygons=polygons, default_domain="default")  # Default

        self.assertNotEqual(dom3, dom2)
        self.assertNotEqual(dom2, dom1)
        self.assertNotEqual(dom1, domd)
        with open("topologies/topology_fullmesh.json", "r") as idp:
            distribute_nodes_meshviewer_json(idp.read(), True)
            idp.close()

        dom3 = get_node_domain("daff61000302", lat=49.795449888, lon=8.754730225, accuracy=10,
                               polygons=polygons, default_domain="default")  # Domain 3
        dom2 = get_node_domain("daff61000402", lat=49.842410779, lon=8.750610352, accuracy=10,
                               polygons=polygons, default_domain="default")  # Domain 2
        dom1 = get_node_domain("c04a00dd692a", lat=49.840639497, lon=8.692588806, accuracy=10,
                               polygons=polygons, default_domain="default")  # Domain 1
        domd = get_node_domain("60e3272f92b2", lat=49.803427592, lon=8.670616150, accuracy=10,
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

        get_node_domain("c04a00dd692a", lat=49.795449888, lon=8.754730225, accuracy=10000,
                        polygons=polygons, default_domain="default")
        get_node_domain("60e3272f92b2", lat=49.842410779, lon=8.750610352, accuracy=10,
                        polygons=polygons, default_domain="default", max_accuracy=250)
        get_node_domain("daff61000402", polygons=polygons, default_domain="default")

        self.assertEqual(Node.get(node_id="c04a00dd692a").mesh_id.decision_criteria,
                         int(DecisionCriteria.USER_LOCATION))
        self.assertEqual(Node.get(node_id="60e3272f92b2").mesh_id.decision_criteria,
                         int(DecisionCriteria.APPROX_LOCATION))
        self.assertEqual(Node.get(node_id="daff61000402").mesh_id.decision_criteria,
                         None)

    def test_get_domain_treshold_distance(self):
        with open("domains/sample_domains.geojson") as gj:
            polygons = load_domain_polygons(gj.read())
        self.assertEqual(get_domain(49.81112, 8.70434, polygons, 1.5), None)
        self.assertEqual(get_domain(49.81112, 8.70434, polygons, 1.6), "domain3")

    def test_manual_switch_time_independent(self):
        with open("domains/sample_domains.geojson") as gj:
            polygons = load_domain_polygons(gj.read())
        with open("topologies/topology_independent.json", "r") as idp:
            distribute_nodes_meshviewer_json(idp.read(), True)

        Mesh.set_manual_switch_time(Node.get(node_id="c04a00dd692a").mesh_id.id, 1650000000)

        _, node_c04a00dd692a_swich_time = get_node_domain("c04a00dd692a", lat=49.795449888, lon=8.754730225, accuracy=10000,
                        polygons=polygons, default_domain="default", default_switch_time=1600000000)
        _, node_60e3272f92b2_switch_time = get_node_domain("60e3272f92b2", lat=49.842410779, lon=8.750610352, accuracy=10,
                        polygons=polygons, default_domain="default", max_accuracy=250, default_switch_time=1600000000)

        self.assertEqual(Node.get(node_id="c04a00dd692a").switch_time, 1650000000)
        self.assertEqual(Node.get(node_id="60e3272f92b2").switch_time, 1600000000)

        self.assertEqual(Node.get(node_id="c04a00dd692a").switch_time, node_c04a00dd692a_swich_time)
        self.assertEqual(Node.get(node_id="60e3272f92b2").switch_time, node_60e3272f92b2_switch_time)

    def test_manual_switch_time_fullmesh(self):
        with open("domains/sample_domains.geojson") as gj:
            polygons = load_domain_polygons(gj.read())

        with open("topologies/topology_fullmesh.json", "r") as idp:
            distribute_nodes_meshviewer_json(idp.read(), True)

        self.assertEqual(Node.get_mesh_id("daff61000302"), Node.get_mesh_id("daff61000402"))

        Mesh.set_manual_switch_time(Node.get(node_id="c04a00dd692a").mesh_id.id, 1650000000)

        _, node_daff61000302_switch_time = get_node_domain("daff61000302", lat=49.795449888, lon=8.754730225, accuracy=10000,
                        polygons=polygons, default_domain="default", default_switch_time=1600000000)
        _, node_daff61000402_switch_time = get_node_domain("daff61000402", lat=49.842410779, lon=8.750610352, accuracy=10,
                        polygons=polygons, default_domain="default", max_accuracy=250, default_switch_time=1600000000)

        self.assertEqual(Node.get(node_id="daff61000302").switch_time, 1650000000)
        self.assertEqual(Node.get(node_id="daff61000402").switch_time, 1650000000)

        self.assertEqual(Node.get(node_id="daff61000302").switch_time, node_daff61000302_switch_time)
        self.assertEqual(Node.get(node_id="daff61000402").switch_time, node_daff61000402_switch_time)
