import json
from flask import Blueprint, request, current_app, jsonify, render_template
from ipaddress import AddressValueError

from director import ipv6_to_mac
from director.db import Node

bp = Blueprint('director', __name__)


@bp.route('/', methods=['GET', 'POST'])
def serve():
    wifis = []
    try:
        wifis = json.loads(request.form.get("wifis", "[]"))
    except ValueError:
        # handle MLS data as optional (it is anyway)
        pass
    ip_address = request.headers.get("X-Real-IP", None) or request.remote_addr
    try:
        node_id = ipv6_to_mac(ip_address).replace(':', '')
    except AddressValueError:
        return "", 400
    domain, switch_time = current_app.director.get_node_domain(node_id=node_id, wifis=wifis)
    return jsonify({
        "node_information": {
            "domain": {
                "name": domain,
                "switch_time": switch_time,
            }
        }})


@bp.route('/nodes', methods=['GET'])
def list_nodes():
    return render_template("nodes.html", meshes=Node.get_nodes_grouped())


@bp.route('/nodes.json', methods=['GET'])
def list_nodes_json():
    return jsonify(Node.get_nodes_grouped())
