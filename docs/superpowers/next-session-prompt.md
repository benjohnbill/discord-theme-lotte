# Next Session — Lotte Live2D — CD-4 blink HIT A WARP WALL (06-03); NEXT = USER runs the opacity-100/Angle-0 localization test (06-06 decision)

> Phase 0 = DONE/GO. Phase 1.0 pilot = DONE/GO. **Phase 1 full build = mechanically DONE/PASS (W1–W5 +
> physics, 2026-06-01) but SUPERSEDED on quality:** the first live Discord render exposed the
> mesh-deform rig as "누더기" (patchwork). A **rig-strategy pivot is decided** (`docs/adr/0001-rig-strategy-pivot-deform-to-swap.md`):
> face mesh-deform → **통짜 (whole-image warp) base + blink frame-swap + BG-scene + gaze = head-lean**. The
> gate-ordered execution plan is **`live2d/ROI.md`**. **`live2d-spike` was merged into `master` and removed —
> `master` is the single authority** (local-only, well ahead of origin, NOT pushed). This launcher is thin —
> substance lives in `live2d/PIPELINE.md` + `live2d/ROI.md` + `live2d/CONTEXT.md` + the ADR + auto-loaded memory.

Paste the body below (inside the `---` block) into the next Claude session as the initial prompt.

---

## Task

**Phase 1's rig is mechanically complete but its QUALITY is superseded** — the live Discord render exposed
the mesh-deform rig as "누더기" (patchwork). The **rig-strategy pivot (ADR-0001) is decided**; the next work
is its gate-ordered execution, NOT "Phase 1 done → Phase 2". Read `live2d/PIPELINE.md` + `live2d/ROI.md` FIRST.

**START HERE — CD-4 BLINK HIT A WARP/DISTORTION WALL (2026-06-03); NEXT = the USER runs ONE localization
test (2026-06-06 decision).** The Angle channel + deformer tree are DONE + GO (2026-06-02); blink is the
SOLE remaining blocker (gaze + breath already drive live in Discord). On 06-03 the full-silhouette opacity-
swap re-rig was completed and rendered — **both band variants fail** (island-to-string → artifacts; full-
silhouette → **warp/distortion on the eyelids**), **root cause UNCONFIRMED** (pixi-live2d-display@0.4.0
runtime bug ⇒ FREE library bump fixes it, vs inherent model/mesh ⇒ re-bind / Cubism PRO mesh-copy which
FREE lacks). Read `live2d/PIPELINE.md` FIRST — its TOP 2026-06-06 frontier bullet carries the wall, the
pixi-vs-model fork, and the exact next action. **NEXT ACTION (USER, Cubism):** set the full-silhouette band
to **opacity 100 at Angle 0** and look — clean ⇒ pixi-specific (Claude then verifies a library bump in the
SwiftShader harness); warps ⇒ model/mesh (re-bind, or PRO mesh-copy). Option 2 (defer blink, ship
gaze+breath as sufficient) is the fallback if the test is discouraging. For context, the as-built rig: in
Cubism the USER has built: import + auto-mesh → deformer nest
`body_warp ▸ head_x ▸ head_y ▸ head_warp ▸ {base, bands, hair, ribbon}` → **Angle X/Y/Z (one param
per warp** — dodges the FREE 2-param cap AND fixes the diagonal-blend distortion) → single-2048 atlas
→ one judgment export (moc3 v5). **④ blink** (CD-4 in `RIG_GUIDE.md`) — key `eyeband_closed`
opacity on `ParamEyeLOpen` (1→0, 0→100) — **was rigged 06-03 and HIT THE WARP WALL (see START HERE); it
resumes only after the localization test clears the warp.** Then ⑤ smile/mouth opacity, ⑥ `ParamBreath`+`ParamBodyAngleX`
keys on `body_warp`, ⑦ hair/ribbon physics, final export to **`live2d/model/`** → `tools/check_model.py`
→ re-render. **Verify recipe:** `live2d/cd_render.html` + `live2d/tools/cd_capture.py` (SwiftShader CDP
over the scene plate; **preserveDrawingBuffer + NO --virtual-time-budget are mandatory**). Eyes read
closed until blink is wired (no runtime hack hides the bands — pixi caches drawable opacity). Phase A (config tune)
**PASS**: head-lean gaze (`im.updateFocus` override, `GAZE={eye:0,xy:8,z:6,body:5}`, eyeball 0 = no iris
cut) shipped in `build_discord_probe.py` + `runtime-check-full.html`; USER-confirmed in real Discord.
Phase B (scene plate) **measured**: USER's GPT-image-2 plate `live2d/gen/scene-plate.png` ACCEPTED; the rig
composited over it (harness `?imgbg=`, **no re-export**) reads as a coherent wallpaper at the **natural BIG
framing** (scale≈0.58 over the 1586×992 plate, body fills the lower frame — matches the `version` wallpaper),
BUT at that scale the rectangular patchwork seams are clearly visible ⇒ **Phase D (collapse face cuts into a
통짜 base + feather) is confirmed NECESSARY.** Evidence `live2d/phase{A,B}-*.png`.

**NEXT — the work (Phase C+D collapse into ONE Cubism re-export):**
1. **AGENT (Tier-1, no re-export) — DONE (2026-06-02).** `tools/full_segment.py` rewritten to the
   **통짜 cut** + `build_psd_full.py` DEPTH updated → new `live2d/lotte.psd`, agent-verified (no
   holes/doubling; a hair/ribbon sway reveals soft colour not a hole; blink/eye-smile/closed-mouth
   swaps read; edge-detect shows NO band rectangle — the feather killed the seam). **As-built = 7
   layers:** `base` (통짜 whole character, open eyes + open mouth baked in; front hair-locks + ribbon
   carved feathered over a soft under-fill backing + real cheek skin) + `mouthband_closed` +
   `eyeband_smile` + `eyeband_closed` + `hair_L` + `hair_R` + `ribbon`. Resolved the open choice →
   **SINGLE `base`, no head/body PSD split** (head-tilt + body-lean = whole-warp deformers in Cubism;
   a neckline cut would re-add a seam). Band coords: eyeband x0.27–0.72 y0.36–0.56, mouthband
   x0.42–0.60 y0.575–0.68; FEATHER=30.
2. **USER (Tier-3, Cubism GUI — `live2d-authoring` boundary) — IN PROGRESS** (import + deformer nest +
   Angle X/Y/Z DONE + GO; **④ blink HIT A WARP WALL 06-03 → the immediate next step is the opacity-100/Angle-0 localization test — see START HERE**): re-import
   `lotte.psd` → rig as **whole-image warp** (`base` under `ParamBreath` / `ParamAngleX/Y/Z` /
   `ParamBodyAngleX`; a head-region warp gives tilt) + `hair_L/R` + `ribbon` on physics deformers
   (reuse `model/lotte.physics3.json` feel) + **blink = `eyeband_closed` drawable OPACITY keyed to
   `ParamEyeLOpen/ROpen`** (0 = open base shows, 1 = closed band covers; 2-state first) + optional
   `eyeband_smile` (^^) / `mouthband_closed` (snap) opacity, decided on-screen (blink overrides smile)
   → export **moc3 5.0** → `check_model.py` → verify over `gen/scene-plate.png` at real Discord scale.

APPROVED part-list + per-band feasibility + step-by-step are in the 통짜 handoff doc (this session's
`/handoff` output) and PIPELINE. **Feasibility (decided this session):** on a flat source ALL expression
is an opacity frame-swap of baked art (same trick as blink; refs already exist in `gen/refs/`). blink =
ideal; **eye-smile ^^ = cheap + good**; **closed-mouth = cheap as a fast SNAP**; **smooth/talking mouth =
INFEASIBLE on flat** (would need mesh-deform = patchwork, or many visemes) → that is the speech-bubble's job.
Plan: include ALL candidate bands in the PSD (cheap), USER wires blink (definite) + ^^/mouth (optional)
in Cubism, deciding on-screen. Verify only in the real Discord client or a SwiftShader throwaway Chrome.

**Open / decided-live-in-Cubism:** which swap bands to actually WIRE (blink definite; ^^ / closed-mouth
optional, decide on-screen) · 2-state vs 3-state blink · blink survival at real scale.

**Background (resolved/deferred — NOT the next step):**
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
- **Phase 2 — productionize the Discord delivery (DEFERRED behind the pivot — NOT next):** a persistent
  always-on background needs a Vencord userplugin (dev Vencord + Node/git on Windows; themes/QuickCSS
  can't run JS). Feasibility already proven in Phase 0. Schedulable only after the pivot lands.
- **Push `master`:** Tier-3, needs explicit user sign-off (never push yourself).

**W3↔W4 re-export loop (Phase D):** edit `full_segment.py` (band coords / `feather_col` / `FEATHER` /
under-fill) → re-run `full_segment.py` + `build_psd_full.py` → re-import to Cubism → re-rig → re-export (moc3 5.0) →
`check_model.py` → re-verify with `live2d/runtime-check-full.html`. The deferred W5 seam-fix (feather)
rides along here.

## Read first (substance, in order)

1. `MEMORY.md` auto-loads → `lotte-live2d-aliveness-direction` (decided design + Phase 0 GO + pilot GO +
   the confirmed learnings + **Phase 1 build DONE**) and `bh-chrome-no-webgl` (no headless WebGL → use a
   SwiftShader throwaway Chrome for any render check).
2. **`live2d/PIPELINE.md`** — the live pipeline-state **authority** (where are we / what's done / what's next).
2b. **`live2d/ROI.md`** — the rig-strategy pivot's gate-ordered plan (Phase A→D) + cost/feasibility table;
   **`docs/adr/0001-rig-strategy-pivot-deform-to-swap.md`** = the pivot decision; **`live2d/CONTEXT.md`** =
   glossary (통짜 base / scene plate / doubling / patchwork).
3. **Spec:** `docs/superpowers/specs/2026-05-31-lotte-live2d-phase1-rig-design.md` — goal, 8 locked
   decisions, layer map, params, success criteria.
4. **Plan (now history):** `docs/superpowers/plans/2026-05-31-lotte-live2d-full-build-w1-w5.md` — the
   W1–W5 build, completed; useful as the record of how each stage was done (don't re-execute).
5. **Runtime/physics evidence:** `live2d/w5-runtime-*.png` + the harness `live2d/runtime-check-full.html`
   (`?autosine`/`?cinema` for motion); `live2d/pilot/RESULT.md` is the pilot record.

## Working directory

`/home/benjohnbill/dev/discord-theme-lotte` on branch **`master`** (the live2d-spike worktree was merged
and removed 2026-06-01 — do not look for it). **`master` is the single authority.** It is **local-only:
well ahead of `origin/master`, NOT pushed** — pushing is Tier-3 (sign-off only; never push/force
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
