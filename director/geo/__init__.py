from math import radians, sin, asin, sqrt, cos

from shapely.geometry import Point, Polygon, LinearRing

class Location:
    def __init__(self, lat, lon, accuracy=0, provider=None):
        self.provider = provider
        self.lat = lat
        self.lon = lon
        self.accuracy = accuracy


def haversine(lon1, lat1, lon2, lat2):
    # https://stackoverflow.com/questions/15736995/how-can-i-quickly-estimate-the-distance-between-two-latitude-longitude-points
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    # Radius of earth in kilometers is 6371
    km = 6371 * c
    return km


def get_point_polygon_distance(point: Point, polygon: Polygon):
    pol_ext = LinearRing(polygon.exterior.coords)
    p = pol_ext.interpolate(pol_ext.project(Point(point.x, point.y)))
    closest_point_coords = list(p.coords)[0]
    return haversine(point.x, point.y, closest_point_coords[0], closest_point_coords[1])
