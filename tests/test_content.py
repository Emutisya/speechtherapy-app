from communication.content import load_content


def test_self_advocacy_is_available_and_every_activity_has_choices():
    cards, activities = load_content()
    assert {"no", "stop", "help", "break", "hurt", "quiet", "not-sure"} <= {card["id"] for card in cards}
    for activity in activities:
        assert 2 <= len(activity["card_ids"]) <= 3
        assert activity["level"] in {1, 2}
        assert activity["caregiver_tip"]
        assert activity["model"]


def test_content_is_original_not_legacy_data():
    import json
    from pathlib import Path
    manifest = json.loads((Path(__file__).resolve().parents[1] / "data_manifest.json").read_text())
    assert all(not dataset["child_runtime_eligible"] for dataset in manifest["legacy_datasets"])
    assert manifest["runtime_content"]["clinical_validation"] == "Not clinically validated"
