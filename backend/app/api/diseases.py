from flask import Blueprint, jsonify

from ..services.disease_info import find_disease, list_diseases

bp = Blueprint("diseases", __name__)


@bp.get("/diseases")
def diseases():
    return jsonify(items=list_diseases())


@bp.get("/diseases/<path:label>")
def disease_detail(label):
    info = find_disease(label)
    if info is None:
        return jsonify(error="Disease not found"), 404
    return jsonify(info)
