# Lotte Live2D — Pipeline Tracker (authority)

Read this FIRST every session. Pipeline state lives here, not in handoffs or memory.

## Current state / next action
- Phase 1.0 pilot: IN PROGRESS. Tasks 0–2 done (runtime PASS, face crop = 803×690). **BLOCKED ON USER: Task 3** — generate eyes-closed reference in GPT-image-2, save to live2d/pilot/gen/eyes-closed.png. Then agent resumes at Task 4 (scripted separation).
- Pilot Python = live2d/pilot/.venv (Pillow 12.2.0); default python3 is 3.14 with no PIL and is PEP-668 externally-managed.

## Phase 1.0 — Vertical-Slice Pilot
| Task | Status | Artifact |
|---|---|---|
| 0 Scaffold docs | DONE | PIPELINE.md, DECISIONS.md, RIG_GUIDE.md |
| 1 Cubism 4 runtime pre-flight | PASS | live2d/pilot/runtime-check.html + 1-runtime-check.png |
| 2 Face crop | DONE (803×690) | live2d/pilot/face-crop.png |
| 3 GPT eyes-closed ref (USER) | AWAITING USER | live2d/pilot/gen/eyes-closed.png |
| 4 Scripted 6-part separation | | live2d/pilot/layers/*.png |
| 5 Cubism rig (user) | | live2d/pilot/model/*.model3.json |
| 6 Runtime verify | | live2d/pilot/RESULT.md + screenshot |
| 7 Gate decision | | RESULT.md decision |

## Full build (W1–W5) — roadmap, detailed AFTER the pilot gate
See the plan's roadmap section.
