import json
from ipaddress import AddressValueError

from flask import Blueprint, request, current_app, jsonify
from mozls import WifiNetwork, query_mls

from domain_director import ipv6_to_mac
from domain_director.domain import decide_node_domain

bp = Blueprint('domain_director', __name__)


@bp.route('/', methods=['GET', 'POST'])
def serve():
    revisit = False
    domain = None
    wifis = request.form["wifis"]

    mls_response = query_mls(
        wifi_networks=[WifiNetwork(mac_address=ap["bssid"], signalStrength=int(ap["signal"]))
                       for ap in json.loads(wifis)],
        apikey=current_app.config["MLS_API_KEY"])
    try:
        node_id = ipv6_to_mac(request.remote_addr).replace(':', '')
        domain = decide_node_domain(node_id=node_id,
                                    lat=mls_response.lat,
                                    lon=mls_response.lon,
                                    accuracy=mls_response.accuracy,
                                    polygons=current_app.domain_polygons,
                                    default_domain=current_app.config["DEFAULT_DOMAIN"])
        if domain == current_app.config["DEFAULT_DOMAIN"]:
            revisit = True
    except AddressValueError:
        revisit = True
    return jsonify({
        "node_information": {
            "location": {"lat": mls_response.lat,
                         "lon": mls_response.lon,
                         "accuracy": mls_response.accuracy, },
            "domain": {
                "name": domain if domain else current_app.config["DEFAULT_DOMAIN"],
                "switch_time": current_app.config["DOMAIN_SWITCH_TIME"],
                "revisit": revisit, }
        }})
