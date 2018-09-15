import json
from flask import Blueprint, request, current_app, jsonify, render_template
from ipaddress import AddressValueError
from mozls import WifiNetwork, query_mls, MLSException

from domain_director import ipv6_to_mac
from domain_director.db import Node
from domain_director.domain import get_node_domain

bp = Blueprint('domain_director', __name__)


@bp.route('/', methods=['GET', 'POST'])
def serve():
    revisit = False
    domain = None

    wifis = request.form["wifis"]
    try:
        mls_response = query_mls(
            wifi_networks=[WifiNetwork(mac_address=ap["bssid"], signalStrength=int(ap["signal"]))
                           for ap in json.loads(wifis)],
            apikey=current_app.config["MLS_API_KEY"])
    except MLSException:
        mls_response = None
    try:
        ip_address = request.headers.get("X-Real-IP", None) or request.remote_addr
        node_id = ipv6_to_mac(ip_address).replace(':', '')
        domain, switch_time = get_node_domain(node_id=node_id,
                                 lat=mls_response.lat if mls_response else None,
                                 lon=mls_response.lon if mls_response else None,
                                 accuracy=mls_response.accuracy if mls_response else None,
                                 polygons=current_app.domain_polygons,
                                 default_domain=current_app.config["DEFAULT_DOMAIN"],
                                 switch_time=current_app.config["DOMAIN_SWITCH_TIME"],
                                 migrate_only_vpn=current_app.config["ONLY_MIGRATE_VPN"])
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
                "name": domain,
                "switch_time": switch_time,
                "revisit": revisit, }
        }})


@bp.route('/nodes', methods=['GET'])
def list_nodes():
    return render_template("nodes.html", meshes=Node.get_nodes_grouped())


@bp.route('/nodes.json', methods=['GET'])
def list_nodes_json():
    return jsonify(Node.get_nodes_grouped())
