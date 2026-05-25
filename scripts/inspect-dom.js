// Manual Discord DevTools console helper.
// Paste this script into the Console, then replace placeholder metadata before
// committing the resulting JSON snapshot.
const selector = "div,section,main,aside,nav,button";

const result = Array.from(document.querySelectorAll(selector))
  .map((el) => {
    const r = el.getBoundingClientRect();
    const s = getComputedStyle(el);
    return {
      tag: el.tagName,
      className: String(el.className),
      rect: [Math.round(r.left), Math.round(r.top), Math.round(r.width), Math.round(r.height)].join(" "),
      background: s.backgroundColor,
      border: s.borderColor,
      text: el.textContent.trim().replace(/\s+/g, " ").slice(0, 120)
    };
  })
  .filter((x) => {
    const [, , width, height] = x.rect.split(" ").map(Number);
    return width > 80 && height > 40;
  });

console.log(JSON.stringify({
  schemaVersion: 1,
  capturedAt: new Date().toISOString(),
  discordBuild: "unknown",
  vencordVersion: "unknown",
  themeVersion: "0.1.0",
  os: "Windows via Discord desktop",
  zoom: "unknown",
  screen: "replace-with-screen-id",
  routeHint: "replace-with-current-route",
  viewport: `${window.innerWidth}x${window.innerHeight}`,
  sourceScreenshot: "replace-with-screenshot-path",
  notes: "Captured from Discord DevTools console.",
  elements: result
}, null, 2));
