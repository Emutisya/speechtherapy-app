import secrets

from flask import request, session
from werkzeug.exceptions import Forbidden


def csrf_token():
    if "csrf" not in session:
        session["csrf"] = secrets.token_urlsafe(32)
    return session["csrf"]


def install_security(app):
    @app.before_request
    def protect_request():
        if request.remote_addr not in {"127.0.0.1", "::1"}:
            raise Forbidden("This app is for this device only. Open it at http://127.0.0.1:3999.")
        if request.method not in {"GET", "HEAD", "OPTIONS"}:
            token = request.headers.get("X-CSRF-Token", "")
            expected = session.get("csrf")
            if not expected or not secrets.compare_digest(token, expected):
                raise Forbidden("Your page session expired. Reload the page and try again.")
            if request.headers.get("Sec-Fetch-Site") == "cross-site":
                raise Forbidden("Open the app directly before saving changes.")
            origin = request.headers.get("Origin")
            if origin and origin != request.host_url.rstrip("/"):
                raise Forbidden("Requests must come from this app's own address.")

    @app.after_request
    def private_headers(response):
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Permissions-Policy"] = "microphone=(), camera=(), geolocation=()"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'self'; "
            "img-src 'self'; connect-src 'self'; object-src 'none'; "
            "base-uri 'self'; form-action 'self'; frame-ancestors 'none'"
        )
        return response
