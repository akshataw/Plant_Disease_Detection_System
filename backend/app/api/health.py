from flask import Blueprint, current_app, jsonify
from sqlalchemy import text

from ..extensions import db

bp = Blueprint("health", __name__)


@bp.get("/health")
def health():
    try:
        db.session.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False
    predictor = current_app.extensions.get("predictor")
    body = {
        "status": "ok" if db_ok and predictor else "degraded",
        "database": db_ok,
        "model_loaded": predictor is not None,
        "model_version": predictor.version if predictor else None,
    }
    return jsonify(body), 200 if db_ok else 503
