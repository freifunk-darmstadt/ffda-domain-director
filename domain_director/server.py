import atexit
import os

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from flask import Flask
from peewee import SqliteDatabase

import domain_director.blueprints
from domain_director.db import create_tables, distribute_nodes_remote_meshviewer
from domain_director.db.model import db, Mesh, Node
from domain_director.director import Director
from domain_director.geo.MozillaProvider import MozillaProvider


def setup_geo_provider(config):
    if config["provider"] == "mozilla":
        return MozillaProvider(config)

    raise NotImplementedError


def setup_database(config, testing):
    db.initialize(SqliteDatabase(config["sqlite_path"]))
    if not Node.table_exists() and not Mesh.table_exists():
        create_tables(db)
        if not testing:
            distribute_nodes_remote_meshviewer(config["meshviewer_json_url"], True)
    else:
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

    app.register_blueprint(domain_director.blueprints.bp)

    return app


