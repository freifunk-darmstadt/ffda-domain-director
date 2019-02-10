import requests
from peewee import DoesNotExist, IntegrityError, Database
from pymeshviewer.parser import parse_meshviewer_json

from director.db.model import Mesh, Node


def distribute_nodes(nodes: list, bridge_meshes: bool):
    for node in nodes:
        mesh_ids = []
        if not node["online"]:
            continue

        if not bridge_meshes:
            try:
                mesh_id = Node.get(node_id=node["node_id"]).mesh_id
                if mesh_id is not None:
                    continue
            except DoesNotExist:
                pass

        for neighbour in node["neighbours"]:
            try:
                mesh_id = Node.get(node_id=neighbour).mesh_id
                if mesh_id not in mesh_ids:
                    mesh_ids.append(mesh_id)
            except DoesNotExist:
                continue
        if len(mesh_ids) is 0:
            mesh_id = Mesh.create().id
        elif len(mesh_ids) is 1:
            mesh_id = mesh_ids[0]
        elif bridge_meshes:
            mesh_id = mesh_ids[0]
            Node.update(mesh_id=mesh_id).where(Node.mesh_id << mesh_ids).execute()
            mesh_ids.remove(mesh_id)
            Mesh.delete().where(Mesh.id == mesh_ids)
        else:
            mesh_id = mesh_ids[0]

        try:
            Node.create(node_id=node["node_id"], mesh_id=mesh_id,
                        latitude=node["location"]["latitude"] if "location" in node else None,
                        longitude=node["location"]["longitude"] if "location" in node else None)
        except IntegrityError:
            if bridge_meshes:
                Node.update(mesh_id=mesh_id,
                            latitude=node["location"]["latitude"] if "location" in node else None,
                            longitude=node["location"]["longitude"] if "location" in node else None).where(
                    Node.node_id == node["node_id"]).execute()


def distribute_nodes_meshviewer_json(meshviewer_json: str, initial_update=False):
    collection = parse_meshviewer_json(meshviewer_json)
    distribute_nodes([{"node_id": node.nodeinfo.node_id,
                       "online": node.online,
                       "location": {
                           "latitude": node.nodeinfo.location.latitude if node.nodeinfo.location is not None else None,
                           "longitude": node.nodeinfo.location.longitude if node.nodeinfo.location is not None else None},
                       "neighbours": [neighbour.node_id for neighbour in node.neighbours if not neighbour.vpn]}
                      for node in collection.nodes], initial_update)


def distribute_nodes_remote_meshviewer(meshviewer_url, initial_update=False):
    distribute_nodes_meshviewer_json(requests.get(meshviewer_url).text, initial_update)


def create_tables(database: Database):
    database.create_tables([Mesh, Node])
