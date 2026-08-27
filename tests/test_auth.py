from app.models.enums import UserRole
from tests.conftest import TEST_PASSWORD, make_user


def test_login_success(client, db_session):
    make_user(db_session, role=UserRole.ADMIN, email="admin@example.com")
    response = client.post(
        "/api/v1/auth/login", json={"email": "admin@example.com", "password": TEST_PASSWORD}
    )
    assert response.status_code == 200
    assert response.json()["email"] == "admin@example.com"
    assert "access_token" in response.cookies


def test_login_wrong_password(client, db_session):
    make_user(db_session, role=UserRole.ADMIN, email="admin@example.com")
    response = client.post(
        "/api/v1/auth/login", json={"email": "admin@example.com", "password": "wrong"}
    )
    assert response.status_code == 401


def test_login_unknown_email(client):
    response = client.post(
        "/api/v1/auth/login", json={"email": "nobody@example.com", "password": TEST_PASSWORD}
    )
    assert response.status_code == 401


def test_me_requires_auth(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_me_returns_current_user(admin_client):
    response = admin_client.get("/api/v1/auth/me")
    assert response.status_code == 200
    assert response.json()["email"] == "admin@example.com"


def test_logout_clears_cookie(admin_client):
    response = admin_client.post("/api/v1/auth/logout")
    assert response.status_code == 204
    assert admin_client.get("/api/v1/auth/me").status_code == 401
