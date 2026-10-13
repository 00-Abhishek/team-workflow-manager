import os
import tempfile

_tmp_db = os.path.join(tempfile.mkdtemp(), "app_test.db")
os.environ["DATABASE_URL"] = f"sqlite+pysqlite:///{_tmp_db}"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.security import hash_password
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.user import User


@pytest.fixture()
def client():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)

    db = TestingSession()
    db.add_all([
        User(email="admin@example.com", full_name="Ada Admin", role="admin", hashed_password=hash_password("admin123")),
        User(email="lead@example.com", full_name="Leah Lead", role="user", hashed_password=hash_password("lead123")),
        User(email="dev@example.com", full_name="Dev Member", role="user", hashed_password=hash_password("dev123")),
        User(email="outsider@example.com", full_name="Otto Outsider", role="user", hashed_password=hash_password("out123")),
    ])
    db.commit()
    db.close()

    def override_get_db():
        session = TestingSession()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def auth_headers(client, email, password):
    resp = client.post("/api/auth/token", data={"username": email, "password": password})
    assert resp.status_code == 200, resp.text
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


def user_id(client, headers, email):
    resp = client.get("/api/auth/me", headers=headers)
    assert resp.json()["email"] == email
    return resp.json()["id"]
