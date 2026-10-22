import {$, state, notify} from "./core.js";

let voices = [];
const synth = window.speechSynthesis;

export function stopSpeech() {
  if (synth) synth.cancel();
}

export function refreshVoices() {
  voices = synth ? synth.getVoices().filter((voice) => voice.localService && /^en(?:-|$)/i.test(voice.lang)) : [];
  const select = $("voice-select");
  const previous = select.value;
  select.replaceChildren();
  if (!voices.length) select.add(new Option("No on-device English voice available", ""));
  for (const voice of voices) select.add(new Option(`${voice.name} (${voice.lang})`, voice.voiceURI));
  if (voices.some((voice) => voice.voiceURI === previous)) select.value = previous;
  select.disabled = !voices.length;
  $("speech-status").textContent = !state.preferences.speech_enabled
    ? "Audio is off. A caregiver can enable an available on-device voice."
    : voices.length ? "Audio is ready. It plays only when you choose Say message or Hear a model."
      : "No on-device English voice is available. The board still works without audio. Check your device's installed voices.";
}

export function speak(text) {
  if (!state.preferences.speech_enabled) { notify("Audio is off. You can still show your message or ask a caregiver to enable audio."); return; }
  const voice = voices.find((item) => item.voiceURI === $("voice-select").value);
  if (!voice || !synth) { notify("No on-device voice is available. Show or copy your message instead."); return; }
  stopSpeech();
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.voice = voice;
  utterance.lang = voice.lang;
  utterance.rate = state.preferences.speech_rate === "gentle" ? 0.8 : 1;
  utterance.onerror = (event) => {
    if (!["canceled", "interrupted"].includes(event.error)) notify("Audio could not play. You can show your message instead. Check your device's voice settings.");
  };
  synth.speak(utterance);
}

export function initSpeech() {
  refreshVoices();
  if (synth) synth.addEventListener("voiceschanged", refreshVoices);
  document.addEventListener("visibilitychange", () => { if (document.hidden) stopSpeech(); });
}
