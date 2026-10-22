import {$, state, api, notify, run} from "./core.js";
import {renderBoard, renderMessage} from "./board.js";
import {refreshVoices, stopSpeech} from "./speech.js";
import {refreshProgress} from "./progress.js";
import {resetPractice} from "./practice.js";

export function applyPreferences() {
  const prefs = state.preferences;
  const system = matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  document.documentElement.dataset.theme = prefs.theme === "system" ? system : prefs.theme;
  document.documentElement.classList.toggle("large-text", prefs.large_text);
  $("theme-select").value = prefs.theme;
  $("large-text").checked = prefs.large_text;
  $("reduced-choices").checked = prefs.reduced_choices;
  $("speech-enabled").checked = prefs.speech_enabled;
  $("speech-rate").value = prefs.speech_rate;
  if (!prefs.speech_enabled) stopSpeech();
  renderBoard(); refreshVoices();
}

export async function loadProfiles(resetMessages = false) {
  const data = await api("/profiles");
  state.profiles = data.profiles;
  state.profile = data.profiles.find((profile) => profile.id === data.active_profile) || null;
  state.preferences = {...state.defaults, ...(state.profile?.preferences || {})};
  const select = $("profile-select");
  select.replaceChildren();
  const empty = new Option("No saved space", "");
  empty.disabled = true; select.add(empty);
  for (const profile of state.profiles) select.add(new Option(profile.alias, profile.id));
  select.value = state.profile?.id || "";
  $("consent-status").textContent = state.profile
    ? `Selected: ${state.profile.alias}. Observation saving is ${state.profile.consent ? "on" : "off"}.`
    : "No space selected. Nothing is being saved.";
  $("storage-consent").checked = state.profile?.consent || false;
  for (const id of ["update-consent", "storage-consent"]) $(id).disabled = !state.profile;
  if (resetMessages) {
    state.message = [];
    renderMessage(); resetPractice(); stopSpeech();
  }
  applyPreferences();
  await refreshProgress();
}

export function initCaregiver() {
  $("profile-form").addEventListener("submit", run(async () => {
    await api("/profiles", "POST", {alias: $("profile-alias").value, consent: $("profile-consent").checked});
    $("profile-form").reset(); await loadProfiles(true); notify("Local space created. The board is ready.");
  }));
  $("profile-select").addEventListener("change", run(async () => {
    await api("/profiles/select", "POST", {id: $("profile-select").value});
    await loadProfiles(true); notify("Space changed. The previous message has been cleared.");
  }));
  $("preferences-form").addEventListener("submit", run(async () => {
    const preferences = {theme: $("theme-select").value, large_text: $("large-text").checked,
      reduced_choices: $("reduced-choices").checked, speech_enabled: $("speech-enabled").checked, speech_rate: $("speech-rate").value};
    if (state.profile) {
      const data = await api("/profiles/current", "PATCH", {preferences});
      state.profile = data.profile;
    }
    state.preferences = preferences; applyPreferences();
    notify(state.profile ? "Preferences saved on this device." : "Preferences applied for this page only.");
  }));
  $("update-consent").addEventListener("click", run(async () => {
    await api("/profiles/current", "PATCH", {consent: $("storage-consent").checked});
    await loadProfiles(); notify(state.profile.consent ? "Observation saving is on." : "Observation saving is off. Previously saved observations for this space were deleted.");
  }));
  $("clear-progress-form").addEventListener("submit", run(async () => {
    await api("/progress", "DELETE", {confirmation: $("clear-confirmation").value});
    $("clear-progress-form").reset(); await refreshProgress(); notify("All observations in this space were deleted.");
  }));
  $("delete-profile-form").addEventListener("submit", run(async () => {
    await api("/profiles/current", "DELETE", {confirmation: $("delete-confirmation").value});
    $("delete-profile-form").reset(); await loadProfiles(true); notify("Space and saved observations deleted.");
  }));
  matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => {
    if (state.preferences.theme === "system") applyPreferences();
  });
}
