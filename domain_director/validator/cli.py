import click
import collections
import json
import os
from slpp import slpp as lua
from typing import TextIO


def print_list(l):
    for e in l:
        print(e)


@click.command()
@click.argument('geojson', type=click.File('r'))
@click.argument('domains', type=click.Path(exists=True))
def run(geojson: TextIO, domains: str):
    domains_site = []
    domains_polygons = []
    polygons = json.loads(geojson.read())["features"]

    # Read domain names from site
    for filename in os.listdir(domains):
        filepath = os.path.join(domains, filename)
        with open(filepath, 'r') as domainfile:
            for dom in lua.decode(domainfile.read())["domain_names"].keys():
                domains_site.append(dom)

    # Read domain names from polygons
    for polygon in polygons:
        print(polygon["properties"]["name"])
        domains_polygons.append(polygon["properties"]["name"])

    print("Domains contained in geojson and site:")
    print_list(sorted(list(set(domains_polygons).intersection(domains_site))))

    print("Domains contained exclusively in geojson:")
    print_list(sorted(list(set(domains_polygons) - set(domains_site))))

    print("Domains contained exclusively in domains:")
    print_list(sorted(list(set(domains_site) - set(domains_polygons))))

    print("Duplicate names in geojson:")
    print_list(sorted([item for item, count in collections.Counter(domains_polygons).items() if count > 1]))
