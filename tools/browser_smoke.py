"""Exercise real browser journeys against an isolated, temporary local database."""

import argparse
import sys
import tempfile
import threading
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from playwright.sync_api import expect, sync_playwright
from werkzeug.serving import WSGIRequestHandler, make_server

from communication import create_app


class QuietHandler(WSGIRequestHandler):
    def log_request(self, _code="-", _size="-"):
        pass


def exercise(browser, base_url, screenshot=None):
    page = browser.new_page(viewport={"width": 1440, "height": 1050})
    errors = []
    external_requests = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.on("console", lambda message: errors.append(message.text) if message.type == "error" else None)
    page.on("request", lambda request: external_requests.append(request.url) if not request.url.startswith(base_url + "/") else None)
    page.goto(base_url)
    expect(page.locator("#loading")).to_be_hidden()
    expect(page.locator("#board-cards > button")).to_have_count(24)
    page.get_by_role("button", name="My needs", exact=True).click()
    for label in ["No", "Stop", "Help", "A break"]:
        expect(page.locator("#board-cards").get_by_role("button", name=label, exact=True)).to_be_visible()
    page.locator("#board-cards").get_by_role("button", name="Water", exact=True).click()
    expect(page.locator("#message-count")).to_have_text("1 of 12 cards")
    for _ in range(12):
        page.locator("#board-cards").get_by_role("button", name="Water", exact=True).click()
    expect(page.locator("#message-count")).to_have_text("12 of 12 cards")
    expect(page.locator("#message-strip button")).to_have_count(12)
    page.get_by_role("button", name="Clear", exact=True).click()
    page.locator("#board-cards").get_by_role("button", name="Water", exact=True).focus()
    page.keyboard.press("Enter")
    expect(page.locator("#message-count")).to_have_text("1 of 12 cards")
    page.get_by_role("button", name="Say message", exact=True).click()
    expect(page.locator("#status")).to_contain_text("Audio is off")
    page.get_by_role("button", name="All cards", exact=True).click()
    if screenshot:
        page.screenshot(path=str(screenshot), full_page=True)
    page.get_by_role("button", name="Take a break", exact=True).click()
    expect(page.get_by_role("dialog")).to_be_visible()
    expect(page.get_by_role("button", name="Return when ready")).to_be_focused()
    page.keyboard.press("Escape")
    expect(page.get_by_role("dialog")).to_be_hidden()
    page.get_by_role("button", name="Caregiver", exact=True).click()
    page.get_by_label("New space label", exact=True).fill("Test space")
    page.locator("#profile-consent").check()
    page.get_by_role("button", name="Create local space", exact=True).click()
    expect(page.locator("#consent-status")).to_contain_text("saving is on")
    page.locator("#reduced-choices").check()
    page.get_by_role("button", name="Apply preferences", exact=True).click()
    expect(page.locator("#status")).to_contain_text("Preferences saved")
    page.get_by_role("button", name="Communicate", exact=True).click()
    expect(page.locator("#board-cards > button")).to_have_count(6)
    page.get_by_role("button", name="Next cards", exact=True).click()
    expect(page.locator("#board-cards")).to_contain_text("Page 2")
    reachable = set()
    page.get_by_role("button", name="Previous cards", exact=True).click()
    while True:
        reachable.update(page.locator("#board-cards > button").all_text_contents())
        next_button = page.get_by_role("button", name="Next cards", exact=True)
        if next_button.is_disabled():
            break
        next_button.click()
    assert len(reachable) == 24, "Reduced choices must preserve access to every card"
    page.evaluate("window.dispatchEvent(new Event('beforeprint'))")
    expect(page.locator("#board-cards > button")).to_have_count(24)
    page.evaluate("window.dispatchEvent(new Event('afterprint'))")
    expect(page.locator("#board-cards > button")).to_have_count(6)
    page.get_by_role("button", name="Gentle practice", exact=True).click()
    page.locator("#activity-list button").filter(has_text="Ask for help").click()
    page.get_by_text("Caregiver: record an observation", exact=True).click()
    page.get_by_role("button", name="Save observation on this device").click()
    expect(page.locator("#status")).to_contain_text("Observation saved")
    page.get_by_role("button", name="Caregiver", exact=True).click()
    expect(page.locator("#progress-rows tr")).to_have_count(1)
    expect(page.locator("#progress-rows")).to_contain_text("Ask for help")
    with page.expect_download() as download_info:
        page.get_by_role("link", name="Download CSV").click()
    assert download_info.value.suggested_filename == "fluent-observations.csv"
    page.locator("#storage-consent").uncheck()
    page.get_by_role("button", name="Update storage choice").click()
    expect(page.locator("#progress-rows")).to_contain_text("No observations yet")
    expect(page.locator("#consent-status")).to_contain_text("saving is off")
    page.get_by_role("button", name="Writing space", exact=True).click()
    page.locator("#writing-text").fill("  Hello\n\U0001f642 play <script>not executable</script>")
    page.locator("#practice-words").fill("play")
    page.get_by_role("button", name="Highlight my words").click()
    expect(page.locator("#writing-result mark")).to_have_text("play")
    expect(page.locator("#writing-result script")).to_have_count(0)
    page.get_by_role("button", name="Caregiver", exact=True).click()
    page.locator("#delete-confirmation").fill("DELETE")
    page.get_by_role("button", name="Delete selected space").click()
    expect(page.locator("#consent-status")).to_contain_text("Nothing is being saved")
    page.set_viewport_size({"width": 390, "height": 844})
    page.get_by_role("button", name="Communicate", exact=True).click()
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth"), "Horizontal overflow at mobile size"
    page.emulate_media(reduced_motion="reduce", color_scheme="dark")
    expect(page.locator("html")).to_have_attribute("data-theme", "dark")
    page.keyboard.press("Tab")
    assert not external_requests, f"Unexpected external requests: {external_requests}"
    assert not errors, "\n".join(errors)
    page.close()


def exercise_voice_boundaries(browser, base_url):
    page = browser.new_page()
    page.add_init_script("""
      window.voiceCalls = {spoken: [], canceled: 0};
      Object.defineProperty(window, "speechSynthesis", {value: {
        getVoices: () => [
          {name: "Remote English", lang: "en-US", localService: false, voiceURI: "remote"},
          {name: "Local English", lang: "en-GB", localService: true, voiceURI: "local"},
          {name: "Local French", lang: "fr-FR", localService: true, voiceURI: "french"}
        ],
        addEventListener: () => {},
        cancel: () => { window.voiceCalls.canceled++; },
        speak: (utterance) => { window.voiceCalls.spoken.push({text: utterance.text, voice: utterance.voice.voiceURI, rate: utterance.rate}); }
      }});
      window.SpeechSynthesisUtterance = class { constructor(text) { this.text = text; } };
    """)
    page.goto(base_url)
    expect(page.locator("#loading")).to_be_hidden()
    page.get_by_role("button", name="Caregiver", exact=True).click()
    expect(page.locator("#voice-select option")).to_have_count(1)
    expect(page.locator("#voice-select")).to_have_value("local")
    page.locator("#speech-enabled").check()
    page.get_by_role("button", name="Apply preferences", exact=True).click()
    expect(page.locator("#status")).to_contain_text("this page only")
    assert page.evaluate("window.voiceCalls.spoken.length") == 0, "Enabling audio must not autoplay"
    page.get_by_role("button", name="Communicate", exact=True).click()
    page.locator("#board-cards").get_by_role("button", name="Help", exact=True).click()
    page.get_by_role("button", name="Say message", exact=True).click()
    assert page.evaluate("window.voiceCalls.spoken") == [{"text": "Help", "voice": "local", "rate": 0.8}]
    before = page.evaluate("window.voiceCalls.canceled")
    page.get_by_role("button", name="Take a break", exact=True).click()
    assert page.evaluate("window.voiceCalls.canceled") > before
    page.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--screenshot", type=Path)
    args = parser.parse_args()
    if args.screenshot:
        args.screenshot.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="fluent-browser-") as temporary:
        app = create_app({"TESTING": True, "SECRET_KEY": "browser-test-only",
                          "DATABASE": str(Path(temporary) / "browser.db")})
        server = make_server("127.0.0.1", 0, app, request_handler=QuietHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch()
                try:
                    exercise(browser, f"http://127.0.0.1:{server.server_port}", args.screenshot)
                    exercise_voice_boundaries(browser, f"http://127.0.0.1:{server.server_port}")
                finally:
                    browser.close()
        finally:
            server.shutdown()
            thread.join(timeout=5)
            server.server_close()
    print("Browser journeys passed: AAC, pause, consent, practice, export, erasure, writing, mobile, dark mode.")


if __name__ == "__main__":
    main()
