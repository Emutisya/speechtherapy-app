import pytest


def test_progress_requires_space_and_consent(client, csrf, observation):
    assert client.post("/api/progress", json=observation, headers=csrf).status_code == 409
    client.post("/api/profiles", json={"alias": "Guest", "consent": False}, headers=csrf)
    assert client.post("/api/progress", json=observation, headers=csrf).status_code == 409


@pytest.mark.parametrize("mode", ["speech", "aac", "gesture", "listening", "mixed", "skipped"])
def test_all_modes_count_without_accuracy_score(client, csrf, profile, observation, mode):
    observation["response_mode"] = mode
    assert client.post("/api/progress", json=observation, headers=csrf).status_code == 201
    data = client.get("/api/progress").get_json()
    assert data["modes"] == {mode: 1}
    assert data["total"] == 1
    assert "score" not in data["events"][0]
    assert data["events"][0]["created_at"].endswith("+00:00")


@pytest.mark.parametrize("field,value", [("activity_id", "missing"), ("response_mode", []), ("support", "force"), ("comfort", "diagnosed")])
def test_invalid_observations_are_not_saved(client, csrf, profile, observation, field, value):
    observation[field] = value
    assert client.post("/api/progress", json=observation, headers=csrf).status_code == 400
    assert client.get("/api/progress").get_json()["total"] == 0


def test_event_removal_is_scoped_to_active_space(client, csrf, profile, observation):
    event_id = client.post("/api/progress", json=observation, headers=csrf).get_json()["id"]
    client.post("/api/profiles", json={"alias": "Other", "consent": True}, headers=csrf)
    assert client.delete(f"/api/progress/{event_id}", headers=csrf).status_code == 404
    client.post("/api/profiles/select", json={"id": profile["id"]}, headers=csrf)
    assert client.get("/api/progress").get_json()["total"] == 1
    assert client.delete(f"/api/progress/{event_id}", headers=csrf).status_code == 200
    assert client.get("/api/progress").get_json()["total"] == 0


def test_clear_requires_exact_confirmation(client, csrf, profile, observation):
    client.post("/api/progress", json=observation, headers=csrf)
    assert client.delete("/api/progress", json={"confirmation": "clear"}, headers=csrf).status_code == 409
    assert client.get("/api/progress").get_json()["total"] == 1
    assert client.delete("/api/progress", json={"confirmation": "CLEAR"}, headers=csrf).status_code == 200
    assert client.get("/api/progress").get_json()["total"] == 0


def test_recent_page_does_not_truncate_totals(client, csrf, profile, observation):
    for _ in range(105):
        client.post("/api/progress", json=observation, headers=csrf)
    data = client.get("/api/progress").get_json()
    assert len(data["events"]) == 100
    assert data["total"] == 105
    assert data["events"][0]["id"] > data["events"][-1]["id"]


def test_capacity_limit_returns_actionable_error(app, client, csrf, profile, observation):
    from communication.db import get_db
    with app.app_context():
        connection = get_db()
        with connection:
            connection.executemany(
                "INSERT INTO events(profile_id, activity_id, response_mode, support, comfort, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                [(profile["id"], "ask-help", "aac", "not-recorded", "not-recorded", "2026-01-01T00:00:00+00:00")] * 10000,
            )
    response = client.post("/api/progress", json=observation, headers=csrf)
    assert response.status_code == 409
    assert "10,000" in response.get_json()["error"]["message"]
    assert client.get("/api/progress").get_json()["total"] == 10000
