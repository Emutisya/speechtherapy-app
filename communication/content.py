import json
from pathlib import Path

CONTENT_DIR = Path(__file__).resolve().parent / "content"


def load_content():
    cards = json.loads((CONTENT_DIR / "cards.json").read_text(encoding="utf-8"))
    activities = json.loads((CONTENT_DIR / "activities.json").read_text(encoding="utf-8"))
    for name, items in (("cards", cards), ("activities", activities)):
        ids = [item["id"] for item in items]
        if len(ids) != len(set(ids)):
            raise ValueError(f"Duplicate {name} identifiers.")
    card_ids = {card["id"] for card in cards}
    for activity in activities:
        if not set(activity["card_ids"]).issubset(card_ids):
            raise ValueError(f"Unknown card in {activity['id']}.")
    return cards, activities
