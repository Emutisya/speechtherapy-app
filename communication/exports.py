import csv
import io

from flask import Blueprint, jsonify, make_response, request
from werkzeug.exceptions import BadRequest

from .db import get_db
from .profiles import active_profile

exports = Blueprint("exports", __name__, url_prefix="/api/export")
FIELDS = ("activity_id", "response_mode", "support", "comfort", "created_at")


@exports.get("")
def export_progress():
    profile = active_profile()
    rows = get_db().execute(
        "SELECT activity_id, response_mode, support, comfort, created_at FROM events WHERE profile_id = ? ORDER BY id",
        (profile["id"],),
    ).fetchall()
    export_format = request.args.get("format", "json")
    if export_format == "json":
        response = jsonify(schema_version=1, observations=[dict(row) for row in rows],
                           notice="Caregiver observations, not clinical scores. Space labels are intentionally excluded.")
    elif export_format == "csv":
        output = io.StringIO(newline="")
        writer = csv.writer(output)
        writer.writerow(FIELDS)
        writer.writerows(tuple(row[field] for field in FIELDS) for row in rows)
        response = make_response(output.getvalue())
        response.mimetype = "text/csv"
    else:
        raise BadRequest("Export format must be json or csv.")
    response.headers["Content-Disposition"] = f'attachment; filename="fluent-observations.{export_format}"'
    return response
