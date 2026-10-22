# Architecture and API

## Runtime

`app.py` creates the Flask application and serves it with Waitress on
`127.0.0.1:3999`. `communication.create_app` accepts an optional configuration
mapping for isolated tests. The runtime depends on Flask and Waitress, not the
original ML stack.

Only `communication/static` is public. Jinja templates are in
`communication/templates`. Browser modules use native ES modules, the Fetch API,
SVG drawings, and optional Web Speech synthesis. No frontend build, CDN,
telemetry, service worker, browser database, or cloud service is required.

Curated JSON content loads once at startup and validates unique identifiers and
card references. Dataset analysis is a separate CLI tool and is never invoked
by a child-facing request.

## Persistence and scope

SQLite has `profiles` and `events` tables. Profile IDs are random UUID hex
strings. Profiles hold a nickname, saving consent, and sensory preferences.
Events hold the activity identifier, communication mode, support, comfort, and
UTC timestamp. Free-text child notes and speech recordings are not collected.

Foreign keys and cascade deletion are enabled for every connection. SQLite
secure deletion is enabled; this is not a guarantee about OS backups or
forensic recovery. Parameterized SQL is used. Capacity checks and insertion use
an immediate transaction to avoid concurrent capacity overflows.

The signed session selects the current household space. **It does not
authenticate a caregiver.** Everyone on the local device can select any space.
Frontend requests send `X-Profile-ID`; active-space operations reject a
conflicting ID to prevent a stale tab from writing into another selected space.
Download links carry the same expected ID in `profile_id`. This is consistency
protection, not authorization.

A secret is created under the ignored `instance` directory and reused across
restarts. The key is not regenerated on every page request. An invalid key or
newer database schema fails startup rather than silently resetting stored data.
Schema version is 1; future changes require explicit migrations.

## Request protection

Hosts are restricted to localhost addresses. Every request checks the direct
remote address is loopback. Do not trust forwarded headers or deploy behind a
proxy: a proxy can collapse remote visitors into a loopback address.

Mutating requests require the session's `X-CSRF-Token`, supplied by bootstrap.
Cross-site Fetch metadata and mismatched Origin are rejected. Cookies are
HttpOnly and SameSite=Strict. TLS/Secure-cookie deployment is intentionally not
configured because this prototype is loopback-only.

Responses disable caching and framing, disallow microphone/camera/geolocation,
and use a self-only Content Security Policy with no inline scripts. HTTP
exceptions return a stable JSON error envelope. Unhandled errors are logged by
Flask and return a generic actionable message without traceback details.

## API overview

JSON request bodies must be objects; unknown keys, invalid types, enum values,
and excessive lengths are rejected. Max request body is 32 KiB.

| Method | Path | Contract |
|---|---|---|
| GET | `/health` | `{status: "ok"}` |
| GET | `/api/bootstrap` | CSRF token, default preferences, cards, activities, selected ID |
| GET | `/api/profiles` | Household space list and active ID |
| POST | `/api/profiles` | `{alias, consent}`; create and select a space |
| POST | `/api/profiles/select` | `{id}`; select an existing space |
| PATCH | `/api/profiles/current` | Optional `{preferences, consent}`; revoked consent deletes observations |
| DELETE | `/api/profiles/current` | `{confirmation: "DELETE"}`; cascade deletion |
| POST | `/api/progress` | `{activity_id, response_mode, support?, comfort?}`; consent required |
| GET | `/api/progress` | Most recent 100 events, all-time mode totals, recent 14 observed UTC dates |
| DELETE | `/api/progress/<id>` | Remove an observation belonging to the active space |
| DELETE | `/api/progress` | `{confirmation: "CLEAR"}` |
| GET | `/api/export?format=json\|csv` | All active-space observations, no nickname |
| POST | `/api/writing/review` | `{text, practice_words}`; Unicode-code-point offsets for selected words |

`response_mode`: `speech`, `aac`, `gesture`, `listening`, `mixed`, `skipped`.
`support`: `independent`, `modeled`, `supported`, `not-recorded`.
`comfort`: `comfortable`, `unsure`, `wanted-break`, `not-recorded`.

`independent` is displayed as "No model offered", not an objective claim about
independent ability. Saved preferences support theme (`system/light/dark`),
large text, reduced choices, speech opt-in, and gentle/regular speaking pace.
Voice identity stays page-local because installed voices vary between devices.

Typical errors:

```json
{"error": {"code": "conflict", "message": "Choose or create a local space in Caregiver before saving progress."}}
```

## Known constraints

No network accounts, tenant isolation, clinician dashboard, role permissions,
automatic retention, encryption at rest, child speech recognition, clinical
assessment, switch scanning, eye-gaze integration, vocabulary editing,
multilingual content, or regulated hosting is implemented. Keyboard users can
activate native buttons, but that is not a claim of compatibility with every
assistive device. There is no offline service worker; the local server must run.

The previous prototype endpoints are intentionally removed. Historical root
assets remain for research continuity, not backward-compatible execution.
