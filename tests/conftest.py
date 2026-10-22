import pytest

from communication import create_app


@pytest.fixture
def app(tmp_path):
    return create_app({"TESTING": True, "SECRET_KEY": "test-only-key",
                       "DATABASE": str(tmp_path / "app.sqlite3")})


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def csrf(client):
    return {"X-CSRF-Token": client.get("/api/bootstrap").get_json()["csrf_token"]}


@pytest.fixture
def profile(client, csrf):
    return client.post("/api/profiles", json={"alias": "Sunflower", "consent": True}, headers=csrf).get_json()["profile"]


@pytest.fixture
def observation():
    return {"activity_id": "ask-help", "response_mode": "aac", "support": "modeled", "comfort": "comfortable"}
