import pytest


@pytest.mark.parametrize("path", ["/data/phonetic_embd.pickle", "/data/TED_transcripts.csv", "/app.py", "/.git/config", "/instance/session.key", "/notebook/res.pickle"])
def test_repository_files_are_not_public(client, path):
    assert client.get(path).status_code == 404


def test_csrf_required_and_cross_origin_rejected(client, csrf):
    body = {"alias": "Local", "consent": False}
    assert client.post("/api/profiles", json=body).status_code == 403
    assert client.post("/api/profiles", json=body, headers={**csrf, "Origin": "https://example.com"}).status_code == 403
    assert client.post("/api/profiles", json=body, headers={**csrf, "Sec-Fetch-Site": "cross-site"}).status_code == 403
    assert client.post("/api/profiles", json=body, headers=csrf).status_code == 201


def test_non_loopback_and_untrusted_host_denied(client):
    assert client.get("/", environ_base={"REMOTE_ADDR": "192.0.2.3"}).status_code == 403
    assert client.get("/", headers={"Host": "untrusted.example"}).status_code == 400


def test_privacy_headers_and_cookie(client):
    response = client.get("/api/bootstrap")
    assert response.headers["Cache-Control"] == "no-store"
    assert "frame-ancestors 'none'" in response.headers["Content-Security-Policy"]
    assert "microphone=()" in response.headers["Permissions-Policy"]
    assert "HttpOnly" in response.headers["Set-Cookie"]
    assert "SameSite=Strict" in response.headers["Set-Cookie"]


def test_request_size_and_invalid_json(client, csrf):
    assert client.post("/api/profiles", data="invalid", content_type="application/json", headers=csrf).status_code == 400
    assert client.post("/api/profiles", json={"alias": "x" * 33000}, headers=csrf).status_code == 413
    assert client.post("/api/profiles", json=[], headers=csrf).status_code == 400
