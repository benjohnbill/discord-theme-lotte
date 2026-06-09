# cd4-blink

| 메타 | 값 |
|---|---|
| 시작 | 2026-06-02 |
| 상태 | active |
| Parent strategy | `docs/features/tongjja-rig/` (ADR-0001 통짜). This investigation archives when blink resolves; the strategy + `RIG_PROCEDURE` outlive it. |

The active investigation: blink (CD-4) under the 통짜 whole-image-warp pivot. Blink is the **sole remaining
blocker** — head-lean gaze (Phase A) + breath already drive live in real Discord.

## 외부 산출물 참조

- **부모 전략(parent strategy): `docs/features/tongjja-rig/`** (INDEX + the 통짜 `RIG_PROCEDURE` walkthrough)
- 결정 (pivot): `docs/adr/0001-rig-strategy-pivot-deform-to-swap.md`
- 결정 (locked constraints): `docs/adr/0004-locked-tier1-rig-constraints.md`
- 사실 (platform/tool): `live2d/DOMAIN_MAP.md`
- 용어: `live2d/CONTEXT.md` (통짜 base / band·frame-swap / under-fill / patchwork / scene plate)
- 상태 권위: `live2d/PIPELINE.md` (current state + done-log)
- 스펙: `docs/superpowers/specs/2026-05-31-lotte-live2d-phase1-rig-design.md`
- 플랜 (history): `docs/superpowers/plans/2026-05-31-lotte-live2d-full-build-w1-w5.md`
- verify recipe: `live2d/cd_render.html` + `live2d/tools/{cd_capture,blink_render}.py` over `gen/scene-plate.png`

## 로컬 산출물

- `RESEARCH.md` — domain learning (❓ 3 open · ✅ 3 graduated)
- `DECISIONS.md` — feature-local decisions
- The 통짜 rig walkthrough is **strategy-level**: `docs/features/tongjja-rig/RIG_PROCEDURE.md`

## 열린 ❓ (blocker — PIPELINE next-action points here)

- **❓ blink warp root cause = pixi-live2d-display@0.4.0 vs inherent model/mesh** (`RESEARCH.md` §2.1).
  Gate = the localization test (full-silhouette band at **opacity 100 / Angle 0** in Cubism). Clean ⇒ pixi
  → FREE library bump; warps ⇒ model → re-bind / PRO mesh-copy. **Re-test cleanly post-restructure** (§3.1).
- ❓ which expression bands to actually WIRE — blink definite; `eyeband_smile` (^^) / `mouthband_closed`
  (snap) optional, decided on-screen · 2-state vs 3-state blink (`RESEARCH.md` §2, `../tongjja-rig/RIG_PROCEDURE.md` CD-5).

## DOMAIN_MAP 승급 후보 (✅ 검증 완료 → 이미 졸업)

- ✅ premultiplied-alpha edge → full-silhouette bands (출처: `RESEARCH.md` §1.2)
- ✅ Replace-not-Add · re-mesh on Enter · verify-exported (출처: `RESEARCH.md` §1.3)
- ⛔ Cubism PRO mesh-copy unavailable in FREE (출처: `RESEARCH.md` §2.1)

## Related

- `scene-plate` (Phase B — the congruent backdrop the rig composites over; ACCEPTED, not yet a folder)
- `phase-d-reexport` (the 통짜 core re-export loop; agent-prep DONE, USER Cubism re-rig pending)
