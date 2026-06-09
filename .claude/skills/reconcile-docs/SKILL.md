---
name: reconcile-docs
description: Use when this project's spec/design/plan or implementation has moved and the orientation docs or cross-session memory may have gone stale or contradictory — at session wrap-up, after a design decision changes, when a launcher or memory still points at a finished phase or names a superseded library/source/path, or whenever a fresh agent could be misled.
---

# Reconcile Docs

## Overview

Keep this project's orientation documents and cross-session memory **fresh and mutually consistent**, so a
future agent with zero context orients correctly.

**Core principle (organizing rule): stale-sensitivity ∝ 1 / load-frequency** (ADR-0003). The more often a
file auto-loads or is read/written, the more aggressively it must refuse stale content. Each knowledge type
has **one home** and others **link, never copy**:

| Type | Home | Note |
|---|---|---|
| Map / read-order | `CLAUDE.md` ("Orientation docs") | static pointer · **user-scope (propose edits)** |
| State (where are we / single next) | `live2d/PIPELINE.md` + active `docs/features/<slug>/INDEX.md` | dynamic cursor · the frontier's ONLY home |
| Fact (platform/tool) | `live2d/DOMAIN_MAP.md` | **✅/⛔ only — no ❓** |
| Hypothesis (open ❓) | `docs/features/<slug>/RESEARCH.md` | the single home of ❓ |
| Decision (why, immutable) | `docs/adr/` | **propose** new/edited ADRs |
| Vocabulary | `live2d/CONTEXT.md` | glossary (denotation) |
| Procedure | strategy-invariant → `DOMAIN_MAP`; strategy-specific walkthrough → active feature | no standalone rig guide |
| Archive | `docs/features/archive/`, completed plans/specs | history banner; never rewrite |

You are a **librarian, not an architect**: surface design drift, do not resolve it. **Load the `CLAUDE.md`
map first** — do not re-derive the doc set from scratch (a from-scratch rediscovery burned 100k+ tokens).

## When to use

- Session wrap-up after meaningful design/planning/implementation changes.
- A launcher or memory file points at a finished phase, or names a superseded library/source/path.
- A spec/plan changed and downstream pointers may not have followed.
- A `❓` resolved (it should **graduate** out of RESEARCH into `DOMAIN_MAP`/ADR), or you sense drift.

**Not for:** code-only changes with no doc impact; resolving design questions (escalate those).

## Procedure

1. **Load the map.** Read the `CLAUDE.md` "Orientation docs" section + know the type-homes above. That is the
   surface set (the dissolved `DOC_ARCHITECTURE.md` registry is replaced by this map + `check_freshness.py`).
2. **Detect drift.** **Run `check_freshness.py` (this skill's dir) first** — it mechanically clears the
   enforceable half: the INV-* denylist (no un-annotated superseded value), W-stage + pivot-phase **frontier
   agreement**, **branch-state** vs `git`, the **DOMAIN_MAP marker rule** (no `❓` in the fact dictionary),
   and a **recency-warn** (authority as-of date vs the latest claude-mem observation). Then the judgment half
   per surface: stale forward-pointers (finished phase / superseded library / wrong path), broken
   cross-references, referenced-but-absent authority files, `git log` recency, **internal fossils**
   (appended-over-time files accreting stale earlier sections), and the two restructure-specific smells —
   **frontier copied instead of linked** (the narrative must live only in PIPELINE; everything else points)
   and **a `❓` that has resolved but not graduated** out of RESEARCH. Always include the **out-of-repo
   memory layer**.
3. **Classify by permission:**
   - **Mechanical staleness** (stale pointers, wrong paths, superseded forward-refs, pointer-level invariant
     violations, a tombstone whose redirect is wrong) → **auto-fix** (Tier-2).
   - **User-scope edits** — `CLAUDE.md` (the map), a **new or edited ADR**, `settings` — **propose**, do not
     apply. (Drafting an ADR file uncommitted = proposing; the user reviews at commit.)
   - **Design/decision drift, anything editing protected `master`, or a merge decision** → **escalate**.
   - **Immutable history** (completed plans, `FINDINGS.md`, `*-pre-restructure-*` snapshots, claude-mem
     observations) → annotate `> ⚠️ SUPERSEDED ➜ see X` at the **top of the stale block**; **never rewrite**.
   - **Cross-surface duplication** → distinguish *intentional* pointer-restatement (a thin launcher naming
     the read order — fine) from *drift-prone* copies or a surface contradicting its declared role (a "thin"
     launcher carrying the full frontier). Surface the latter as a smell and *propose* single-source; the
     frontier's single home is `PIPELINE.md`.
4. **Apply write-backs across ALL layers** — in-repo docs **and** the out-of-repo memory layer (`MEMORY.md`
   index + the memory `.md` files; edit the on-disk files, the session-injected copy is a summary) **and** the
   launcher.
5. **Graduate + self-audit the homes:** when a `❓` resolved, move it from RESEARCH to a one-line `✅`/`⛔` in
   `DOMAIN_MAP` (or a rule/ADR) with a back-link. Diff the `CLAUDE.md` map against the actual tree and the
   type-homes; **propose** map edits (user-scope). When an ADR/DOMAIN_MAP names a *new* superseded value, add
   it to `check_freshness.py`'s `DENYLIST` in the same pass.
6. **Verify → commit:** clean working tree, cross-refs resolve, the frontier appears in `PIPELINE.md` only.
   **Re-run `check_freshness.py` — it must exit 0** (no un-annotated INV value, frontier agrees, branch-state
   matches `git`, no `❓` in DOMAIN_MAP, recency not stale — bump PIPELINE's *as-of date* when you reconcile).
   Then commit (the doc/memory write-back is Tier-2, autonomous; ADR/CLAUDE.md/`master` push need sign-off).

## Quick reference

| Layer | Location | Fix mode |
|---|---|---|
| State / launcher / DOMAIN_MAP / CONTEXT / active feature | in-repo (see map) | auto-fix |
| `CLAUDE.md` map · new/edited ADR | in-repo | **propose** (user-scope) |
| Completed plans / FINDINGS / `*-pre-restructure-*` | in-repo `docs/features/archive/` etc. | annotate SUPERSEDED, don't rewrite |
| Memory index + files | `~/.claude/projects/-home-benjohnbill-dev-discord-theme-lotte/memory/` | auto-fix (edit on-disk files) |
| claude-mem observations | search tools | never edit; disambiguate elsewhere |
| `master` orientation files | other branch | **escalate** (protected), don't edit/push |

## Tooling

`check_freshness.py` (this skill's dir) — the executable half of Steps 2 & 6. Stdlib only;
`python3 check_freshness.py` from the worktree root. It parses the surface list from the **`CLAUDE.md` map**
(plus the explicit type-homes + memory dir; not a registry), exempts history surfaces by path, and passes
negated/annotated mentions. Five checks: INV **denylist**, **frontier** agreement (W-stage + Phase A–D),
**branch-state** vs `git`, **DOMAIN_MAP marker** (no `❓`), **recency-warn** (vs claude-mem). Extend
`DENYLIST` whenever an ADR/DOMAIN_MAP names a new superseded value (Step 5).

## Common mistakes

- **Forgetting the memory layer.** It is OUTSIDE the repo and auto-loaded — most trusted, easiest to miss.
- **Copying the frontier instead of linking.** The frontier narrative lives in `PIPELINE.md` only; every
  other surface points. Restating it is the quadruple-drift this architecture removed.
- **Putting a `❓` in `DOMAIN_MAP`.** The fact dictionary holds settled `✅`/`⛔` only; open questions live in
  `RESEARCH.md`. (The checker fails this.)
- **Editing `CLAUDE.md`, an ADR, or `master` on your own.** Those are user-scope / protected — propose/escalate.
- **Rewriting history.** Completed plans, archive snapshots, and observations are the record — annotate.
- **Resolving design drift yourself.** Surface it; the decision is the user's.
- **Letting a resolved `❓` rot in RESEARCH.** Graduate it to `DOMAIN_MAP`/ADR with a back-link.
