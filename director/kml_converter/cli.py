from typing import TextIO

import click

from . import convert_kml_to_geojson


@click.command()
@click.argument('kml_in', type=click.File('r'))
@click.argument('geojson_out', type=click.File('w'))
def run(kml_in: TextIO, geojson_out: TextIO):
    kml_str = kml_in.read()
    kml_in.close()

    geojson_out.write(convert_kml_to_geojson(kml_str.encode()))
    geojson_out.close()
