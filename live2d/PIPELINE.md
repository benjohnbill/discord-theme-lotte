# Lotte Live2D — Pipeline Tracker (authority)

Read this FIRST every session. Pipeline state lives here, not in handoffs or memory.

## Current state / next action
- **Phase 1.0 pilot: COMPLETE — gate = GO.** Whole chain proven end to end (art→harvest→separation→PSD→Cubism rig→moc3 v5→runtime render+tilt+blink). See live2d/pilot/RESULT.md Task 7.
- **Next action: detail the full W1–W5 plan** (separate writing-plans pass), carrying the pilot learnings below. Headline: moc3 export must target ≤ v5 (Cubism 5.3 default v6 won't load on the pinned Core); Cubism FREE atlas cap = 2048 (update BASE.md 4096); W4 rig = mesh-deformation blink + split L/R eyes + gaze + ~20 parts.
- Pilot Python = live2d/pilot/.venv (Pillow/rembg/psd-tools/pytoshop); default python3 is 3.14 with no PIL and is PEP-668 externally-managed.

## Phase 1.0 — Vertical-Slice Pilot
| Task | Status | Artifact |
|---|---|---|
| 0 Scaffold docs | DONE | PIPELINE.md, DECISIONS.md, RIG_GUIDE.md |
| 1 Cubism 4 runtime pre-flight | PASS | live2d/pilot/runtime-check.html + 1-runtime-check.png |
| 2 Face crop | DONE (803×690) | live2d/pilot/face-crop.png |
| 3 GPT eyes-closed ref (USER) | DONE (drift: mouth) | live2d/pilot/gen/eyes-closed.png |
| 4 Scripted 6-part separation | DONE (rembg matte clean; mouth marginal) | live2d/pilot/layers/*.png + RESULT.md |
| 5 Cubism rig (user) | DONE | lotte-pilot.cmo3 + model/lotte-pilot.model3.json (moc3 v5) |
| 6 Runtime verify | PASS | 6-model-check.png + 6-model-check-blink.png |
| 7 Gate decision | **GO** | RESULT.md Task 7 |

## Full build (W1–W5) — roadmap, detailed AFTER the pilot gate
See the plan's roadmap section.
