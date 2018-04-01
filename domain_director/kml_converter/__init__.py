import geojson
from fastkml import kml
from geojson import FeatureCollection, Feature, Polygon


def get_domaincode(data, fieldnames=None):
    if fieldnames is None:
        fieldnames = ["Description", "description"]

    if data.extended_data is not None:
        for df in data.extended_data.elements:
            for name in fieldnames:
                if df.name == name and len(df.value) > 0:
                    return df.value
    return data.description


def convert_kml_to_geojson(kml_input):
    k = kml.KML()
    k.from_string(kml_input)

    features = FeatureCollection([Feature(
        geometry=Polygon([[(coordinate[0], coordinate[1]) for coordinate in area.geometry.exterior.coords]]),
        properties={"name": get_domaincode(area), "pretty_name": area.name}
    ) for area in list(k.features()).pop().features()])

    return geojson.dumps(features)
