from flask import Flask
from peewee import SqliteDatabase

import domain_director.blueprints
from domain_director.db import create_tables, distribute_nodes_remote_meshviewer
from domain_director.db.model import db, Mesh, Node
from domain_director.domain import load_domain_polygons


def create_app(config, testing=False):
    app = Flask('domain-director')
    app.testing = testing

    app.config.update(dict(
        GEOJSON_FILE="geojson.json",
        MLS_API_KEY="test",
        DOMAIN_SWITCH_TIME=1600000000,
        DEFAULT_DOMAIN="default",
        SQlITE_PATH=":memory:",
    ))
    app.config.update(config or {})
    app.config.from_envvar('DOMAIN_DIRECTOR_SETTINGS', silent=True)

    with open(app.config["GEOJSON_FILE"], "r") as f:
        app.domain_polygons = load_domain_polygons(f.read())

    setup_database(app)
    register_blueprints(app)

    return app


def setup_database(app):
    db.initialize(SqliteDatabase(app.config["SQlITE_PATH"]))
    if not Node.table_exists() and not Mesh.table_exists():
        create_tables(db)
        if not app.testing:
            distribute_nodes_remote_meshviewer(app.config["MESHVIEWER_JSON_URL"], True)
    else:
        if not app.testing:
            distribute_nodes_remote_meshviewer(app.config["MESHVIEWER_JSON_URL"], False)


def register_blueprints(app):
    app.register_blueprint(domain_director.blueprints.bp)
