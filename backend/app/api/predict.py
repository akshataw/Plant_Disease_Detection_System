from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from ..services.image_validation import ImageValidationError, load_and_validate
from ..services.prediction_service import ModelUnavailableError, run_prediction, serialize_prediction

bp = Blueprint("predict", __name__)


@bp.post("/predict")
@jwt_required()
def predict():
    upload = request.files.get("image")
    max_bytes = current_app.config["MAX_UPLOAD_MB"] * 1024 * 1024
    try:
        image = load_and_validate(upload, max_bytes)
        prediction = run_prediction(int(get_jwt_identity()), image, upload.filename)
    except ImageValidationError as e:
        return jsonify(error=str(e)), 400
    except ModelUnavailableError as e:
        return jsonify(error=str(e)), 503
    return jsonify(serialize_prediction(prediction)), 201
