from peewee import Model, AutoField, CharField, Proxy, ForeignKeyField, DoesNotExist, IntegerField, FloatField, \
    DateTimeField


class BaseModel(Model):
    class Meta:
        database = Proxy()


class Mesh(BaseModel):
    id = AutoField(unique=True, primary_key=True)
    domain = CharField(null=True)
    decision_criteria = IntegerField(null=True)
    switch_time = IntegerField(column_name='switch_time', null=True)

    @staticmethod
    def set_domain(mesh_id, domain, decision_criteria):
        Mesh.update(domain=domain, decision_criteria=int(decision_criteria)).where(Mesh.id == mesh_id).execute()

    @staticmethod
    def get_switch_time(mesh_id):
        try:
            mesh_db_entry = Mesh.select().where(Mesh.id == mesh_id).get()
        except DoesNotExist:
            return None
        return mesh_db_entry.switch_time

    @staticmethod
    def set_switch_time(mesh_id, switch_time):
        Mesh.update(switch_time=switch_time).where(Mesh.id == mesh_id).execute()

    class Meta:
        table_name = 'meshes'


class Node(BaseModel):
    id = AutoField()
    node_id = CharField(unique=True)
    mesh_id = ForeignKeyField(Mesh, backref='nodes')
    latitude = FloatField(null=True)
    longitude = FloatField(null=True)
    query_time = DateTimeField(null=True)
    response = CharField(null=True)
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
        output = {}
        for node in Node.select():
            if node.mesh_id.id not in output:
                output[node.mesh_id.id] = {
                    "domain": node.mesh_id.domain,
                    "switch_time": node.mesh_id.switch_time,
                    "nodes": []
                }
            output[node.mesh_id.id]["nodes"].append({"node_id": node.node_id,
                                                     "domain": node.response,
                                                     "switch_time": node.switch_time,
                                                     "query_time": node.query_time})
        return output

    class Meta:
        table_name = 'mesh_members'
