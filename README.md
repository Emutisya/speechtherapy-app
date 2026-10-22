# Fluent

**Every way of communicating counts.**

A local-first Python communication app for autistic children with caregiver
support. Fluent offers an AAC-style board, optional practice, a calm sensory
interface, and consent-based observation tracking. Speaking is never required.

**This is a communication support prototype, not a medical device, diagnostic
tool, validated treatment, or replacement for a speech-language professional or
an individually selected AAC system.** It has not been clinically validated or
tested with autistic children. "World-class" effectiveness cannot be established
by a code upgrade alone.

## Start on Windows

Requires Python 3.11 or newer.

```powershell
git clone https://github.com/Emutisya/speechtherapy-app.git
Set-Location speechtherapy-app
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

Open **http://127.0.0.1:3999**. No spaCy model, NumPy, GPU, cloud account, API key,
or internet connection is required at runtime. Dependencies need downloading
during initial installation. Optional browser speech requires an installed
English voice reported as local by your browser.

## What is included

| Area | Capability |
|---|---|
| Communicate | 24 labeled cards, pinned no/stop/help/break choices, 12-card message strip, undo, removal, copy, print |
| Gentle practice | 18 optional activities; filter by communication goal and message length |
| Access and comfort | Keyboard controls, visible focus, live status/error messages, large text, reduced choices, responsive light/dark UI, no timers or animation |
| Audio | Off by default; explicit playback only; local English browser voices only; pause cancels playback; no recording |
| Caregiver | Up to 12 household spaces with nicknames, explicit saving consent, sensory preferences |
| Observations | Speech, AAC, gesture/sign, listening, mixed participation, or skipping; optional support and child-reported comfort |
| Data control | Scoped JSON/CSV exports, observation correction/removal, consent revocation, space deletion |
| Writing | Highlight self-selected practice words, preserving Unicode and multiline text; no difficulty prediction |
| Dataset research | Streaming aggregate audit, checksums, encoding/quality flags, provenance manifest, documented limitations |

There are no scores, rankings, streaks, forced repetitions, microphone uploads,
remote AI calls, or third-party frontend dependencies. Observation counts describe
what a caregiver entered, not clinical improvement.

## Privacy and deployment boundaries

The production entry point uses Waitress, binds to loopback only, validates
hosts, and rejects non-loopback clients. **Do not expose it through a tunnel,
reverse proxy, port forwarding, or public hosting.** Proxying can make remote
traffic appear local. Authentication, permissions, TLS deployment, regulated
record handling, and clinical governance are outside this prototype's scope.

Saved data lives under the ignored `instance` folder: `communication.sqlite3`
and `session.key`. Board messages and writing are not stored. A signed,
HttpOnly, SameSite session cookie identifies the selected space; cookie signing
is not database encryption. All local spaces are visible to people using this
device. Use an OS account lock and disk encryption.

Turning saving off deletes that space's observations. Deleting a space also
deletes its preferences and observations. Copies in exports, backups, device
snapshots, and filesystem history are not erased by the app. See
[the caregiver guide](docs/CAREGIVER_GUIDE.md).

## Dataset findings

The original app was an AI-augmented writing prototype for people who stutter.
Its adult talk transcripts and word embeddings are not child therapy data:

* **2,467** TED transcript rows, including **3** repeated normalized transcripts.
* **133,859** 50-dimensional phonetic-vector rows; **1** line is not valid UTF-8.
* A semantic binary header declares **50,000 x 300**; payload is not validated.
* Legacy pickles and the object NumPy array are never loaded by the new runtime.

See the [full dataset report](reports/DATASET_REPORT.md),
[machine-readable audit](reports/dataset-audit.json), and
[provenance manifest](data_manifest.json). No child dataset or model efficacy is
claimed. Dataset-specific redistribution permissions remain unverified.

## Development

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe tools\audit_datasets.py --output reports\dataset-audit.json
```

Optional real-browser journeys use a temporary isolated database:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-browser.txt
.\.venv\Scripts\python.exe -m playwright install chromium
.\.venv\Scripts\python.exe tools\browser_smoke.py
```

See [architecture and API](docs/ARCHITECTURE.md) and
[design and clinical boundaries](docs/DESIGN_PRINCIPLES.md).

## Migration from the original prototype

The previous `/update`, `/check_if_word_difficult`, `/get_default_content`, and
`/getFileNames/` endpoints are retired. The old root `templates`, `css`, `js`,
notebooks, and media are retained as historical research assets but are not
served by the new app. The app now serves only `communication/static`.

The original SVM prediction loop and executable pickle loading are intentionally
not carried into children's activities. Writing support is now the explicit
`POST /api/writing/review` selected-word workflow. Existing prototype clients must
migrate; the API is not backward compatible. Old filesystem session artifacts
are not imported. No license grant for legacy third-party content is implied.
