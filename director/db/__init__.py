from datetime import datetime

import requests
from peewee import Database
from playhouse.migrate import SqliteMigrator, migrate
from pymeshviewer.parser import parse_meshviewer_json

from director.db.model import Mesh, Node, BaseModel


def insert_nodes(nodes: list):
    for node in nodes:
        if not node["online"]:
            continue

        Node.replace(node_id=node["node_id"],
                     last_seen=datetime.now(),
                     latitude=node["location"]["latitude"] if "location" in node else None,
                     longitude=node["location"]["longitude"] if "location" in node else None)


def insert_links(links):



def distribute_nodes_meshviewer_json(meshviewer_json: str):
    collection = parse_meshviewer_json(meshviewer_json)

    insert_nodes([
        {
            "node_id": node.nodeinfo.node_id,
            "online": node.online,
            "location": {
                "latitude": node.nodeinfo.location.latitude if node.nodeinfo.location is not None else None,
                "longitude": node.nodeinfo.location.longitude if node.nodeinfo.location is not None else None}
        }
        for node in collection.nodes])

    insert_links([
        {
            "node_a": link.source,
            "node_b": link.target,
            ""
        }
    for link in collection.links])


def distribute_nodes_remote_meshviewer(meshviewer_url, initial_update=False):
    distribute_nodes_meshviewer_json(requests.get(meshviewer_url).text, initial_update)


def create_tables(database: Database):
    database.create_tables([Mesh, Node])


def update_tables():
    migrator = SqliteMigrator(BaseModel._meta.database)
    mesh_columns = [e.name for e in BaseModel._meta.database.get_columns('meshes')]
    if 'switch_time' not in mesh_columns:
        migrate(
            migrator.add_column('meshes', 'switch_time', Mesh.switch_time),
        )
