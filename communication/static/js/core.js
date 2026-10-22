export const state = {cards: [], activities: [], profiles: [], profile: null, preferences: {}, message: [], activity: null};
export const $ = (id) => document.getElementById(id);

export function element(tag, text, className) {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = text;
  if (className) node.className = className;
  return node;
}

let statusTimer;
export function notify(message) {
  clearTimeout(statusTimer);
  $("status").textContent = message;
  statusTimer = setTimeout(() => { $("status").textContent = ""; }, 6000);
}

export function report(error) {
  $("error-text").textContent = error.message || "Something went wrong. Reload the page and try again.";
  $("error").hidden = false;
}

export function run(action) {
  return async (event) => {
    if (event?.type === "submit") event.preventDefault();
    const button = event?.submitter;
    if (button) button.disabled = true;
    try { await action(event); }
    catch (error) { report(error); }
    finally { if (button) button.disabled = false; }
  };
}

export async function api(path, method = "GET", body) {
  let response;
  try {
    response = await fetch(`/api${path}`, {
      method, credentials: "same-origin",
      headers: {"Content-Type": "application/json", "X-CSRF-Token": state.csrf || ""},
      ...(body === undefined ? {} : {body: JSON.stringify(body)}),
    });
  } catch {
    throw new Error("Cannot reach the app on this device. Check that the Python server is running, then try again.");
  }
  const type = response.headers.get("Content-Type") || "";
  if (!type.includes("application/json")) throw new Error("The server sent an unexpected response. Reload the app and try again.");
  const data = await response.json();
  if (!response.ok) throw new Error(data.error?.message || `Request failed (${response.status}). Try again.`);
  return data;
}
