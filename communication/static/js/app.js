import {$, state, api, report} from "./core.js";
import {initBoard} from "./board.js";
import {initSpeech, stopSpeech} from "./speech.js";
import {initPractice} from "./practice.js";
import {initCaregiver, loadProfiles} from "./caregiver.js";
import {initProgress, refreshProgress} from "./progress.js";
import {initWriting} from "./writing.js";

function initNavigation() {
  for (const button of document.querySelectorAll("[data-page]")) {
    button.addEventListener("click", async () => {
      stopSpeech();
      for (const section of document.querySelectorAll("main > section")) section.hidden = section.id !== `page-${button.dataset.page}`;
      for (const tab of document.querySelectorAll("[data-page]")) tab.removeAttribute("aria-current");
      button.setAttribute("aria-current", "page");
      $("main").focus();
      if (button.dataset.page === "caregiver") {
        try { await refreshProgress(); } catch (error) { report(error); }
      }
    });
  }
  $("break-button").addEventListener("click", () => {
    stopSpeech();
    $("break-dialog").showModal();
    $("end-break").focus();
  });
  $("end-break").addEventListener("click", () => $("break-dialog").close());
  $("dismiss-error").addEventListener("click", () => {
    $("error").hidden = true;
    $("main").focus();
  });
}

async function start() {
  initNavigation();
  try {
    const data = await api("/bootstrap");
    Object.assign(state, {cards: data.cards, activities: data.activities, defaults: data.defaults, preferences: {...data.defaults}, csrf: data.csrf_token});
    initSpeech(); initBoard(); initPractice(); initCaregiver(); initProgress(); initWriting();
    await loadProfiles();
    $("loading").hidden = true;
  } catch (error) {
    $("loading").textContent = "The app could not open fully. Check the error below, then reload this page.";
    report(error);
  }
}

start();
