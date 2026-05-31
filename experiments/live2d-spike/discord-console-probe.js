// Lotte Live2D — Discord feasibility probe (DevTools console paste).
//
// Purpose: answer Phase 0 Gate 1's real unknowns WITHOUT standing up a Vencord dev build:
//   (1) Does Discord's CSP allow loading the remote CDN scripts?  → proven: YES, no blocks.
//   (2) Does the Live2D scene render in Electron, full-window, behind the UI, tracking the cursor?
//       → proven: YES (WebGL 2; Shizuku renders as background; gaze follows the cursor).
//
// HOW TO RUN: Discord → Ctrl+Shift+I → Console → (if warned, type  allow pasting  + Enter)
//   → paste this whole file → Enter.
// CLEANUP: run  __lotteSpikeStop()  in the console, or Ctrl+R to reload Discord.
//
// This is the v4 that worked: it also takes over the theme's background slot so the character is
// visible. Discord paints its themed background image on a hashed container (e.g. `.app__<hash>`),
// which sits on top of a body-level canvas — so the probe auto-detects large background-image
// elements (selector-agnostic, since the hash is volatile) and clears the structural base
// background colors, letting the back canvas show through the still-translucent message panels.
// This mirrors what a production Vencord userplugin would do; the console is just the delivery here.

(() => {
  const SCRIPTS = [
    "https://cdn.jsdelivr.net/gh/dylanNew/live2d/webgl/Live2D/lib/live2d.min.js", // Cubism 2 core (mirror; original 404s)
    "https://cdn.jsdelivr.net/npm/pixi.js@6.5.10/dist/browser/pixi.min.js",        // PIXI v6
    "https://cdn.jsdelivr.net/npm/pixi-live2d-display@0.4.0/dist/cubism2.min.js",  // Cubism-2-only (NOT index.min.js)
  ];
  const MODEL = "https://cdn.jsdelivr.net/gh/guansss/pixi-live2d-display/test/assets/shizuku/shizuku.model.json";
  const TAG = "[LotteSpike]";

  if (window.__lotteSpikeStop) { try { window.__lotteSpikeStop(); } catch (e) {} }

  const cspHits = [];
  const onCsp = (e) => {
    if (/jsdelivr|cubism|live2d/i.test(e.blockedURI || "")) {
      cspHits.push(e.blockedURI + " (" + e.violatedDirective + ")");
      console.error(TAG, "CSP BLOCKED:", e.blockedURI, e.violatedDirective);
    }
  };
  document.addEventListener("securitypolicyviolation", onCsp);

  // Detect & disable large background-IMAGE layers (theme background) — selector-agnostic.
  const W = window.innerWidth, H = window.innerHeight;
  const killedEls = [];
  const report = [];
  document.querySelectorAll("*").forEach((el) => {
    if (el.tagName === "CANVAS") return;
    const r = el.getBoundingClientRect();
    if (!(r.width > W * 0.6 && r.height > H * 0.6)) return;
    const bi = getComputedStyle(el).backgroundImage;
    if (bi && bi !== "none" && /url\(/.test(bi)) {
      el.dataset.lotteKilled = "1";
      el.style.setProperty("background-image", "none", "important");
      killedEls.push(el);
      report.push(el.id ? "#" + el.id : (el.className && typeof el.className === "string" ? "." + el.className.trim().split(/\s+/)[0] : el.tagName));
    }
  });

  // Clear base background-images/colors on the structural app layers so the back canvas shows.
  const bgKill = document.createElement("style");
  bgKill.id = "__lotteBgKill";
  bgKill.textContent = `
    html, body, #app-mount, #app-mount > *,
    [class*="appMount"], [class*="appAsidePanelWrapper"],
    [class^="app_"], [class*=" app_"], [class*="appDevToolsWrapper"],
    [class*="layers_"], [class*="layer_"],
    [class*="baseLayer"], [class^="base_"], [class*=" base_"], [class*="container_"] {
      background-color: transparent !important; background-image: none !important;
    }
    body::before, body::after, #app-mount::before, #app-mount::after,
    #app-mount *::before, #app-mount *::after { background-image: none !important; }
  `;
  document.head.appendChild(bgKill);
  console.log(TAG, "bg-image layers disabled:", report.length ? report : "(none matched size>60%)");

  let container = null, onMove = null;
  window.__lotteSpikeStop = () => {
    document.removeEventListener("securitypolicyviolation", onCsp);
    if (onMove) document.removeEventListener("mousemove", onMove);
    if (container) container.remove();
    document.getElementById("__lotteBgKill")?.remove();
    killedEls.forEach((el) => { el.style.removeProperty("background-image"); delete el.dataset.lotteKilled; });
    container = null; onMove = null;
    console.log(TAG, "stopped + background restored");
  };

  const loadScript = (src) => new Promise((resolve, reject) => {
    const s = document.createElement("script");
    s.src = src;
    s.onload = () => { console.log(TAG, "loaded", src); resolve(); };
    s.onerror = () => reject(new Error("failed/blocked: " + src));
    document.head.appendChild(s);
  });

  (async () => {
    try {
      container = document.createElement("div");
      Object.assign(container.style, {
        position: "fixed", inset: "0", zIndex: "0", pointerEvents: "none",
        overflow: "hidden", background: "#1e1f3a",
      });
      const canvas = document.createElement("canvas");
      canvas.style.width = "100vw"; canvas.style.height = "100vh";
      container.appendChild(canvas);
      document.body.insertBefore(container, document.body.firstChild);

      for (const src of SCRIPTS) await loadScript(src);

      const PIXI = window.PIXI;
      if (!(PIXI && PIXI.live2d && PIXI.live2d.Live2DModel)) {
        throw new Error("PIXI.live2d.Live2DModel missing after load");
      }
      const app = new PIXI.Application({ view: canvas, resizeTo: window, backgroundAlpha: 0, autoStart: true });
      const model = await PIXI.live2d.Live2DModel.from(MODEL);
      app.stage.addChild(model);
      let frames = 0;
      const fit = () => {
        const sc = Math.min(window.innerWidth / model.width, window.innerHeight / model.height) * 0.9;
        model.scale.set(sc); model.anchor.set(0.5, 0.5);
        model.position.set(window.innerWidth / 2, window.innerHeight / 2);
      };
      const refit = () => { fit(); if (++frames < 30) requestAnimationFrame(refit); };
      refit();
      window.addEventListener("resize", fit);
      onMove = (e) => model.focus(e.clientX, e.clientY);
      document.addEventListener("mousemove", onMove);

      console.log(TAG, "✅ RENDERED as background. Move the mouse — eyes/head should follow.");
      console.log(TAG, "CSP verdict:", cspHits.length ? ("BLOCKED → " + cspHits.join("; ")) : "no CSP blocks on our domains");
      console.log(TAG, "Restore:  __lotteSpikeStop()");
    } catch (e) {
      console.error(TAG, "❌ FAILED:", e && e.message ? e.message : e);
    }
  })();
})();
