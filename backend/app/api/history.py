import os

from flask import Blueprint, current_app, jsonify, request, send_from_directory
from flask_jwt_extended import get_jwt_identity, jwt_required

from ..extensions import db
from ..models import Image, Prediction
from ..services.prediction_service import delete_prediction, serialize_prediction

bp = Blueprint("history", __name__)

MAX_PER_PAGE = 50


def _owned_or_404(model, obj_id):
    # 404 (not 403) for other users' records so IDs can't be probed
    obj = db.session.get(model, obj_id)
    if obj is None or obj.user_id != int(get_jwt_identity()):
        return None
    return obj


@bp.get("/history")
@jwt_required()
def list_history():
    page = max(request.args.get("page", 1, type=int), 1)
    per_page = min(max(request.args.get("per_page", 10, type=int), 1), MAX_PER_PAGE)
    query = (Prediction.query.filter_by(user_id=int(get_jwt_identity()))
             .order_by(Prediction.prediction_date.desc(), Prediction.id.desc()))
    result = query.paginate(page=page, per_page=per_page, error_out=False)
    return jsonify(
        items=[serialize_prediction(p, detailed=False) for p in result.items],
        page=result.page, per_page=result.per_page, total=result.total, pages=result.pages,
    )


@bp.get("/history/<int:prediction_id>")
@jwt_required()
def get_history_item(prediction_id):
    p = _owned_or_404(Prediction, prediction_id)
    if p is None:
        return jsonify(error="Prediction not found"), 404
    return jsonify(serialize_prediction(p))


@bp.delete("/history/<int:prediction_id>")
@jwt_required()
def delete_history_item(prediction_id):
    p = _owned_or_404(Prediction, prediction_id)
    if p is None:
        return jsonify(error="Prediction not found"), 404
    delete_prediction(p)
    return "", 204


@bp.get("/images/<int:image_id>")
@jwt_required()
def get_image(image_id):
    image = _owned_or_404(Image, image_id)
    if image is None or not os.path.isfile(os.path.join(current_app.config["UPLOAD_DIR"], image.image_path)):
        return jsonify(error="Image not found"), 404
    response = send_from_directory(current_app.config["UPLOAD_DIR"], image.image_path, mimetype=image.content_type)
    response.headers["Cache-Control"] = "private, max-age=3600"
    return response
