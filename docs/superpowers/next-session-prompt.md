# Next Session — Lotte Live2D Aliveness, Phase 1 (Rig the real Lotte) — EXECUTE the pilot

> Phase 0 = DONE/GO. Phase 1 brainstorm + spec + plan = DONE (2026-05-31). This launcher is thin
> by design — substance lives in the spec + plan + auto-loaded memory, not here.

Paste the body below (inside the `---` block) into the next Claude session as the initial prompt.

---

## Task

**Phase 1 design is settled — do NOT re-brainstorm.** Execute the Phase 1.0 vertical-slice pilot:
`docs/superpowers/plans/2026-05-31-lotte-live2d-phase1-rig.md`, using `superpowers:executing-plans`
(recommended — the plan interleaves agent scripts with user GUI work in ChatGPT/Cubism, so inline +
user-verification fits better than autonomous subagents).

Start at **Task 0** (scaffold `live2d/PIPELINE.md` / `DECISIONS.md` / `RIG_GUIDE.md`), then **Task 1**
(Cubism 4 runtime pre-flight) — the cheapest de-risk, agent-only, no art needed. STOP at the user-action
tasks (Task 3 GPT-image-2 edit, Task 5 Cubism rig) and at the Task 7 gate.

## Read first (substance, in order)

1. `MEMORY.md` auto-loads → `lotte-live2d-aliveness-direction` (decided design + Phase 0 GO + how-to-apply)
   and `bh-chrome-no-webgl` (no headless WebGL → use a SwiftShader throwaway Chrome for any render check).
2. **Spec:** `docs/superpowers/specs/2026-05-31-lotte-live2d-phase1-rig-design.md` — goal, 8 locked
   decisions, layer map, params, workstreams, doc spine, success criteria.
3. **Plan:** `docs/superpowers/plans/2026-05-31-lotte-live2d-phase1-rig.md` — Phase 1.0 pilot (bite-sized)
   + W1–W5 roadmap.
4. Once Task 0 runs, **`live2d/PIPELINE.md` is the authority** for live pipeline state — read it first thereafter.

## Working directory

This worktree: `/home/benjohnbill/dev/discord-theme-lotte/.worktrees/live2d-spike` (branch `live2d-spike`,
unmerged). Already staged under `live2d/`: `source/` (4 rasters + lineage README + SHA256SUMS),
`gen/PROMPTS.md` (the discord-version bridge prompt + style vocabulary + W2 cookbook), `BASE.md`
(display targets + upscale plan). Phase 0 artifacts in `experiments/live2d-spike/` (FINDINGS.md,
index.html, discord-console-probe.js).

## Carry-forward facts (do not re-derive)

- **RUNTIME — Phase 1 uses Cubism 4, NOT Cubism 2.** The new Lotte rig is authored in Cubism 5 → a
  Cubism 4 `.moc3`. Runtime triplet = **official Cubism 4 core** (`live2dcubismcore.min.js`) +
  `pixi.js@6.5.10` + **`pixi-live2d-display@0.4.0/dist/cubism4.min.js`**. Task 1 verifies this load
  with a free Cubism 4 sample. (Phase 0's `cubism2.min.js` + `dylanNew` Cubism 2 core were for the
  Shizuku *sample* only — do NOT carry that into the Lotte rig.)
- **Base:** rig the character from `lotte-discord-original.png` (more facial px); borrow the extended
  background from `lotte-discord-version.png` (its outpaint, character pixel-aligned). waifu2x ×2,
  atlas 4096. See `live2d/BASE.md`.
- **Flat-rig discipline:** reactivity on flat channels (gaze, blink, breath, tilt, physics, smile);
  head turn tiny + planar + lag only, NO pseudo-3D parallax (spec §2.6).
- **Displays:** 1920×1200, 2560×1440, 2560×1600; author for the densest (2560×1600); one rig serves
  all via `fit()`; rig is aspect-agnostic, background adapts via `background-size: cover`.
- **Phase 2 delivery (later, separate):** a persistent always-on Discord background needs a Vencord
  userplugin → dev Vencord (Windows has no Node/git yet) that takes over the theme bg slot
  (`.app__<hash>`, hash volatile — detect by element size, never hardcode). Not part of Phase 1.

## Hard rules

- **Shell:** prefix dev commands with `rtk`. **`master`:** never edit or push directly; no PRs without
  sign-off. **No amend/force-push** — new commits only. **Aesthetic:** Tier 1 restraint is the whole game.

## Stopping conditions

Stop and report at: a pilot user-action task (Task 3 GPT edit, Task 5 Cubism rig), the Task 7 gate, or
any decision that genuinely needs the user.
