# Lotte Live2D — Context (glossary)

Canonical language for the Lotte aliveness work. Glossary only — no implementation detail.

## Terms

### Aliveness
The project's North Star. Defined as **attention / presence** — "Lotte notices me, reacts to me." It is NOT
expression range, NOT big motion, NOT image-swap variety. A still illustration that *reacts* (gaze, lean toward
the cursor, breathe) is more alive than a busy one that ignores the viewer. Reaffirmed 2026-06-01 after the first
live in-Discord view.

### Patchwork separation ("누더기")
The **load-bearing failure mode** observed in the first live in-Discord rig (2026-06-01). The face reads as
**discrete rectangular components stacked and sliding over each other** rather than one cohesive surface. It is
what breaks the *living character* read — "absolutely not a living character." Has two halves:
- **Hard-edge half** — the rectangular crop-box outlines of separated parts. Fixable on the flat source by
  feathering the part alpha.
- **Fundamental half** — separated parts slide/double on **runtime deformation** because the flat source has
  **no under-drawing** (no skin under an eyelid, no socket behind an eye). This is why blink must be a
  **frame-swap** of a baked state, not a runtime deform. (The earlier claim that AI-harvested closed-eye art
  also "reads foreign in tone, unfixable by feathering" is **contended**: the W2 edit-on-base discipline —
  landmark-align + color-match + feathered band (FEATHER=20) — was built to prevent tone drift, and the pilot
  opacity-swap passed with it at small scale. Real-scale confirmation is pending the verification gate.)

Distinct from **flippancy ("경박함")** = secondary defect, motion amplitude too large (violates flat-rig
discipline). Cheap tuning fix; not the load-bearing complaint.

### Living illustration vs Deforming character
Two opposed rig strategies, named to keep the trade-off explicit:
- **Living illustration** — the original image moves *mostly as a whole* (tilt, breath, gaze, hair sway); the
  face is not cut into deforming parts. Maximises fidelity to the original art; avoids patchwork by construction.
- **Deforming character** — the face is cut into parts that deform (blink, smile, head-turn) for more
  expressiveness. On a flat (un-layered) source this produces patchwork.

### 통짜 (base)
The whole-image-warp foundation that realises the **Living illustration** strategy: Lotte's mass (hair, posture,
collar) held as one cohesive surface, animated by whole-image warp + physics rather than cut into deforming parts.
The agreed floor for the rig (2026-06-01); anything separated from it must earn its place on feasibility × ROI.

### Character consistency
Fidelity of the rigged result to **the original Lotte illustration the user presented** (its exact look and
feel). A first-class success criterion alongside aliveness. Every AI-synthesized or AI-harvested part is a fresh
generation that risks drifting from it; the more the face is cut and re-synthesized, the more consistency erodes.

## Compositing

### Scene plate
The character-removed background — the lavender scene, halo ring, and bokeh of `lotte-discord-version` with Lotte
herself inpainted out. The rigged character composites over the scene plate. Distinct from the **version
wallpaper**, which still contains a static, pixel-aligned copy of the character.
_Avoid_: "background wallpaper" (ambiguous — the wallpaper still holds the twin).

### Doubling (ghost-twin)
The artifact where a moving rigged part would expose its own pixel-aligned static copy in the background behind
it, reading as a detached double. A **forward risk** if the rig were composited over the version wallpaper (the
twin) — avoided by compositing over a **scene plate** instead. NOT the cause of the observed gray-background live
render: as of 2026-06-01 the rigged character and any background have never been combined, so no twin was present
there. The gray render's "detached" read came from a matted part reading as a sticker over an *alien* (gray)
backdrop, not from doubling.
