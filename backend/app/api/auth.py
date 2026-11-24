import re

from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required
from sqlalchemy.exc import IntegrityError

from ..extensions import db
from ..models import User
from ..models.user import MAX_PASSWORD_BYTES

bp = Blueprint("auth", __name__)

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MIN_PASSWORD_LEN = 8


def _json_body():
    """Return the request body if it is a JSON object, else None."""
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else None


def _str_field(data, key):
    """Return data[key] if it is a string (missing → ""), else None."""
    value = data.get(key, "")
    if value is None:
        return ""
    return value if isinstance(value, str) else None


def _tokens_for(user):
    identity = str(user.id)
    return {
        "access_token": create_access_token(identity=identity),
        "refresh_token": create_refresh_token(identity=identity),
        "user": user.to_dict(),
    }


@bp.post("/auth/register")
def register():
    data = _json_body()
    if data is None:
        return jsonify(error="Request body must be a JSON object"), 400
    fields = {k: _str_field(data, k) for k in ("first_name", "last_name", "email", "password")}
    if any(v is None for v in fields.values()):
        return jsonify(error="All fields must be strings"), 400
    first = fields["first_name"].strip()
    last = fields["last_name"].strip()
    email = fields["email"].strip().lower()
    password = fields["password"]

    if not first or not last or len(first) > 100 or len(last) > 100:
        return jsonify(error="First and last name are required (max 100 characters)"), 400
    if not EMAIL_RE.match(email) or len(email) > 255:
        return jsonify(error="A valid email is required"), 400
    if len(password) < MIN_PASSWORD_LEN:
        return jsonify(error=f"Password must be at least {MIN_PASSWORD_LEN} characters"), 400
    if len(password.encode("utf-8")) > MAX_PASSWORD_BYTES:
        return jsonify(error=f"Password is too long (max {MAX_PASSWORD_BYTES} bytes)"), 400
    if User.query.filter_by(email=email).first():
        return jsonify(error="An account with this email already exists"), 409

    user = User(first_name=first, last_name=last, email=email)
    user.set_password(password)
    db.session.add(user)
    try:
        db.session.commit()
    except IntegrityError:  # concurrent registration with the same email
        db.session.rollback()
        return jsonify(error="An account with this email already exists"), 409
    return jsonify(_tokens_for(user)), 201


@bp.post("/auth/login")
def login():
    data = _json_body()
    email = _str_field(data, "email") if data is not None else None
    password = _str_field(data, "password") if data is not None else None
    if email is None or password is None:
        return jsonify(error="Request body must be a JSON object with string fields"), 400
    user = User.query.filter_by(email=email.strip().lower()).first()
    if not user or not user.check_password(password):
        return jsonify(error="Invalid email or password"), 401
    return jsonify(_tokens_for(user))


@bp.post("/auth/refresh")
@jwt_required(refresh=True)
def refresh():
    return jsonify(access_token=create_access_token(identity=get_jwt_identity()))


@bp.get("/auth/me")
@jwt_required()
def me():
    user = db.session.get(User, int(get_jwt_identity()))
    if not user:
        return jsonify(error="User not found"), 404
    return jsonify(user.to_dict())
