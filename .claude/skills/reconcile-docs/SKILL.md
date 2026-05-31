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
2. **Detect drift.** For each registry surface, check: invariant violations (INV-*), stale forward-pointers (finished phase / superseded library / wrong path), broken cross-references, referenced-but-absent authority files, and `git log` recency (a spec/plan committed after a launcher → launcher likely stale). Include the **out-of-repo memory layer** and the **split-brain** check (orientation files on BOTH `master` and the active worktree). Also check each surface for **internal fossils** — files appended over time (memory `.md`, long specs, completed-plan roadmaps) accumulate stale *earlier* sections that contradict newer ones in the same file.
3. **Classify by permission:**
   - **Mechanical staleness** (stale pointers, wrong paths, superseded forward-refs, pointer-level invariant violations) → **auto-fix**.
   - **Design/decision drift, anything editing protected `master`, or a merge decision** → **propose / escalate to the user**; do not apply.
   - **Immutable history** (completed plans, `FINDINGS.md`, claude-mem observations) → annotate "SUPERSEDED ➜ see X"; **never rewrite**. A superseded plan's *roadmap / forward-looking* section is the likeliest to mislead — annotate it first.
   - **Registry↔spec tie-break:** if an invariant declares a decision *locked* but a spec section still presents it as *open* ("may instead", "decide in W1") → escalate to reconcile (tighten the spec to the invariant, or re-open the decision); don't silently rewrite a spec decision.
   - **`master` split-brain:** escalate the merge-vs-keep-worktree decision; you may *propose* a one-line "SUPERSEDED → see worktree" banner on master's launcher, but never edit master yourself.
4. **Apply write-backs across ALL layers** — in-repo docs **and** the out-of-repo memory layer (`MEMORY.md` index + the memory `.md` files; edit the on-disk files, the session-injected copy is a summary) **and** the launcher.
5. **Self-audit the registry:** diff it against the actual file tree and current decisions. Append new docs, remove dead entries, update changed invariants. Keep the registry from going stale.
6. **Verify → commit:** clean working tree, cross-refs resolve, no remaining INV violations. Then commit (the doc/memory write-back is Tier-2, autonomous).

## Quick reference

| Layer | Location | Fix mode |
|---|---|---|
| Launcher / spec / pipeline / working docs | in-repo (see registry) | auto-fix (spec *decisions* → propose) |
| Completed plans / FINDINGS | in-repo | annotate SUPERSEDED, don't rewrite |
| Memory index + files | `~/.claude/projects/-home-benjohnbill-dev-discord-theme-lotte/memory/` | auto-fix (edit on-disk files) |
| claude-mem observations | search tools | never edit; disambiguate elsewhere |
| `master` orientation files | other branch | **escalate** (protected), don't edit |

## Common mistakes

- **Forgetting the memory layer.** It is OUTSIDE the repo and auto-loaded, so it is the most trusted *and* the easiest to miss. Always reconcile it. A self-contradiction inside one auto-loaded memory file is the worst kind of staleness.
- **Re-deriving the doc map.** That is what the registry is for. Read it first.
- **Editing `master` or merging on your own.** Split-brain resolution is the user's call — escalate.
- **Rewriting history.** Completed plans, FINDINGS, and observations are the record — annotate, don't overwrite.
- **Resolving design drift yourself.** Surface it; the decision is the user's.
- **Leaving the registry stale.** If you found a new doc or a changed decision, update `DOC_ARCHITECTURE.md` in the same pass.
