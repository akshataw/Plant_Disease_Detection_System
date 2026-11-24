import io

import pytest
from PIL import Image as PILImage

from app import create_app
from app.config import TestingConfig
from app.extensions import db
from app.ml.base import Predictor


class FakePredictor(Predictor):
    """Deterministic predictor so tests never need TensorFlow or a trained model."""

    version = "fake-v0"
    class_names = ["Tomato___Late_blight", "Tomato___healthy", "Potato___Early_blight"]

    def predict(self, image, top_k=3):
        return [
            {"label": "Tomato___Late_blight", "confidence": 0.91},
            {"label": "Tomato___healthy", "confidence": 0.06},
            {"label": "Potato___Early_blight", "confidence": 0.03},
        ][:top_k]


@pytest.fixture
def app(tmp_path):
    class Cfg(TestingConfig):
        UPLOAD_DIR = str(tmp_path / "uploads")

    app = create_app(Cfg, predictor=FakePredictor())
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def register(client, email="alice@example.com", password="password123"):
    res = client.post("/api/v1/auth/register", json={
        "first_name": "Alice", "last_name": "Grower", "email": email, "password": password})
    assert res.status_code == 201, res.get_json()
    return res.get_json()


def auth_header(tokens):
    return {"Authorization": f"Bearer {tokens['access_token']}"}


def png_bytes(size=(64, 64), color=(30, 160, 60)):
    buf = io.BytesIO()
    PILImage.new("RGB", size, color).save(buf, format="PNG")
    buf.seek(0)
    return buf
