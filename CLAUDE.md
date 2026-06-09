# Agent Instructions

This repo holds two concerns — don't infer one's state from the other's rules:
1. **Vencord CSS theme** — the shipping artifact (`src/` → `dist/`).
2. **Lotte Live2D rig** (`live2d/`) — the active main work; a sub-project outside the CSS build.

## Orientation docs (in authority order)
1. **`live2d/PIPELINE.md` — READ FIRST every session.** Live pipeline-state authority (dynamic cursor: active feature + single next + done-log); state lives HERE, never in CLAUDE.md, memory, or handoffs.
2. **`live2d/DOMAIN_MAP.md` — platform/tool facts (✅/⛔).** What the toolchain always does (Cubism-FREE caps, moc3 ≤5, machine-ops, the verify recipe). No open questions — those live in `docs/features/<slug>/RESEARCH.md`.
3. **`docs/adr/` — decision records (immutable "why").** 0001 rig-strategy pivot · 0003 doc architecture · 0004 locked rig constraints; read before reopening a settled call.
4. **`docs/features/<slug>/` — active investigations.** `tongjja-rig/` = the 통짜 strategy (its `RIG_PROCEDURE` walkthrough); `cd4-blink/` = the current blink work (`INDEX` hub → `RESEARCH` open ❓ + saga · `DECISIONS`).
5. Consult as needed: `live2d/CONTEXT.md` (glossary) · `docs/superpowers/{specs,plans}/` + `docs/features/archive/` (history) · `docs/superpowers/next-session-prompt.md` (thin launcher).

> Doc architecture = ADR-0003. `reconcile-docs` + its `check_freshness.py` keep these fresh (parses this map, enforces the DOMAIN_MAP marker rule, warns on claude-mem recency, and rejects a live doc citing a dissolved one). The former registry is dissolved into this map + DOMAIN_MAP + ADR-0003 + the checker.

## Directory roles
- `src/` — CSS source of truth; `dist/NewKemonoFriends.theme.css` — generated output (never hand-edit).
- `registry/` — `selectors.yaml` (inventory) + `do-not-touch.yaml` (dangerous media/render selectors); `theme.manifest.yaml` — the only CSS build-order authority; `snapshots/YYYY-MM-DD/*.json` — raw DOM observations.
- `schema/` — JSON Schemas validating `registry/` + `snapshots/` entries.
- `scripts/` — Node theme tooling: `build-theme.js` (→ `dist/`), `validate-registry.js`, `sync-to-vencord.js`, `inspect-dom.js` (run via `npm run build|validate|sync|check`).
- `live2d/` — the rig: `source/ model/ tools/ pilot/ assets/ gen/` (+ the orientation docs above).
- `experiments/live2d-spike/` — Phase 0 record (history).

## CSS theme rules
- Treat `src/` as the CSS source of truth; `dist/…` is generated.
- Do not edit files in the Vencord themes directory directly from this repo.
- Add raw DOM observations to `snapshots/YYYY-MM-DD/*.json`.
- Update `registry/selectors.yaml` when a selector is added, removed, or reclassified.
- Add dangerous media/rendering selectors to `registry/do-not-touch.yaml`.
- Run `npm run check` before syncing.
