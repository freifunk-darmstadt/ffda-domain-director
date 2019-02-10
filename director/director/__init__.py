import datetime
import json
from enum import Enum
from peewee import DoesNotExist
from shapely.geometry import shape, Point

from director.db import Node, Mesh
from director.geo import get_point_polygon_distance, Location


class DecisionCriteria(Enum):
    APPROX_LOCATION = 1
    USER_LOCATION = 2
    DEFAULT_DOMAIN = 3

    def __int__(self):
        return self.value


class Director:
    def __init__(self, config, geo_provider, polygons):
        self.config = config
        self.geo_provider = geo_provider
        self.polygons = polygons

        if type(self.polygons) is str:
            self.polygons = Director.load_polygons(polygons)

    @staticmethod
    def load_polygons(geojson_input):
        polygons = {}

        for feature in json.loads(geojson_input)['features']:
            polygon = shape(feature['geometry'])
            domain_name = feature["properties"]["name"]
            polygons[domain_name] = polygon

        return polygons

    def get_domain(self, location):
        closest_domain = None
        closest_domain_distance = None
        for domain_name, polygon in self.polygons.items():
            if polygon.contains(Point((location.lon, location.lat))):
                return domain_name

            distance = get_point_polygon_distance(Point((location.lon, location.lat)), polygon)
            if closest_domain_distance is None or distance < closest_domain_distance:
                closest_domain = domain_name
                closest_domain_distance = distance

        if closest_domain and closest_domain_distance <= self.config.get("tolerance_distance", 0):
            return closest_domain
        return None

    def decide_node_domain(self, node_id, location):
        if location is not None and location.accuracy < self.config["max_accuracy"]:
            domain = self.get_domain(location)
            criteria = DecisionCriteria.APPROX_LOCATION
        else:
            criteria = DecisionCriteria.USER_LOCATION
            db_loc = Node.get_location(node_id)
            if db_loc is None or (db_loc["latitude"] is None and db_loc["longitude"] is None):
                # No location supplied by user
                # Can't decide domain
                return None, DecisionCriteria.USER_LOCATION
            domain = self.get_domain(Location(db_loc["latitude"], db_loc["longitude"]))

        # If we do not have decided on a domain yet, we know the nodes location, but it is not covered by a domain
        # nor close enough to one domain. So we are assigning it to the default domain.
        # If no default domain is set, we are returning None here.
        domain = domain or self.config["default_domain"]

        return domain, criteria

    def get_node_domain(self, node_id, wifis=None, location=None):
        is_vpn_only = False
        mesh_id = Node.get_mesh_id(node_id)
        if mesh_id is None:
            domain = self.config["default_domain"]
        else:
            domain = Node.get_domain(node_id)
            is_vpn_only = len(list(Node.select().where(Node.mesh_id == mesh_id))) == 1

        if not domain:
            if wifis is not None and len(wifis) > 2:
                location = self.geo_provider.get_location(wifis)

            domain, criteria = self.decide_node_domain(node_id, location)

            if domain and criteria:
                Mesh.set_domain(mesh_id, domain, criteria)

        domain = domain or self.config["default_domain"]

        if self.config["only_migrate_vpn"] is True and not is_vpn_only:
            out_switch_time = -1
        else:
            out_switch_time = self.config["domain_switch_time"]

        try:
            Node.update(response=domain, query_time=datetime.datetime.now(), switch_time=out_switch_time).where(
                Node.node_id == node_id).execute()
        except DoesNotExist:
            pass

        return domain, out_switch_time
