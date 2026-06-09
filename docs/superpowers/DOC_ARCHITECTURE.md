# Doc Architecture Registry — DISSOLVED (2026-06-09)

> This registry (surface list + `INV-*` invariants) was **dissolved** (ADR-0003). It had become a fourth
> copy of the frontier and a second place to keep in sync. Its parts were routed by type:

| Was… | Now lives in |
|---|---|
| The **doc map / read-order** (surface table) | `CLAUDE.md` ("Orientation docs" entry-path) |
| The **`INV-*` platform facts** (runtime, base, atlas, moc3, eye-smile, …) | `live2d/DOMAIN_MAP.md` (✅/⛔) |
| The **doc-architecture decision** (this restructure, the organizing principle) | `docs/adr/0003-doc-architecture-harness-alignment.md` |
| The **cross-doc agreement *rules*** (INV denylist, frontier agreement, branch-state) | `.claude/skills/reconcile-docs/check_freshness.py` (the executable half — **capability preserved, re-aimed**, not deleted) |
| The frozen full registry text | `docs/features/archive/doc-architecture-pre-restructure-2026-06-09.md` |

The `reconcile-docs` skill no longer reads a registry: `check_freshness.py` now parses its target list from
the `CLAUDE.md` map, enforces the DOMAIN_MAP marker rule, and warns when claude-mem has observations newer
than the authority's as-of date.
