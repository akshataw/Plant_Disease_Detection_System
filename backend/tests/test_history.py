import os

from .conftest import auth_header, png_bytes, register
from .test_predict import upload


def test_history_list_and_detail(client):
    tokens = register(client)
    for _ in range(3):
        upload(client, tokens, png_bytes())
    res = client.get("/api/v1/history?per_page=2", headers=auth_header(tokens))
    body = res.get_json()
    assert res.status_code == 200 and body["total"] == 3 and len(body["items"]) == 2 and body["pages"] == 2

    pid = body["items"][0]["id"]
    detail = client.get(f"/api/v1/history/{pid}", headers=auth_header(tokens)).get_json()
    assert detail["details"]["crop"] == "Tomato"

    img = client.get(detail["image_url"], headers=auth_header(tokens))
    assert img.status_code == 200 and img.mimetype == "image/jpeg"


def test_history_is_isolated_between_users(client):
    alice = register(client, "alice@example.com")
    bob = register(client, "bob@example.com")
    pred = upload(client, alice, png_bytes()).get_json()

    assert client.get("/api/v1/history", headers=auth_header(bob)).get_json()["total"] == 0
    assert client.get(f"/api/v1/history/{pred['id']}", headers=auth_header(bob)).status_code == 404
    assert client.get(pred["image_url"], headers=auth_header(bob)).status_code == 404
    assert client.delete(f"/api/v1/history/{pred['id']}", headers=auth_header(bob)).status_code == 404


def test_delete_history_removes_file(app, client):
    tokens = register(client)
    pred = upload(client, tokens, png_bytes()).get_json()
    assert client.delete(f"/api/v1/history/{pred['id']}", headers=auth_header(tokens)).status_code == 204
    assert os.listdir(app.config["UPLOAD_DIR"]) == []
    assert client.get(f"/api/v1/history/{pred['id']}", headers=auth_header(tokens)).status_code == 404
