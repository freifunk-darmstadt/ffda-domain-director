import json
from enum import Enum

from shapely.geometry import shape, Point

from domain_director.db import Node, Mesh


class DecisionCriteria(Enum):
    APPROX_LOCATION = 1
    USER_LOCATION = 2
    DEFAULT_DOMAIN = 3

    def __int__(self):
        return self.value


def load_domain_polygons(geojson_input):
    polygons = {}
    for feature in json.loads(geojson_input)['features']:
        polygon = shape(feature['geometry'])
        domain_name = feature["properties"]["name"]
        polygons[domain_name] = polygon

    return polygons


def get_domain(lat, lon, domain_polygons):
    for domain_name, polygon in domain_polygons.items():
        if polygon.contains(Point(lon, lat)):
            return domain_name
    return None


def decide_node_domain(node_id, polygons, lat=None, lon=None, accuracy=None, default_domain=None, max_accuracy=250):
    criteria = None
    mesh_id = Node.get_mesh_id(node_id)
    domain = Node.get_domain(node_id)
    location = Node.get_location(node_id)
    if domain:
        return domain

    if lat and lon and accuracy and accuracy < max_accuracy:
        domain = get_domain(lat, lon, polygons)
        criteria = DecisionCriteria.APPROX_LOCATION
    elif location["latitude"] is not None and location["longitude"] is not None:
        domain = get_domain(location["latitude"], location["longitude"], polygons)
        criteria = DecisionCriteria.USER_LOCATION

    if domain and criteria:
        Mesh.set_domain(mesh_id, domain, criteria)

    return domain or default_domain
