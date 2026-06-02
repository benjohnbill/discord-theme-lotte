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

### Band / frame-swap (opacity-swap)
The mechanism that adds expression to a 통짜 base WITHOUT cutting deforming face parts. A **band** is a thin,
**feathered** strip of a *baked alternate-state* art (closed eyes, smiling eyes ^^, closed mouth — the
`gen/refs/*` keyforms) covering one feature: its interior is opaque (covers the feature), its edges fade to
transparent so it blends into the base with no rectangular seam. A **frame-swap (opacity-swap)** drives that
band's opacity 0→1 on a param (e.g. `ParamEyeLOpen/ROpen` for blink) — at 0 the base's drawn state shows, at 1
the band covers it with the baked alternate. It is a *frame replacement*, not a geometry deform, so it needs no
under-drawing and produces no patchwork (it replaces exactly the W4 mesh-deform of hard lid crops; the pilot's
swap blink passed). The cross-fade ghosts mid-transition, so it suits fast / discrete states (blink, a settled
^^, a snap to closed-mouth) — NOT a smooth morph or lip-sync, which a flat source cannot do cleanly.

### Under-fill backing
The fix for the **Fundamental half** of patchwork (no under-drawing) under a 통짜 cut. When a moving part
(front hair-lock, ribbon) is carved out of the `base` so it does not double on sway, the flat source leaves
no art behind it — a sway would reveal a hole (the scene plate). The under-fill is a heavily-blurred, opaque
copy of the character matte, bounded to the silhouette, composited *beneath* the sharp base; real cheek/jaw
skin (the W2 `cheekjaw` patch) is laid over it where the side-locks sway most. It is **fully hidden at rest**
(the sharp layers cover it) and only a sway reveals it — as soft local colour instead of a hole. Introduced in
the Phase C+D 통짜 re-cut (`full_segment.py`, 2026-06-02). Cheap, invisible-at-rest, robust to small-amplitude
physics — pairs with feathered carve edges. NOT a substitute for real under-drawing (it is a soft smear), so
it only holds at the small physics amplitudes the rig actually uses.

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
