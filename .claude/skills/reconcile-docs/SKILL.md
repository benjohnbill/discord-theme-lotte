---
name: reconcile-docs
description: Use when this project's spec/design/plan or implementation has moved and the orientation docs or cross-session memory may have gone stale or contradictory — at session wrap-up, after a design decision changes, when a launcher or memory still points at a finished phase or names a superseded library/source/path, or whenever a fresh agent could be misled.
---

# Reconcile Docs

## Overview

Keep this project's orientation documents and cross-session memory **fresh and mutually
consistent**, so a future agent with zero context orients correctly.

**Core principle:** the *procedure* is stable (this skill); the *target list* is volatile and
lives in `docs/superpowers/DOC_ARCHITECTURE.md` (the registry). Load the registry — do not
re-derive the doc map from scratch (a from-scratch rediscovery burned 100k+ tokens in testing).
Reconcile every stale surface **toward the single source of truth**, fixing mechanical staleness
and escalating design/destructive changes.

You are a **librarian, not an architect**: surface design drift, do not resolve it.

## When to use

- Session wrap-up after meaningful design/planning/implementation changes.
- A launcher or memory file points at a finished phase, or names a superseded library/source/path.
- A spec/plan changed and downstream pointers may not have followed.
- You sense drift, or a fresh agent could be misled.

**Not for:** code-only changes with no doc impact; resolving design questions (escalate those).

## Procedure

1. **Load the registry** `docs/superpowers/DOC_ARCHITECTURE.md`: the surfaces, the read order, and the cross-doc **invariants (INV-*)**. This is your checklist.
2. **Detect drift.** **Run `check_freshness.py` (this skill's dir) first** — it mechanically clears the enforceable half: the INV-* denylist (no un-annotated superseded value), cross-surface **frontier agreement** (catches "next = W4" vs the authority's "W4.2"), and **branch-state** counts vs `git`. Then do the judgment half per surface: stale forward-pointers (finished phase / superseded library / wrong path), broken cross-references, referenced-but-absent authority files, `git log` recency, the **split-brain** check (orientation files on BOTH `master` and the active worktree), **internal fossils** (appended-over-time files — memory `.md`, long specs, completed-plan roadmaps — accrue stale *earlier* sections that contradict newer ones in the same file), and **cross-surface redundancy** (the same load-bearing fact restated across N surfaces). Always include the **out-of-repo memory layer**.
3. **Classify by permission:**
   - **Mechanical staleness** (stale pointers, wrong paths, superseded forward-refs, pointer-level invariant violations) → **auto-fix**.
   - **Design/decision drift, anything editing protected `master`, or a merge decision** → **propose / escalate to the user**; do not apply.
   - **Immutable history** (completed plans, `FINDINGS.md`, claude-mem observations) → annotate "SUPERSEDED ➜ see X" at the **top of the stale block** (a `> ⚠️ SUPERSEDED` line — `check_freshness.py` whitelists a dead value only when the marker sits on or just above it); **never rewrite**. A superseded plan's forward-looking section misleads most — annotate it first.
   - **Cross-surface duplication** → distinguish *intentional* load-bearing restatement (a launcher repeating key facts so a fresh agent need not open five files — fine) from *drift-prone* duplication or a surface contradicting its own declared role (e.g. a "thin" launcher carrying full substance). For the latter only, **surface it as a smell** and *propose* a single-source refactor (one authority + pointers); do NOT refactor yourself — surface roles are the architect's call.
   - **Registry↔spec tie-break:** if an invariant declares a decision *locked* but a spec section still presents it as *open* ("may instead", "decide in W1") → escalate to reconcile (tighten the spec to the invariant, or re-open the decision); don't silently rewrite a spec decision.
   - **`master` split-brain:** escalate the merge-vs-keep-worktree decision; you may *propose* a one-line "SUPERSEDED → see worktree" banner on master's launcher, but never edit master yourself.
4. **Apply write-backs across ALL layers** — in-repo docs **and** the out-of-repo memory layer (`MEMORY.md` index + the memory `.md` files; edit the on-disk files, the session-injected copy is a summary) **and** the launcher.
5. **Self-audit the registry:** diff it against the actual file tree and current decisions. Append new docs, remove dead entries, update changed invariants. Keep the registry from going stale — and when an INV-* adds a superseded value, add it to `check_freshness.py`'s `DENYLIST` in the same pass.
6. **Verify → commit:** clean working tree, cross-refs resolve. **Re-run `check_freshness.py` — it must exit 0** (no un-annotated INV value, frontier agrees across surfaces *including the auto-loaded memory index*, branch-state matches `git`). The memory layer is the most trusted and the most often left under-reconciled, so the checker reads it too. Then commit (the doc/memory write-back is Tier-2, autonomous).

## Quick reference

| Layer | Location | Fix mode |
|---|---|---|
| Launcher / spec / pipeline / working docs | in-repo (see registry) | auto-fix (spec *decisions* → propose) |
| Completed plans / FINDINGS | in-repo | annotate SUPERSEDED, don't rewrite |
| Memory index + files | `~/.claude/projects/-home-benjohnbill-dev-discord-theme-lotte/memory/` | auto-fix (edit on-disk files) |
| claude-mem observations | search tools | never edit; disambiguate elsewhere |
| `master` orientation files | other branch | **escalate** (protected), don't edit |

## Tooling

`check_freshness.py` (this skill's dir) — the executable half of Steps 2 & 6. Stdlib only;
`python3 check_freshness.py` from the worktree root. It parses the surface list from the registry
table (don't duplicate it), exempts history surfaces, and passes negated/annotated mentions. Three
checks: INV-* **denylist**, **frontier** agreement, **branch-state** vs `git`. Extend `DENYLIST`
whenever an INV-* names a new superseded value (Step 5). Tuning a denylist for precision is real
work — it currently flags only un-annotated, non-negated, live-surface hits.

## Common mistakes

- **Forgetting the memory layer.** It is OUTSIDE the repo and auto-loaded, so it is the most trusted *and* the easiest to miss. Always reconcile it; `check_freshness.py` reads it too. A self-contradiction inside one auto-loaded memory file is the worst kind of staleness.
- **Over-flagging redundancy.** Some restatement is intentional (a launcher repeating key facts so a fresh agent need not chase five files). Flag only drift-prone copies, or a surface contradicting its own declared role — not every repeated fact.
- **Re-deriving the doc map.** That is what the registry is for. Read it first.
- **Editing `master` or merging on your own.** Split-brain resolution is the user's call — escalate.
- **Rewriting history.** Completed plans, FINDINGS, and observations are the record — annotate, don't overwrite.
- **Resolving design drift yourself.** Surface it; the decision is the user's.
- **Leaving the registry stale.** If you found a new doc or a changed decision, update `DOC_ARCHITECTURE.md` (and `check_freshness.py`'s `DENYLIST`) in the same pass.
