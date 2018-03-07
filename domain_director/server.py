from flask import Flask

import domain_director.blueprints
from domain_director.domain import load_domain_polygons


def create_app(config):
    app = Flask('domain-director')

    app.config.update(dict(
        GEOJSON_FILE="geojson.json",
        MLS_API_KEY="test",
        DOMAIN_SWITCH_TIME=1600000000,
        DEFAULT_DOMAIN="default",
    ))
    app.config.update(config or {})
    app.config.from_envvar('DOMAIN_DIRECTOR_SETTINGS', silent=True)

    with open(app.config["GEOJSON_FILE"], "r") as f:
        app.domain_polygons = load_domain_polygons(f.read())

    register_blueprints(app)

    return app


def register_blueprints(app):
    app.register_blueprint(domain_director.blueprints.bp)
