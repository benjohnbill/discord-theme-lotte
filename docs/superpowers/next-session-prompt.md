# Next Session — Lotte Live2D Aliveness, Phase 1 (Rig the real Lotte) — EXECUTE the full build (W1–W5)

> Phase 0 = DONE/GO. **Phase 1.0 vertical-slice pilot = DONE/GO (2026-05-31)** — the whole
> art→rig→runtime chain is proven. **Full-build W1 (base lock+upscale) + W2 (4 hidden-state patches)
> + W3 (19-part separation → `lotte.psd`) = DONE (2026-05-31).** Frontier = **W4** (full Cubism rig,
> USER). This launcher is thin by design — substance lives in the spec + plan + `live2d/PIPELINE.md`
> + auto-loaded memory.

Paste the body below (inside the `---` block) into the next Claude session as the initial prompt.

---

## Task

**Phase 1 design is settled and the pilot already proved the chain — do NOT re-brainstorm or re-run the pilot.**
Execute the full build: `docs/superpowers/plans/2026-05-31-lotte-live2d-full-build-w1-w5.md`, using
`superpowers:executing-plans` (recommended — the plan interleaves agent scripts with user GUI work in
ChatGPT/Cubism/Discord, so inline + user-verification fits better than autonomous subagents).

**W1 + W2 + W3 are DONE (2026-05-31).** Start at **W4** (full Cubism rig — USER GUI in Cubism 5.3 FREE).
Read `live2d/PIPELINE.md` FIRST for live state. W3 produced the 19-part `live2d/lotte.psd` (on-disk,
gitignored — regenerate via `full_segment.py` + `build_psd_full.py` if missing). W4 = append the full
Tier-1 walkthrough to `RIG_GUIDE.md` (agent), then the USER rigs `lotte.cmo3` and exports
`model/lotte.model3.json` (+ `.moc3` **at version 5.0**), then `check_model.py` validates. Carry the W3
realities into W4: atlas — parts at full res are ~3× one FREE 2048 atlas, so scale the Cubism import
~0.5× (≈1254²) or use 2 atlases (BASE.md W3.4); part set — bangs are baked into face_base, hair is
`hair_L`/`hair_R` (front side locks). **W3↔W4 loop:** if rigging needs a part split/merged, edit
`full_segment.py` (`BOXES` dict / `col_layer` calls) and re-run. STOP at the W4 Cubism rig (USER) and
W5 Discord verify, and at any decision that genuinely needs the user.

## Read first (substance, in order)

1. `MEMORY.md` auto-loads → `lotte-live2d-aliveness-direction` (decided design + Phase 0 GO + **pilot
   GO + the confirmed learnings**) and `bh-chrome-no-webgl` (no headless WebGL → use a SwiftShader
   throwaway Chrome for any render check).
2. **`live2d/PIPELINE.md`** — the live pipeline-state **authority**. Read it first for "where are we / what's next".
3. **Plan:** `docs/superpowers/plans/2026-05-31-lotte-live2d-full-build-w1-w5.md` — W1–W5, complete
   scripts + per-reference GPT prompts + guided rig + the W5 smile state machine.
4. **Spec:** `docs/superpowers/specs/2026-05-31-lotte-live2d-phase1-rig-design.md` — goal, 8 locked
   decisions, layer map, params, workstreams, success criteria.
5. **Pilot record:** `live2d/pilot/RESULT.md` — what the pilot proved + the learnings the plan carries.

## Working directory

This worktree: `/home/benjohnbill/dev/discord-theme-lotte/.worktrees/live2d-spike` (branch `live2d-spike`).
**Branch state (2026-05-31): `live2d-spike` is AHEAD of `master`** — master is at `a6674fb` (the FF-merge
point, docs only); W1+W2+W3 commits (`b910cb5`…`aacc3b8`) live on `live2d-spike` ONLY, not merged, not
pushed. The earlier "the two are even" note is stale — split-brain reopened after the merge. Do W4 here;
merge/push needs sign-off. Under `live2d/`: `PIPELINE.md` (authority), `DECISIONS.md`,
`BASE.md`, `RIG_GUIDE.md`, `source/` (rasters + SHA256SUMS), `gen/PROMPTS.md`, and `pilot/` (the
complete Phase 1.0 pilot: scripts, layers, `lotte-pilot.psd`, `model/` moc3 v5, `RESULT.md`). Pilot
Python = `live2d/pilot/.venv` (Pillow/rembg/psd-tools/pytoshop). Phase 0 artifacts in
`experiments/live2d-spike/`.

## Carry-forward facts (do not re-derive)

- **RUNTIME — the Lotte rig is Cubism 4.** Triplet = official Cubism 4 core (`live2dcubismcore.min.js`)
  + `pixi.js@6.5.10` + `pixi-live2d-display@0.4.0/dist/cubism4.min.js`. (Phase 0's `cubism2.min.js` +
  `dylanNew` core were for the Shizuku *sample* only — never for the Lotte rig.)
- **moc3 export MUST target ≤ v5.** Cubism Editor 5.3 exports moc3 **v6** by default; the pinned web
  Core reports `csmGetLatestMocVersion()=5` and **rejects v6**. Export at `.moc3 file version` **5.0**
  (or 4.2). Fallback: bump the Core / use the `pixi-live2d-display-lipsyncpatch` fork. *(Pilot-confirmed.)*
- **Texture atlas: Cubism FREE caps it at 2048×2048** (NOT 4096). Keep hi-res masters in
  `live2d/assets/`, but scale the Cubism source so ~20 tight-bounded parts fit one 2048 atlas (or use
  2 atlases / lower upscale). *(Pilot-confirmed — supersedes BASE.md's earlier 4096 assumption.)*
- **Base:** rig the character from `lotte-discord-original.png` (more facial px); ambient background
  from `lotte-discord-version.png` (pixel-aligned outpaint). Rasters in `live2d/source/`, never `src/`.
- **Eye-smile param:** use the Cubism template's standard **`EyeL Smile` / `EyeR Smile`** — **there is
  no standard `ParamEyeForm`** (spec §5 names it; the plan/RIG_GUIDE correct it).
- **Flat-rig discipline:** reactivity on flat channels (gaze, blink, breath, tilt, physics, smile);
  head turn tiny + planar + lag only, NO pseudo-3D parallax (spec §2.6).
- **Displays:** 1920×1200, 2560×1440, 2560×1600; author for the densest; one rig serves all via
  `fit()`; aspect-agnostic; background adapts via `background-size: cover`.
- **Phase 2 delivery (later, separate):** a persistent always-on Discord background needs a Vencord
  userplugin → dev Vencord that takes over the theme bg slot (`.app__<hash>`, hash volatile — detect
  by element size, never hardcode). Not part of Phase 1.

## Hard rules

- **Shell:** prefix dev commands with `rtk`. **`master`:** the worktree is already merged into `master`
  locally (2026-05-31, **not pushed** — pushing needs sign-off); never push or force-push without sign-off;
  new commits only (no amend). **Aesthetic:** Tier 1 restraint is the whole game.

## Stopping conditions

Stop and report at: a user-action task (W2 GPT edits, W4 Cubism rig, W5 Discord verify), any workstream
gate, or any decision that genuinely needs the user.
