import json

from shapely.geometry import shape, Point


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
