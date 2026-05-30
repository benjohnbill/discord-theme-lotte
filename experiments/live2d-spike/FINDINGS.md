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
Running the throwaway `LotteLive2dSpike` userplugin (Task 3) requires standing up a **Vencord
source/dev build** and re-injecting it into the Windows Discord install. This is the real cost
that gates Task 3.

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
into the plugin. Loading remote `<script>` tags additionally needs a `script-src` entry for the CDN
domains (`cdn.jsdelivr.net`, `cubism.live2d.com`). This is a lighter mitigation path than full
bundling — to be confirmed in Task 3 if/when we proceed.

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
target point via `model.focus(x, y)` — the exact call the Task 3 plugin uses.

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

Final working runtime triplet (use this verbatim in Task 3):
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

**DEFERRED (not run; user decision, 2026-05-31).** Task 3 patches the real Discord desktop
client (`pnpm inject`), which is an invasive Tier-3 action. At the Task-2 hard stop the user
chose to record a go/no-go from current evidence rather than stand up a throwaway Vencord dev
build this session. The in-Discord render + CSP proof is therefore **deferred, not abandoned**.

What remains to close this gate later:
- Stand up a Vencord source build (steps recorded in the Gate 1 dev-build path above), build on
  the side that owns the Discord install, run `pnpm inject`.
- Create the userplugin from `vencord-plugin/lotteLive2dSpike/index.tsx`, **using the corrected
  runtime triplet from the Task 2 section** (`cubism2.min.js`, not `index.min.js`; the `dylanNew`
  Cubism 2 core mirror). The plugin code as drafted in the plan would fail identically to the
  standalone bug we already fixed.
- Watch the DevTools console for a CSP `Refused to load the script …` error. If it appears,
  first try relaxing it via `native-settings.json` `customCspRules` (already proven to work for
  this install) with a `script-src` entry for `cdn.jsdelivr.net`; bundling the runtime into the
  plugin is the heavier fallback.

---

## Decision (Task 4)

### The three gates

1. **Does the runtime render + track the cursor?** (Task 2) — **YES.** `pixi-live2d-display@0.4.0`
   (`cubism2.min.js`) + PIXI v6 + the `dylanNew` Cubism 2 core mirror renders the Shizuku sample
   and follows a target via `model.focus(x, y)`. Proven with software WebGL (SwiftShader);
   evidence committed.
2. **Can a custom plugin run in this Vencord, and at what cost?** (Task 1) — **NOT as-is.** This is
   a STOCK install with no source clone. Custom plugins require standing up a Vencord **source/dev
   build** and `pnpm inject`-ing it into the Windows Discord, plus re-building after Discord/Vencord
   updates. The actual in-Discord run was **deferred** (Task 3 not executed).
3. **Does Discord's CSP allow the remote scripts, or is bundling required?** (Task 3) — **UNTESTED**
   (Task 3 deferred). Positive signal: this install already uses Vencord `customCspRules`
   (`native-settings.json`), so a per-domain `script-src` relaxation is a plausible lighter path
   than full bundling.

### Recommendation: **GO-WITH-COST**

The runtime half of the stack is proven. The Discord-injection half is technically expected to
work (Discord's Electron has real WebGL; Vencord supports custom plugins and custom CSP), but it
carries a **real, recurring cost**: a self-built Vencord that must be re-built/re-injected on
updates, set up across the WSL↔Windows boundary. That cost must be **explicitly accepted by the
user before Phase 1/2**.

**Important de-risking note:** the proven standalone rig is the portable artifact reused across
*all* target surfaces. The desktop wallpaper (Lively) and mobile live-wallpaper surfaces have **no
plugin/CSP constraints** — the Task 2 PASS already guarantees the rig works there. Discord is the
*only* surface gated on the still-unverified injection. So rigging the real Lotte (Phase 1) is
low-risk regardless of the Discord-injection outcome: if Discord injection later proves
unacceptable, the same rig still ships on wallpaper/mobile (the plan's documented NO-GO fallback).

### Next-step options for the user (no work started without sign-off)

- **A — Close Gate 1 first:** do the deferred Task 3 (throwaway Vencord dev build + inject) before
  any rigging, to fully confirm Discord before investing art labor.
- **B — Proceed to Phase 1 rigging now:** accept the GO-WITH-COST; rig Lotte against the proven
  plumbing (safe because the rig is portable to the unconstrained surfaces even if Discord slips).
- **C — Pivot the flagship to desktop wallpaper (Lively):** if the Discord dev-build maintenance
  cost is unwelcome, make the constraint-free wallpaper surface the primary target.
