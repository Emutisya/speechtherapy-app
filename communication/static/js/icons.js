const shapes = {
  check: [["path", {d: "m5 12 4 4L19 6"}]],
  stop: [["path", {d: "M8 3h8l5 5v8l-5 5H8l-5-5V8Z"}], ["path", {d: "M8 12h8"}]],
  hand: [["path", {d: "M8 13V5a1.5 1.5 0 0 1 3 0v7-9a1.5 1.5 0 0 1 3 0v9-7a1.5 1.5 0 0 1 3 0v8-4a1.5 1.5 0 0 1 3 0v6c0 5-3 7-7 7-3 0-4-2-5-4l-4-5a1.5 1.5 0 0 1 2-2Z"}]],
  pause: [["path", {d: "M8 5v14M16 5v14"}]],
  plus: [["path", {d: "M12 4v16M4 12h16"}]],
  drop: [["path", {d: "M12 2S5 10 5 15a7 7 0 0 0 14 0c0-5-7-13-7-13Z"}]],
  bowl: [["path", {d: "M3 10h18c0 7-4 10-9 10S3 17 3 10ZM8 3v3M12 2v4M16 3v3"}]],
  home: [["path", {d: "m3 11 9-8 9 8M5 10v11h14V10M10 21v-7h4v7"}]],
  moon: [["path", {d: "M20 15A9 9 0 0 1 9 3a9 9 0 1 0 11 12Z"}]],
  heart: [["path", {d: "M12 21 3 12C-2 6 6-1 12 6c6-7 14 0 9 6Z"}]],
  sun: [["circle", {cx: "12", cy: "12", r: "4"}], ["path", {d: "M12 1v3M12 20v3M1 12h3M20 12h3M4 4l2 2M18 18l2 2M20 4l-2 2M6 18l-2 2"}]],
  question: [["circle", {cx: "12", cy: "12", r: "9"}], ["path", {d: "M9 8a3 3 0 1 1 4 3c-1 0-1 1-1 3M12 17h.01"}]],
  play: [["path", {d: "m8 4 12 8-12 8Z"}]],
  book: [["path", {d: "M12 5C8 2 4 3 2 4v16c4-2 7-1 10 1 3-2 6-3 10-1V4c-4-2-7-1-10 1ZM12 5v16"}]],
  music: [["path", {d: "M9 18V5l12-2v13M9 8l12-2"}], ["ellipse", {cx: "6", cy: "18", rx: "3", ry: "2"}], ["ellipse", {cx: "18", cy: "16", rx: "3", ry: "2"}]],
};

export function icon(name) {
  const ns = "http://www.w3.org/2000/svg";
  const svg = document.createElementNS(ns, "svg");
  for (const [key, value] of Object.entries({viewBox: "0 0 24 24", fill: "none", stroke: "currentColor", "stroke-width": "1.5", "stroke-linecap": "round", "stroke-linejoin": "round", "aria-hidden": "true", focusable: "false"})) svg.setAttribute(key, value);
  for (const [tag, attributes] of shapes[name] || shapes.question) {
    const node = document.createElementNS(ns, tag);
    for (const [key, value] of Object.entries(attributes)) node.setAttribute(key, value);
    svg.append(node);
  }
  return svg;
}
