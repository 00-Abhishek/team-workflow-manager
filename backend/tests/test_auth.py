from tests.conftest import auth_headers


def test_health(client):
    assert client.get("/health").json()["status"] == "ok"


def test_login_and_me(client):
    headers = auth_headers(client, "lead@example.com", "lead123")
    assert client.get("/api/auth/me", headers=headers).json()["email"] == "lead@example.com"


def test_unauthenticated_is_401(client):
    assert client.get("/api/projects").status_code == 401
