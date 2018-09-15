import datetime
import json
from enum import Enum
from peewee import DoesNotExist
from shapely.geometry import shape, Point

from domain_director.db import Node, Mesh
from domain_director.geo import get_point_polygon_distance


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


def get_domain(lat, lon, domain_polygons, treshold_distance=0):
    closest_domain = None
    closest_domain_distance = None
    for domain_name, polygon in domain_polygons.items():
        if polygon.contains(Point(lon, lat)):
            return domain_name

        distance = get_point_polygon_distance(Point((lon, lat)), polygon)
        if closest_domain_distance is None or distance < closest_domain_distance:
            closest_domain = domain_name
            closest_domain_distance = distance

    if closest_domain and closest_domain_distance <= treshold_distance:
        return closest_domain
    return None


def decide_node_domain(node_id, polygons, lat=None, lon=None, accuracy=None, max_accuracy=250,
                       treshold_distance=0):
    domain = None
    criteria = None
    if lat and lon and accuracy and accuracy < max_accuracy:
        domain = get_domain(lat, lon, polygons, treshold_distance)
        criteria = DecisionCriteria.APPROX_LOCATION
    else:
        location = Node.get_location(node_id)
        if location["latitude"] is not None and location["longitude"] is not None:
            domain = get_domain(location["latitude"], location["longitude"], polygons, treshold_distance)
            criteria = DecisionCriteria.USER_LOCATION

    return domain, criteria


def get_node_domain(node_id, polygons, lat=None, lon=None, accuracy=None, default_domain=None, max_accuracy=250,
                    treshold_distance=0):
    mesh_id = Node.get_mesh_id(node_id)
    if mesh_id is None:
        domain = default_domain
    else:
        domain = Node.get_domain(node_id)

    if not domain:
        domain, criteria = decide_node_domain(node_id, polygons, lat, lon, accuracy, max_accuracy, treshold_distance)
        if domain and criteria:
            Mesh.set_domain(mesh_id, domain, criteria)

    domain = domain or default_domain

    try:
        Node.update(response=domain, query_time=datetime.datetime.now()).where(Node.node_id == node_id).execute()
    except DoesNotExist:
        pass

    return domain
