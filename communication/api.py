from flask import Blueprint, current_app, jsonify, session

from .preferences import DEFAULTS
from .security import csrf_token

api = Blueprint("api", __name__, url_prefix="/api")


@api.get("/bootstrap")
def bootstrap():
    cards, activities = current_app.extensions["content"]
    return jsonify(
        csrf_token=csrf_token(),
        active_profile=session.get("profile_id"),
        cards=cards,
        activities=activities,
        defaults=DEFAULTS,
        version="0.2.0",
        notice="Communication support, not diagnosis or a replacement for a speech-language professional.",
    )
