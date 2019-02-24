import unittest

import yaml
from peewee import SqliteDatabase

from director.db import create_tables, distribute_nodes_meshviewer_json
from director.db.model import Node, BaseModel
from director.director import Director, DecisionCriteria
from director.geo import Location

db = BaseModel._meta.database


class TestDomainModule(unittest.TestCase):

    def setUp(self):
        database = SqliteDatabase(':memory:')
        db.initialize(database)
        create_tables(database)
        with open("domains/sample_domains.geojson", "r") as f:
            polygons = f.read()
        with open("config/config0.yml", "r") as f:
            config = yaml.load(f.read())
        self.director = Director(config["director"], None, polygons)

    def test_domains(self):
        self.assertEqual(self.director.get_domain(Location(49.843996, 8.700313)), "domain1")
        self.assertEqual(self.director.get_domain(Location(49.859322, 8.754904)), "domain2")
        self.assertEqual(self.director.get_domain(Location(49.797885, 8.754848)), "domain3")
        self.assertEqual(self.director.get_domain(Location(49.791845, 8.693972)), None)

    def test_domain_query_no_approx_location(self):
        with open("topologies/topology_independent.json", "r") as idp:
            distribute_nodes_meshviewer_json(idp.read(), True)
            idp.close()
        dom0, decision_criteria = self.director.get_node_domain("c04a00dd692a")
        self.assertEqual(dom0, "domain1")

    def test_topology_update_no_bridging(self):
        # Test correct handling of topology update when bridging is not active
        with open("topologies/topology_independent.json", "r") as idp:
            distribute_nodes_meshviewer_json(idp.read(), True)
            idp.close()

        dom3_0 = self.director.get_node_domain("daff61000302",
                                               location=Location(49.795449888, 8.754730225, 10))  # Domain 3
        dom2_0 = self.director.get_node_domain("daff61000402",
                                               location=Location(49.842410779, 8.750610352, 10))  # Domain 2
        dom1_0 = self.director.get_node_domain("c04a00dd692a",
                                               location=Location(49.840639497, 8.692588806, 10))  # Domain 1
        domd_0 = self.director.get_node_domain("60e3272f92b2",
                                               location=Location(49.803427592, 8.670616150, 10))  # Default

        with open("topologies/topology_fullmesh.json", "r") as idp:
            distribute_nodes_meshviewer_json(idp.read(), False)
            idp.close()

        dom3_1 = self.director.get_node_domain("daff61000302",
                                               location=Location(49.795449888, 8.754730225, 10))  # Domain 3
        dom2_1 = self.director.get_node_domain("daff61000402",
                                               location=Location(49.842410779, 8.750610352, 10))  # Domain 2
        dom1_1 = self.director.get_node_domain("c04a00dd692a",
                                               location=Location(49.840639497, 8.692588806, 10))  # Domain 1
        domd_1 = self.director.get_node_domain("60e3272f92b2",
                                               location=Location(49.803427592, 8.670616150, 10))  # Default

        self.assertEqual(dom3_0, dom3_1)
        self.assertEqual(dom2_0, dom2_1)
        self.assertEqual(dom1_0, dom1_1)
        self.assertEqual(domd_0, domd_1)

    def test_topology_update_bridging(self):
        # Test correct handling of topology update when bridging is not active
        with open("topologies/topology_independent.json", "r") as idp:
            distribute_nodes_meshviewer_json(idp.read(), True)
            idp.close()

        dom3_0 = self.director.get_node_domain("daff61000302",
                                               location=Location(49.795449888, 8.754730225, 10))  # Domain 3
        dom2_0 = self.director.get_node_domain("daff61000402",
                                               location=Location(49.842410779, 8.750610352, 10))  # Domain 2
        dom1_0 = self.director.get_node_domain("c04a00dd692a",
                                               location=Location(49.840639497, 8.692588806, 10))  # Domain 1
        domd_0 = self.director.get_node_domain("60e3272f92b2",
                                               location=Location(49.803427592, 8.670616150, 10))  # Default

        self.assertNotEqual(dom3_0, dom2_0)
        self.assertNotEqual(dom2_0, dom1_0)
        self.assertNotEqual(dom1_0, domd_0)
        with open("topologies/topology_fullmesh.json", "r") as idp:
            distribute_nodes_meshviewer_json(idp.read(), True)
            idp.close()

        dom3_1 = self.director.get_node_domain("daff61000302",
                                               location=Location(49.795449888, 8.754730225, 10))  # Domain 3
        dom2_1 = self.director.get_node_domain("daff61000402",
                                               location=Location(49.842410779, 8.750610352, 10))  # Domain 2
        dom1_1 = self.director.get_node_domain("c04a00dd692a",
                                               location=Location(49.840639497, 8.692588806, 10))  # Domain 1
        domd_1 = self.director.get_node_domain("60e3272f92b2",
                                               location=Location(49.803427592, 8.670616150, 10))  # Default

        self.assertEqual(dom3_1, dom2_1)
        self.assertEqual(dom2_1, dom1_1)
        self.assertNotEqual(dom2_1, domd_1)

    def test_decision_criteria(self):
        with open("topologies/topology_independent.json", "r") as idp:
            distribute_nodes_meshviewer_json(idp.read(), True)
            idp.close()

        self.director.get_node_domain("c04a00dd692a", location=Location(49.795449888, 8.754730225, 10000))
        self.director.get_node_domain("60e3272f92b2", location=Location(49.842410779, 8.750610352, 10))
        self.director.get_node_domain("daff61000402")

        self.assertEqual(Node.get(node_id="c04a00dd692a").mesh_id.decision_criteria,
                         int(DecisionCriteria.USER_LOCATION))
        self.assertEqual(Node.get(node_id="60e3272f92b2").mesh_id.decision_criteria,
                         int(DecisionCriteria.APPROX_LOCATION))
        self.assertEqual(Node.get(node_id="daff61000402").mesh_id.decision_criteria,
                         None)

    def test_get_domain_treshold_distance(self):
        self.director.config["tolerance_distance"] = 1.5
        self.assertEqual(self.director.get_domain(Location(49.81112, 8.70434)), None)
        self.director.config["tolerance_distance"] = 1.6
        self.assertEqual(self.director.get_domain(Location(49.81112, 8.70434)), "domain3")

    def test_migrate_only_vpn(self):
        self.director.config["migrate_only_vpn"] = True
        with open("topologies/topology_independent.json", "r") as idp:
            distribute_nodes_meshviewer_json(idp.read(), True)
            idp.close()
        domain, switch_time = self.director.get_node_domain("c04a00dd692a",
                                                            location=Location(49.803427592, 8.670616150, 10))
        self.assertEqual(switch_time, 1600000000)

        with open("topologies/topology_fullmesh.json", "r") as idp:
            distribute_nodes_meshviewer_json(idp.read(), True)
            idp.close()
        domain, switch_time = self.director.get_node_domain("c04a00dd692a",
                                                            location=Location(49.803427592, 8.670616150, 10))
        self.assertEqual(switch_time, -1)
