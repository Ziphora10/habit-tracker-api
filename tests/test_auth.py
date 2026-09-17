def test_signup_creates_user(client):
    response = client.post(
        "/auth/signup", json={"email": "new@example.com", "password": "secret123"}
    )
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "new@example.com"
    assert "id" in body
    assert "password" not in body


def test_signup_duplicate_email_fails(client):
    client.post(
        "/auth/signup", json={"email": "dup@example.com", "password": "secret123"}
    )
    response = client.post(
        "/auth/signup", json={"email": "dup@example.com", "password": "other123"}
    )
    assert response.status_code == 400


def test_login_success(client):
    client.post(
        "/auth/signup", json={"email": "login@example.com", "password": "secret123"}
    )
    response = client.post(
        "/auth/login",
        data={"username": "login@example.com", "password": "secret123"},
    )
    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


def test_login_wrong_password_fails(client):
    client.post(
        "/auth/signup", json={"email": "wrongpw@example.com", "password": "secret123"}
    )
    response = client.post(
        "/auth/login",
        data={"username": "wrongpw@example.com", "password": "nope"},
    )
    assert response.status_code == 401


def test_protected_route_requires_token(client):
    response = client.get("/habits")
    assert response.status_code == 401
