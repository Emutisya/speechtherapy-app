import {$, state, element, api, notify, run} from "./core.js";

const names = {aac: "Tapping / AAC", gesture: "Gesture / sign", speech: "Speech", listening: "Listening", mixed: "Mixed", skipped: "Chose to skip",
  independent: "No model offered", modeled: "Model offered", supported: "Support offered", "not-recorded": "Not recorded",
  comfortable: "Comfortable", unsure: "Not sure", "wanted-break": "Wanted a break"};

export async function refreshProgress() {
  $("progress-rows").replaceChildren();
  $("progress-summary").replaceChildren();
  $("mode-summary").replaceChildren();
  for (const id of ["export-json", "export-csv"]) {
    $(id).hidden = !state.profile;
  }
  if (!state.profile) {
    $("progress-summary").append(element("p", "No space selected. You can use the board and practice without saving."));
    return;
  }
  const data = await api("/progress");
  const metric = (value, label) => {
    const box = element("div", undefined, "metric");
    box.append(element("strong", String(value)), element("span", label, "small"));
    return box;
  };
  $("progress-summary").append(metric(data.total, "observations saved"), metric(data.modes.skipped || 0, "choices to skip honored"));
  for (const [mode, count] of Object.entries(data.modes)) $("mode-summary").append(element("span", `${names[mode]}: ${count}`, "pill"));
  for (const event of data.events) {
    const row = element("tr");
    const title = state.activities.find((activity) => activity.id === event.activity_id)?.title || event.activity_id;
    for (const value of [title, names[event.response_mode], names[event.support], names[event.comfort], new Date(event.created_at).toLocaleString()]) row.append(element("td", value));
    const cell = element("td");
    const button = element("button", "Remove");
    button.setAttribute("aria-label", `Remove observation: ${title}, ${new Date(event.created_at).toLocaleString()}`);
    button.addEventListener("click", run(async () => {
      button.disabled = true;
      try { await api(`/progress/${event.id}`, "DELETE"); await refreshProgress(); $("refresh-progress").focus(); notify("Observation removed."); }
      finally { button.disabled = false; }
    }));
    cell.append(button); row.append(cell); $("progress-rows").append(row);
  }
  if (!data.events.length) {
    const row = element("tr");
    const cell = element("td", "No observations yet. Saving is always optional.");
    cell.colSpan = 6; row.append(cell); $("progress-rows").append(row);
  }
}

export function initProgress() {
  $("refresh-progress").addEventListener("click", run(refreshProgress));
}
