from .conftest import auth_header, register


def test_register_login_me(client):
    tokens = register(client)
    assert tokens["user"]["email"] == "alice@example.com"
    assert "password_hash" not in tokens["user"]

    res = client.post("/api/v1/auth/login", json={"email": "ALICE@example.com", "password": "password123"})
    assert res.status_code == 200
    me = client.get("/api/v1/auth/me", headers=auth_header(res.get_json()))
    assert me.status_code == 200 and me.get_json()["first_name"] == "Alice"


def test_duplicate_email_rejected(client):
    register(client)
    res = client.post("/api/v1/auth/register", json={
        "first_name": "A", "last_name": "B", "email": "alice@example.com", "password": "password123"})
    assert res.status_code == 409


def test_register_validation(client):
    res = client.post("/api/v1/auth/register", json={
        "first_name": "A", "last_name": "B", "email": "not-an-email", "password": "password123"})
    assert res.status_code == 400
    res = client.post("/api/v1/auth/register", json={
        "first_name": "A", "last_name": "B", "email": "a@b.co", "password": "short"})
    assert res.status_code == 400


def test_wrong_password(client):
    register(client)
    res = client.post("/api/v1/auth/login", json={"email": "alice@example.com", "password": "wrong-pass"})
    assert res.status_code == 401


def test_refresh_token(client):
    tokens = register(client)
    res = client.post("/api/v1/auth/refresh", headers={"Authorization": f"Bearer {tokens['refresh_token']}"})
    assert res.status_code == 200 and "access_token" in res.get_json()
    # an access token must not be accepted as a refresh token
    res = client.post("/api/v1/auth/refresh", headers=auth_header(tokens))
    assert res.status_code == 401


def test_password_is_hashed(app, client):
    from app.models import User
    register(client)
    user = User.query.filter_by(email="alice@example.com").one()
    assert user.password_hash != "password123" and user.password_hash.startswith("$2")


def test_overlong_password_rejected_not_500(client):
    for pw in ["a" * 73, "क" * 25]:  # 73 bytes ASCII; 75 bytes Devanagari
        res = client.post("/api/v1/auth/register", json={
            "first_name": "A", "last_name": "B", "email": "long@example.com", "password": pw})
        assert res.status_code == 400, pw
    register(client)
    res = client.post("/api/v1/auth/login", json={"email": "alice@example.com", "password": "a" * 100})
    assert res.status_code == 401


def test_password_of_exactly_72_bytes_works(client):
    register(client, email="max@example.com", password="b" * 72)
    res = client.post("/api/v1/auth/login", json={"email": "max@example.com", "password": "b" * 72})
    assert res.status_code == 200


def test_malformed_auth_bodies_return_400(client):
    bad_register = [[1], {"first_name": "A", "last_name": "B", "email": 123, "password": "password123"}]
    for body in bad_register:
        assert client.post("/api/v1/auth/register", json=body).status_code == 400
    for body in [[1], {"email": 123, "password": "x"}, {"email": "a@b.co", "password": ["x"]}]:
        assert client.post("/api/v1/auth/login", json=body).status_code == 400
