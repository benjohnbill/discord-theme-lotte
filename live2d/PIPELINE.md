# Lotte Live2D — Pipeline Tracker (authority)

Read this FIRST every session. **This is the dynamic cursor only — active feature + the single next action
+ a one-line done-log.** Facts live in `DOMAIN_MAP.md`, decisions in `docs/adr/`, the active investigation in
`docs/features/cd4-blink/`; this file links them, it does not copy them. History (the pre-restructure
14-bullet stack) is frozen in `docs/features/archive/`.

## Current state / next action  *(as of 2026-06-10)*

- **Active feature: `docs/features/cd4-blink/`** — blink (CD-4) under the 통짜 whole-image-warp pivot
  (ADR-0001). **Blink is the SOLE remaining blocker:** head-lean gaze (Phase A) + breath already drive live
  in real Discord; the deformer tree + Angle X/Y/Z are DONE + GO (2026-06-02).
- **Blink state = UNRESOLVED, `❓`.** CD-4 hit a warp/distortion wall (06-03); a later read showed
  Cubism-clean / runtime-patchwork, but that verdict is **not trusted** — stale docs had contaminated the
  verification loop. Root cause (pixi-live2d-display@0.4.0 runtime vs inherent model/mesh) is **unconfirmed**.
  Full narrative: `docs/features/cd4-blink/RESEARCH.md` §2–§3.
- **▶ SINGLE NEXT ACTION:** within **Phase C**, the USER runs the **localization test** — full-silhouette
  band at **opacity 100 / Angle 0** in Cubism, **re-tested cleanly now that the docs are restructured**.
  Clean ⇒ pixi-specific (agent verifies a library bump in the SwiftShader harness); warps ⇒ model/mesh
  (re-bind, or Cubism PRO mesh-copy which FREE lacks). Fallback = defer blink, ship gaze+breath
  (cd4-blink/DECISIONS 2026-06-06). Verify recipe + open ❓: `docs/features/cd4-blink/INDEX.md`.
- **`.cmo3` inventory:** `live2d/lotte.cmo3` was **deleted intentionally**; **`live2d/pilot/lotte-good.cmo3`
  = the working master.** Latest runtime export lands in `live2d/model/`.
- Platform/tool constraints for any of the above (moc3 ≤ 5, single-2048 atlas, Replace-not-Add, SwiftShader
  recipe, etc.) → `DOMAIN_MAP.md`. Locked rig constraints (scope / bg-out / flat / restraint) → ADR-0004.

## Done log (one line each; detail → archive / feature)

- **Phase 0** GO · **Phase 1.0 pilot** GO (`pilot/RESULT.md`).
- **Phase 1 full build — mechanically DONE/PASS, SUPERSEDED on quality (ADR-0001):** W1 base lock + Lanczos×2
  master · W2 gen pack · W3 19-part separation · W4.1 walkthrough · W4.2 USER Cubism rig · W4.3 export checker
  · W5 runtime verify (all Tier-1 channels drive) · W4 Step 9B hair/ribbon physics (CDP phase-lag verified).
  Detail → `docs/features/archive/pipeline-pre-restructure-2026-06-09.md`.
- **Pivot execution (ADR-0001):** Phase A (config tune — head-lean gaze, eyeball 0) committed `3228a2a`,
  USER-confirmed in real Discord · Phase B (scene plate `gen/scene-plate.png` ACCEPTED, composited) measured →
  **Phase D confirmed NECESSARY** · Phase C+D agent-prep (`full_segment.py` 통짜 rewrite → 7-layer `lotte.psd`)
  DONE · Phase C re-rig: import + deformer nest + Angle X/Y/Z DONE + GO; **blink = the wall (above).**
- **`master`** is the single authority (live2d-spike was merged into master and removed, 2026-06-01).
  Local-only, well ahead of `origin/master`, **NOT pushed** — pushing is Tier-3, sign-off only.

## History

The full pre-restructure tracker (every frontier bullet, the W-stage detail, W5-polish writeups, the physics
CDP measurement, the Phase 1.0 pilot table) is frozen verbatim at
`docs/features/archive/pipeline-pre-restructure-2026-06-09.md`. The blink saga is distilled in
`docs/features/cd4-blink/RESEARCH.md`. Do not duplicate either back into this cursor.
