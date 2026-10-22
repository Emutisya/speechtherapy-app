import {$, api, notify, run, element} from "./core.js";

export function initWriting() {
  $("writing-form").addEventListener("submit", run(async () => {
    const text = $("writing-text").value;
    const data = await api("/writing/review", "POST", {text, practice_words: $("practice-words").value});
    const result = $("writing-result");
    result.replaceChildren();
    // Python offsets count Unicode code points; JavaScript slices UTF-16 by default.
    const characters = Array.from(text);
    let cursor = 0;
    for (const match of data.matches) {
      result.append(document.createTextNode(characters.slice(cursor, match.start).join("")));
      result.append(element("mark", characters.slice(match.start, match.end).join("")));
      cursor = match.end;
    }
    result.append(document.createTextNode(characters.slice(cursor).join("")));
    notify(`${data.matches.length} selected word occurrences highlighted.`);
  }));
}
