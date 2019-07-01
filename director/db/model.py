from datetime import datetime

from peewee import Model, AutoField, CharField, Proxy, ForeignKeyField, DoesNotExist, IntegerField, FloatField, \
    DateTimeField


class BaseModel(Model):
    class Meta:
        database = Proxy()


class Link(BaseModel):
    id = AutoField(unique=True, primary_key=True)
    node_a = CharField(null=True)
    node_b = CharField(null=True)
    first_seen = DateTimeField(column_name='first_seen', null=True)
    last_seen = DateTimeField(column_name='last_seen', null=True)

    @staticmethod
    def get_links(node_id):
        links = Link.select().where(Link.node_a == node_id or Link.node_b).get()
        return links if len(links) > 0 else []

    class Meta:
        table_name = 'links'


class Node(BaseModel):
    node_id = CharField(primary_key=True)
    latitude = FloatField(null=True)
    longitude = FloatField(null=True)
    last_seen = DateTimeField()
    query_time = DateTimeField(null=True)
    domain = CharField(null=True)
    switch_time = IntegerField(null=True)

    @staticmethod
    def get_domain(node_id):
        try:
            node_db_entry = Node.select().where(Node.node_id == node_id).get()
        except DoesNotExist:
            return None
        return node_db_entry.mesh_id.domain

    @staticmethod
    def get_mesh_id(node_id):
        try:
            node_db_entry = Node.select().where(Node.node_id == node_id).get()
        except DoesNotExist:
            return None
        return node_db_entry.mesh_id.id

    @staticmethod
    def get_location(node_id):
        try:
            node_db_entry = Node.select().where(Node.node_id == node_id).get()
        except DoesNotExist:
            return None
        return {"latitude": node_db_entry.latitude, "longitude": node_db_entry.longitude}

    @staticmethod
    def get_nodes_grouped():
        all_nodes = list(Node.select())
        nodes = list(all_nodes)
        meshes = []

        def follow_path(path_node):
            nodes.remove(path_node)
            node_links = Link.get_links(path_node.id)
            neighbour_nodes = []
            for link in node_links:
                neighbour_node_id = link.node_a if link.node_a != path_node.node_id else link.node_b
                neighbour_node_list = list(filter(lambda n: n.id == neighbour_node_id, all_nodes))

                if len(neighbour_node_list) is 0:
                    continue

                neighbour_node = neighbour_node_list[0]
                if neighbour_node in nodes:
                    neighbour_nodes += follow_path(neighbour_node)

            return neighbour_nodes

        while len(nodes) > 0:
            node = nodes[0]
            mesh = follow_path(node)
            meshes.append(mesh)

        return meshes

    class Meta:
        table_name = 'nodes'
