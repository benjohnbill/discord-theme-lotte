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
- **INV-3 Frontier.** Phase 1.0 pilot = DONE/GO; full build **W1+W2+W3+W4 (rig, atlas, moc3 v5 export, W4.3 checker, Step 9B hair+ribbon physics) + W5 (runtime verify) all DONE/PASS (W4.2–W5 on 2026-06-01)**. The full Lotte rig drives in pixi-live2d-display@0.4.0 + Core 5.1. **Current frontier = W4/Phase 1 COMPLETE.** Next is OPTIONAL: W5 polish (USER art/tune — eye-smile too strong, faint eye seam; **hair-edge halo+vignette CLOSED 2026-06-01** — verified a non-issue on the real `version` lavender backdrop, the dark-navy W5 verify was an env-alignment artifact) and/or **Phase 2 (productionize the Discord delivery — Vencord userplugin)**. Any launcher/memory naming Phase 0, the pilot, W1–W4.x, "W4.2 USER rigs", "physics deferred/next", "execute the pilot / start with brainstorming", or **the halo/vignette as an open polish item**, as the next action is STALE.
- **INV-4 Authorities exist.** `live2d/PIPELINE.md` (live-state authority), `DECISIONS.md`, `RIG_GUIDE.md` were created in pilot Task 0 and now EXIST; `PIPELINE.md` is read-first. Any doc still saying these are "not yet created / created in Task 0" is STALE.
- **INV-5 Split-brain — RESOLVED (2026-06-01).** `live2d-spike` was **merged into `master`** at Phase 1 / W5 completion (3-way merge `553f2a2`; the interim STALE banner `336822a` was dropped — commit `6ffae29`), and the worktree + branch were removed. **`master` is now the single authority** — there is no live2d-spike worktree any more. Any doc still saying "`live2d-spike` is the authority / ahead of master / NOT merged", or "merge at W5 (pending sign-off)", or referencing the STALE banner as live, is STALE. **`master` is still local-only (~55 commits ahead of `origin/master`, NOT pushed)** — pushing remains a Tier-3 action needing user sign-off; never push `master` yourself.
- **INV-6 moc3 version.** The rig `.moc3` must export at **version ≤ 5** (the pinned web Core reports `csmGetLatestMocVersion()=5`). Cubism Editor 5.3 defaults to **v6**, which **fails to load**. Any doc/plan exporting the default or assuming "any moc3 loads" is STALE; fix = export 5.0/4.2, or bump the Core / use the `pixi-live2d-display-lipsyncpatch` fork. *(Pilot-confirmed.)*
- **INV-7 Atlas cap.** Cubism **FREE** = a **single 2048×2048** texture atlas, ≤100 pieces; **multiple atlases are PRO-only** (web-verified W4.1, 2026-05-31). Any doc asserting **4096** for the rig, OR offering "2 atlases / multi-atlas" as a FREE fallback, is STALE. The fix for ~19 parts: pack into the one atlas via the atlas tool's **Auto Layout → "set magnification automatically"** (≈0.5× on layout); the hi-res master stays in `assets/`. (PRO or a lower upscale are the only ways to more atlas budget.)
- **INV-8 Eye-smile param.** The eye-smile uses the Cubism template's standard **`EyeL Smile` / `EyeR Smile`** — there is **no standard `ParamEyeForm`**. All surfaces now agree (spec §5 corrected 2026-05-31 with a note; plan + `RIG_GUIDE.md` already correct). Any *new* doc reintroducing `ParamEyeForm` as a rig parameter is STALE.

## Branches / worktrees in play

- `master` — main; the **single authority** for Live2D now. Carries the full Phase 1 build (W1–W5 + physics) after the `live2d-spike` merge (`553f2a2`) + banner drop (`6ffae29`). **Local-only: ~55 commits ahead of `origin/master`, NOT pushed** — pushing is Tier-3, needs sign-off (never push/force `master` yourself). Also carries an unrelated uncommitted change (background-image swap in `src/base/background.css` + dist rebuild) that predates this session — not Live2D, leave to the user.
- `live2d-spike` — **GONE** (merged + worktree removed 2026-06-01). Do not look for it; do not treat it as authority.
- Other worktrees (`discord-dom-probe-and-archive`, `m5-drift-conventions`, `registry-hardening`, `theme-change-workflow`, `workspace-memory-foundation`) are separate initiatives — out of scope for Live2D reconciliation unless they hold a shared `CONTEXT.md`/glossary.
