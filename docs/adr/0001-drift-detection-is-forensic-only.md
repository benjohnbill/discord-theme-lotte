# ADR 0001: Drift detection is forensic-only

Date: 2026-05-26
Status: Accepted (retroactive — decision was implicit in the M4 plan; this ADR records the rationale via post-hoc review of alternatives)

## Context

M4 introduced the drift detection layer for the discord-theme-lotte workspace: a probe command (read-only Chrome DevTools Protocol query) and an archive command (forensic tombstone for selector entries removed from active registries). The archive command writes to `registry/archive.yaml`, an append-only YAML file.

Two design questions sit behind the archive command:

1. Should `registry/archive.yaml` be garbage-collected over time, or grow append-only?
2. When a selector is archived, should the matching CSS block in its former `cssOwner` partial be pruned automatically?

The M4 plan answered both with "forensic-only, manual prune." This ADR documents the rationale and the alternatives considered.

## Decision

`registry/archive.yaml` is forensic-only. No automatic garbage collection. The archive command modifies the source registry and the archive file; it never touches CSS partials. CSS pruning, when needed, is performed manually by the user.

## Alternatives considered

- **Automatic garbage collection** (e.g., remove archive entries older than N months, or move them to a cold-storage file). Rejected. The forensic value of an archive entry grows with time — "what did Discord look like 1 year ago" is precisely the kind of question forensic records answer. Garbage collection runs in the opposite direction from forensic preservation.

- **Integrated `archive`-and-`cssprune`** (the archive command both removes the registry entry and removes the matching CSS block from the partial). Rejected. CSS pruning is a *judgment* operation: an archived selector's class may still be intentionally referenced elsewhere in CSS (for parent-context cascading, for Vencord plugin classes, for kept-as-comment historical residue). Automatic pruning would mutate visual surface area without explicit user review, which conflicts with the project's Visual Direction principle in CONTEXT.md.

- **Orphan warning** (informational signal that flags CSS classes present in partials but absent from any active registry, without modifying anything). **Deferred, not rejected.** This mechanism is *compatible with* forensic-only. It operates on a different plane: forensic-only governs `archive.yaml` and the `archive` command; an orphan warning would govern the partial-vs-registry asymmetry as a memory aid. A future ADR can introduce orphan warning without superseding this one.

## Consequences

- `registry/archive.yaml` grows monotonically. Audit periodically when looking for replaced entries.
- Orphan CSS blocks accumulate after archiving until the user prunes them. This is intentional residue. The user's visual review remains the gate for CSS change.
- Adding an orphan warning mechanism does not require superseding this ADR — it operates on a separate concern. A new ADR would only be needed if `archive.yaml`'s forensic guarantee itself is reversed (e.g., auto-GC is later introduced).
- Reversing the forensic-only stance for `archive.yaml` would require a new ADR superseding 0001, including a migration policy for already-accumulated entries.
