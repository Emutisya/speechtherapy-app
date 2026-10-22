from flask import request
from werkzeug.exceptions import BadRequest


def payload():
    value = request.get_json()
    if not isinstance(value, dict):
        raise BadRequest("Send a JSON object.")
    return value


def text(value, name, maximum=40, *, multiline=False):
    if not isinstance(value, str) or not value.strip():
        raise BadRequest(f"{name} must be non-empty text.")
    value = value if multiline else value.strip()
    allowed_controls = "\n\r\t" if multiline else ""
    if len(value) > maximum or any(ord(char) < 32 and char not in allowed_controls for char in value):
        raise BadRequest(f"{name} must be at most {maximum} characters without control characters.")
    return value


def choice(value, name, options):
    if not isinstance(value, str) or value not in options:
        raise BadRequest(f"{name} must be one of: {', '.join(sorted(options))}.")
    return value


def boolean(value, name):
    if type(value) is not bool:
        raise BadRequest(f"{name} must be true or false.")
    return value


def only_keys(data, allowed):
    unknown = set(data) - set(allowed)
    if unknown:
        raise BadRequest(f"Unrecognized fields: {', '.join(sorted(unknown))}.")
