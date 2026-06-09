# Lotte Rig Guide — DISSOLVED (bifurcated 2026-06-09)

> This standalone rig guide was **dissolved** (ADR-0003). A standalone procedure doc churned wholesale every
> strategy pivot (three generations: Pilot / W4 / CD) and had no archive path. Its content is bifurcated by
> type. **There is no longer a single rig guide — go to the home for what you need:**

| You want… | Now lives in |
|---|---|
| The **current** rig procedure (통짜 whole-image warp + opacity-swap bands, CD-1..9) | `docs/features/tongjja-rig/RIG_PROCEDURE.md` |
| **Strategy-invariant editor facts** (Replace-not-Add, re-mesh on Enter, single-2048 atlas, moc3 ≤ 5, the SwiftShader verify recipe, 1-param-per-deformer) | `live2d/DOMAIN_MAP.md` |
| **Locked rig constraints** (flat discipline — formerly "`DECISIONS.md §6`" — scope / background-out / Tier-1 restraint) | `docs/adr/0004-locked-tier1-rig-constraints.md` |
| The **pivot decision** (why mesh-deform → 통짜) | `docs/adr/0001-rig-strategy-pivot-deform-to-swap.md` |
| Glossary (통짜 base / band / under-fill / patchwork) | `live2d/CONTEXT.md` |
| The **first build** (Pilot Step 0–8 + W4 Step 1–11 mesh-deform rig) — history | `docs/features/archive/rig-guide-pre-restructure-2026-06-09.md` |

The **as-built** deformer tree / params are owned by the model files (`live2d/pilot/lotte-good.cmo3`,
`live2d/model/lotte.model3.json`), not duplicated in docs.
