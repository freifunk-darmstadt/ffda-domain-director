import json

from flask import Blueprint, request, current_app, jsonify

from domain_director.domain import get_domain
from domain_director.location import get_location

bp = Blueprint('domain_director', __name__)


@bp.route('/', methods=['GET', 'POST'])
def serve():
    wifis = request.form["wifis"]
    networks = [{"macAddress": ap["bssid"], "signalStrength": int(ap["signal"])}
                for ap in json.loads(wifis)]
    lat, lon, accuracy = get_location(networks, current_app.config["MLS_API_KEY"])
    # node_id = ipv6_to_mac(request.remote_addr)
    domain = get_domain(lat, lon, current_app.domain_polygons)
    domain = domain if domain is not None else current_app.config["DEFAULT_DOMAIN"]
    return jsonify({
        "node_information": {
            "location": {"lat": lat,
                         "lon": lon,
                         "accuracy": accuracy, },
            "domain": {
                "name": domain,
                "switch_time": current_app.config["DOMAIN_SWITCH_TIME"], }
        }})
