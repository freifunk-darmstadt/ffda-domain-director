import json
from datetime import datetime
from flask import Blueprint, request, current_app, jsonify, render_template, abort
from ipaddress import AddressValueError
from peewee import DoesNotExist

from director import ipv6_to_mac
from director.db import Node, Mesh
from director.director import DecisionCriteria

bp = Blueprint('director', __name__)
bp_admin = Blueprint('domain_director_admin', __name__)


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/get_domain', methods=['GET', 'POST'])
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


@bp_admin.route('/mesh/<int:mesh_id>/', methods=['PATCH'])
def update_mesh(mesh_id):
    if not request.is_json:
        abort(400)

    values = request.get_json()
    try:
        mesh_db_entry = Mesh.select().where(Mesh.id == int(mesh_id)).get()
    except DoesNotExist:
        abort(404)

    if 'switch_time' in values:
        try:
            switch_time = int(values['switch_time'])
            switch_time_parsed = datetime.utcfromtimestamp(switch_time)
        except ValueError:
            return 'invalid switch time specified', 400

        now = datetime.utcnow()

        force = 'force' in values and values['force'].lower() in ['true', 'yes', '1']

        if not force and (switch_time_parsed - now).total_seconds() < 0:
            return 'Specified switch time lies in the past. Force to set value.', 400

        Mesh.set_switch_time(mesh_db_entry.id, switch_time)

    if 'domain' in values:
        Mesh.set_domain(mesh_db_entry.id, values['domain'], DecisionCriteria.MANUAL)

    return "", 200
