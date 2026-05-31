# Lotte Live2D Aliveness — Phase 0 (Feasibility Spike) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. This plan is a **feasibility spike**, not a TDD feature — verification steps are "run X, observe Y / screenshot", not unit tests. Honor the bite-sized, concrete, no-placeholder spirit regardless.

**Goal:** Prove (or disprove) that a single Live2D rig can be rendered live inside the Discord desktop client as a cursor-aware full-window background, before investing any art-rigging or Vencord-maintenance labor.

**Architecture:** De-risk in cheapest-first order using a FREE sample model (zero rigging cost): (1) investigate whether this Vencord install can load custom JS plugins at all; (2) stand up `pixi-live2d-display` rendering a sample model with cursor tracking in a plain browser page; (3) inject that same scene into Discord via a throwaway Vencord userplugin and confirm it renders behind the UI and follows the cursor. Phase 0 ends with an explicit go/no-go.

**Tech Stack:** PIXI.js v6, pixi-live2d-display, Live2D Cubism Core, Vencord (custom userplugin → requires a source/dev build), WSL2 + Windows-side Discord.

---

## Background — Decided Design (from the 2026-05-31 grill; preserved here so the "why" is not lost)

This section substitutes for a separate spec/ADR until Phase 0 resolves the feasibility gates. ADRs and CONTEXT.md glossary entries will be written **after** Phase 0 confirms the approach is real (per the repo's ADR-0001 precedent of recording decisions once accepted).

**Core goal.** Make the Lotte character feel *alive* = **attention/presence** ("Lotte notices me / is here with me"), NOT image-swap variety. On any single surface the motif stays fixed (swapping images on the same surface reads as a defect, e.g. moving the window across monitors).

**Rejected alternatives (do not re-litigate without new information):**
- *Image-swap variety* — rejected: jarring when triggered by incidental window actions; user values per-surface consistency.
- *GIF / baked animation* — rejected: a closed loop cannot react; "presence" requires code-driven reactivity, not a canned loop. (Also: GIF does not work as an OS wallpaper on either iOS or Android.)
- *Informational presence (③ "she tells me things")* — deferred: the meaningful version needs life-integration (Obsidian/calendar) and is too complex now; the shallow version (press button → tells time) is a gimmick (the clock is already on screen).
- *Corner mascot widget for Discord* — rejected **for this user**: the user lives in idle/Friends views where a full-background face shows fully, loves the current background look, and a mascot adds a new UI element for little gain.
- *Layered-parallax / sprite-swap rigs* — rejected as the spine: only Live2D delivers real eye/head cursor tracking, and it is the portable artifact that unifies every surface.

**Decided approach.**
- **Tech spine: Live2D** (DIY, no outsourcing budget; the agent does all *code*, the user does the Cubism Editor GUI rigging by hand). One rig = a portable web artifact (`pixi-live2d-display`) reused across Discord, desktop wallpaper (Lively), mobile (Samsung live wallpaper), and a possible future workspace pet.
- **Discord = full background** + **Tier 1 intensity** (breathe, hair sway, blink, time-of-day light; only occasional gentle cursor glance). The face is large, so restraint is essential — strong cursor snapping on a big face reads as uncanny/"과격".
- **Desktop wallpaper** = ambient (time-of-day) only, via Lively, same rig.
- **Mobile (Samsung)** = home-screen Live2D live wallpaper, idle motion only, subtle/battery-conscious.
- **Deferred:** avatar/banner (static), Tier 2/3 attention, deep informational presence, workspace pet.

**Aesthetic guardrails (carry into every phase):** restraint is the whole game. Tier 1 only. Big face → no aggressive tracking. Start under-animated and add only if it feels dead.

**Two feasibility gates (the reason Phase 0 exists):**
1. Custom Vencord plugins likely require a self-built/dev Vencord, not the stock installer — **UNVERIFIED**. Discord here runs on Windows; the build/inject is cross-environment (WSL ↔ Windows).
2. Live2D rigging labor (Phase 1) — real, but only worth paying once Gate 1 is green.

The user explicitly required: verify feasibility completely *before* committing effort. Phase 0 (sample-model-first) is exactly that de-risk.

---

## Scope of THIS plan

**Phase 0 only.** Phases 1–4 are captured as a high-level roadmap at the end; their bite-sized detail genuinely depends on Phase 0's findings (e.g., *how* we inject depends on what Gate 1 reveals) and writing it now would force placeholders. Write the Phase 1 plan after Phase 0 goes green.

**Repo structure note:** Execute Phase 0 in an isolated worktree (repo convention — one worktree per initiative), branched from `master`. Spike artifacts live in `experiments/live2d-spike/` — **outside** the theme build pipeline (not in `src/`, not listed in `theme.manifest.yaml` partials), so they never get concatenated into the generated theme. CONTEXT.md / ADR infrastructure currently lives only in the unmerged `m5-drift-conventions` worktree; do not depend on it for Phase 0.

---

## File Structure

| File | Responsibility |
|---|---|
| `experiments/live2d-spike/index.html` | Standalone browser spike: PIXI + pixi-live2d-display + sample model + cursor tracking. No Discord. |
| `experiments/live2d-spike/FINDINGS.md` | Living record of Gate-1 investigation results, CSP findings, and the final go/no-go. |
| `experiments/live2d-spike/vencord-plugin/lotteLive2dSpike/index.tsx` | Throwaway Vencord userplugin that injects the spike scene into Discord as a full-window background. |
| `experiments/live2d-spike/.gitignore` | Ignore downloaded model binaries / `node_modules` so only code is committed. |

---

## Task 1: Investigate Vencord install & custom-plugin capability (Gate 1)

**Files:**
- Create: `experiments/live2d-spike/FINDINGS.md`

**Goal:** Determine whether this Vencord can load a custom JS plugin, and if not, exactly what setting one up costs. Pure investigation — no Discord changes yet.

- [ ] **Step 1: Confirm the Vencord user-data dir and inspect it**

Run:
```bash
ls -la "/mnt/c/Users/benjohnbill/AppData/Roaming/Vencord/"
ls -la "/mnt/c/Users/benjohnbill/AppData/Roaming/Vencord/themes/"
ls -la "/mnt/c/Users/benjohnbill/AppData/Roaming/Vencord/settings/" 2>/dev/null
```
Expected: a `themes/` dir containing `NewKemonoFriends.theme.css` (confirms Vencord is installed and is the sync target). A `settings/settings.json` likely exists.

- [ ] **Step 2: Read the Vencord settings to see enabled plugins / install hints**

Run:
```bash
cat "/mnt/c/Users/benjohnbill/AppData/Roaming/Vencord/settings/settings.json" 2>/dev/null | head -60
```
Expected: JSON listing enabled built-in plugins. Note: presence of this dir is consistent with BOTH stock and dev installs — it does not by itself prove which.

- [ ] **Step 3: Search the Windows drive for a Vencord SOURCE clone (the marker of a dev build)**

Run (bounded to likely dev locations to avoid scanning the whole drive):
```bash
for base in "/mnt/c/Users/benjohnbill" "/mnt/c/Users/benjohnbill/dev" "/mnt/c/Users/benjohnbill/Documents" "/mnt/c/Users/benjohnbill/source"; do
  find "$base" -maxdepth 4 -type d -name "userplugins" 2>/dev/null
done
# Also check WSL home in case a clone lives Linux-side:
find "$HOME" -maxdepth 5 -type d -name "userplugins" 2>/dev/null
```
Expected: either a path ending in `Vencord/src/userplugins` (→ a dev/source build exists) OR no results (→ stock installer build, custom plugins NOT yet possible).

- [ ] **Step 4: Record the verdict in FINDINGS.md**

Write `experiments/live2d-spike/FINDINGS.md` with a "Gate 1 — Vencord plugin capability" section stating: install type (stock vs source), the userplugins path if found, and the conclusion:
- If a source build exists → custom plugins are loadable; Task 3 can proceed directly.
- If stock only → custom plugins require setting up a Vencord source build and re-injecting into the Windows Discord. Document this as the cost; the actual setup happens in Task 3 only if we proceed.

- [ ] **Step 5: If stock-only, document the dev-build path (do NOT execute yet)**

In FINDINGS.md, record the canonical Vencord self-build steps so Task 3 has them ready, and flag the cross-environment caveat:
```text
Dev-build path (run on the side that owns the Discord install — Windows here):
  git clone https://github.com/Vendicated/Vencord
  cd Vencord && pnpm install --frozen-lockfile
  mkdir -p src/userplugins
  (place the plugin under src/userplugins/lotteLive2dSpike/)
  pnpm build
  pnpm inject     # patches the local Discord desktop install; pick the right branch
Maintenance cost: re-run `pnpm build` (and sometimes re-inject) after Discord/Vencord updates.
Cross-env caveat: building can be done in WSL, but `pnpm inject` must target the Windows
Discord install. If WSL-side inject cannot see the Windows Discord, run the build/inject on
the Windows side (Node + pnpm on Windows). Confirm which works during Task 3.
```

- [ ] **Step 6: Commit**

```bash
git add experiments/live2d-spike/FINDINGS.md
git commit -m "spike(live2d): record Vencord plugin-capability investigation (Gate 1)"
```

---

## Task 2: Standalone Live2D runtime spike (browser, no Discord)

**Files:**
- Create: `experiments/live2d-spike/index.html`
- Create: `experiments/live2d-spike/.gitignore`

**Goal:** Prove `pixi-live2d-display` renders a sample model and tracks the cursor in a plain browser. This is the cheap, near-guaranteed win and proves half the stack independent of Vencord.

- [ ] **Step 1: Create the .gitignore**

```bash
mkdir -p experiments/live2d-spike
printf "node_modules/\n*.moc\n*.moc3\nmodels/\n" > experiments/live2d-spike/.gitignore
```

- [ ] **Step 2: Write the standalone spike page**

Create `experiments/live2d-spike/index.html`:
```html
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <style>
    html, body { margin: 0; height: 100%; background: #1e1f3a; overflow: hidden; }
    #c { display: block; width: 100vw; height: 100vh; }
    #status { position: fixed; top: 8px; left: 8px; color: #fff; font: 14px monospace; }
  </style>
</head>
<body>
  <div id="status">loading…</div>
  <canvas id="c"></canvas>
  <!-- Cubism 2 Core (the Shizuku sample model is Cubism 2.1). -->
  <script src="https://cubism.live2d.com/webgl/live2d.min.js"></script>
  <!-- PIXI v6 (pixi-live2d-display 0.4.x targets PIXI v6). -->
  <script src="https://cdn.jsdelivr.net/npm/pixi.js@6.5.10/dist/browser/pixi.min.js"></script>
  <!-- pixi-live2d-display UMD bundle (exposes PIXI.live2d.*). -->
  <script src="https://cdn.jsdelivr.net/npm/pixi-live2d-display/dist/index.min.js"></script>
  <script>
    (async () => {
      const status = document.getElementById('status');
      try {
        const app = new PIXI.Application({
          view: document.getElementById('c'),
          resizeTo: window,
          backgroundAlpha: 0,
          autoStart: true,
        });
        // Canonical sample model from the pixi-live2d-display test assets (jsDelivr gh CDN).
        const model = await PIXI.live2d.Live2DModel.from(
          'https://cdn.jsdelivr.net/gh/guansss/pixi-live2d-display/test/assets/shizuku/shizuku.model.json'
        );
        app.stage.addChild(model);
        const fit = () => {
          const s = Math.min(window.innerWidth / model.width, window.innerHeight / model.height) * 0.9;
          model.scale.set(s);
          model.anchor.set(0.5, 0.5);
          model.position.set(window.innerWidth / 2, window.innerHeight / 2);
        };
        fit();
        window.addEventListener('resize', fit);
        // autoInteract is ON by default → moving the mouse drives model.focus().
        status.textContent = 'rendered. move the mouse — eyes/head should follow.';
      } catch (e) {
        status.textContent = 'ERROR: ' + (e && e.message ? e.message : e);
        console.error(e);
      }
    })();
  </script>
</body>
</html>
```

- [ ] **Step 3: Serve it locally (file:// can block CDN fetches in some browsers)**

Run:
```bash
cd experiments/live2d-spike && python3 -m http.server 8123
```
Expected: server listening on `http://localhost:8123`.

- [ ] **Step 4: Open in a browser and verify visually**

Open `http://localhost:8123/index.html`. Use the project's browser-harness for a scripted screenshot, e.g.:
```bash
browser-harness <<'PY'
new_tab("http://localhost:8123/index.html")
wait_for_load()
switch_tab(current_tab())
print(page_info())
PY
```
Expected observations (record in FINDINGS.md):
1. The status line reads "rendered…" (NOT "ERROR:"). If it errors, note the message (common: Cubism Core URL moved, or PIXI/plugin version mismatch — pin a known-good pixi-live2d-display version from its docs).
2. The Shizuku character is visible, centered.
3. Moving the cursor across the canvas makes the model's eyes and head follow it.

- [ ] **Step 5: Capture a screenshot as evidence and stop the server**

Save a screenshot to `experiments/live2d-spike/0b-standalone.png`. Stop the http.server (Ctrl-C / kill the background job).

- [ ] **Step 6: Record result + commit**

Append a "Gate runtime — standalone Live2D" section to FINDINGS.md (PASS/FAIL + the screenshot reference + any version pins that were needed).
```bash
git add experiments/live2d-spike/index.html experiments/live2d-spike/.gitignore experiments/live2d-spike/FINDINGS.md experiments/live2d-spike/0b-standalone.png
git commit -m "spike(live2d): standalone pixi-live2d-display render + cursor tracking"
```

---

## Task 3: Inject the spike into Discord as a full-window background (Gate 1 proof)

**Precondition:** Task 1 concluded custom plugins are loadable, OR you are willing to stand up a *throwaway* Vencord dev build to prove the concept (not a commitment to maintain it forever — that judgment comes in Task 4).

**Files:**
- Create: `experiments/live2d-spike/vencord-plugin/lotteLive2dSpike/index.tsx` (source kept in THIS repo; copied into the Vencord `src/userplugins/` tree to build)

**Goal:** Confirm the Live2D scene renders inside Discord, behind the UI, full-window, tracking the cursor — and discover any Discord CSP obstacles.

- [ ] **Step 1: Ensure a Vencord source build exists**

If Task 1 found a source clone, use it. Otherwise follow the dev-build path recorded in FINDINGS.md Step 5 (run on the side that owns the Discord install). Verify with:
```bash
# from the Vencord clone root:
ls src/userplugins 2>/dev/null && cat package.json | grep '"name"'
```
Expected: `src/userplugins` exists and package name is `vencord`.

- [ ] **Step 2: Write the throwaway userplugin (kept in this repo for review)**

Create `experiments/live2d-spike/vencord-plugin/lotteLive2dSpike/index.tsx`:
```tsx
import definePlugin from "@utils/types";

// Throwaway feasibility plugin: inject a full-window Live2D canvas behind Discord's UI
// and drive model focus from the global cursor. NOT production code — proves Gate 1 only.

const SCRIPTS = [
    "https://cubism.live2d.com/webgl/live2d.min.js",
    "https://cdn.jsdelivr.net/npm/pixi.js@6.5.10/dist/browser/pixi.min.js",
    "https://cdn.jsdelivr.net/npm/pixi-live2d-display/dist/index.min.js",
];
const MODEL = "https://cdn.jsdelivr.net/gh/guansss/pixi-live2d-display/test/assets/shizuku/shizuku.model.json";

let container: HTMLDivElement | null = null;
let onMove: ((e: MouseEvent) => void) | null = null;

function loadScript(src: string) {
    return new Promise<void>((resolve, reject) => {
        const s = document.createElement("script");
        s.src = src;
        s.onload = () => resolve();
        s.onerror = () => reject(new Error("failed to load " + src));
        document.head.appendChild(s);
    });
}

export default definePlugin({
    name: "LotteLive2dSpike",
    description: "Feasibility spike: full-window Live2D background that tracks the cursor.",
    authors: [{ name: "lotte-spike", id: 0n }],

    async start() {
        try {
            container = document.createElement("div");
            Object.assign(container.style, {
                position: "fixed", inset: "0", zIndex: "0",
                pointerEvents: "none", overflow: "hidden",
            } as CSSStyleDeclaration);
            const canvas = document.createElement("canvas");
            canvas.style.width = "100vw";
            canvas.style.height = "100vh";
            container.appendChild(canvas);
            // Insert at the very back of the body so Discord's (translucent-themed) UI sits on top.
            document.body.insertBefore(container, document.body.firstChild);

            for (const s of SCRIPTS) await loadScript(s);

            const PIXI = (window as any).PIXI;
            const app = new PIXI.Application({ view: canvas, resizeTo: window, backgroundAlpha: 0 });
            const model = await PIXI.live2d.Live2DModel.from(MODEL);
            app.stage.addChild(model);
            const fit = () => {
                const sc = Math.min(window.innerWidth / model.width, window.innerHeight / model.height) * 0.9;
                model.scale.set(sc);
                model.anchor.set(0.5, 0.5);
                model.position.set(window.innerWidth / 2, window.innerHeight / 2);
            };
            fit();
            window.addEventListener("resize", fit);
            // Drive focus from the GLOBAL cursor (canvas has pointer-events:none, so track on document).
            onMove = (e: MouseEvent) => model.focus(e.clientX, e.clientY);
            document.addEventListener("mousemove", onMove);
            console.log("[LotteLive2dSpike] rendered");
        } catch (e) {
            console.error("[LotteLive2dSpike] FAILED", e);
        }
    },

    stop() {
        if (onMove) document.removeEventListener("mousemove", onMove);
        onMove = null;
        container?.remove();
        container = null;
    },
});
```

- [ ] **Step 3: Copy the plugin into the Vencord build tree, build, and inject**

Run (adjust the Vencord clone path to the one from Task 1):
```bash
VENCORD=/path/to/Vencord
mkdir -p "$VENCORD/src/userplugins/lotteLive2dSpike"
cp experiments/live2d-spike/vencord-plugin/lotteLive2dSpike/index.tsx "$VENCORD/src/userplugins/lotteLive2dSpike/index.tsx"
cd "$VENCORD" && pnpm build && pnpm inject
```
Expected: build succeeds; inject reports patching the Discord install.

- [ ] **Step 4: Enable the plugin and restart Discord**

In Discord → Settings → Vencord → Plugins, enable **LotteLive2dSpike**. Fully restart Discord (Ctrl+R reload may not re-run a freshly built bundle reliably — prefer a full quit/relaunch).

- [ ] **Step 5: Verify in Discord (and watch for CSP errors)**

Open Discord DevTools console (Ctrl+Shift+I). Observe:
1. Console shows `[LotteLive2dSpike] rendered` and NOT a CSP error like `Refused to load the script … because it violates the … Content Security Policy`.
   - **If CSP blocks the remote scripts:** record it in FINDINGS.md. Mitigation for the real build: bundle PIXI + Cubism Core + pixi-live2d-display *into* the plugin (import them as dependencies) and host the model locally/as a data asset instead of remote `<script>`/CDN. Note this as a known production change, not a blocker.
2. On the Friends/home view (open center area), the Shizuku model is visible behind the translucent UI.
3. Moving the cursor anywhere over the window makes the model's eyes/head follow.

- [ ] **Step 6: Screenshot evidence + record + commit the plugin source**

Save `experiments/live2d-spike/0c-in-discord.png`. Append a "Gate 1 proof — in Discord" section to FINDINGS.md (PASS/FAIL, CSP outcome, screenshot ref).
```bash
git add experiments/live2d-spike/vencord-plugin experiments/live2d-spike/FINDINGS.md experiments/live2d-spike/0c-in-discord.png
git commit -m "spike(live2d): inject full-window Live2D background into Discord via userplugin"
```

- [ ] **Step 7: Disable the spike plugin**

Disable LotteLive2dSpike in Vencord settings (leave Discord clean). The spike has served its purpose; productionization is a later phase.

---

## Task 4: Go / No-Go decision record

**Files:**
- Modify: `experiments/live2d-spike/FINDINGS.md`

- [ ] **Step 1: Summarize the three gate results**

In FINDINGS.md add a "Decision" section answering:
1. Does pixi-live2d-display render + track cursor? (Task 2)
2. Can a custom plugin run in this Vencord, and at what setup/maintenance cost? (Task 1 + 3)
3. Did Discord's CSP allow it, or is bundling required? (Task 3 Step 5)

- [ ] **Step 2: Write the recommendation**

State one of:
- **GO** → proceed to Phase 1 (rig the real Lotte). Note any required production changes (e.g., bundle the runtime to satisfy CSP; pin specific library versions).
- **GO-WITH-COST** → technically works, but the dev-build maintenance burden is real; surface it to the user as an explicit accept/decline before Phase 1.
- **NO-GO** → injection infeasible/unacceptable. Fall back: Discord stays static/ambient CSS background; redirect the Live2D investment to the desktop-wallpaper surface (Lively, which has no plugin/CSP constraints) as the new flagship.

- [ ] **Step 3: Commit the decision**

```bash
git add experiments/live2d-spike/FINDINGS.md
git commit -m "spike(live2d): Phase 0 go/no-go decision"
```

- [ ] **Step 4: If GO — write the Phase 1 plan**

Use superpowers:writing-plans to create `docs/superpowers/plans/<date>-lotte-live2d-rig.md` covering: source image (`Lotte discord version.png`) layer separation + inpaint, modest Cubism rig (blink, breathe, hair sway, gentle gaze), and swapping the sample model for the Lotte model in the proven plumbing. Also write the deferred ADRs (Live2D adoption; full-bg over mascot; theme→plugin expansion) and add CONTEXT.md glossary entries, now that the decisions are real.

---

## Roadmap — Phases 1–4 (high-level; detail AFTER Phase 0 goes green)

> **SUPERSEDED for Phase 1** (2026-05-31): the Phase 1 design + plan replace the framing below — base = `lotte-discord-original.png` (character) + `lotte-discord-version.png` (background), runtime = **Cubism 4**, restructured into a Phase 1.0 pilot + W1–W5. Authority: `docs/superpowers/specs/2026-05-31-lotte-live2d-phase1-rig-design.md` and `docs/superpowers/plans/2026-05-31-lotte-live2d-phase1-rig.md`.

- **Phase 1 — Rig the real Lotte.** Source = `Lotte discord version.png` (the 16:10 bust currently used in Discord). Layer-separate (eyes/eyelids, brows, mouth, bangs, side hair, back hair, face base, body, background) and inpaint occluded regions (forehead behind bangs, neck/shoulder behind side hair, behind the bow, under the collar, eye sockets for blink). The bokeh/petals/sparkles background becomes a separate drifting-particle layer (free ambient life). Modest rig only. Output: a Cubism model swapped into the Phase 0 plumbing.
- **Phase 2 — Tier 1 polish on Discord.** Breathing, hair physics, blink cadence, time-of-day lighting, very gentle damped cursor glance. Productionize the plugin (bundle runtime if CSP required; local model asset; settings toggle). Decide repo home (theme repo vs sibling plugin repo).
- **Phase 3 — Port to other surfaces.** Desktop wallpaper via Lively (same rig, time-of-day ambient only). Mobile: Samsung home-screen Live2D live wallpaper host app, idle motion only, subtle/battery-conscious.
- **Phase 4+ — Deferred.** Tier 2/3 attention, animated avatar/banner, deep informational presence (Obsidian/calendar life-integration), workspace pet.

---

## Self-Review

- **Spec coverage:** Phase 0's three gates (runtime, plugin capability, in-Discord injection + CSP) each map to Tasks 2, 1, and 3; the go/no-go is Task 4. The decided design + rejected alternatives are recorded in Background so they survive into execution. Phases 1–4 are intentionally roadmap-only (their detail depends on Phase 0 findings — decomposing now would require placeholders).
- **Placeholder scan:** Spike code is complete (full HTML + full plugin). The one genuine external unknown — exact Cubism Core / library CDN URLs and Discord CSP behavior — is handled as explicit *verify-and-record* steps with named mitigations (version pinning; bundling the runtime), not hand-waved.
- **Consistency:** Library set (PIXI v6, pixi-live2d-display UMD exposing `PIXI.live2d.Live2DModel`, Cubism 2 core for the Shizuku sample) and the sample model URL are identical across Task 2 and Task 3. `model.focus(x, y)` is the tracking call in both. Spike artifacts stay in `experiments/live2d-spike/`, outside the theme build pipeline, in both tasks.
