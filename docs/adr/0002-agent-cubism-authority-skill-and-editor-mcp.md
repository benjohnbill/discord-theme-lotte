# 0002 — Agent's Cubism authority: thin authoring skill + deferred Editor-API MCP; geometry stays human-in-loop

Status: **accepted** (2026-06-02). Does not supersede any prior ADR.

## Context

USER asked whether Cubism could be made directly usable by the agent (as an MCP or skill) so the agent holds
more active technical authority in rigging & design, rather than every rig change routing through a manual
Cubism-GUI step the agent cannot touch. A grill session resolved the feasibility.

The pipeline splits into three tiers, and only the lowest is cleanly automatable:

- **Tier 1 — post-export artifacts** (`model3 / cdi3 / physics3 / motion3 / exp3.json`, the probe, the runtime
  harness): plain JSON/JS the agent already authors. Full authority, no Cubism needed.
- **Tier 2 — live Editor drive:** the Cubism Editor **External Application Integration API** (added Editor 5.0;
  WebSocket port **22033**; JSON; token handshake; the channel VTube Studio uses; not listed PRO-only → almost
  certainly available in FREE). It exposes **read params + `SetParameterValues` (pose) + export-event
  notifications** — but **NOT** deformer/keyform/mesh authoring, and it **cannot trigger an export**.
- **Tier 3 — geometry rigging** (ArtMesh/vertices, deformers, keyforms, creating params, export): **no official
  API.** Reverse-engineered moc3 writers exist but violate Live2D's "No Reverse Engineering" clause and are
  brittle.

The pivot (ADR-0001) deliberately moves the heavy work OUT of Tier 3 (통짜 warp + opacity-swap + head-lean is
config/JSON), so most remaining iteration is Tier-1 authorable.

## Decision

1. **Tier-1 thin router skill** `live2d-authoring` (`.claude/skills/`): routes task → tier → file → verify →
   handoff, consolidates the no-WebGL verification recipe (SwiftShader + CDP + `runtime-check-full.html`), marks
   the geometry boundary, and unlocks `motion3`/`exp3` authoring (the idle-physics-only rig has none). Thin —
   references PIPELINE/ROI/CONTEXT/RIG_GUIDE for state and schemas; copies nothing (respects the anti-duplication
   doc architecture / `reconcile-docs`).
2. **Tier-2 Editor MCP** = a passive **export-event hook** (on USER export, auto-run `check_model.py` + `sync`),
   structured so blind `SetParameterValues` posing (USER watches; the agent cannot screenshot the Windows-native
   Editor from WSL) flips on for a rigging sprint. **Built just-in-time at Phase C/D** (the first real Editor
   re-export) — dead weight until the Editor re-opens; gated on a live connect (`netsh portproxy :22033`,
   handshake, prove `GetParameters`). WSL→Windows reach uses the same portproxy pattern as chrome-devtools.
3. **Tier 3 stays human-in-loop** — geometry is the USER's Cubism GUI.

ToS posture: official External API + plain JSON only; never a reverse-engineered moc3 writer.

## Why

- The Editor has no rig-authoring API; the honest-feasible target is the authorable layer + verification +
  routing, not mesh/deformer authoring. Pretending otherwise (GUI automation, RE writers) buys brittleness.
- The agent already drives parameters in the *runtime* harness (where it can see); the Editor API's posing
  overlaps that and is blind on the agent's side — so its non-overlapping value is the **export hook**, which is
  what the MCP is scoped to.
- JIT sequencing keeps the cheap, high-information rig work (Phase A/B) unblocked; the MCP's first real use is
  Phase C/D anyway, when the live-connect gate naturally fires. Measurement gates commitment.
- A thin skill fits the project's "automate the enforceable, document the judgment" ethos and won't rot against
  `reconcile-docs`.

## Considered and rejected

- **MCP that authors geometry (drives the Editor to build mesh/deformers)** — no such API; would require fragile
  GUI automation.
- **Reverse-engineered moc3 writer** (e.g. `moc3-reader-re`) — violates the No-Reverse-Engineering clause; brittle.
- **Inochi2D (open-source alternative ecosystem)** — abandons Cubism Core + `pixi-live2d-display` + the existing
  `.cmo3` investment.
- **Full Tier-2 drive with Windows-side screenshot capture (Opt 2b)** — medium-cost, brittle (window must be
  visible); the autonomous "drive + see" need is already met by the runtime harness.
- **Fat self-contained skill** — duplicates repo state, fights the anti-duplication architecture, goes stale.

## Open (decided later, not here)

Whether the External API is FREE-available (confirm on first live connect); whether the blind `SetParameterValues`
co-pilot mode (2a) earns its keep once a rigging sprint actually arrives.
