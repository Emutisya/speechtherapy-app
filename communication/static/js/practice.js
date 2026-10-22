import {$, state, element, notify, api, run} from "./core.js";
import {cardButton, addCard} from "./board.js";
import {speak, stopSpeech} from "./speech.js";

export function renderActivities() {
  const list = $("activity-list");
  list.replaceChildren();
  const filtered = state.activities.filter((activity) =>
    ($("goal-filter").value === "all" || activity.goal === $("goal-filter").value) &&
    ($("level-filter").value === "all" || String(activity.level) === $("level-filter").value));
  for (const activity of filtered) {
    const button = element("button", undefined, "activity-card");
    button.append(element("span", activity.goal.replaceAll("-", " ").toUpperCase(), "eyebrow"),
      element("span", activity.title, "activity-name"),
      element("span", activity.level === 1 ? "Single words or choices" : "Short phrases", "small"));
    button.addEventListener("click", () => openActivity(activity));
    list.append(button);
  }
  if (!filtered.length) list.append(element("p", "No activities match both filters. Try another goal or message length."));
}

function openActivity(activity) {
  stopSpeech();
  state.activity = activity;
  $("activity-detail").hidden = false;
  $("activity-list").hidden = true;
  $("activity-title").textContent = activity.title;
  $("activity-step").textContent = "CHOOSE / EXPLORE / REST WHEN YOU WANT";
  $("activity-prompt").textContent = activity.prompt;
  $("activity-tip").textContent = `Caregiver note: ${activity.caregiver_tip}`;
  $("activity-cards").replaceChildren();
  for (const id of activity.card_ids) {
    const card = state.cards.find((item) => item.id === id);
    $("activity-cards").append(cardButton(card, (selected) => {
      addCard(selected);
      notify(`${selected.phrase}. Added to your message on Communicate.`);
    }));
  }
  $("observation-form").reset();
  $("activity-detail").querySelector("details").open = false;
  $("activity-title").focus();
}

export function resetPractice() {
  state.activity = null;
  $("activity-detail").hidden = true;
  $("activity-list").hidden = false;
}

export function initPractice() {
  for (const id of ["goal-filter", "level-filter"]) $(id).addEventListener("change", () => { resetPractice(); renderActivities(); });
  $("model-activity").addEventListener("click", () => { if (state.activity) speak(state.activity.model); });
  $("next-activity").addEventListener("click", () => { resetPractice(); $("goal-filter").focus(); stopSpeech(); });
  $("observation-form").addEventListener("submit", run(async () => {
    if (!state.activity) throw new Error("Choose an activity before recording an observation.");
    await api("/progress", "POST", {activity_id: state.activity.id, response_mode: $("response-mode").value, support: $("support").value, comfort: $("comfort").value});
    notify("Observation saved on this device. This is not a clinical score.");
  }));
  renderActivities();
}
