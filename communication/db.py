import sqlite3
from pathlib import Path

from flask import current_app, g


SCHEMA = """
CREATE TABLE IF NOT EXISTS profiles (
    id TEXT PRIMARY KEY,
    alias TEXT NOT NULL,
    consent INTEGER NOT NULL CHECK (consent IN (0, 1)),
    preferences TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    profile_id TEXT NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    activity_id TEXT NOT NULL,
    response_mode TEXT NOT NULL,
    support TEXT NOT NULL,
    comfort TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS events_profile_date ON events(profile_id, created_at);
PRAGMA user_version = 1;
"""


def get_db():
    if "db" not in g:
        connection = sqlite3.connect(current_app.config["DATABASE"], timeout=10)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        g.db = connection
    return g.db


def close_db(_error=None):
    connection = g.pop("db", None)
    if connection is not None:
        connection.close()


def init_app(app):
    Path(app.config["DATABASE"]).parent.mkdir(parents=True, exist_ok=True)
    app.teardown_appcontext(close_db)
    with app.app_context():
        version = get_db().execute("PRAGMA user_version").fetchone()[0]
        if version > 1:
            raise RuntimeError("This database is newer than this app. Restore the matching app version.")
        get_db().executescript(SCHEMA)
