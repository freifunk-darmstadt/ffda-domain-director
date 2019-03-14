import os
import sys
from datetime import datetime

import click as click
import yaml
from waitress import serve

from domain_director.server import create_app, init_database
from domain_director.db.model import db, Mesh


def read_config_file(path):
    with open(path, "r") as f:
        content = f.read()
        config = yaml.load(content)
        return config

@click.group(invoke_without_command=True)
@click.option('--config', default='config.yml', help='YAML config file')
@click.pass_context
def cli(ctx, config):
    config_file_path = os.path.join(os.getcwd(), config) if config[0] != os.sep else config
    app_config = read_config_file(config_file_path)
    ctx.meta['config'] = app_config

    if ctx.invoked_subcommand is None:
        geojson_file_path = os.path.join(os.getcwd(), app_config["geojson"]) if app_config["geojson"][0] != os.sep else \
            app_config["geojson"]

        app = create_app(dict(
            GEOJSON_FILE=geojson_file_path,
            MLS_API_KEY=app_config["mls_api_key"],
            DOMAIN_SWITCH_TIME=app_config["domain_switch_time"],
            DEFAULT_DOMAIN=app_config["default_domain"],
            MESHVIEWER_JSON_URL=app_config["meshviewer_json_url"],
            SQLITE_PATH=app_config["sqlite_path"],
            UPDATE_INTERVAL=app_config["update_interval"],
            ONLY_MIGRATE_VPN=app_config["only_migrate_vpn"]
        ))
        serve(app, listen='{host}:{port}'.format(host=app_config["host"], port=app_config["port"]))

@cli.command()
@click.option('--force', is_flag=True)
@click.argument('meshid', nargs=1)
@click.argument('switch_time', nargs=1)
@click.pass_context
def set_switch_time(ctx, force, **kwargs):
    init_database(ctx.meta['config']['sqlite_path'])

    try:
        mesh_db_entry = Mesh.select().where(Mesh.id == int(kwargs['meshid'])).get()
    except DoesNotExist:
        print('Mesh with ID {} not found.'.format(kwargs['meshid']))
        sys.exit(1)
    except ValueError:
        print('Invalid meshid specified')
        sys.exit(1)

    try:
        switch_time = int(kwargs['switch_time'])
        switch_time_parsed = datetime.utcfromtimestamp(switch_time)
    except ValueError:
        print('Invalid switch time specified')
        sys.exit(1)

    now = datetime.utcnow()

    if not force and (switch_time_parsed - now).total_seconds() < 0:
        print('Specified switch time lies in the past. Force to set value.')
        sys.exit(1)

    Mesh.set_manual_switch_time(mesh_db_entry.id, switch_time)

    print("Set switch time for mesh {} to {}.".format(mesh_db_entry.id, switch_time_parsed.strftime("%Y-%m-%d %H:%M")))
