import os

import click as click
import yaml
from waitress import serve

from domain_director.server import create_app


def read_config_file(path):
    with open(path, "r") as f:
        content = f.read()
        config = yaml.load(content)
        return config


@click.command()
@click.option('--config', default='config.yml', help='Host of web-server.')
def run(config):
    config_file_path = os.path.join(os.getcwd(), config) if config[0] != os.sep else config
    app_config = read_config_file(config_file_path)

    app = create_app(config=app_config)
    serve(app, listen='{host}:{port}'.format(host=app_config["host"], port=app_config["port"]))
