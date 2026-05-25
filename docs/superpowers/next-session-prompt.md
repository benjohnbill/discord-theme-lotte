# Next Session Handoff — M3 + M4 Implementation

Paste the body below (everything inside the `---` block) into the next Claude session as the initial prompt. It is self-contained; the next session's controller agent will not see this session's history.

---

## Task

Execute two implementation plans sequentially using the `superpowers:subagent-driven-development` skill:

1. **M3** — `docs/superpowers/plans/2026-05-25-theme-change-workflow.md`
2. **M4** — `docs/superpowers/plans/2026-05-25-discord-dom-probe-and-archive.md`

Both plans were authored in a prior session, reviewed inline, and committed to master. Do not re-write or "improve" them. Execute as written.

## Working directory

`/home/benjohnbill/dev/discord-theme-lotte`

## Repo state at handoff (2026-05-25)

Origin branches:

| Branch | Status | Notes |
|---|---|---|
| `master` | base | Latest commit adds three plans under `docs/superpowers/plans/`. |
| `workspace-memory-foundation` | M1, open as PR #1 (https://github.com/benjohnbill/discord-theme-lotte/pull/1) | NOT merged. |
| `registry-hardening` | M2, pushed, no PR | Stacks on `workspace-memory-foundation`. 8 commits. |

Test/check baseline on `registry-hardening` tip: `rtk npm test` → 17 tests pass; `rtk npm run check` → prints `ok registry cross-references` before the build line.

## Branch strategy — linear stack

- **M3** → new branch `theme-change-workflow`, branched off `registry-hardening` (M2 tip).
- **M4** → new branch `discord-dom-probe-and-archive`, branched off `theme-change-workflow` (M3 tip).

Final stack: `master → workspace-memory-foundation (M1) → registry-hardening (M2) → theme-change-workflow (M3) → discord-dom-probe-and-archive (M4)`.

Reason for stacking M3 on M2: M3's Task 5 Step 4 expects `rtk npm run check` to print `ok registry cross-references`, which is M2's behavior.

## Workflow per milestone

For each plan in order (M3 first, then M4):

1. Invoke `superpowers:using-git-worktrees`. Create worktree at `.worktrees/<branch-name>` (already gitignored). Branch off the previous milestone's tip per the strategy above. Example for M3:
   ```bash
   rtk git worktree add /home/benjohnbill/dev/discord-theme-lotte/.worktrees/theme-change-workflow -b theme-change-workflow registry-hardening
   ```
2. Inside the worktree, run `rtk npm install`.
3. Confirm baseline: `rtk npm test` and `rtk npm run check`. Stop and escalate if anything is red before M3 starts.
4. Read the plan file ONCE and extract all tasks verbatim, then create a `TaskCreate` entry per plan task.
5. Invoke `superpowers:subagent-driven-development`. For each task:
   - Dispatch one implementer subagent (general-purpose) with the FULL task text + context. Do not have the subagent read the plan file — paste the task body into the prompt.
   - After implementer reports DONE: dispatch spec compliance reviewer (independent verification, must read code not report).
   - After spec ✅: dispatch code quality reviewer.
   - Fix loop until both reviewers approve.
   - Mark TaskUpdate completed.
6. After all tasks complete, dispatch a final code reviewer over the whole branch diff (base = previous milestone's tip).
7. Push the branch with upstream tracking:
   ```bash
   rtk git push -u origin <branch-name>
   ```
8. Move to the next milestone.

## Hard rules

- **Shell:** prefix every command with `rtk` (token-optimization proxy). Examples: `rtk npm test`, `rtk git add`, `rtk git worktree add ...`.
- **Sync:** NEVER run `rtk npm run sync`. NEVER edit `/mnt/c/Users/benjohnbill/AppData/Roaming/Vencord/themes/...`.
- **Probe:** NEVER run `rtk npm run probe` against real Discord during plan execution. M4's Task 7 explicitly verifies the probe CLI handles the missing-env-var case; it does NOT invoke a real probe.
- **Master:** NEVER edit or push `master` directly.
- **PRs:** Do NOT open PRs in this session. Defer to user.
- **Amends/force-push:** NEVER amend or force-push. Always create new commits.
- **Plan fidelity:** match the plan's commit messages verbatim. Match every code block verbatim. Match every command verbatim.
- **Scope:** if a plan task seems too small / too big / poorly factored, escalate as a concern in the implementer's report — do NOT silently restructure.

## Reference — prior milestone shape (so you know what "good" looks like)

M2's 8 commits on `registry-hardening` follow a strict shape:

- One commit per plan task.
- Each TDD task = 5 steps: write failing test → run-fail → implement → run-pass → commit.
- Pure module + CLI shim pattern: `scripts/<name>-lib.js` (no I/O, exports pure functions) consumed by both tests and `scripts/<name>.js` CLI shim.
- Tests use synthetic fixtures, never real registry data, never touch the filesystem in unit tests.
- Defensive `?? {}` / `?? []` patterns throughout.

M3 and M4 follow this same shape. Don't drift.

## Stopping conditions

Stop and report to the user when:
- Both branches are pushed, all tasks complete, final code reviewers approved.
- OR: A plan task is genuinely blocked (ambiguity, environment issue, or escalation from implementer subagent).
- OR: A spec/code reviewer rejects work that the implementer cannot fix within one re-review cycle.

Do NOT stop to ask "should I continue?" between tasks. Auto-execute the full plan.

## What success looks like

At end of session:
- `theme-change-workflow` branch pushed to origin. All M3 tasks complete. Tests: 17 → ~20 (build-contract + 16 cross-reference + ~3 new from M3).
- `discord-dom-probe-and-archive` branch pushed to origin. All M4 tasks complete. Tests: ~20 → 31 (adds 7 archive-lib + 7 probe-lib subtests).
- `master` untouched, no PRs created, Vencord live dir untouched, no `npm run sync` invocation, no real Discord probe invocation.

Final report should include each branch's HEAD SHA, commit count vs base, test counts, and any concerns from the final code reviews.
