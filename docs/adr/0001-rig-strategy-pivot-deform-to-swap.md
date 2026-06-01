# 0001 — Rig-strategy pivot: face mesh-deform → 통짜 (whole-image warp) base + blink frame-swap

Status: accepted (2026-06-01). Supersedes the Phase 1 face-rigging approach **on quality grounds**; Phase 1
remains mechanically valid (it proved the load + drive chain end to end).

## Context

The first live in-Discord render of the Phase 1 rig succeeded mechanically (it loads, every Tier-1 channel
drives, it cursor-tracks) but read as "누더기" (patchwork): the flat, un-layered source has no under-drawing, so
W4's mesh-deformation of ~13 hard-rectangular face cuts (eyebrows, sclera, iris, upper/lower lids, mouth — the
`full_segment.py` box crops) slid and seamed over each other. Re-sourcing properly layered art is off the table
(DIY, no budget; the base is an irreplaceable flat AI illustration that cannot be regenerated as layers).
Reference Live2D wallpapers stay clean because they are rigged from hand-layered art with real under-drawing —
the one input we cannot produce.

## Decision

Drop face mesh-deformation. Animate Lotte as a **통짜 (whole-image warp) base + physics**, and add blink as a
**feathered eye-band frame-swap** — an opacity-swap on `ParamEyeLOpen/ROpen` between a baked open-eye band and a
baked closed-eye band, NOT a runtime deform of cut lid parts. Composite the rig over a **scene plate** (the
character inpainted out of the `version` wallpaper), not the character-bearing wallpaper. Drive **gaze by
head/body-lean** toward the cursor (`model.focus()` → Angle/Body, eyeball weight 0), with no iris cut.

## Why

- The pilot's opacity-**swap** blink passed its gate (`pilot/RESULT.md`); the W4 "upgrade" to mesh-deform is
  what introduced the patchwork. Reverting to swap is a return to what worked, not a new gamble.
- A frame-swap of a *baked* state needs no runtime under-drawing and produces no sliding — it sidesteps the
  flat-source failure mode by construction. The closed-eye art's "foreign tone" was a contended claim, not the
  observed cause (the W2 edit-on-base discipline color-matches; see `CONTEXT.md`).
- North Star = presence, not motion range. References confirm cloth/hair physics + gaze + breath clear the
  aliveness bar without busy part-deform.
- A scene plate avoids **doubling** (a moving part exposing its pixel-aligned static twin in the wallpaper) and
  gives the rig a congruent backdrop. The live patchwork was judged over an *alien gray* background the rig was
  never meant to sit on — the rig and a background have never actually been composited.

## Considered and rejected

- **Keep mesh-deform, just re-rig** — re-rigs the same patchwork; the defect is the flat source, not the rig.
- **Re-source hand-layered art** — no budget; the base cannot be regenerated as layers.
- **BG-twin (composite over the `version` wallpaper as-is)** — a free backing plate, but bounds motion to micro
  and makes free-edge sway double against the static twin.
- **Iris-track gaze** — reveals undrawn sclera on a flat source and conflicts with a whole-eye-band swap.

## Open (decided by the gate, NOT here)

Whether blink survives at real Discord scale; 2-state vs 3-state blink; mouth keep vs drop (speech-bubble
substitute — claim unverified); the ROI contribution weights themselves. The gate-ordered execution plan
(Phase A→D) and the cost/feasibility table live in `live2d/ROI.md`.
