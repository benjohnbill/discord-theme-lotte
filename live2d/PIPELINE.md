# Lotte Live2D — Pipeline Tracker (authority)

Read this FIRST every session. Pipeline state lives here, not in handoffs or memory.

## Current state / next action
- **Phase 1.0 pilot: COMPLETE — gate = GO.** Whole chain proven end to end (art→harvest→separation→PSD→Cubism rig→moc3 v5→runtime render+tilt+blink). See live2d/pilot/RESULT.md Task 7.
- **W1 (base lock + upscale): DONE (2026-05-31).** Base re-confirmed = `lotte-discord-original.png` (1254², more facial px than `version`'s 992). Hi-res master = `live2d/assets/lotte_base.png` (2508×2508) via **PIL Lanczos x2 fallback** (no neural upscaler in env — softer; re-upscale before W3 if edge crispness insufficient). Source checksums byte-identical (unchanged). **Atlas-packing decision still pending W3.4** (FREE 2048 cap). **Next action: execute W2** (generative source pack — first agent task W2.1 harvest_check.py, then USER GPT-image-2 edits W2.2–W2.5).
- **W1–W5 full-build plan WRITTEN:** `docs/superpowers/plans/2026-05-31-lotte-live2d-full-build-w1-w5.md` (carries all pilot learnings). Headline constraints baked in: moc3 export ≤ v5; Cubism FREE atlas cap = 2048; W4 = mesh-deformation blink + L/R eyes + gaze + ~20 parts + restrained smile state machine.
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
