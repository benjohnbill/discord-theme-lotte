# Doc Architecture Registry

> The **volatile target list** for the `reconcile-docs` skill. The skill is the stable
> *procedure*; this file is the *what-to-check*. When the doc structure or a locked decision
> changes, update THIS file — not the skill. The skill audits this registry against reality
> each run (and proposes updates when it finds drift between them).

## Orientation surfaces — where "where are we / what's next / what was decided" lives

| # | Surface | Path | Role | Fix mode |
|---|---|---|---|---|
| 1 | Launcher | `docs/superpowers/next-session-prompt.md` | Thin "paste to start" handoff | auto-fix (but see split-brain) |
| 2 | Design spec | `docs/superpowers/specs/<date>-*-design.md` | The "why" + locked decisions | auto-fix wording; **propose** decision changes |
| 3 | Plan | `docs/superpowers/plans/<date>-*.md` | The "how". **Completed plans = history** | annotate "SUPERSEDED"; never rewrite |
| 4 | Pipeline tracker | `live2d/PIPELINE.md` | Live pipeline-state **authority** (created in pilot Task 0) | auto-fix |
| 5 | Working docs | `live2d/{DECISIONS,BASE,RIG_GUIDE}.md`, `live2d/source/README.md`, `live2d/gen/PROMPTS.md` | Decisions, base lock, rig guide, source lineage, prompt audit log | auto-fix |
| 6 | Phase 0 record | `experiments/live2d-spike/FINDINGS.md` | History (Phase 0 GO) | annotate; don't rewrite |
| 7 | **Memory index** | `~/.claude/projects/-home-benjohnbill-dev-discord-theme-lotte/memory/MEMORY.md` | Auto-loaded each session | auto-fix |
| 8 | **Memory files** | `~/.claude/projects/-home-benjohnbill-dev-discord-theme-lotte/memory/*.md` | Auto-loaded; load-bearing | auto-fix |
| 9 | claude-mem observations | (search / `get_observations`) | Immutable point-in-time history | never edit; disambiguate via 1/2/7/8 |

**Memory-layer mechanic (easy to forget — it is OUTSIDE the repo):** surfaces 7/8 are the cross-session memory. Editing the on-disk `.md` files is what persists; the shorter copy injected into the session prompt is a *summary* of them. Always reconcile the memory layer, not just in-repo docs.

**Read order for a fresh session:** launcher (1) → memory (7 → 8) → spec (2) → plan (3) → PIPELINE (4, once Task 0 created it).

## Cross-doc invariants — must hold; check every run

These are the "if A changed, B must match" rules. **They are volatile — update them as decisions change.**

- **INV-1 Runtime.** The Lotte **rig** uses **Cubism 4** (`live2dcubismcore.min.js` + `pixi-live2d-display@0.4.0/dist/cubism4.min.js`). Cubism 2 (`dylanNew` core + `cubism2.min.js`) was Phase 0's Shizuku **sample** only. Any doc telling the next session to use cubism2 *for the rig* is STALE.
- **INV-2 Base.** Rig the character from `lotte-discord-original.png` (more facial px); background from `lotte-discord-version.png` (pixel-aligned outpaint). Rasters live in `live2d/source/`, **never** `src/`. Any doc saying base = `version`, or path `src/...`, is STALE.
- **INV-3 Frontier.** Current frontier = the **Phase 1.0 vertical-slice pilot** (execute `plans/2026-05-31-lotte-live2d-phase1-rig.md`). Any launcher/memory saying "start with brainstorming" or naming Phase 0 as the next action is STALE.
- **INV-4 Not-yet-created authorities.** `PIPELINE.md` / `DECISIONS.md` / `RIG_GUIDE.md` are created in pilot Task 0. Docs must say "authority **once Task 0 creates it**", not assert it exists now.
- **INV-5 Split-brain.** The Live2D work is on the **unmerged `live2d-spike` worktree**; `master` still holds Phase 0 orientation (its launcher is stale). `master` is protected (no direct edits) → **escalate** the merge-vs-keep-worktree decision to the user; do not silently edit master.

## Branches / worktrees in play

- `master` — main; protected. Holds an old Phase 0 launcher (split-brain source).
- `live2d-spike` — the Live2D initiative (unmerged). All Phase 1 work + this registry live here.
- Other worktrees (`m5-drift-conventions`, `registry-hardening`, …) are separate initiatives — out of scope for Live2D reconciliation unless they hold a shared `CONTEXT.md`/glossary.
