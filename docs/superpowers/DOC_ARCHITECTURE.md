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
- **INV-3 Frontier.** Phase 1.0 pilot = DONE/GO; full build **W1+W2+W3+W4.1 = DONE (2026-05-31)**. Current frontier = **W4.2 — the USER rigs `live2d/lotte.psd` in Cubism 5.3 FREE** per `RIG_GUIDE.md` "Full Build (W4)", then agent runs `check_model.py` → W5. Any launcher/memory naming Phase 0, the pilot, W1, W2, W3, or "execute the pilot / start with brainstorming" as the next action is STALE.
- **INV-4 Authorities exist.** `live2d/PIPELINE.md` (live-state authority), `DECISIONS.md`, `RIG_GUIDE.md` were created in pilot Task 0 and now EXIST; `PIPELINE.md` is read-first. Any doc still saying these are "not yet created / created in Task 0" is STALE.
- **INV-5 Split-brain — RE-ACTIVATED (2026-05-31).** The earlier FF-merge is now STALE: W1+W2+W3+W4.1 (14 commits, `b910cb5`…`7c2ea75`) landed on `live2d-spike` ONLY, so **`live2d-spike` is 14 commits AHEAD of `master`** (master still at `a6674fb`; 0 commits master-only → a clean fast-forward is available). **`master`'s orientation docs (PIPELINE/launcher/etc.) are 14 commits stale** — a fresh agent landing on `master` would be badly misled (its PIPELINE says "execute W1"). **Decision (2026-05-31, user):** keep working on the worktree; **FF-merge `live2d-spike` → `master` at Phase 1 (W5) completion**, not before (W4–W5 would just re-diverge). Until then **the `.worktrees/live2d-spike` copy is the authority**; a one-line "SUPERSEDED → worktree" banner on `master`'s launcher is proposed (apply pending user sign-off — `master` is protected, never merge/push/edit it without sign-off).
- **INV-6 moc3 version.** The rig `.moc3` must export at **version ≤ 5** (the pinned web Core reports `csmGetLatestMocVersion()=5`). Cubism Editor 5.3 defaults to **v6**, which **fails to load**. Any doc/plan exporting the default or assuming "any moc3 loads" is STALE; fix = export 5.0/4.2, or bump the Core / use the `pixi-live2d-display-lipsyncpatch` fork. *(Pilot-confirmed.)*
- **INV-7 Atlas cap.** Cubism **FREE** = a **single 2048×2048** texture atlas, ≤100 pieces; **multiple atlases are PRO-only** (web-verified W4.1, 2026-05-31). Any doc asserting **4096** for the rig, OR offering "2 atlases / multi-atlas" as a FREE fallback, is STALE. The fix for ~19 parts: pack into the one atlas via the atlas tool's **Auto Layout → "set magnification automatically"** (≈0.5× on layout); the hi-res master stays in `assets/`. (PRO or a lower upscale are the only ways to more atlas budget.)
- **INV-8 Eye-smile param.** The eye-smile uses the Cubism template's standard **`EyeL Smile` / `EyeR Smile`** — there is **no standard `ParamEyeForm`**. All surfaces now agree (spec §5 corrected 2026-05-31 with a note; plan + `RIG_GUIDE.md` already correct). Any *new* doc reintroducing `ParamEyeForm` as a rig parameter is STALE.

## Branches / worktrees in play

- `master` — main; protected. **STALE: 14 commits behind `live2d-spike`** (at `a6674fb`, the old FF-merge point — its Live2D docs predate W1–W4.1). A clean fast-forward to `live2d-spike` is available; **decision = merge at Phase 1/W5 completion** (INV-5), needs **user sign-off** (never merge/push/edit `master` yourself).
- `live2d-spike` — the Live2D initiative worktree (`.worktrees/live2d-spike`); **AHEAD of `master` by 14 commits** (W1+W2+W3+W4.1). This is the live authority until the user merges.
- Other worktrees (`m5-drift-conventions`, `registry-hardening`, …) are separate initiatives — out of scope for Live2D reconciliation unless they hold a shared `CONTEXT.md`/glossary.
