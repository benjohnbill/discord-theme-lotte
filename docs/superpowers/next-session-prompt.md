# Next Session — Lotte Live2D Aliveness, Phase 1 (Rig the real Lotte) — brainstorm first

> Phase 0 is DONE → **GO** (every gate green, confirmed in the real Discord client). This is a thin
> launcher by design — substance lives in auto-loaded memory and in `FINDINGS.md`, not here (handoff
> files are low-trust per the project's memory model; nothing here should go stale).

Paste the body below (inside the `---` block) into the next Claude session as the initial prompt.

---

## Task

Begin **Phase 1 — rig the real Lotte**, and **start with brainstorming** (`superpowers:brainstorming`)
the rigging approach before any code/art. Then write the Phase 1 plan with `superpowers:writing-plans`.
Do NOT start rigging without user sign-off. (Brainstorming / workflow-mode is user-scope — propose once.)

## Read first (substance lives here, not in this launcher)

1. `MEMORY.md` auto-loads → memory **`lotte-live2d-aliveness-direction`** has the decided design, the
   Phase 0 RESULT (GO), and the "How to apply" pointer. Also **`bh-chrome-no-webgl`** (env caveat).
2. **`experiments/live2d-spike/FINDINGS.md`** (this branch) — the proven plumbing, the corrected
   library triplet, and the Phase 2 background-slot finding.

## Working directory

This worktree: `/home/benjohnbill/dev/discord-theme-lotte/.worktrees/live2d-spike` (branch
`live2d-spike`, unmerged) — Phase 0 artifacts (`FINDINGS.md`, proven `index.html`,
`discord-console-probe.js`) are here to reuse.

## Brainstorm topics (Phase 1)

- Source image: `Lotte discord version.png` (the 16:10 bust currently used in Discord).
- Layer separation (eyes/eyelids, brows, mouth, bangs, side hair, back hair, face base, body, bg) +
  inpaint occluded regions — **which tool** (Photoshop/Krita/AI segmentation)?
- Inpaint strategy for forehead-behind-bangs, neck/shoulder behind side hair, behind bow/collar, eye sockets.
- Background bokeh/petals/sparkles → separate drifting-particle layer (free ambient life).
- Rig scope: **Tier 1 only** — blink, breathe, hair sway, gentle gaze. Big face → restraint; under-animated beats uncanny.
- Repo home for the Live2D model + (future) Vencord plugin: this CSS-theme repo vs a sibling repo.
- Swap the rigged Lotte model into the proven Phase 0 plumbing (`index.html`).

## Carry-forward facts (do not re-derive)

- **Runtime triplet (proven):** `dylanNew` Cubism 2 core + `pixi.js@6.5.10` + `pixi-live2d-display@0.4.0/dist/cubism2.min.js`.
  The plan's Roadmap Task-3 code uses `index.min.js` — that is WRONG (demands Cubism 4 runtime); use `cubism2.min.js`.
- **Phase 2 delivery (separate, schedulable later):** persistent always-on Discord background needs a
  Vencord userplugin → dev Vencord (Windows has no Node/git yet) that dynamically takes over the theme's
  background slot (`.app__<hash>`, hash is volatile — detect by element size, never hardcode).

## Hard rules

- **Shell:** prefix dev commands with `rtk`.
- **`master`:** never edit or push directly. No PRs without user sign-off.
- **No amend/force-push.** New commits only.
- **Aesthetic:** Tier 1 restraint is the whole game.

## Stopping conditions

Stop and report when: the Phase 1 brainstorm + plan is ready for sign-off; OR a decision genuinely needs the user.
