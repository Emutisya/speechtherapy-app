from werkzeug.exceptions import BadRequest

from .validation import boolean, choice, only_keys

DEFAULTS = {
    "theme": "system",
    "large_text": False,
    "reduced_choices": False,
    "speech_enabled": False,
    "speech_rate": "gentle",
}


def validate_preferences(data):
    if not isinstance(data, dict):
        raise BadRequest("Preferences must be an object.")
    only_keys(data, DEFAULTS)
    result = {}
    for key, value in data.items():
        if key == "theme":
            result[key] = choice(value, key, {"system", "light", "dark"})
        elif key == "speech_rate":
            result[key] = choice(value, key, {"gentle", "regular"})
        else:
            result[key] = boolean(value, key)
    return result
