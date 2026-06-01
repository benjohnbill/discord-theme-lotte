# Next Session — Lotte Live2D Aliveness — Phase 1 COMPLETE; next = optional polish or Phase 2

> Phase 0 = DONE/GO. Phase 1.0 pilot = DONE/GO. **Phase 1 FULL BUILD = DONE/PASS (W1–W5 + physics,
> finished 2026-06-01).** The full Lotte rig drives end-to-end in pixi-live2d-display@0.4.0 + Cubism
> Core 5.1. **`live2d-spike` was merged into `master` and removed — `master` is now the single
> authority** (local-only, ~55 commits ahead of origin, NOT pushed). This launcher is thin by design —
> substance lives in `live2d/PIPELINE.md` + the spec + auto-loaded memory.

Paste the body below (inside the `---` block) into the next Claude session as the initial prompt.

---

## Task

**Phase 1 is COMPLETE — do NOT re-brainstorm, re-run the pilot, or re-execute W1–W5.** The rig is built,
exported (moc3 v5), runtime-verified, and physics (hair + independent ribbon sway) is rigged and
CDP-phase-verified. Read `live2d/PIPELINE.md` FIRST for live state.

There is no forced next step. Pick up one of these, per the user:
- **W5 polish (OPTIONAL, USER art/tune calls — not blockers):** (a) ~~hair-edge halo + circular vignette~~
  **CLOSED 2026-06-01 — non-issue on the real backdrop.** Re-verified the rig composited over the real
  `version` lavender background (not the dark navy W5 used): the matte fringe blends invisibly there, at
  rest and tilted. The "halo" is the `original` 1×1 avatar's decorative circular frame; it only stood out
  on dark navy. Environment-alignment artifact, not a rig bug — defringe NOT needed (reopen only for a
  dark/non-lavender backdrop). Evidence `live2d/w5-halo-*.png`; spec `docs/superpowers/specs/2026-06-01-lotte-live2d-w5-halo-defringe-design.md`.
  (b) ~~eye-smile too strong~~ **CLOSED 2026-06-01 — not real (measurement conflation).** Smile alone barely
  closes the eye (iris retained L96.7% / R93.5% at Smile=1, EyeOpen=1); closing is `ParamEyeOpen`'s job, so the
  prior "Smile=1 ≈ blink" was a blink-panel mislabel. If anything the crescent is subtle. Evidence `live2d/w5-b-*.png`.
  (c) rectangular seam **REAL but faint, DEFERRED 2026-06-01.** `full_segment.py` hard crop-box edges show a faint
  rectangular outline over face_base (located: forehead ~y0.31, under-eye ~y0.54, verticals between eyes + right
  face). Faint at real bg scale. Fix = feather the box alpha in `full_segment.py`, done **opportunistically at the
  next re-export** (not worth a standalone Cubism round-trip). Evidence `live2d/w5-c-seam-located.png`.
- **Phase 2 — productionize the Discord delivery:** a persistent always-on background needs a Vencord
  userplugin (dev Vencord + Node/git on Windows; themes/QuickCSS can't run JS). Feasibility already
  proven in Phase 0 (CSP allows the CDN runtime, Electron has WebGL 2). This is the recommended real
  next arc once polish is settled.
- **Push `master`:** Tier-3, needs explicit user sign-off (never push yourself).

**W3↔W4 loop (still valid for polish):** if a part needs split/merge, edit `full_segment.py`
(`BOXES` / `col_layer`) → re-run `full_segment.py` + `build_psd_full.py` → re-import to Cubism → re-rig →
re-export (moc3 5.0) → `check_model.py` → re-verify with `live2d/runtime-check-full.html`.

## Read first (substance, in order)

1. `MEMORY.md` auto-loads → `lotte-live2d-aliveness-direction` (decided design + Phase 0 GO + pilot GO +
   the confirmed learnings + **Phase 1 build DONE**) and `bh-chrome-no-webgl` (no headless WebGL → use a
   SwiftShader throwaway Chrome for any render check).
2. **`live2d/PIPELINE.md`** — the live pipeline-state **authority**. Read it first for "where are we / what's done / what's optional next".
3. **Spec:** `docs/superpowers/specs/2026-05-31-lotte-live2d-phase1-rig-design.md` — goal, 8 locked
   decisions, layer map, params, success criteria.
4. **Plan (now history):** `docs/superpowers/plans/2026-05-31-lotte-live2d-full-build-w1-w5.md` — the
   W1–W5 build, completed; useful as the record of how each stage was done (don't re-execute).
5. **Runtime/physics evidence:** `live2d/w5-runtime-*.png` + the harness `live2d/runtime-check-full.html`
   (`?autosine`/`?cinema` for motion); `live2d/pilot/RESULT.md` is the pilot record.

## Working directory

`/home/benjohnbill/dev/discord-theme-lotte` on branch **`master`** (the live2d-spike worktree was merged
and removed 2026-06-01 — do not look for it). **`master` is the single authority.** It is **local-only:
~55 commits ahead of `origin/master`, NOT pushed** — pushing is Tier-3 (sign-off only; never push/force
yourself). `master` also has one unrelated uncommitted change (a background-image swap in
`src/base/background.css` + dist rebuild) that predates this work — leave it to the user.

Under `live2d/`: `PIPELINE.md` (authority), `DECISIONS.md`, `BASE.md`, `RIG_GUIDE.md`, `lotte.cmo3`
(editable rig master — committed), `model/` (runtime set: moc3 v5 + textures + physics3 + cdi3),
`runtime-check-full.html` + `w5-runtime-*.png` (verify harness + evidence), `source/` (rasters +
SHA256SUMS), `gen/PROMPTS.md`, `tools/` (separation + `check_model.py`), and `pilot/` (the Phase 1.0
pilot). Python = `live2d/pilot/.venv` (Pillow/rembg/psd-tools/pytoshop). Phase 0 artifacts in
`experiments/live2d-spike/`.

## Carry-forward facts (do not re-derive)

- **RUNTIME — the Lotte rig is Cubism 4.** Triplet = official Cubism 4 core (`live2dcubismcore.min.js`)
  + `pixi.js@6.5.10` + `pixi-live2d-display@0.4.0/dist/cubism4.min.js`. (Phase 0's `cubism2.min.js` +
  `dylanNew` core were for the Shizuku *sample* only — never for the Lotte rig.)
- **moc3 export MUST target ≤ v5.** Cubism Editor 5.3 exports moc3 **v6** by default; the pinned web
  Core reports `csmGetLatestMocVersion()=5` and **rejects v6**. Export at `.moc3 file version` **5.0**
  (or 4.2). Fallback: bump the Core / use the `pixi-live2d-display-lipsyncpatch` fork. *(Pilot-confirmed.)*
- **Texture atlas: Cubism FREE = a SINGLE 2048×2048 atlas** (NOT 4096; multiple atlases are PRO-only —
  web-verified W4.1). Keep hi-res masters in `live2d/assets/`, and pack the ~19 parts into the one atlas
  via Auto Layout "set magnification automatically" (≈0.5× on layout). *(Supersedes BASE.md's earlier
  4096 assumption and any "2-atlas" wording.)*
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

- **Shell:** prefix dev commands with `rtk`. **`master`:** it is the authority now (spike merged in), but
  **local-only and NOT pushed** — never push or force-push without sign-off; new commits only (no amend
  of pushed history). **Aesthetic:** Tier 1 restraint is the whole game — for hair/ribbon physics the
  liveness comes from phase *lag*, not amplitude (CDP-verified: ribbon trails the head ~5 frames).

## Stopping conditions

Stop and report at: any user-action task (a Cubism GUI edit for polish, a Discord verify), any decision
that genuinely needs the user (esp. an art/tune call, or pushing `master`).
