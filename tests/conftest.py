import shutil
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import hash_password
from app.db.session import engine, get_db
from app.main import app
from app.models.enums import UserRole
from app.models.user import User

TEST_PASSWORD = "password123"


@pytest.fixture(autouse=True)
def _cleanup_uploaded_documents():
    yield
    storage_path = Path(get_settings().document_storage_path)
    if storage_path.exists():
        shutil.rmtree(storage_path, ignore_errors=True)


@pytest.fixture()
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    try:
        yield session
    finally:
        session.close()
        if transaction.is_active:
            transaction.rollback()
        connection.close()


@pytest.fixture()
def db_override(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    try:
        yield
    finally:
        app.dependency_overrides.pop(get_db, None)


@pytest.fixture()
def client(db_override) -> TestClient:
    return TestClient(app)


def make_user(db_session, *, role: UserRole, email: str) -> User:
    user = User(
        email=email, full_name="Test User", hashed_password=hash_password(TEST_PASSWORD), role=role
    )
    db_session.add(user)
    db_session.flush()
    return user


def _new_logged_in_client(db_session, role: UserRole, email: str) -> TestClient:
    make_user(db_session, role=role, email=email)
    logged_in = TestClient(app)
    response = logged_in.post(
        "/api/v1/auth/login", json={"email": email, "password": TEST_PASSWORD}
    )
    assert response.status_code == 200
    return logged_in


@pytest.fixture()
def admin_client(db_override, db_session) -> TestClient:
    return _new_logged_in_client(db_session, UserRole.ADMIN, "admin@example.com")


@pytest.fixture()
def staff_client(db_override, db_session) -> TestClient:
    return _new_logged_in_client(db_session, UserRole.STAFF, "staff@example.com")


@pytest.fixture()
def viewer_client(db_override, db_session) -> TestClient:
    return _new_logged_in_client(db_session, UserRole.VIEWER, "viewer@example.com")
