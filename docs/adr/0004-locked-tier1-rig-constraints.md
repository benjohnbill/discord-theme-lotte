# 0004 — Locked Tier-1 rig design constraints: scope · background-out · flat discipline · restraint

Status: **accepted** (2026-05-31; relocated to an ADR 2026-06-09). These are the original Phase 1
design constraints (spec §2) that **survived the rig-strategy pivot** (ADR-0001) and still bind the rig.
They were previously held in `live2d/DECISIONS.md` #2/#5/#6/#7; that file is dissolved (ADR-0003 doc
architecture), so they live here as the immutable decision record. Do not re-litigate without new
information.

## Context

The Phase 1 rig design brainstorm (2026-05-31) locked a set of constraints, recorded in spec
`docs/superpowers/specs/2026-05-31-lotte-live2d-phase1-rig-design.md` §2 and seeded into
`live2d/DECISIONS.md`. The mesh-deform *technique* among them (DECISIONS #1) was later superseded on
quality by ADR-0001's 통짜 (whole-image warp) pivot. The four constraints below are orthogonal to that
technique choice — they constrain *what the rig is for and how restrained it is*, not *how the face is
cut* — so the pivot left them intact (in fact the 통짜 base is flat **by construction**, strengthening
flat discipline).

## Decision

These four constraints are locked for the Lotte rig:

1. **Scope — Discord bust only.** The rig targets the Discord background bust. The mobile surface stays
   a **static** wallpaper; a mobile rig is deferred, not in scope. *(DECISIONS #2)*

2. **Background is OUT of the model.** The model is **character-only, transparent**; any background is a
   separate ambient layer (post-pivot: the **scene plate** — see ADR-0001 + `CONTEXT.md`). Particle
   drift is deferred. *(DECISIONS #5)*

3. **Flat discipline** *(the constraint formerly cited as "DECISIONS §6")*. Reactivity lives on **flat
   channels** — gaze, blink, breath, head-tilt (`ParamAngleZ`), physics, smile. Head **turn**
   (`ParamAngleX` / `ParamAngleY`) is **tiny + planar + lag only**: a small planar offset, a slight
   rotation, and hair/body follow-through. **No pseudo-3D parallax** — never build cheek / nose / mouth
   parallax (the easiest way to accidentally get the 3D look). Post-pivot this is enforced structurally:
   tilt/turn/breath are **whole-image warp** over the 통짜 base, not part deform. *(DECISIONS #6)*

4. **Tier-1 restraint.** Most of the life is **free** — runtime auto-blink + auto-breath + physics. The
   cursor drives only a **small, damped** reaction (head-lean gaze post-pivot, ADR-0001) plus an
   occasional eye-contact smile. **Start under-animated**; loosen only if it reads dead. *(DECISIONS #7)*

## Why

- The North Star is **presence, not motion range** (`CONTEXT.md` — Aliveness). Restraint + flat channels
  serve presence; busy parallax and large motion read as flippancy ("경박함") and, on a flat source,
  as patchwork ("누더기").
- These four are **technique-independent**, so they outlived the mesh-deform→통짜 pivot. Keeping them in
  an ADR (immutable "why") rather than a mutable working doc prevents their re-litigation each time the
  rig technique churns.

## Relationship to other records

- **ADR-0001** supersedes the *technique* (DECISIONS #1: mesh-deform → 통짜 warp + frame-swap). It does
  **not** touch these four — it operationalizes #3/#4 (flat by construction; head-lean gaze; restraint).
- **Platform facts** that sat alongside these in `DECISIONS.md` (base lock #3, Cubism-FREE/runtime-core
  #4, checksums #8, the part set #9) moved to `live2d/DOMAIN_MAP.md`, not here — those are *facts*, these
  are *decisions*.

## Open

None — these are settled. New expressive channels (e.g. wiring `eyeband_smile` / `mouthband_closed`) are
decided live in Cubism within the Tier-1 restraint ceiling; that is an execution choice, not a re-opening
of these constraints.
