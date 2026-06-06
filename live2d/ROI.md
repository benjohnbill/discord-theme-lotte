# Lotte rig — pivot ROI / cost / feasibility pass + gated execution plan

Status: **confirmed 2026-06-01** (grill-with-docs). Companion docs: `CONTEXT.md` (glossary),
`PIPELINE.md` (authority/frontier). This doc is the rig-strategy pivot's cost/feasibility analysis and
the gate-ordered execution plan.

**Reading rule:** nothing here overrides a measurement. The *Locked architecture* section is
evidence-backed and stable. The *Gate-dependent* items are decided by their phase, not asserted here.

## Locked architecture (evidence-backed; stable across the gate)

- **Pivot:** drop face mesh-deform → **통짜 (whole-image warp) base + frame-SWAP for blink.** Root cause of
  the live patchwork = W4 mesh-deform of ~13 hard-rectangular face cuts (`full_segment.py` brow/sclera/iris/
  lid/mouth boxes) on a **flat, no-under-drawing** source. The pilot's opacity-**swap** blink passed its gate
  (`pilot/RESULT.md`). We revert to swap — at full scale, single **feathered** eye-band, no hard cuts.
- **Compositing:** **BG-scene** (scene plate — character inpainted out of `version`), not the character-bearing
  version wallpaper (which would cause **doubling**). See CONTEXT.md.
- **Gaze:** head/body-lean toward the cursor (`model.focus()` driving Angle/Body, **eyeball weight 0**) — no
  iris cut. Iris-translate would reveal undrawn sclera on a flat source and would conflict with the eye-band swap.
- **Blink mechanism (if it survives the gate):** feathered eye-band **opacity-swap** on `ParamEyeLOpen/ROpen`.
  NOT mesh-deform, NOT hard lid crops.

## Gate-dependent (NOT locked — each phase measures, then decides)

- (a) mouth keep/drop · (b) 2-state vs 3-state blink · whether blink survives at real Discord scale ·
  the ROI **contribution** weights themselves (contribution cannot be measured without rendering).

## Element table

Contribution shown with *confidence*; cost grounded in the reuse basis below.

| # | Element | Realization | Feasibility (flat + BG-scene) | Cost (art + rig) | Contribution + confidence | Disposition |
|---|---|---|---|---|---|---|
| 1 | breath / micro-sway | whole-warp `ParamBreath` | PROVEN | ~0 (reuse) | baseline life · high-conf | FREE |
| 2 | **gaze = head-lean** | `focus()`→Angle/Body, eyeball=0 | PROVEN | LOW (focus config + damp) | HIGH (presence = North Star) · high-conf | FREE-tier |
| 3 | restrained tilt/turn | whole-warp Angle, small | PROVEN small / AVOID large | ~0 + amplitude clamp | medium · high-conf (live "too large" → clamp) | FREE |
| 4 | ribbon / hair-tail sway | physics (existing deformers) | CONDITIONAL (over scene plate, untested) | LOW-MED (reuse + retune) | medium (the scarf liveness) · **uncertain** (only seen fail over gray) | TEST EARLY |
| 5 | scene plate | AI inpaint (remove character) | PROVEN-ish (soft bokeh) | LOW-MED (1 pass, no manual) | infra: unlocks #4 + prevents doubling + fair backdrop · high-conf | PREREQ |
| 6 | **blink** | feathered band opacity-swap | UNCERTAIN @ real scale (pilot = small only) | MED (re-align closed band + rig; reuse raw) | HIGH · **uncertain** (Genshin alive without blink) | GATE before commit |
| 7 | mouth open/close | needs inner-mouth under-drawing | INFEASIBLE-clean on flat | HIGH (new art + rig) | low · **unverified** (speech-bubble doesn't exist yet) | VERIFY claim → DROP |
| 8 | remove failed face cuts + bake into 통짜 | re-run `full_segment.py` with fewer parts → re-export | PROVEN (W3↔W4 loop) | MED-HIGH (heavy re-export; W5 seam-fix rides along) | removes class-B patchwork · high-conf necessary | CORE (after B/C signal) |

## Gate-ordered execution (cheap measurements gate expensive commits)

- **Phase A — PASS (2026-06-02, committed `3228a2a`).** Clamp tilt/turn amplitude + gaze = head-lean,
  wired in `build_discord_probe.py` + `runtime-check-full.html` (`im.updateFocus` override; `GAZE = {eye:0, xy:8,
  z:6, body:5}` — eyeball weight 0 = no iris cut; Angle/Body gains clamped from the lib default 30/30/10 → 8/6/5;
  FocusController spring still damps). USER-confirmed in real Discord (calmer / less 경박, iris steady) → Phase B.
- **Phase B — DONE (2026-06-02): verdict = Phase D NEEDED.** Scene plate `gen/scene-plate.png` (USER GPT-image-2;
  character removed + halo completed) ACCEPTED; rendered the existing rig over it (harness `?imgbg=`, **no
  re-export**). Result: (1) ✅ congruent-backdrop hypothesis confirmed — coherent wallpaper, no floating-sticker /
  no fringe; (2) natural BIG framing chosen (body fills frame, matches `version`); (3) ⚠️ at that scale the
  rectangular patchwork seams are clearly visible ⇒ **Phase D confirmed NECESSARY** (element #8). Evidence
  `live2d/phaseB-*.png`.
- **Phase C — blink: HIT A WARP/DISTORTION WALL (2026-06-03); now gated behind a localization test (USER
  decision 2026-06-06).** The closed-eye band was rigged as an opacity-swap and re-rigged across ~10 rounds.
  **Both band variants fail:** island-to-string → visible artifacts; full-silhouette (the landing mechanism) →
  **warp/distortion on the eyelids** when the blink opacity drives. **Root cause UNCONFIRMED** — pixi-live2d-
  display@0.4.0 runtime bug (⇒ clean in Cubism ⇒ FREE-tier library bump fixes it) vs inherent model/mesh
  (⇒ warps in Cubism ⇒ re-bind / PRO mesh-copy, which FREE lacks). Gaze (Phase A) + breath already drive live
  in Discord, so **blink is the SOLE blocker.** USER DECISION (2026-06-06) = run the single definitive
  localization test FIRST (full-silhouette band at **opacity 100, Angle 0** in Cubism) before any more dev;
  routes to a library bump (pixi) or a model re-bind / PRO mesh-copy (model). Option 2 (defer blink, ship
  gaze+breath) is the fallback if the test is discouraging. Authority + full saga = `PIPELINE.md` top frontier
  bullet + memory [[live2d-cubism-rig-gotchas]] §3.
- **Phase D — core re-export (commit only after B/C signal). AGENT PREP DONE (2026-06-02).** `full_segment.py`
  rewritten to the 통짜 cut + `build_psd_full.py` updated → new `lotte.psd`, agent-verified (no holes/doubling,
  soft sway reveal, swaps read, edge-detect = no band rectangle). As-built = 7 layers: a SINGLE feathered
  `base` (no head/body PSD split; eyebrows baked in; front locks + ribbon carved over a soft under-fill backing)
  + `eyeband_closed`/`eyeband_smile`/`mouthband_closed` swap bands + `hair_L/R` + `ribbon`. The deferred W5 (c)
  seam-fix (FEATHER=30) rides along. **Remaining = the USER Cubism re-rig (whole-warp + opacity-swap blink) →
  re-export (moc3 5.0) → verify over the scene plate.**
- **mouth (#7) + eye-smile — feasibility decided (2026-06-02):** on a flat source all expression = an opacity
  frame-swap of baked art (same trick as blink; refs in `gen/refs/`). **eye-smile ^^ and closed-mouth-SNAP are
  cheap + feasible** (one band + one opacity binding each); **smooth / talking mouth is INFEASIBLE** (would need
  mesh-deform = patchwork, or many visemes) → revises #7: DROP *smooth* mouth, speech-bubble carries talking
  (still unverified). Plan: include all candidate bands in the 통짜 PSD; USER wires blink (definite) + ^^ /
  closed-mouth (optional) in Cubism, deciding on-screen.

### Why this order
Phase A + B need no heavy work and no re-export — config tuning + one inpaint + a re-render. They are the
cheapest, fastest, highest-information moves, and they gate the expensive re-export (D) and blink art (C).
Measurement gates commitment.

## Reuse basis (cost-column grounding, verified 2026-06-01)

- Rig already exposes: `ParamAngleX/Y/Z`, `ParamBodyAngleX/Y/Z`, `ParamBreath`, `ParamHairSide/Front/Back`
  (physics-driven), `ParamEyeLOpen/ROpen`, `ParamEyeBallX/Y`, brow/cheek/`MouthForm`/`MouthOpenY`, `EyeL/RSmile`.
- Probe (`tools/build_discord_probe.py`) already wires cursor → `model.focus(clientX, clientY)` (currently
  drives the iris too → set eyeball weight 0 for head-lean).
- Closed-eye source `pilot/gen/eyes-closed-raw-1353x1163.png` exists (face-crop scale → re-harvest at full base).
- hair/ribbon physics deformers exist (`model/lotte.physics3.json`), CDP-verified for phase-lag.
