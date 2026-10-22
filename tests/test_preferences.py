import pytest


def test_preferences_round_trip(client, csrf, profile):
    prefs = {"theme": "dark", "large_text": True, "reduced_choices": True, "speech_enabled": True, "speech_rate": "regular"}
    result = client.patch("/api/profiles/current", json={"preferences": prefs}, headers=csrf)
    assert result.status_code == 200
    assert result.get_json()["profile"]["preferences"] == prefs
    assert client.get("/api/profiles").get_json()["profiles"][0]["preferences"] == prefs


@pytest.mark.parametrize("preferences", [[], {"theme": "pink"}, {"large_text": 1}, {"speech_rate": 2}, {"unknown": False}])
def test_invalid_preferences_cannot_replace_saved_values(client, csrf, profile, preferences):
    response = client.patch("/api/profiles/current", json={"preferences": preferences}, headers=csrf)
    assert response.status_code == 400
    assert client.get("/api/profiles").get_json()["profiles"][0]["preferences"]["theme"] == "system"


def test_partial_preferences_preserve_other_fields(client, csrf, profile):
    client.patch("/api/profiles/current", json={"preferences": {"large_text": True}}, headers=csrf)
    response = client.patch("/api/profiles/current", json={"preferences": {"theme": "dark"}}, headers=csrf)
    assert response.get_json()["profile"]["preferences"]["large_text"] is True
