def test_matches_preserve_original_unicode_offsets(client, csrf):
    passage = "\U0001f642 Play, PLAY! playground. caf\u00e9"
    data = client.post("/api/writing/review", json={"text": passage, "practice_words": "play, caf\u00e9"}, headers=csrf).get_json()
    assert [match["word"] for match in data["matches"]] == ["Play", "PLAY", "caf\u00e9"]
    assert all(passage[match["start"]:match["end"]] == match["word"] for match in data["matches"])


def test_writing_is_not_persisted(client, csrf, profile):
    response = client.post("/api/writing/review", json={"text": "<script>play</script>", "practice_words": "play"}, headers=csrf)
    assert response.status_code == 200
    assert client.get("/api/progress").get_json()["total"] == 0


def test_writing_requires_bounded_text(client, csrf):
    for body in [{"text": "", "practice_words": "play"}, {"text": "x" * 5001, "practice_words": "play"}, {"text": "play"}]:
        assert client.post("/api/writing/review", json=body, headers=csrf).status_code == 400


def test_multiline_and_leading_whitespace_preserve_offsets(client, csrf):
    passage = "  Hello\nplay\tmore "
    data = client.post("/api/writing/review", json={"text": passage, "practice_words": "play"}, headers=csrf).get_json()
    assert data["matches"] == [{"word": "play", "start": 8, "end": 12}]
