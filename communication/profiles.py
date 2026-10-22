import json
from datetime import datetime, timezone
from uuid import uuid4

from flask import Blueprint, jsonify, session
from werkzeug.exceptions import Conflict, NotFound

from .db import get_db
from .preferences import DEFAULTS, validate_preferences
from .validation import boolean, only_keys, payload, text

profiles = Blueprint("profiles", __name__, url_prefix="/api/profiles")


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def active_profile():
    row = get_db().execute("SELECT * FROM profiles WHERE id = ?", (session.get("profile_id"),)).fetchone()
    if row is None:
        raise Conflict("Choose or create a local space in Caregiver before saving progress.")
    return row


def serialize(row):
    return {"id": row["id"], "alias": row["alias"], "consent": bool(row["consent"]),
            "preferences": {**DEFAULTS, **json.loads(row["preferences"])}}


@profiles.get("")
def list_profiles():
    rows = get_db().execute("SELECT * FROM profiles ORDER BY created_at, id").fetchall()
    return jsonify(profiles=[serialize(row) for row in rows], active_profile=session.get("profile_id"))


@profiles.post("")
def create_profile():
    data = payload()
    only_keys(data, {"alias", "consent"})
    alias = text(data.get("alias"), "Space label")
    consent = boolean(data.get("consent"), "Progress storage consent")
    connection = get_db()
    if connection.execute("SELECT count(*) FROM profiles").fetchone()[0] >= 12:
        raise Conflict("This household already has 12 spaces. Delete an unused space before adding another.")
    profile_id = uuid4().hex
    with connection:
        connection.execute("INSERT INTO profiles(id, alias, consent, created_at) VALUES (?, ?, ?, ?)",
                           (profile_id, alias, int(consent), now()))
    session["profile_id"] = profile_id
    return jsonify(profile=serialize(active_profile())), 201


@profiles.post("/select")
def select_profile():
    data = payload()
    only_keys(data, {"id"})
    profile_id = text(data.get("id"), "Space ID", 32)
    row = get_db().execute("SELECT * FROM profiles WHERE id = ?", (profile_id,)).fetchone()
    if row is None:
        raise NotFound("This local space no longer exists. Refresh the list.")
    session["profile_id"] = profile_id
    return jsonify(profile=serialize(row))


@profiles.patch("/current")
def update_profile():
    row = active_profile()
    data = payload()
    only_keys(data, {"preferences", "consent"})
    preferences = {**json.loads(row["preferences"]), **validate_preferences(data.get("preferences", {}))}
    consent = boolean(data.get("consent", bool(row["consent"])), "Progress storage consent")
    connection = get_db()
    with connection:
        connection.execute("UPDATE profiles SET preferences = ?, consent = ? WHERE id = ?",
                           (json.dumps(preferences), int(consent), row["id"]))
        if not consent:
            connection.execute("DELETE FROM events WHERE profile_id = ?", (row["id"],))
    return jsonify(profile=serialize(active_profile()))


@profiles.delete("/current")
def delete_profile():
    row = active_profile()
    data = payload()
    only_keys(data, {"confirmation"})
    if data.get("confirmation") != "DELETE":
        raise Conflict("Type DELETE to confirm permanent removal of this space and its saved progress.")
    connection = get_db()
    with connection:
        connection.execute("DELETE FROM profiles WHERE id = ?", (row["id"],))
    session.pop("profile_id", None)
    return jsonify(deleted=True)
