# Caregiver guide

## Start with the child

Use Fluent together initially and check whether the labels, symbols, size, and
layout make sense to the child. Follow their preferred communication methods.
This English-only starter board may be too small, too large, or otherwise
unsuitable. Keep their existing AAC system and usual supports available.

No spoken response, eye contact, stillness, imitation, or completion is required.
Respect no, stop, all done, and requests for a break. Do not withhold essential
items or help to prompt communication.

## Communicate

Choose a category and tap labeled cards. No, stop, help, and a break remain
available across categories. The message strip uses short card labels, not
full-sentence phrases, so combinations remain under the child's control.
Select a message card to remove it, or use Undo last and Clear.

Show the message to someone, copy it, or enable optional audio in Caregiver.
Clipboard contents can be visible outside this app. Board messages disappear
when the page reloads or the selected space changes. They are not logged.

Print board includes all 24 cards, even with reduced choices or another category
selected. Keep the printed copy somewhere the child can access it. Printed
symbols are a backup, not a replacement for individual AAC assessment.

## Make the space comfortable

In Caregiver, choose light/dark/device appearance, larger text, or fewer choices.
Reduced choices show six cards at most: four essential choices plus two other
cards, with Previous/Next controls. Every card remains reachable.

Audio is off initially and never plays automatically. Enable it only if welcome.
Only English voices the browser reports as local are offered. If none are
available, install an appropriate operating-system voice or use the silent
board. Browser and OS voice behavior varies; verify device speech privacy
settings. There is no microphone, recording, or pronunciation assessment.

Take a break is always available. It cancels speech and opens a quiet pause
dialog. Escape or Return when ready closes it. Leaving the app is also fine.

## Practice without pressure

Choose an activity by goal and message length. Single-word and phrase labels are
organizational categories, not developmental stages or assigned difficulty.
Follow the caregiver note. Use a model only if welcome; tapping, pointing,
signing, speech, listening, a mix, or skipping are valid.

Some activities mention needs. They must never become tests that block access
to water, food, toileting, comfort, help, or a break. Respond to pain or distress
with appropriate support, not another activity.

## Optional local observations

The app works without a saved space. If you are the responsible caregiver and
want observations, create a local space with a nickname and choose saving
consent. Do not enter a child's full name, birth date, diagnosis, or contact
information. The consent checkbox records your software choice; it is not a
complete legal consent or safeguarding process.

Under an activity, open Caregiver: record an observation. Record the mode, any
support offered, and comfort only if shared by the child. Do not infer internal
feelings from a face or behavior. This is a manual observation, not a measured
accuracy or assessment.

The latest 100 entries appear in the table; totals include all stored entries,
up to 10,000 per space. Remove mistaken entries and record a replacement if
needed. JSON and CSV exports contain all entries, omit the space nickname,
and use UTC timestamps. The interface shows your local time.

## Privacy and deletion

All spaces are accessible to anyone using this browser/device. There is no
caregiver password or lock, and no confidentiality boundary between spaces.
The selected-space identifier is kept in a signed browser session cookie.
Cookies are not encryption and clearing them does not remove saved spaces.
Avoid using a shared or unprotected device for sensitive observations.

Turning saving off deletes observations for the selected space. CLEAR removes
observations without removing the space. DELETE removes the selected space,
preferences, and observations. Other spaces remain.

Database deletion is not a promise of forensic erasure: downloads, backups,
snapshots, and operating-system copies are outside the app's control. SQLite's
secure-delete setting is enabled, but disk protection and retention remain the
caregiver's responsibility.

The app does not automatically expire old data. Review retention regularly.
Back up only when necessary, protect backups, and delete unneeded copies.
Never email an unprotected database or commit the `instance` folder to Git.

## Troubleshooting

| Situation | What to do |
|---|---|
| App will not open | Start `.\.venv\Scripts\python.exe app.py`, then open `http://127.0.0.1:3999` |
| Session expired | Reload the page; unsaved messages and writing will be cleared |
| Space changed in another tab | Reload before saving or exporting, and check the selected nickname |
| No audio voice | Check installed English device voices; use silent cards meanwhile |
| Progress saving is off | Continue without saving, or explicitly enable it for the selected space |
| Cannot copy | Check clipboard permission or show the message on screen |
| Port 3999 already in use | Stop your own earlier Fluent server; do not terminate unrelated processes |
| Server error persists | Ask a developer to inspect the local server log without sharing child data publicly |

For individualized communication support, consult a qualified speech-language
professional. For pain, swallowing difficulty, or other health concerns, seek
appropriate healthcare. Use local emergency services in an emergency.
