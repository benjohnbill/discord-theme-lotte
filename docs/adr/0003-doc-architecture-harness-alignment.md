# 0003 — Documentation architecture: align the `live2d/` orientation system to the harness pattern

Status: **accepted** (2026-06-09). Supersedes the bespoke "registry + INV-* + reconcile-docs" orientation
system **as a structure** (the freshness-checking *capability* is preserved, re-aimed — see below). This ADR
records the decision; it is self-referential (the restructure includes writing this record).

## Context

The `live2d/` orientation system grew organically into a bespoke shape: a registry
(`docs/superpowers/DOC_ARCHITECTURE.md`) listing surfaces + cross-doc invariants (`INV-*`), policed by the
`reconcile-docs` skill + `check_freshness.py`, with `live2d/PIPELINE.md` as the live-state authority. It
worked, but exposed three structural defects:

1. **Fossil stack.** `PIPELINE.md` carried *state* + *research journal* + *history* in one file, so
   `SUPERSEDED` bullets accreted (14 deep: 06-06 → 06-02PM → 06-02 → 06-01PM → …). Finding the one live
   frontier meant reading thirteen fossils.
2. **Quadruple-copy drift.** The same ~400-word frontier narrative was duplicated across PIPELINE top /
   the launcher Task / registry `INV-3` / `MEMORY`. When 06-07 work landed, all four went stale at once and
   none was updated; the checker only saw "surfaces mutually agree" and returned EXIT 0 (a false green).
3. **Verification knowledge outside the repo.** The Cubism-FREE traps + the no-WebGL verify recipe lived in
   out-of-repo memory (`live2d-cubism-rig-gotchas`) — the most-trusted but least-versioned location.

## Decision

Align `live2d/` to the global harness pattern (`~/.claude/docs/tool-guides/harness-pattern.md`), keyed for a
single long-lived rig feature. The CSS theme concern stays as-is — only `live2d/` is restructured.

- **Organizing principle: stale-sensitivity ∝ 1 / load-frequency.** The more often a file auto-loads or is
  read/written, the more aggressively it must refuse stale content. Auto-loaded files (`CLAUDE.md`,
  `MEMORY.md`) hold **pointers only**; volatile content (current state, hypotheses) is confined to
  read-first, non-auto-loaded files.
- **One home per knowledge type (7-type model), pointer-not-copy.** Each fact lives in exactly one home and
  others **link**, never copy — so contradiction becomes structurally impossible (the quadruple-drift was a
  "remember to update" vigilance failure; a single writable home removes the failure mode):
  fact → `live2d/DOMAIN_MAP.md` · decision (why, immutable) → `docs/adr/` · vocabulary → `live2d/CONTEXT.md`
  · state → `live2d/PIPELINE.md` (tiny cursor) + active `docs/features/<slug>/INDEX.md` · hypothesis →
  `docs/features/<slug>/RESEARCH.md` · fire-on-action guard → hookify · archive → `docs/features/archive/`,
  completed plans/specs.
- **Marker-flip.** `DOMAIN_MAP.md` holds **only `✅`/`⛔`** (settled facts) — **no `❓`**. Open questions
  live solely in `RESEARCH.md`; a resolved one **graduates** to `DOMAIN_MAP`/`.claude/rules` as a one-line
  `✅`/`⛔` with a back-link. A frequently-read dictionary therefore advertises no unsettled content
  (stale surface ≈ 0).
- **3-tier cascade buffers the auto-loaded entry doc.** `CLAUDE.md` (static map + "current work → PIPELINE")
  → `PIPELINE.md` (dynamic cursor: active feature + single next + done-log) → `features/<slug>/INDEX →
  RESEARCH`. PIPELINE absorbs the volatility so `CLAUDE.md` need not change each session — and so the agent
  never edits the user-scope entry doc to advance state.
- **Source of truth = the model files.** As-built rig facts (deformer tree, atlas contents) are owned by
  `*.cmo3` / `*.model3.json`; docs describe intent or point, they do not duplicate the artifact.
- **Dispositions** (failure-test driven — role-mixed catch-alls dissolve, load-bearing duplicates slim,
  re-accumulating procedures bifurcate):
  - **Dissolve** (role-mixed grab-bags) → type-homes: `ROI.md`, `DECISIONS.md`, `BASE.md`,
    `DOC_ARCHITECTURE.md`. Each becomes a **permanent tombstone redirect** (kept, not deleted — see
    "Considered and rejected").
  - **Slim** (load-bearing duplication) → pointer: `PIPELINE.md` (frontier stays single-source here),
    `next-session-prompt.md`.
  - **Bifurcate** (re-accumulating procedure — three generations of churn): `RIG_GUIDE.md` →
    strategy-invariant machine-ops to `DOMAIN_MAP`, strategy-specific walkthrough to the active feature
    folder (archived whole at the next strategy pivot), Pilot/W4 to history.
  - **New**: `DOMAIN_MAP.md`, `docs/features/<slug>/` (first slug `cd4-blink`), ADR-0003 (this) + ADR-0004
    (the locked constraints DECISIONS held).
  - **Keep**: `CONTEXT.md` (+ minor cleanup), `docs/adr/` (elevated to first-class), `gen/PROMPTS.md`,
    `source/README.md`, `pilot/RESULT.md`, hookify.
- **The registry's capability is preserved, re-aimed — not deleted.** The freshness check moves from
  "parse a registry table" to: parse targets from the `CLAUDE.md` map, enforce the `DOMAIN_MAP` marker rule
  (no `❓`), and **compare the authority frontier date against the latest claude-mem observation date** (warn
  when memory is newer — the signal that would have caught the 06-06 ↔ 06-07 gap). `reconcile-docs` is
  reworked to the new layer-map, not retired.

## Why

- A file that mixes roles cannot stay fresh — the fossil stack is the proof. Narrowing each file to one role
  is what makes it trustworthy again ("it gets solid because its role got small").
- Single writable home > "remember to update N copies." Structure beats vigilance; the quadruple-drift
  proved vigilance fails silently and the checker's surface-agreement test rubber-stamps it.
- Graduating verification knowledge into in-repo `DOMAIN_MAP`/ADRs versions it and makes it survivable; the
  memory layer reverts to its proper job (collaboration patterns, ambient history) — scoped to a separate
  handoff, out of this ADR.

## Considered and rejected

- **Absorb state into `CLAUDE.md`** — violates the organizing principle (the most-loaded file would change
  every session) and the permission line (the agent would constantly edit a user-scope file). PIPELINE
  exists precisely to absorb that volatility.
- **Keep `RIG_GUIDE.md` standalone** — a strategy-pivot churns it wholesale (three generations: Pilot / W4 /
  CD). A standalone procedure doc has no archive path; bifurcating sends the volatile half to a feature
  folder that *can* be archived.
- **Keep the registry** — it became a fourth copy of the frontier and a second place to keep in sync. Its
  enforceable half belongs in the checker; its map belongs in `CLAUDE.md`; its INV-facts belong in
  `DOMAIN_MAP`.
- **Hard-delete the dissolved docs** — immutable history points at the old paths and is **never rewritten**:
  completed specs/plans, ADR-0001/0002, and the `§6` anchor web all cite `ROI.md` / `RIG_GUIDE.md` /
  `DECISIONS.md` / `DOC_ARCHITECTURE.md`. A delete would dangle those references permanently. So the
  tombstones are **kept as permanent redirects** — the standing translation layer from old path → new home,
  not a temporary bridge. (Updating `CLAUDE.md`'s map is still required so the *live* entry doc stops
  treating a dissolved doc as an authority; the checker's dissolved-ref test enforces that — but the
  tombstone files themselves stay.)

## Open (out of scope here)

The residual role of the out-of-repo memory layer once in-repo homes exist (what still deserves an
auto-loaded `MEMORY.md` slot) — tracked in a separate memory-layer handoff, not decided here.
