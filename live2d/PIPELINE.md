# Lotte Live2D — Pipeline Tracker (authority)

Read this FIRST every session. Pipeline state lives here, not in handoffs or memory.

## Current state / next action
- Phase 1.0 pilot: IN PROGRESS. Tasks 0–4 + Task 5 Step 1 done (runtime PASS; aligned 6-layer source + lotte-pilot.psd; RIG_GUIDE.md pilot walkthrough written). **BLOCKED ON USER: Task 5 rig** — open lotte-pilot.psd in Cubism 5 FREE, follow RIG_GUIDE.md, export to live2d/pilot/model/lotte-pilot.model3.json. Then agent resumes Task 6 (runtime verify) → Task 7 gate.
- Pilot Python = live2d/pilot/.venv (Pillow 12.2.0); default python3 is 3.14 with no PIL and is PEP-668 externally-managed.

## Phase 1.0 — Vertical-Slice Pilot
| Task | Status | Artifact |
|---|---|---|
| 0 Scaffold docs | DONE | PIPELINE.md, DECISIONS.md, RIG_GUIDE.md |
| 1 Cubism 4 runtime pre-flight | PASS | live2d/pilot/runtime-check.html + 1-runtime-check.png |
| 2 Face crop | DONE (803×690) | live2d/pilot/face-crop.png |
| 3 GPT eyes-closed ref (USER) | DONE (drift: mouth) | live2d/pilot/gen/eyes-closed.png |
| 4 Scripted 6-part separation | DONE (rembg matte clean; mouth marginal) | live2d/pilot/layers/*.png + RESULT.md |
| 5 Cubism rig (user) | Step1 DONE (guide+PSD); AWAITING USER rig | live2d/pilot/lotte-pilot.psd → model/*.model3.json |
| 6 Runtime verify | | live2d/pilot/RESULT.md + screenshot |
| 7 Gate decision | | RESULT.md decision |

## Full build (W1–W5) — roadmap, detailed AFTER the pilot gate
See the plan's roadmap section.
