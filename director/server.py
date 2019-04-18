import atexit

import os
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from flask import Flask
from peewee import SqliteDatabase
from playhouse.migrate import migrate, SqliteMigrator

import director.blueprints
from director.db import create_tables, distribute_nodes_remote_meshviewer
from director.db.model import Mesh, Node, BaseModel
from director.director import Director
from director.geo.MozillaProvider import MozillaProvider

db = BaseModel._meta.database


def setup_geo_provider(config):
    if config["provider"] == "mozilla":
        return MozillaProvider(config)

    raise NotImplementedError


def migrate_database():
    migrator = SqliteMigrator(db)
    mesh_columns = [e.name for e in db.get_columns('meshes')]
    if 'switch_time' not in mesh_columns:
        migrate(
            migrator.add_column('meshes', 'switch_time', Mesh.switch_time),
        )

def setup_database(config, testing):
    db.initialize(SqliteDatabase(config["sqlite_path"]))
    if not Node.table_exists() and not Mesh.table_exists():
        create_tables(db)
        if not testing:
            distribute_nodes_remote_meshviewer(config["meshviewer_json_url"], True)
    else:
        migrate_database()
        if not testing:
            distribute_nodes_remote_meshviewer(config["meshviewer_json_url"], False)


def setup_director(geo_provider, config, testing):
    setup_database(config, testing)

    def update_nodes():
        distribute_nodes_remote_meshviewer(config["meshviewer_json_url"], False)

    if config["update_interval"] > 0:
        scheduler = BackgroundScheduler()
        scheduler.start()
        scheduler.add_job(
            func=update_nodes,
            trigger=IntervalTrigger(seconds=config["update_interval"]),
            id='update_meshviewer_job',
            name='Update nodes from meshviewer instance',
            replace_existing=True)
        atexit.register(lambda: scheduler.shutdown())

    with open(config["geojson"], "r") as f:
        return Director(config, geo_provider, f.read())


def create_app(config, testing=False):
    tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    app = Flask('domain-director', template_folder=tmpl_dir)
    app.testing = testing

    app.config.update(config)

    app.geo_provider = setup_geo_provider(app.config["geo"])

    if app.config.get("director", None) is not None:
        app.director = setup_director(app.geo_provider, app.config["director"], app.testing)
        app.register_blueprint(director.blueprints.bp_director)
        if app.config["director"].get("enabled", False):
            app.register_blueprint(director.blueprints.bp_director_admin)

    if app.config.get("locator", {}).get("enabled", False):
        app.register_blueprint(director.blueprints.bp_locator)

    return app
