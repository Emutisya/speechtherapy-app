from communication import create_app


def test_home_and_bootstrap_without_models(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Every way of communicating counts" in response.data
    data = client.get("/api/bootstrap").get_json()
    assert len(data["cards"]) == 24
    assert len(data["activities"]) == 18
    assert data["active_profile"] is None
    assert data["defaults"]["speech_enabled"] is False


def test_restart_keeps_profile(tmp_path):
    config = {"TESTING": True, "SECRET_KEY": "stable-test-key", "DATABASE": str(tmp_path / "persistent.db")}
    client = create_app(config).test_client()
    headers = {"X-CSRF-Token": client.get("/api/bootstrap").get_json()["csrf_token"]}
    client.post("/api/profiles", json={"alias": "Local", "consent": False}, headers=headers)
    restarted = create_app(config).test_client()
    assert restarted.get("/api/profiles").get_json()["profiles"][0]["alias"] == "Local"


def test_health_does_not_disclose_database(client):
    assert client.get("/health").get_json() == {"status": "ok"}


def test_newer_schema_is_not_downgraded(tmp_path):
    import sqlite3
    import pytest
    database = tmp_path / "newer.db"
    with sqlite3.connect(database) as connection:
        connection.execute("PRAGMA user_version = 99")
    with pytest.raises(RuntimeError, match="newer"):
        create_app({"TESTING": True, "SECRET_KEY": "test", "DATABASE": str(database)})
