import geojson
from fastkml import kml, LineStyle, PolyStyle
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

    a = list(list(k.features()).pop().features())[0].styleUrl

    styles = list(list(k.features()).pop().styles())
    features = FeatureCollection([Feature(
        geometry=Polygon([[(coordinate[0], coordinate[1]) for coordinate in area.geometry.exterior.coords]]),
        properties={"name": get_domaincode(area),
                    "pretty_name": area.name,
                    "color": "#" + [polystyle for polystyle in [list(style.styles()) for style in styles
                                                               if area.styleUrl[1:] + '-normal' == style.id][0]
                                   if type(polystyle) == PolyStyle][0].color[2:]
                    }
    ) for area in list(k.features()).pop().features()])

    return geojson.dumps(features)
