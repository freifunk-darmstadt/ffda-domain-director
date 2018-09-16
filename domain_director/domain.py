import datetime
import json
from enum import Enum
from mozls import MLSException, query_mls, WifiNetwork
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
                       treshold_distance=0, default_domain=None):
    if lat and lon and accuracy and accuracy < max_accuracy:
        domain = get_domain(lat, lon, polygons, treshold_distance)
        criteria = DecisionCriteria.APPROX_LOCATION
    else:
        criteria = DecisionCriteria.USER_LOCATION
        location = Node.get_location(node_id)
        if location is None or (location["latitude"] is None and location["longitude"] is None):
            # No location supplied by user
            # Can't decide domain
            return None, DecisionCriteria.USER_LOCATION
        domain = get_domain(location["latitude"], location["longitude"], polygons, treshold_distance)

    # If we do not have decided on a domain yet, we know the nodes location, but it is not covered by a domain
    # nor close enough to one domain. So we are assigning it to the default domain.
    # If no default domain is set, we are returning None here.
    domain = domain or default_domain

    return domain, criteria


def get_node_domain(node_id, polygons, wifis=None, api_key="test", lat=None, lon=None, accuracy=None,
                    default_domain=None,
                    max_accuracy=250, treshold_distance=0, switch_time=-1, migrate_only_vpn=False):
    is_vpn_only = False
    mesh_id = Node.get_mesh_id(node_id)
    if mesh_id is None:
        domain = default_domain
    else:
        domain = Node.get_domain(node_id)
        is_vpn_only = len(list(Node.select().where(Node.mesh_id == mesh_id))) == 1

    if not domain:
        if wifis is not None and len(wifis) > 2:
            try:
                mls_response = query_mls(
                    wifi_networks=[WifiNetwork(mac_address=ap["bssid"], signalStrength=int(ap["signal"]))
                                   for ap in wifis],
                    apikey=api_key)
                lat = mls_response.lat
                lon = mls_response.lon
                accuracy = mls_response.accuracy
            except MLSException:
                # handle MLS data as optional (it is anyway)
                pass
        domain, criteria = decide_node_domain(node_id, polygons, lat, lon, accuracy, max_accuracy, treshold_distance,
                                              default_domain)
        if domain and criteria:
            Mesh.set_domain(mesh_id, domain, criteria)

    domain = domain or default_domain

    if migrate_only_vpn is True and not is_vpn_only:
        out_switch_time = -1
    else:
        out_switch_time = switch_time

    try:
        Node.update(response=domain, query_time=datetime.datetime.now(), switch_time=out_switch_time).where(Node.node_id == node_id).execute()
    except DoesNotExist:
        pass

    return domain, out_switch_time
