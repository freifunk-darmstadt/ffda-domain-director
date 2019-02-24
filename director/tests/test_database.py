import unittest

from peewee import SqliteDatabase

from director.db import create_tables, distribute_nodes, distribute_nodes_remote_meshviewer
from director.db.model import Mesh, Node, BaseModel

database = BaseModel._meta.database


class TestDatabaseModule(unittest.TestCase):
    nodes = [
        {"node_id": "de:ad:be:ef:ba:ba", "neighbours": ["de:ad:be:ef:ba:bb", "de:ad:be:ef:ba:bc"], "online": True, },
        {"node_id": "de:ad:be:ef:ba:bb", "neighbours": ["de:ad:be:ef:ba:bc", "de:ad:be:ef:ba:ba"], "online": True, },
        {"node_id": "de:ad:be:ef:ba:bc",
         "neighbours": ["de:ad:be:ef:ba:bd", "de:ad:be:ef:ba:bb", "de:ad:be:ef:ba:ba"], "online": True, },
        {"node_id": "de:ad:be:ef:ba:bd", "neighbours": ["de:ad:be:ef:ba:be", "de:ad:be:ef:ba:bc"], "online": True, },
        {"node_id": "de:ad:be:ef:ba:be", "neighbours": ["de:ad:be:ef:ba:bd"], "online": True, },
        {"node_id": "de:ad:be:ef:ba:bf", "neighbours": [], "online": True, },
    ]

    initial_nodes = [
        {"node_id": "de:ad:be:ef:ba:ba", "neighbours": ["de:ad:be:ef:ba:bb"], "online": True, },
        {"node_id": "de:ad:be:ef:ba:bb", "neighbours": ["de:ad:be:ef:ba:ba"], "online": True, },
        {"node_id": "de:ad:be:ef:ba:bd", "neighbours": ["de:ad:be:ef:ba:be"], "online": True, },
        {"node_id": "de:ad:be:ef:ba:be", "neighbours": ["de:ad:be:ef:ba:bd"], "online": True, },
    ]

    extra_nodes = [
        {"node_id": "de:ad:be:ef:ba:bc",
         "neighbours": ["de:ad:be:ef:ba:bd", "de:ad:be:ef:ba:bb", "de:ad:be:ef:ba:ba"], "online": True, },
        {"node_id": "de:ad:be:ef:ba:bf", "neighbours": [], "online": True, },
    ]

    nodes_state_0 = [
        {"node_id": "de:ad:be:ef:ba:ba", "neighbours": [], "online": True, },
        {"node_id": "de:ad:be:ef:ba:bb", "neighbours": [], "online": True, }
    ]

    nodes_state_1 = [
        {"node_id": "de:ad:be:ef:ba:ba", "neighbours": ["de:ad:be:ef:ba:bb"], "online": True, },
        {"node_id": "de:ad:be:ef:ba:bb", "neighbours": ["de:ad:be:ef:ba:ba"], "online": True, }
    ]

    def setUp(self):
        self.db = SqliteDatabase(':memory:')
        database.initialize(self.db)
        create_tables(database)

    def test_mesh_creation(self):
        mesh_ids = [Mesh.create().id for m in range(len(self.nodes))]
        self.assertListEqual(mesh_ids, [m for m in range(1, len(self.nodes) + 1)])

    def test_node_distribution_new_node_bridging(self):
        distribute_nodes(self.initial_nodes, True)
        m0_0 = Node.get(Node.node_id == "de:ad:be:ef:ba:ba")
        m0_1 = Node.get(Node.node_id == "de:ad:be:ef:ba:bb")
        m1_0 = Node.get(Node.node_id == "de:ad:be:ef:ba:be")
        m1_1 = Node.get(Node.node_id == "de:ad:be:ef:ba:bd")
        self.assertEqual(m0_0.mesh_id, m0_1.mesh_id)
        self.assertEqual(m1_0.mesh_id, m1_1.mesh_id)
        self.assertNotEqual(m1_0.mesh_id, m0_0.mesh_id)

        distribute_nodes(self.extra_nodes, True)
        m0_0 = Node.get(Node.node_id == "de:ad:be:ef:ba:ba")
        m0_1 = Node.get(Node.node_id == "de:ad:be:ef:ba:bb")
        m1_0 = Node.get(Node.node_id == "de:ad:be:ef:ba:be")
        m1_1 = Node.get(Node.node_id == "de:ad:be:ef:ba:bd")
        m2_0 = Node.get(Node.node_id == "de:ad:be:ef:ba:bf")

        self.assertEqual(m0_0.mesh_id, m0_1.mesh_id)
        self.assertEqual(m1_0.mesh_id, m1_1.mesh_id)
        self.assertEqual(m1_0.mesh_id, m0_0.mesh_id)
        self.assertNotEqual(m1_0.mesh_id, m2_0.mesh_id)

    def test_node_distribution_new_node_no_bridging(self):
        distribute_nodes(self.initial_nodes, True)
        m0_0 = Node.get(Node.node_id == "de:ad:be:ef:ba:ba")
        m0_1 = Node.get(Node.node_id == "de:ad:be:ef:ba:bb")
        m1_0 = Node.get(Node.node_id == "de:ad:be:ef:ba:be")
        m1_1 = Node.get(Node.node_id == "de:ad:be:ef:ba:bd")
        self.assertEqual(m0_0.mesh_id, m0_1.mesh_id)
        self.assertEqual(m1_0.mesh_id, m1_1.mesh_id)
        self.assertNotEqual(m1_0.mesh_id, m0_0.mesh_id)

        distribute_nodes(self.extra_nodes, False)
        m0_0 = Node.get(Node.node_id == "de:ad:be:ef:ba:ba")
        m0_1 = Node.get(Node.node_id == "de:ad:be:ef:ba:bb")
        m1_0 = Node.get(Node.node_id == "de:ad:be:ef:ba:be")
        m1_1 = Node.get(Node.node_id == "de:ad:be:ef:ba:bd")
        m2_0 = Node.get(Node.node_id == "de:ad:be:ef:ba:bf")

        self.assertEqual(m0_0.mesh_id, m0_1.mesh_id)
        self.assertEqual(m1_0.mesh_id, m1_1.mesh_id)
        self.assertNotEqual(m1_0.mesh_id, m0_0.mesh_id)
        self.assertNotEqual(m0_0.mesh_id, m2_0.mesh_id)
        self.assertNotEqual(m1_0.mesh_id, m2_0.mesh_id)

    def test_node_distribution_new_link_bridging(self):
        distribute_nodes(self.nodes_state_0, True)
        n0 = Node.get(Node.node_id == "de:ad:be:ef:ba:ba")
        n1 = Node.get(Node.node_id == "de:ad:be:ef:ba:bb")
        self.assertNotEqual(n0.mesh_id, n1.mesh_id)
        distribute_nodes(self.nodes_state_1, True)
        n0 = Node.get(Node.node_id == "de:ad:be:ef:ba:ba")
        n1 = Node.get(Node.node_id == "de:ad:be:ef:ba:bb")
        self.assertEqual(n0.mesh_id, n1.mesh_id)

    def test_node_distribution_new_link_no_bridging(self):
        distribute_nodes(self.nodes_state_0, True)
        n0 = Node.get(Node.node_id == "de:ad:be:ef:ba:ba")
        n1 = Node.get(Node.node_id == "de:ad:be:ef:ba:bb")
        self.assertNotEqual(n0.mesh_id, n1.mesh_id)
        distribute_nodes(self.nodes_state_1, False)
        n0 = Node.get(Node.node_id == "de:ad:be:ef:ba:ba")
        n1 = Node.get(Node.node_id == "de:ad:be:ef:ba:bb")
        self.assertNotEqual(n0.mesh_id, n1.mesh_id)

    def test_remote_update(self):
        distribute_nodes_remote_meshviewer("https://meshviewer.darmstadt.freifunk.net/data/meshviewer.json", True)
        distribute_nodes_remote_meshviewer("https://meshviewer.darmstadt.freifunk.net/data/meshviewer.json", False)
