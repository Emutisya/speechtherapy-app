import re

from flask import Blueprint, jsonify

from .validation import only_keys, payload, text

writing = Blueprint("writing", __name__, url_prefix="/api/writing")


@writing.post("/review")
def review():
    data = payload()
    only_keys(data, {"text", "practice_words"})
    passage = text(data.get("text"), "Writing", 5000)
    practice = text(data.get("practice_words"), "Practice words", 500)
    words = {word.casefold() for word in re.findall(r"[^\W\d_]+(?:['-][^\W\d_]+)*", practice)}
    matches = [{"start": match.start(), "end": match.end(), "word": match.group()}
               for match in re.finditer(r"[^\W\d_]+(?:['-][^\W\d_]+)*", passage)
               if match.group().casefold() in words]
    return jsonify(matches=matches, notice="These are your selected practice words, not an AI assessment of difficulty.")
