import logging
import os

from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException

from .config import Config
from .extensions import bcrypt, db, jwt, migrate
from .ml.registry import build_predictor

API_PREFIX = "/api/v1"


def create_app(config_object=Config, predictor=None):
    app = Flask(__name__)
    app.config.from_object(config_object)
    logging.basicConfig(level=logging.INFO)

    if not app.config.get("JWT_SECRET_KEY"):
        raise RuntimeError("JWT_SECRET_KEY must be set (see .env.example)")
    os.makedirs(app.config["UPLOAD_DIR"], exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    bcrypt.init_app(app)

    from . import models  # noqa: F401  (register tables with SQLAlchemy/Alembic)

    # The predictor can be injected (tests); otherwise it is built from config
    app.extensions["predictor"] = predictor if predictor is not None else build_predictor(app.config)

    _register_blueprints(app)
    _register_error_handlers(app)
    return app


def _register_blueprints(app):
    from .api.auth import bp as auth_bp
    from .api.diseases import bp as diseases_bp
    from .api.health import bp as health_bp
    from .api.history import bp as history_bp
    from .api.predict import bp as predict_bp

    for bp in (health_bp, auth_bp, predict_bp, history_bp, diseases_bp):
        app.register_blueprint(bp, url_prefix=API_PREFIX)


def _register_error_handlers(app):
    @app.errorhandler(HTTPException)
    def handle_http_error(e):
        return jsonify(error=e.description), e.code

    @app.errorhandler(413)
    def handle_too_large(_e):
        return jsonify(error=f"File too large (max {app.config['MAX_UPLOAD_MB']} MB)"), 413

    @app.errorhandler(Exception)
    def handle_unexpected(e):
        app.logger.exception("Unhandled error: %s", e)
        return jsonify(error="Internal server error"), 500

    @jwt.unauthorized_loader
    def missing_token(reason):
        return jsonify(error="Authentication required"), 401

    @jwt.invalid_token_loader
    def invalid_token(reason):
        return jsonify(error="Invalid token"), 401

    @jwt.expired_token_loader
    def expired_token(_header, _payload):
        return jsonify(error="Token expired"), 401
