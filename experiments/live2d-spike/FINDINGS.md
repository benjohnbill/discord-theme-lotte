# Live2D Spike — FINDINGS

Living record of Phase 0 feasibility results. Three gates: (1) Vencord custom-plugin
capability, (runtime) standalone Live2D render + cursor tracking, (3) in-Discord
injection + CSP. Ends with a go/no-go in the Decision section.

Working environment: Discord desktop runs on Windows; this repo and the spike run in WSL2.
The Vencord user-data dir is at `/mnt/c/Users/benjohnbill/AppData/Roaming/Vencord/`.

---

## Gate 1 — Vencord plugin capability (Task 1)

**Verdict: STOCK installer build. Custom JS userplugins are NOT loadable as-is.**

Evidence (read-only investigation, no Discord changes):

- **User-data dir confirmed.** `AppData/Roaming/Vencord/` contains `themes/`, `settings/`, `dist/`.
  `themes/NewKemonoFriends.theme.css` is present — this is the theme sync target, confirming
  Vencord is installed and active.
- **No source clone found.** Searched for a `userplugins/` directory across the likely Windows
  dev locations (`~`, `~/dev`, `~/Documents`, `~/source`, maxdepth 4) and the WSL home (maxdepth 5).
  **Zero results.** The only directory named `Vencord` anywhere is the AppData user-data dir
  (the stock installer's data dir), not a Git source checkout.
- **settings.json** lists only the canonical Vencord built-in plugins (CommandsAPI,
  MessageAccessoriesAPI, UserSettingsAPI, CrashHandler enabled; the rest of the standard catalog
  disabled). No custom userplugin entries.

**Conclusion:** A stock Vencord install loads themes (CSS) but cannot load custom JS plugins.
A *persistent production* Live2D background therefore needs a **Vencord source/dev build** +
re-inject — the real Phase 2 delivery cost. (The Task 3 feasibility proof itself was done WITHOUT
a dev build, via a DevTools console probe — see the Task 3 section below.)

### Bonus finding — custom CSP is already in use (relevant to Gate 3 / CSP)

`settings/native-settings.json` contains:

```json
"customCspRules": {
  "images5.alphacoders.com": ["connect-src", "img-src", "style-src", "font-src"]
}
```

The user already whitelists a remote domain via Vencord's `customCspRules` mechanism (almost
certainly to let the current theme load its background image). **Implication for Task 3:** Discord's
CSP can be relaxed per-domain through `native-settings.json` rather than only by bundling the runtime
into the plugin. This mechanism existed as a fallback in case Discord's CSP blocked remote scripts.
**Task 3 later showed it is not needed at all** — Discord loaded the `cdn.jsdelivr.net` scripts with
zero CSP violations (see the Task 3 section).

### Dev-build path (recorded for Task 3 — NOT executed in this session)

Run on the side that owns the Discord install — Windows here:

```text
git clone https://github.com/Vendicated/Vencord
cd Vencord && pnpm install --frozen-lockfile
mkdir -p src/userplugins
(place the plugin under src/userplugins/lotteLive2dSpike/)
pnpm build
pnpm inject     # patches the local Discord desktop install; pick the right branch
```

Maintenance cost: re-run `pnpm build` (and sometimes re-inject) after Discord/Vencord updates.

Cross-env caveat: building can be done in WSL, but `pnpm inject` must target the **Windows**
Discord install. If WSL-side inject cannot see the Windows Discord, run the build/inject on the
Windows side (Node + pnpm on Windows). Confirm which works during Task 3.

---

## Gate runtime — standalone Live2D (Task 2)

**Verdict: PASS.** `pixi-live2d-display` renders the Shizuku sample model and tracks a
target point via `model.focus(x, y)` — the exact call the Task 3 probe (and any Phase 2 plugin) uses.

Evidence (committed):
- `0b-standalone.png` — `index.html` rendered: Shizuku visible, status line reads
  `rendered. move the mouse — eyes/head should follow.` (close framing is a cosmetic
  fit-timing artifact, not a render failure).
- `0b-track-tl.png` / `0b-track-br.png` — gaze pinned to opposite corners
  (`focus(0,0)` vs `focus(innerW, innerH)`). The head rotation and eye direction
  visibly differ between the two → focus-driven cursor tracking confirmed.

### Three corrections vs the plan's literal code (all were authorized verify-and-record steps)

1. **Cubism 2 core URL moved.** `https://cubism.live2d.com/webgl/live2d.min.js` now returns
   **404**. Replaced with the canonical community mirror the pixi-live2d-display docs point to:
   `https://cdn.jsdelivr.net/gh/dylanNew/live2d/webgl/Live2D/lib/live2d.min.js` (200, exposes `window.Live2D`).
2. **Wrong pixi-live2d-display bundle.** The combined `dist/index.min.js` throws at load:
   `Uncaught Error: Could not find Cubism 4 runtime. This plugin requires live2dcubismcore.js to be loaded.`
   It demands the Cubism **4** runtime even for a Cubism **2.1** model, which leaves
   `PIXI.live2d` as an empty namespace (so `Live2DModel` is undefined). Fix: load the
   **Cubism-2-only** bundle `dist/cubism2.min.js` (no Cubism 4 dependency; still exposes
   `PIXI.live2d.Live2DModel`). Version pinned to `@0.4.0` (targets PIXI v6).
3. **Deterministic loading + re-fit.** `index.html` now loads the three scripts sequentially
   (awaited `loadScript` loop, mirroring the Task 3 plugin) and re-fits across the first frames
   (model bounds settle only after textures load).

Final working runtime triplet (used verbatim by the Task 3 probe; reuse in any Phase 2 plugin):
```
https://cdn.jsdelivr.net/gh/dylanNew/live2d/webgl/Live2D/lib/live2d.min.js   # Cubism 2 core
https://cdn.jsdelivr.net/npm/pixi.js@6.5.10/dist/browser/pixi.min.js          # PIXI v6
https://cdn.jsdelivr.net/npm/pixi-live2d-display@0.4.0/dist/cubism2.min.js    # NOT index.min.js
```

### Environment-alignment caveat (important — do not misread as a NO-GO signal)

The project's default headless browser (`bh-chrome` / WSLg Chrome) has **no WebGL at all**
(`webgl`, `webgl2`, `experimental-webgl` all return null; the service launches plain
`google-chrome` with no GL flags, and WSLg's GPU passthrough yields no usable GL context).
PIXI requires WebGL, so on that browser the spike fails with
`WebGL unsupported in this browser` — a **false negative** that says nothing about the real target.

To get a valid render, the spike was run in a throwaway headless Chrome with **software WebGL**
(`--enable-unsafe-swiftshader --use-gl=angle --use-angle=swiftshader`). All three screenshots
above were produced this way.

Implication for Task 3: Discord's Electron client ships a full Chromium GPU stack **with** WebGL,
so the WebGL gate is expected to pass there. SwiftShader proves the code path; it does **not**
measure GPU performance (not a Phase 0 goal). Any future headless verification of this rig must
use SwiftShader flags or the real client — never plain `bh-chrome`.

---

## Gate 1 proof — in Discord (Task 3)

**DONE — GREEN, via a lighter method than planned (user-run DevTools console probe, 2026-05-31).**

Recon found the Windows side has **no Node/pnpm/git**, so a full Vencord dev build was a heavy
detour. But the dev build is only a *delivery* mechanism; the actual feasibility unknowns (CSP +
Electron render) are answerable by pasting the same injection logic into Discord's DevTools console
— same renderer, same CSP, same scripts, same `model.focus(x,y)`. So Task 3 was run that way: no
Discord patching, fully reversible (Ctrl+R or `__lotteSpikeStop()`).

Probe: `experiments/live2d-spike/discord-console-probe.js` (a copy was dropped on the Windows
Desktop for easy copy-paste). Results, confirmed in the real Discord client:
- **CSP: no blocks.** All three CDN scripts (`cdn.jsdelivr.net`, incl. the `dylanNew` Cubism 2 core)
  loaded with zero `securitypolicyviolation` events. **No `customCspRules`, no bundling required.**
- **WebGL:** console printed `PixiJS 6.5.10 - ✰ WebGL 2 ✰` — Discord's Electron has full GPU WebGL
  (unlike the headless bh-chrome; see the environment caveat above).
- **Render + cursor tracking: confirmed visually.** Shizuku renders full-window behind Discord's
  translucent message panels and follows the cursor exactly like the standalone page (user-confirmed:
  "마우스 따라가는 것이 기존 index.html 처럼 잘 적용").
- **Background layering — key Phase 2 finding:** the canvas must occupy the theme's background slot,
  not `document.body`'s back. This theme paints its background image on a hashed Discord container
  (`.app__<hash>`, observed `.app__160d8`) over an opaque base background-color. Two earlier probe
  versions (canvas at body-back; killing only `body`/`#app-mount` bg) stayed hidden. The working v4
  auto-detects large background-IMAGE elements by size (selector-agnostic — the hash is volatile) and
  also clears the structural base background-COLORS, letting the back canvas show through. A
  production plugin must do this detection dynamically, never hardcode the hash.

Conclusion: every hard Discord unknown is GREEN. What remains is production *delivery* (a persistent
always-on injector) and clean theme-layer integration — Phase 2, not feasibility.

---

## Decision (Task 4)

### The three gates

1. **Does the runtime render + track the cursor?** (Task 2) — **YES.** `pixi-live2d-display@0.4.0`
   (`cubism2.min.js`) + PIXI v6 + the `dylanNew` Cubism 2 core mirror renders the Shizuku sample
   and follows a target via `model.focus(x, y)`. Proven with software WebGL (SwiftShader);
   evidence committed.
2. **Can a custom plugin run in this Vencord, and at what cost?** (Task 1) — **STOCK install**, no
   source clone. Feasibility was proven via a DevTools console probe (Task 3) instead of a dev build.
   A Vencord userplugin is only needed for *persistent* production delivery; that is where the
   dev-build + re-inject-on-update cost applies (Phase 2).
3. **Does Discord's CSP allow the remote scripts, or is bundling required?** (Task 3) — **YES, allowed.**
   The console probe loaded all three CDN scripts with zero CSP violations. No `customCspRules`, no
   bundling required. Discord's Electron also reported WebGL 2, and the model rendered + tracked.

### Recommendation: **GO**

Every hard feasibility unknown is now GREEN, confirmed in the real Discord client: CSP allows the
remote runtime (no bundling, no `customCspRules`), Electron has WebGL 2, and the Live2D character
renders full-window behind the translucent UI and tracks the cursor (user-confirmed). The one
remaining cost is **production delivery**: a persistent, always-on background needs a JS-injection
host (a Vencord userplugin → a self-built dev Vencord, re-built on updates), because themes/QuickCSS
cannot run JS. That dev-build cost is a **Phase 2 productionization** decision, not a feasibility
blocker — and it is lighter than feared (CSP needs no special handling; the runtime loads from CDN
as-is).

**Why Phase 1 is fully de-risked:** the proven rig is one portable artifact reused across *all*
target surfaces. Discord is now confirmed GREEN (Task 3); the desktop wallpaper (Lively) and mobile
live-wallpaper surfaces have no plugin/CSP constraints at all, so the Task 2 PASS already guarantees
the rig works there too. Every target surface is therefore green or unconstrained — rigging the real
Lotte (Phase 1) carries no remaining feasibility risk.

### Next-step options for the user (no work started without sign-off)

- **A — (DONE) Gate 1 is closed.** Discord feasibility is confirmed in the real client; proceed on
  that basis.
- **B — Proceed to Phase 1 rigging (recommended next):** rig the real Lotte against the proven
  plumbing. Safe because the rig is portable to every surface (Discord proven; wallpaper/mobile
  unconstrained).
- **C — Phase 2 production delivery (later):** turn the console probe into a Vencord userplugin
  (requires Node+git on Windows, a dev Vencord, dynamic `.app__<hash>` background-slot takeover).
  Independent of Phase 1; can be scheduled whenever the always-on version is wanted.
