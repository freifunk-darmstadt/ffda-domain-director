import geojson
from fastkml import kml
from geojson import FeatureCollection, Feature, Polygon


def convert_kml_to_geojson(kml_input):
    k = kml.KML()
    k.from_string(kml_input)

    features = FeatureCollection([Feature(
        geometry=Polygon([[(coordinate[0], coordinate[1]) for coordinate in area.geometry.exterior.coords]]),
        properties={"name": area.description, "pretty_name": area.name}
    ) for area in list(k.features()).pop().features()])

    return geojson.dumps(features)
