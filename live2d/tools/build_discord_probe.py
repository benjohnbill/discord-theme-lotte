import base64, json, io, os, os.path as _p, numpy as np
from PIL import Image
D = "/home/benjohnbill/dev/discord-theme-lotte/live2d"
# source dir + basename are overridable so we can probe a WIP export (e.g. rt6/lotte-good)
# without clobbering the convention model/ dir.  PROBE_SRC=<dir> PROBE_NAME=<basename>
SRC = os.environ.get("PROBE_SRC", f"{D}/model")
NAME = os.environ.get("PROBE_NAME", "lotte")

# 1. atlas 2048 -> 1024 PNG bytes (UVs are normalized, so downscale is safe; halves paste size)
atlas = Image.open(f"{SRC}/{NAME}.2048/texture_00.png").convert("RGBA").resize((1024,1024), Image.LANCZOS)
buf = io.BytesIO(); atlas.save(buf, "PNG", optimize=True); tex = buf.getvalue()
tex_b64 = base64.b64encode(tex).decode()
moc_b64 = base64.b64encode(open(f"{SRC}/{NAME}.moc3","rb").read()).decode()
# physics is optional (hair sway only; irrelevant to a blink check). Use SRC's if present, else
# the convention model/ one, else none -> the probe omits the Physics reference.
_phys = f"{SRC}/{NAME}.physics3.json"
if not _p.exists(_phys):
    _phys = f"{D}/model/lotte.physics3.json"
phys_b64 = base64.b64encode(open(_phys, "rb").read()).decode() if _p.exists(_phys) else ""
# Cubism 5 Core inlined (only cubism.live2d.com serves v5; Discord CSP blocks that origin but allows
# blob: scripts, so we load the core from an inlined blob). Cache to /tmp; download if absent.
import urllib.request
try:
    core_bytes = open("/tmp/core_official.js","rb").read()
except FileNotFoundError:
    core_bytes = urllib.request.urlopen("https://cubism.live2d.com/sdk-web/cubismcore/live2dcubismcore.min.js").read()
    open("/tmp/core_official.js","wb").write(core_bytes)
core_b64 = base64.b64encode(core_bytes).decode()
_m3 = f"{SRC}/{NAME}.model3.json"
groups = json.dumps(json.load(open(_m3)).get("Groups", []) if _p.exists(_m3) else [])

# ambient lavender sampled from version.png corner (so the halo fringe blends, no double-girl)
ver = np.asarray(Image.open(f"{D}/source/lotte-discord-version.png").convert("RGB"))
c = ver[0:int(ver.shape[0]*0.14), 0:int(ver.shape[1]*0.14)].reshape(-1,3).mean(axis=0)
lav = "#%02x%02x%02x" % tuple(int(x) for x in c)

TEMPLATE = r"""/* Lotte Live2D - REAL rig, one-time in-Discord visual check (DevTools console paste).
   Cubism 4 + the actual Lotte moc3/atlas(1024)/physics inlined as base64 -> blob URLs.
   CSP-safe: all 3 scripts from jsdelivr (Phase-0-proven origin); model assets via blob: (same-origin).
   RUN:  Discord -> Ctrl+Shift+I -> Console -> (type `allow pasting` + Enter if warned) -> paste this -> Enter.
   STOP: __lotteStop()    RESET: Ctrl+R
*/
(() => {
  // Discord CSP script-src allows: 'unsafe-inline' 'unsafe-eval' blob: cdn.jsdelivr.net (+others).
  // The Cubism-5 Core (needed for the v5 moc3) is only served by cubism.live2d.com, which CSP blocks
  // as a script origin -> so it is INLINED here as base64 and loaded via a blob: script (blob: IS
  // allowed). Zero external core origin, zero customCspRules edit. pixi + the cubism4 plugin come from
  // jsdelivr (allowed).
  const CDN_SCRIPTS = [
    "https://cdn.jsdelivr.net/npm/pixi.js@6.5.10/dist/browser/pixi.min.js",
    "https://cdn.jsdelivr.net/npm/pixi-live2d-display@0.4.0/dist/cubism4.min.js",
  ];
  const TAG = "[Lotte]", LAV = "__LAV__";
  const B64 = { core: "__CORE__", moc: "__MOC__", tex: "__TEX__", phys: "__PHYS__" };
  const GROUPS = __GROUPS__;
  if (window.__lotteStop) { try { window.__lotteStop(); } catch (e) {} }

  const bytes = (b) => { const s = atob(b), u = new Uint8Array(s.length); for (let i = 0; i < s.length; i++) u[i] = s.charCodeAt(i); return u; };
  const burl = (b, t) => URL.createObjectURL(new Blob([bytes(b)], { type: t }));
  const mocURL = burl(B64.moc, "application/octet-stream");
  const texURL = burl(B64.tex, "image/png");
  const physURL = B64.phys ? burl(B64.phys, "application/json") : null;

  const W = innerWidth, H = innerHeight, killed = [];
  const cspHits = [];
  const onCsp = (e) => { if (/jsdelivr|blob:|cubism|live2d/i.test((e.blockedURI || "") + (e.violatedDirective || ""))) { cspHits.push(e.blockedURI + " (" + e.violatedDirective + ")"); console.error(TAG, "CSP BLOCKED:", e.blockedURI, e.violatedDirective); } };
  document.addEventListener("securitypolicyviolation", onCsp);

  document.querySelectorAll("*").forEach((el) => {
    if (el.tagName === "CANVAS") return;
    const r = el.getBoundingClientRect();
    if (r.width > W * 0.6 && r.height > H * 0.6) {
      const bi = getComputedStyle(el).backgroundImage;
      if (bi && bi !== "none" && /url\(/.test(bi)) { el.style.setProperty("background-image", "none", "important"); killed.push(el); }
    }
  });
  const bgKill = document.createElement("style"); bgKill.id = "__lotteBgKill";
  bgKill.textContent = 'html,body,#app-mount,#app-mount>*,[class*="appMount"],[class^="app_"],[class*=" app_"],[class*="baseLayer"],[class^="base_"],[class*=" base_"],[class*="container_"]{background-color:transparent!important;background-image:none!important}';
  document.head.appendChild(bgKill);

  let container = null, onMove = null, app = null;
  window.__lotteStop = () => {
    document.removeEventListener("securitypolicyviolation", onCsp);
    if (onMove) removeEventListener("mousemove", onMove);
    if (app) { try { app.destroy(true); } catch (e) {} }
    if (container) container.remove();
    document.getElementById("__lotteBgKill")?.remove();
    killed.forEach((el) => el.style.removeProperty("background-image"));
    [mocURL, texURL, physURL].filter(Boolean).forEach((u) => URL.revokeObjectURL(u));
    container = null; onMove = null; app = null; console.log(TAG, "stopped + background restored");
  };

  const load = (src) => new Promise((res, rej) => { const s = document.createElement("script"); s.src = src; s.onload = res; s.onerror = () => rej(new Error("blocked/failed: " + src)); document.head.appendChild(s); });

  (async () => {
    try {
      container = document.createElement("div");
      Object.assign(container.style, { position: "fixed", inset: "0", zIndex: "0", pointerEvents: "none", overflow: "hidden", background: LAV });
      const canvas = document.createElement("canvas"); canvas.style.width = "100vw"; canvas.style.height = "100vh";
      container.appendChild(canvas); document.body.insertBefore(container, document.body.firstChild);

      // core first (inlined -> blob: script, CSP-allowed), then pixi + the cubism4 plugin from jsdelivr
      await load(burl(B64.core, "text/javascript"));
      if (!window.Live2DCubismCore) throw new Error("Live2DCubismCore missing after inline core load");
      for (const s of CDN_SCRIPTS) await load(s);
      const PIXI = window.PIXI;
      if (!(PIXI && PIXI.live2d && PIXI.live2d.Live2DModel)) throw new Error("pixi-live2d-display not present after load");

      const fileRefs = { Moc: mocURL, Textures: [texURL] };
      if (physURL) fileRefs.Physics = physURL;
      const json = { url: "./lotte.model3.json", Version: 3, FileReferences: fileRefs, Groups: GROUPS };
      // blob: URLs must NOT be re-resolved (the lib's resolver mangles "blob:http://..." -> "blob:http//..."),
      // so wrap in ModelSettings and override resolveURL to identity.
      let source = json;
      if (PIXI.live2d.Cubism4ModelSettings) {
        const ms = new PIXI.live2d.Cubism4ModelSettings(json);
        ms.resolveURL = (u) => u;
        source = ms;
      }
      app = new PIXI.Application({ view: canvas, resizeTo: window, backgroundAlpha: 0, antialias: true, autoStart: true });
      const model = await PIXI.live2d.Live2DModel.from(source);
      app.stage.addChild(model);
      const im = model.internalModel;
      // Phase A - head-lean gaze: remap focus() so the cursor drives a gentle, clamped
      // head/body lean (NOT the iris). The lib default is eye x1 / AngleX/Y x30 /
      // AngleZ(cross) x30 / Body x10 -- reads "too large" live and cuts the iris on a
      // flat source. eye weight 0 = no iris cut (ADR-0001). FocusController spring still
      // supplies temporal damping. Gains are the Phase A tuning levers.
      const GAZE = { eye: 0, xy: 8, z: 6, body: 5 };
      im.updateFocus = function () {
        const f = this.focusController, cm = this.coreModel;
        cm.addParameterValueById("ParamEyeBallX", f.x * GAZE.eye);
        cm.addParameterValueById("ParamEyeBallY", f.y * GAZE.eye);
        cm.addParameterValueById("ParamAngleX", f.x * GAZE.xy);
        cm.addParameterValueById("ParamAngleY", f.y * GAZE.xy);
        cm.addParameterValueById("ParamAngleZ", f.x * f.y * -GAZE.z);
        cm.addParameterValueById("ParamBodyAngleX", f.x * GAZE.body);
      };
      const cw = im.originalWidth || model.width, ch = im.originalHeight || model.height; // intrinsic canvas (stable)
      const fit = () => { const s = Math.min(innerWidth / cw, innerHeight / ch) * 0.92; model.scale.set(s); model.anchor.set(0.5, 0.5); model.position.set(innerWidth / 2, innerHeight / 2); };
      let n = 0; const refit = () => { fit(); if (++n < 20) requestAnimationFrame(refit); }; refit();
      addEventListener("resize", fit);
      onMove = (e) => model.focus(e.clientX, e.clientY); addEventListener("mousemove", onMove);

      // --- CD-4 blink verification driver ---------------------------------------------------
      // We drive the eyes ourselves (not the auto-blink group) so the state is controllable for
      // a clean screenshot. Default: auto-cycle open<->closed (square wave) so the blink is
      // visible. Freeze for inspection from the console:
      //   __lotteEyes(0)  -> hold CLOSED   (screenshot this for the iris/line/warp check)
      //   __lotteEyes(1)  -> hold OPEN
      //   __lotteEyes()   -> resume auto-cycle
      try { im.eyeBlink = null; } catch (e) {}
      let eyeMode = "cycle", t0 = performance.now();
      window.__lotteEyes = (v) => {
        eyeMode = (v === 0 || v === 1) ? v : "cycle";
        console.log(TAG, "eyes:", eyeMode === "cycle" ? "AUTO-CYCLE" : (v ? "OPEN(1)" : "CLOSED(0)"));
      };
      app.ticker.add(() => {
        const cm = im.coreModel; let v;
        if (eyeMode === "cycle") { v = (((performance.now() - t0) / 1600) % 1) < 0.5 ? 1 : 0; }
        else { v = eyeMode; }
        cm.setParameterValueById("ParamEyeLOpen", v);
        cm.setParameterValueById("ParamEyeROpen", v);
      });

      console.log(TAG, "LOTTE_PROBE_OK rendered. Mouse = head-lean. Eyes auto-blink.");
      console.log(TAG, "FREEZE for screenshot:  __lotteEyes(0)=closed  __lotteEyes(1)=open  __lotteEyes()=auto");
      console.log(TAG, "Stop with __lotteStop()  | CSP:", cspHits.length ? cspHits : "no blocks");
    } catch (e) { console.error(TAG, "LOTTE_PROBE_FAIL", e && e.message ? e.message : e); }
  })();
})();
"""

snippet = (TEMPLATE.replace("__LAV__", lav).replace("__GROUPS__", groups).replace("__CORE__", core_b64)
           .replace("__MOC__", moc_b64).replace("__PHYS__", phys_b64).replace("__TEX__", tex_b64))
open(f"{D}/discord-lotte-probe.js", "w").write(snippet)
# pre-test page (blank body + inline snippet) for SwiftShader verification
open(f"{D}/_pretest-lotte.html", "w").write(
    "<!doctype html><html><head><meta charset=utf-8><style>html,body{margin:0;height:100%;overflow:hidden}"
    "#st{position:fixed;top:4px;left:6px;color:#0f0;font:12px monospace;z-index:9;text-shadow:0 0 3px #000}</style>"
    "</head><body><div id=st>pretest</div><script>\n" + snippet + "\n</script></body></html>")

print(f"lavender bg = {lav}")
print(f"atlas1024 png = {len(tex)//1024} KB  (b64 {len(tex_b64)//1024} KB)")
print(f"moc3 b64 = {len(moc_b64)//1024} KB | physics b64 = {len(phys_b64)//1024} KB")
print(f"SNIPPET total = {len(snippet)//1024} KB  -> {D}/discord-lotte-probe.js")
print(f"pretest -> {D}/_pretest-lotte.html")
