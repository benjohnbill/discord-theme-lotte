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

**Active plan (surface 3):** `plans/2026-05-31-lotte-live2d-full-build-w1-w5.md` (W1–W5). The Phase 1.0 pilot plan `plans/2026-05-31-lotte-live2d-phase1-rig.md` is **completed history** — its W1–W5 roadmap is annotated SUPERSEDED.

**Read order for a fresh session:** launcher (1) → memory (7 → 8) → **PIPELINE (4, the live authority — now exists)** → active plan (3) → spec (2) → pilot record `live2d/pilot/RESULT.md`.

## Cross-doc invariants — must hold; check every run

These are the "if A changed, B must match" rules. **They are volatile — update them as decisions change.**

- **INV-1 Runtime.** The Lotte **rig** uses **Cubism 4** (`live2dcubismcore.min.js` + `pixi-live2d-display@0.4.0/dist/cubism4.min.js`). Cubism 2 (`dylanNew` core + `cubism2.min.js`) was Phase 0's Shizuku **sample** only. Any doc telling the next session to use cubism2 *for the rig* is STALE.
- **INV-2 Base.** Rig the character from `lotte-discord-original.png` (more facial px); background from `lotte-discord-version.png` (pixel-aligned outpaint). Rasters live in `live2d/source/`, **never** `src/`. Any doc saying base = `version`, or path `src/...`, is STALE.
- **INV-3 Frontier.** Phase 1.0 pilot = **DONE/GO (2026-05-31)**. Current frontier = **execute `plans/2026-05-31-lotte-live2d-full-build-w1-w5.md` starting at W1**. Any launcher/memory saying "execute the pilot", "start with brainstorming", or naming Phase 0 / the pilot as the next action is STALE.
- **INV-4 Authorities exist.** `live2d/PIPELINE.md` (live-state authority), `DECISIONS.md`, `RIG_GUIDE.md` were created in pilot Task 0 and now EXIST; `PIPELINE.md` is read-first. Any doc still saying these are "not yet created / created in Task 0" is STALE.
- **INV-5 Split-brain.** All Live2D work is on the **unmerged `live2d-spike` worktree** (~9 commits ahead). `master` is at the **pre-pilot** state — its launcher still says "execute the pilot", and it has no pilot execution, no full-build plan, no `PIPELINE.md`. `master` is protected → **escalate** the merge-vs-keep decision; do not edit master (a one-line "SUPERSEDED → see worktree" banner on master's launcher may be *proposed*, never applied by the agent).
- **INV-6 moc3 version.** The rig `.moc3` must export at **version ≤ 5** (the pinned web Core reports `csmGetLatestMocVersion()=5`). Cubism Editor 5.3 defaults to **v6**, which **fails to load**. Any doc/plan exporting the default or assuming "any moc3 loads" is STALE; fix = export 5.0/4.2, or bump the Core / use the `pixi-live2d-display-lipsyncpatch` fork. *(Pilot-confirmed.)*
- **INV-7 Atlas cap.** Cubism **FREE** caps the texture atlas at **2048×2048**. Any doc asserting a single **4096** atlas for the rig (e.g. BASE.md's earlier planned "atlas 4096") is STALE vs the FREE reality — plan multi-atlas / lower upscale / PRO. *(Pilot-confirmed.)*
- **INV-8 Eye-smile param.** The eye-smile uses the Cubism template's standard **`EyeL Smile` / `EyeR Smile`** — there is **no standard `ParamEyeForm`**. All surfaces now agree (spec §5 corrected 2026-05-31 with a note; plan + `RIG_GUIDE.md` already correct). Any *new* doc reintroducing `ParamEyeForm` as a rig parameter is STALE.

## Branches / worktrees in play

- `master` — main; protected. Pre-pilot state: holds the "execute the pilot" launcher but none of the pilot execution / full-build plan / `PIPELINE.md` (split-brain source — escalate merge).
- `live2d-spike` — the Live2D initiative (unmerged, ~9 commits ahead). All Phase 1 work (pilot + full-build plan) + this registry live here.
- Other worktrees (`m5-drift-conventions`, `registry-hardening`, …) are separate initiatives — out of scope for Live2D reconciliation unless they hold a shared `CONTEXT.md`/glossary.
