# Lotte Live2D — Locked Decisions

Source: docs/superpowers/specs/2026-05-31-lotte-live2d-phase1-rig-design.md §2. Do not re-litigate without new information.

1. Technique = Live2D mesh deformation (not frame/sprite).
2. Scope = Discord bust only; mobile stays static.
3. Base locked, not regenerated. Character source likely `original` (more facial px); background from `version` (its outpaint, pixel-aligned). Confirm in W1. See live2d/BASE.md.
4. Cubism 5 FREE (.moc3); runtime swaps the Cubism 2 core for the official Cubism 4 core. Verified in Phase 1.0 Task 1.
5. Background is OUT of the model (character-only, transparent). Particle drift deferred.
6. Flat-rig discipline: reactivity on flat channels (gaze, blink, breath, tilt, physics, smile); head turn (AngleX/Y) tiny + planar + lag only, NO pseudo-3D parallax.
7. Tier-1 restraint: most life from auto-blink/breath + physics; cursor reaction small + damped; occasional eye-contact smile; start under-animated.
8. Source-of-truth durability: locked base raster committed/checksummed (see live2d/source/SHA256SUMS).
