import csv
import io


def test_export_formats_and_no_alias(client, csrf, profile, observation):
    client.post("/api/progress", json=observation, headers=csrf)
    response = client.get("/api/export")
    data = response.get_json()
    assert data["schema_version"] == 1
    assert len(data["observations"]) == 1
    assert profile["alias"] not in response.get_data(as_text=True)
    csv_response = client.get("/api/export?format=csv")
    records = list(csv.DictReader(io.StringIO(csv_response.get_data(as_text=True))))
    assert len(records) == 1
    assert records[0]["response_mode"] == "aac"
    assert "attachment" in csv_response.headers["Content-Disposition"]
    assert client.get("/api/export?format=xml").status_code == 400


def test_exports_do_not_mix_spaces(client, csrf, profile, observation):
    client.post("/api/progress", json=observation, headers=csrf)
    client.post("/api/profiles", json={"alias": "Other", "consent": True}, headers=csrf)
    assert client.get("/api/export").get_json()["observations"] == []


def test_export_without_space_is_actionable(client):
    response = client.get("/api/export")
    assert response.status_code == 409
    assert "Caregiver" in response.get_json()["error"]["message"]
