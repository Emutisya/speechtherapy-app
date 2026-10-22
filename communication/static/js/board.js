import {$, state, element, notify, run} from "./core.js";
import {icon} from "./icons.js";
import {speak} from "./speech.js";

const categories = {all: "All cards", essentials: "Essentials", needs: "My needs", feelings: "My feelings", activities: "Things to do"};
let category = "all";
let page = 0;
const pinned = new Set(["no", "stop", "help", "break"]);

export function cardButton(card, action) {
  const button = element("button", undefined, `communication-card${card.category === "essentials" ? " essential" : ""}`);
  button.type = "button";
  button.append(icon(card.icon), element("span", card.label));
  button.addEventListener("click", () => action(card));
  return button;
}

export function addCard(card) {
  if (state.message.length >= 12) { notify("Your message has 12 cards. Remove a card or clear the message to add another."); return; }
  state.message.push(card);
  renderMessage();
  notify(`Added ${card.label}.`);
}

export function renderMessage() {
  const strip = $("message-strip");
  strip.replaceChildren();
  if (!state.message.length) strip.append(element("p", "Your message starts here."));
  state.message.forEach((card, index) => {
    const button = element("button", card.label, "message-chip");
    button.setAttribute("aria-label", `Remove ${card.label}, message card ${index + 1}`);
    button.addEventListener("click", () => {
      state.message.splice(index, 1);
      renderMessage();
      const remaining = $("message-strip").querySelectorAll("button");
      (remaining[Math.min(index, remaining.length - 1)] || $("clear-message")).focus();
      notify(`Removed ${card.label}.`);
    });
    strip.append(button);
  });
  $("message-count").textContent = `${state.message.length} of 12 cards`;
  for (const id of ["say-message", "copy-message", "undo-message", "clear-message"]) $(id).disabled = state.message.length === 0;
}

export function renderBoard(printAll = false) {
  const cards = $("board-cards");
  cards.replaceChildren();
  let available = state.cards.filter((card) => category === "all" || card.category === category || pinned.has(card.id));
  if (state.preferences.reduced_choices && !printAll) {
    const fixed = available.filter((card) => pinned.has(card.id));
    const rest = available.filter((card) => !pinned.has(card.id));
    const pages = Math.max(1, Math.ceil(rest.length / 2));
    page = Math.min(page, pages - 1);
    available = [...fixed, ...rest.slice(page * 2, page * 2 + 2)];
    for (const card of available) cards.append(cardButton(card, addCard));
    const pagination = element("div", undefined, "button-row");
    const previous = element("button", "Previous cards");
    const next = element("button", "Next cards");
    previous.disabled = page === 0;
    next.disabled = page === pages - 1;
    previous.addEventListener("click", () => { page--; renderBoard(); $("board-cards").querySelector("button")?.focus(); });
    next.addEventListener("click", () => { page++; renderBoard(); $("board-cards").querySelector("button")?.focus(); });
    pagination.append(previous, element("span", `Page ${page + 1} of ${pages}`, "small"), next);
    cards.append(pagination);
  } else {
    for (const card of (printAll ? state.cards : available)) cards.append(cardButton(card, addCard));
  }
}

export function initBoard() {
  for (const [key, label] of Object.entries(categories)) {
    const button = element("button", label);
    button.setAttribute("aria-pressed", String(key === category));
    button.addEventListener("click", () => {
      category = key; page = 0;
      for (const item of $("categories").children) item.setAttribute("aria-pressed", String(item === button));
      renderBoard();
    });
    $("categories").append(button);
  }
  $("say-message").addEventListener("click", () => speak(state.message.map((card) => card.label).join(" ")));
  $("copy-message").addEventListener("click", run(async () => {
    if (!navigator.clipboard) throw new Error("Clipboard access is unavailable. You can show the message on screen instead.");
    try { await navigator.clipboard.writeText(state.message.map((card) => card.label).join(" ")); }
    catch { throw new Error("Your browser blocked copying. Allow clipboard access or show the message on screen."); }
    notify("Message copied. Pasted text may be visible to other apps on this device.");
  }));
  $("undo-message").addEventListener("click", () => { state.message.pop(); renderMessage(); notify("Last card removed."); });
  $("clear-message").addEventListener("click", () => { state.message = []; renderMessage(); notify("Message cleared."); });
  $("print-board").addEventListener("click", () => window.print());
  window.addEventListener("beforeprint", () => renderBoard(true));
  window.addEventListener("afterprint", () => renderBoard());
  renderBoard(); renderMessage();
}
