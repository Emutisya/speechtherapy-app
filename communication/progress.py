from flask import Blueprint, current_app, jsonify
from werkzeug.exceptions import Conflict, NotFound

from .db import get_db
from .profiles import active_profile, now
from .validation import choice, only_keys, payload

progress = Blueprint("progress", __name__, url_prefix="/api/progress")
MODES = {"speech", "aac", "gesture", "listening", "mixed", "skipped"}
SUPPORTS = {"independent", "modeled", "supported", "not-recorded"}
COMFORTS = {"comfortable", "unsure", "wanted-break", "not-recorded"}


@progress.post("")
def record_event():
    profile = active_profile()
    if not profile["consent"]:
        raise Conflict("Progress saving is off. A caregiver can enable it, or continue without saving.")
    data = payload()
    only_keys(data, {"activity_id", "response_mode", "support", "comfort"})
    ids = {activity["id"] for activity in current_app.extensions["content"][1]}
    activity_id = choice(data.get("activity_id"), "Activity", ids)
    mode = choice(data.get("response_mode"), "Communication mode", MODES)
    support = choice(data.get("support", "not-recorded"), "Support", SUPPORTS)
    comfort = choice(data.get("comfort", "not-recorded"), "Comfort", COMFORTS)
    connection = get_db()
    with connection:
        if connection.execute("SELECT count(*) FROM events WHERE profile_id = ?", (profile["id"],)).fetchone()[0] >= 10000:
            raise Conflict("This space has reached 10,000 observations. Export and clear progress before saving more.")
        cursor = connection.execute(
            "INSERT INTO events(profile_id, activity_id, response_mode, support, comfort, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (profile["id"], activity_id, mode, support, comfort, now()),
        )
    return jsonify(id=cursor.lastrowid, saved=True), 201


@progress.get("")
def get_progress():
    profile = active_profile()
    connection = get_db()
    rows = connection.execute(
        "SELECT id, activity_id, response_mode, support, comfort, created_at FROM events WHERE profile_id = ? ORDER BY id DESC LIMIT 100",
        (profile["id"],),
    ).fetchall()
    totals = connection.execute(
        "SELECT response_mode, count(*) AS count FROM events WHERE profile_id = ? GROUP BY response_mode",
        (profile["id"],),
    ).fetchall()
    days = connection.execute(
        "SELECT substr(created_at, 1, 10) AS day, count(*) AS count FROM events WHERE profile_id = ? GROUP BY day ORDER BY day DESC LIMIT 14",
        (profile["id"],),
    ).fetchall()
    return jsonify(events=[dict(row) for row in rows], modes={row["response_mode"]: row["count"] for row in totals},
                   days=[dict(row) for row in days], total=sum(row["count"] for row in totals),
                   interpretation="Caregiver observations only. Counts do not measure speech accuracy, ability, or clinical improvement.")


@progress.delete("/<int:event_id>")
def delete_event(event_id):
    profile = active_profile()
    connection = get_db()
    with connection:
        cursor = connection.execute("DELETE FROM events WHERE id = ? AND profile_id = ?", (event_id, profile["id"]))
        if not cursor.rowcount:
            raise NotFound("This observation was not found in the selected space.")
    return jsonify(deleted=True)


@progress.delete("")
def clear_progress():
    profile = active_profile()
    data = payload()
    only_keys(data, {"confirmation"})
    if data.get("confirmation") != "CLEAR":
        raise Conflict("Type CLEAR to remove all observations in the selected space.")
    connection = get_db()
    with connection:
        connection.execute("DELETE FROM events WHERE profile_id = ?", (profile["id"],))
    return jsonify(deleted=True)
