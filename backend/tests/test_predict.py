import io
import os

from PIL import Image as PILImage

from .conftest import auth_header, png_bytes, register


def upload(client, tokens, data, filename="leaf.png"):
    return client.post("/api/v1/predict", headers=auth_header(tokens),
                       data={"image": (data, filename)}, content_type="multipart/form-data")


def test_predict_requires_auth(client):
    res = client.post("/api/v1/predict", data={"image": (png_bytes(), "leaf.png")},
                      content_type="multipart/form-data")
    assert res.status_code == 401


def test_predict_success_returns_details(app, client):
    tokens = register(client)
    res = upload(client, tokens, png_bytes())
    assert res.status_code == 201, res.get_json()
    body = res.get_json()
    assert body["disease_label"] == "Tomato___Late_blight"
    assert body["disease_name"] == "Tomato — Late blight"
    assert len(body["top_k"]) == 3
    assert body["details"]["treatment"] and body["details"]["prevention"]
    assert body["low_confidence"] is False and body["is_healthy"] is False
    assert body["model_version"] == "fake-v0"
    assert len(os.listdir(app.config["UPLOAD_DIR"])) == 1


def test_predict_rejects_non_image(client):
    tokens = register(client)
    res = upload(client, tokens, io.BytesIO(b"definitely not an image"), "leaf.png")
    assert res.status_code == 400


def test_predict_rejects_bad_extension(client):
    tokens = register(client)
    res = upload(client, tokens, png_bytes(), "leaf.gif")
    assert res.status_code == 400


def test_predict_rejects_missing_file(client):
    tokens = register(client)
    res = client.post("/api/v1/predict", headers=auth_header(tokens), data={},
                      content_type="multipart/form-data")
    assert res.status_code == 400


def test_predict_rejects_tiny_image(client):
    tokens = register(client)
    res = upload(client, tokens, png_bytes(size=(8, 8)))
    assert res.status_code == 400


def test_stored_image_has_no_exif(app, client):
    tokens = register(client)
    buf = io.BytesIO()
    exif = PILImage.Exif()
    exif[0x010F] = "SecretCameraMaker"
    PILImage.new("RGB", (64, 64), (10, 120, 30)).save(buf, format="JPEG", exif=exif)
    buf.seek(0)
    assert upload(client, tokens, buf, "leaf.jpg").status_code == 201
    stored = os.path.join(app.config["UPLOAD_DIR"], os.listdir(app.config["UPLOAD_DIR"])[0])
    with PILImage.open(stored) as img:
        assert len(img.getexif()) == 0


def test_model_unavailable_returns_503(app, client):
    tokens = register(client)
    app.extensions["predictor"] = None
    assert upload(client, tokens, png_bytes()).status_code == 503


def mpo_bytes(size=(64, 64)):
    """A two-frame MPO, i.e. what many phones write into a normal-looking .jpg file."""
    buf = io.BytesIO()
    first = PILImage.new("RGB", size, (30, 160, 60))
    first.save(buf, format="MPO", save_all=True, append_images=[PILImage.new("RGB", size, (0, 0, 0))])
    buf.seek(0)
    return buf


def test_predict_accepts_mpo_phone_jpeg(client):
    data = mpo_bytes()
    assert PILImage.open(io.BytesIO(data.getvalue())).format == "MPO"
    res = upload(client, register(client), data, filename="phone.jpg")
    assert res.status_code == 201, res.get_json()


def test_predict_rejects_huge_dimensions_before_decoding(client):
    # ~1.3x MAX_PIXELS: Pillow alone would only warn and fully decode this; tiny on the wire
    buf = io.BytesIO()
    PILImage.new("L", (7300, 7300)).save(buf, format="PNG")
    buf.seek(0)
    res = upload(client, register(client), buf)
    assert res.status_code == 400
    assert "too large" in res.get_json()["error"]


def test_stored_image_is_downscaled(app, client):
    res = upload(client, register(client), png_bytes(size=(3000, 1500)))
    assert res.status_code == 201
    (name,) = os.listdir(app.config["UPLOAD_DIR"])
    with PILImage.open(os.path.join(app.config["UPLOAD_DIR"], name)) as stored:
        assert stored.size == (1280, 640)
