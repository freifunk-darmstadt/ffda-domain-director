import json

from flask import Blueprint, request, current_app, jsonify
from mozls import WifiNetwork, query_mls

from domain_director.domain import get_domain

bp = Blueprint('domain_director', __name__)


@bp.route('/', methods=['GET', 'POST'])
def serve():
    wifis = request.form["wifis"]

    mls_response = query_mls(
        wifi_networks=[WifiNetwork(mac_address=ap["bssid"], signalStrength=int(ap["signal"]))
                       for ap in json.loads(wifis)],
        apikey=current_app.config["MLS_API_KEY"])
    # node_id = ipv6_to_mac(request.remote_addr)
    domain = get_domain(mls_response.lat, mls_response.lon, current_app.domain_polygons)
    domain = domain if domain is not None else current_app.config["DEFAULT_DOMAIN"]
    return jsonify({
        "node_information": {
            "location": {"lat": mls_response.lat,
                         "lon": mls_response.lon,
                         "accuracy": mls_response.accuracy, },
            "domain": {
                "name": domain,
                "switch_time": current_app.config["DOMAIN_SWITCH_TIME"], }
        }})
