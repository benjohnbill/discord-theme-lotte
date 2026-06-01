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

- **Phase A — near-free, high-confidence (no new art, no re-export).** Clamp tilt/turn amplitude (fixes the
  live "too large" / 경박); set gaze = head-lean (zero the focus controller's eyeball weight + damp); confirm
  breath. Applies to the **current** rig as-is → should already read better than the gray-bg footage.
- **Phase B — cheap, high-information gate.** Produce the scene plate (#5, one inpaint), then **re-render the
  existing rig over the scene plate.** Measures: (1) does ribbon/hair-tail sway (#4) read clean over a congruent
  backdrop? (2) how much of the "누더기" was alien-gray-bg unfairness vs class-B face cuts? **No re-export needed.**
- **Phase C — gated high-value, medium cost.** Re-align the closed-eye band at full base + feather; rig as
  opacity-swap. Gate at **real Discord scale**: does it read as a blink or a glitch (2-state first)?
- **Phase D — core re-export (commit only after B/C signal).** Re-segment with fewer cuts + bake eyebrows into
  `face_base` + feather + the eye-band swap + the deferred W5 seam-fix → re-import to Cubism → re-export.
- **mouth (#7):** sanity-check the "speech-bubble carries talking" claim (even a mock) before formally
  dropping; default = DROP.

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
