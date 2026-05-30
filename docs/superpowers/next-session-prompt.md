# Next Session Handoff — Lotte Live2D Aliveness, Phase 0 (Feasibility Spike)

> Replaces the completed M3/M4 handoff (those milestones shipped; PR #2). This is a thin launcher by design — the substance lives in the plan and in auto-loaded memory, not here. (Per the project's own memory model, handoff files are low-trust; do not put substance here that could go stale.)

Paste the body below (inside the `---` block) into the next Claude session as the initial prompt. It is self-contained; the next session will not see this session's history.

---

## Task

Execute **Phase 0 only** of the plan `docs/superpowers/plans/2026-05-31-lotte-live2d-aliveness.md`. Do not rewrite or "improve" the plan — execute as written.

Phase 0 is a **feasibility spike**: prove (or disprove) that a single Live2D rig can render live inside the Discord desktop client as a cursor-aware full-window background, using a FREE sample model — before any art-rigging or Vencord-maintenance labor.

## Read first (substance lives here, not in this handoff)

1. `MEMORY.md` auto-loads — see memory `lotte-live2d-aliveness-direction` for the decided design + open gates.
2. The plan's **Background** section carries the full design rationale and the rejected alternatives. Do not re-derive or re-litigate them.

## Working directory

`/home/benjohnbill/dev/discord-theme-lotte`

## Setup

- Work in an isolated worktree off `master`, per repo convention (one worktree per initiative). Invoke `superpowers:using-git-worktrees`; suggested branch `live2d-spike`:
  ```bash
  rtk git worktree add /home/benjohnbill/dev/discord-theme-lotte/.worktrees/live2d-spike -b live2d-spike master
  ```
- Spike artifacts go in `experiments/live2d-spike/` — outside the theme build pipeline (NOT in `src/`, NOT in `theme.manifest.yaml`).

## Execution order & the hard safety boundary

Use `superpowers:subagent-driven-development` or `executing-plans`.

- **Task 1 (read-only Vencord inspection)** and **Task 2 (standalone browser Live2D spike)** are SAFE — auto-execute both. They do not touch Discord.
- **STOP after Task 2 and report to the user before Task 3.** Task 3 stands up a Vencord dev build and runs `pnpm inject`, which **patches the user's real Discord desktop client** — an invasive, semi-irreversible, external-effect action (Tier 3 in the user's operating model). Do NOT inject autonomously. Present Task 1's findings (stock vs dev install, the dev-build cost) and Task 2's result, and get explicit user go-ahead before proceeding to Task 3.

## Hard rules

- **Shell:** prefix dev commands with `rtk` (token-optimization proxy): `rtk npm install`, `rtk git ...`.
- **Existing Vencord install:** READ-ONLY. Never run `rtk npm run sync`. Never edit `/mnt/c/Users/benjohnbill/AppData/Roaming/Vencord/themes/...`. (Task 1 only *reads* that tree.)
- **master:** never edit or push directly. No PRs this session — defer to the user.
- **No amend/force-push.** New commits only, with the plan's commit messages verbatim.
- **Aesthetic guardrails (for any rendering you eyeball):** Tier 1 only — restraint is the whole game. The face is large, so no aggressive cursor tracking; gentle/under-animated beats uncanny.

## What success looks like (Phase 0)

- `experiments/live2d-spike/FINDINGS.md` records: Gate-1 install type + plugin-capability verdict (Task 1), standalone runtime PASS/FAIL + screenshot (Task 2), and — only if the user approved Task 3 — in-Discord injection result + CSP outcome (Task 3), plus a final GO / GO-WITH-COST / NO-GO recommendation (Task 4).
- A working `experiments/live2d-spike/index.html` + `0b-standalone.png` committed.
- `master` untouched; existing Vencord themes dir untouched; no `npm run sync`.
- If GO: the session ends by proposing the Phase 1 plan (rig the real Lotte) — do not start Phase 1 without user sign-off.

## Stopping conditions

Stop and report when: Task 2 is done and you need user approval for Task 3; OR Phase 0 reaches a go/no-go; OR a task is genuinely blocked (environment/ambiguity).
