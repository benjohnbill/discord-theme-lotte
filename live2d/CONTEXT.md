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
- **Fundamental half** — separated parts slide/double on deformation because the flat source has **no
  under-drawing** (no skin drawn under an eyelid, no socket behind an eye), and AI-harvested hidden states
  (closed-eye, smile) read as foreign in tone. NOT fixable by feathering; needs layered source art.

Distinct from **flippancy ("경박함")** = secondary defect, motion amplitude too large (violates flat-rig
discipline). Cheap tuning fix; not the load-bearing complaint.

### Living illustration vs Deforming character
Two opposed rig strategies, named to keep the trade-off explicit:
- **Living illustration** — the original image moves *mostly as a whole* (tilt, breath, gaze, hair sway); the
  face is not cut into deforming parts. Maximises fidelity to the original art; avoids patchwork by construction.
- **Deforming character** — the face is cut into parts that deform (blink, smile, head-turn) for more
  expressiveness. On a flat (un-layered) source this produces patchwork.

### Character consistency
Fidelity of the rigged result to **the original Lotte illustration the user presented** (its exact look and
feel). A first-class success criterion alongside aliveness. Every AI-synthesized or AI-harvested part is a fresh
generation that risks drifting from it; the more the face is cut and re-synthesized, the more consistency erodes.
