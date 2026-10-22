import pytest


@pytest.mark.parametrize("body", [
    {"alias": "", "consent": True}, {"alias": "a" * 41, "consent": True},
    {"alias": "Line\nbreak", "consent": True}, {"alias": "Local", "consent": "true"},
    {"alias": "Local"}, {"alias": "Local", "consent": False, "diagnosis": "unused"},
])
def test_invalid_profile_input(client, csrf, body):
    assert client.post("/api/profiles", json=body, headers=csrf).status_code == 400


def test_select_delete_and_cascade(client, csrf, profile, observation):
    client.post("/api/progress", json=observation, headers=csrf)
    second = client.post("/api/profiles", json={"alias": "Second", "consent": False}, headers=csrf).get_json()["profile"]
    assert client.get("/api/progress").get_json()["total"] == 0
    assert client.post("/api/profiles/select", json={"id": profile["id"]}, headers=csrf).status_code == 200
    assert client.delete("/api/profiles/current", json={"confirmation": "wrong"}, headers=csrf).status_code == 409
    assert client.delete("/api/profiles/current", json={"confirmation": "DELETE"}, headers=csrf).status_code == 200
    listing = client.get("/api/profiles").get_json()
    assert listing["active_profile"] is None
    assert [item["id"] for item in listing["profiles"]] == [second["id"]]
    assert client.post("/api/profiles/select", json={"id": profile["id"]}, headers=csrf).status_code == 404


def test_profile_creation_replaces_stale_browser_selection(client, csrf, profile):
    response = client.post("/api/profiles", json={"alias": "Another", "consent": False},
                           headers={**csrf, "X-Profile-ID": profile["id"]})
    assert response.status_code == 201
    assert response.get_json()["profile"]["id"] != profile["id"]


def test_consent_revoke_deletes_observations_not_space(client, csrf, profile, observation):
    client.post("/api/progress", json=observation, headers=csrf)
    response = client.patch("/api/profiles/current", json={"consent": False}, headers=csrf)
    assert response.get_json()["profile"]["consent"] is False
    assert client.get("/api/progress").get_json()["total"] == 0
    assert client.post("/api/progress", json=observation, headers=csrf).status_code == 409
    assert len(client.get("/api/profiles").get_json()["profiles"]) == 1


def test_profile_capacity(client, csrf):
    for index in range(12):
        assert client.post("/api/profiles", json={"alias": f"Space {index}", "consent": False}, headers=csrf).status_code == 201
    assert client.post("/api/profiles", json={"alias": "Overflow", "consent": False}, headers=csrf).status_code == 409


def test_stale_tab_cannot_save_or_export_into_another_space(client, csrf, profile, observation):
    client.post("/api/profiles", json={"alias": "Other", "consent": True}, headers=csrf)
    stale_headers = {**csrf, "X-Profile-ID": profile["id"]}
    assert client.post("/api/progress", json=observation, headers=stale_headers).status_code == 409
    assert client.get(f"/api/export?profile_id={profile['id']}").status_code == 409
    assert client.patch("/api/profiles/current", json={"consent": False}, headers=stale_headers).status_code == 409
    assert client.get("/api/progress").get_json()["total"] == 0
