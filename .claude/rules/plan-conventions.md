# Plan Conventions

Scope: Applies when authoring or executing implementation plans under `docs/superpowers/plans/`.

## Plan Convention Augmentations

The `## Non-Goals` section in implementation plans serves two purposes:

1. **Scope constraints** — free-form one-liners describing what the plan never sets out to do (`Do not …`). This is the existing usage carried over from M1–M4 plans.

2. **Deferred fixes** — concerns surfaced during implementation review or grilling that are intentionally not addressed in this milestone. Each deferred item appears under a `### Deferred` subsection inside `## Non-Goals` and includes:
   - **Why deferred** — one sentence explaining the rationale.
   - **Trigger to revisit** — the concrete event or condition that should prompt reopening the item in a future plan.

This convention augments `superpowers:writing-plans` without overriding it. The plan author chooses scope; this rule formalizes how deferral is recorded once that choice is made, so the rationale is preserved alongside the plan rather than lost to session memory.
