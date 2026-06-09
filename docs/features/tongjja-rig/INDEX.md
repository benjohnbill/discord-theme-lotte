# tongjja-rig

| 메타 | 값 |
|---|---|
| 시작 | 2026-06-02 |
| 상태 | active |
| Level | **strategy** (ADR-0001) — not a single investigation |
| Lifetime | lives for ADR-0001's lifetime; archived **whole** only at the next strategy pivot (a new ADR superseding 0001) |

The 통짜 (whole-image-warp + opacity-swap) rig **strategy** folder. It holds the reusable rigging procedure
and is the parent of the per-investigation feature folders that run under this strategy.

## 로컬 산출물

- `RIG_PROCEDURE.md` — the 통짜 CD-1..9 Cubism re-rig walkthrough (the current rig procedure, reused across
  investigations).

## Investigations under this strategy

- `docs/features/cd4-blink/` — **active.** Blink (CD-4) — the sole remaining blocker.
- (future) expression bands (^^ / closed-mouth) · re-export loops (Phase D).

## Succession (read before archiving any investigation)

`RIG_PROCEDURE.md` is **strategy-level**: it does **not** archive when an investigation closes. When
`cd4-blink` resolves and archives, the procedure's blink-specific caveats (the CD-4 warp-wall note pointing
at `cd4-blink/RESEARCH.md`) hand off to the next active 통짜 investigation — update those pointers, do not
archive the walkthrough. Only a strategy pivot (a new ADR superseding ADR-0001) archives this whole folder.

## 외부 참조

- 전략 결정: `docs/adr/0001-rig-strategy-pivot-deform-to-swap.md`
- 사실/기계조작: `live2d/DOMAIN_MAP.md` · 제약: `docs/adr/0004-locked-tier1-rig-constraints.md`
- 상태: `live2d/PIPELINE.md` · 용어: `live2d/CONTEXT.md`
