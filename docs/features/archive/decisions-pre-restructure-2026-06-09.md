# ⚠️ HISTORY — Pre-restructure live2d/DECISIONS.md snapshot (frozen 2026-06-09)

> **DISSOLVED (ADR-0003).** Live content was routed to type-homes: facts (#3/#4/#8/#9) → live2d/DOMAIN_MAP.md · principles (#2/#5/#6/#7) → docs/adr/0004 · superseded (#1 mesh-deform, #9 19-part) = history below.
> This is the original frozen verbatim. `DECISIONS.md §6` = now `docs/adr/0004-locked-tier1-rig-constraints.md`. Not a live surface.

---

# Lotte Live2D — Locked Decisions

Source: docs/superpowers/specs/2026-05-31-lotte-live2d-phase1-rig-design.md §2. Do not re-litigate without new information.

1. Technique = Live2D mesh deformation (not frame/sprite).
2. Scope = Discord bust only; mobile stays static.
3. Base locked, not regenerated. **Confirmed in W1 (2026-05-31): character source = `original`** (1254², more facial px); background from `version` (its outpaint, pixel-aligned). Upscaled master = `live2d/assets/lotte_base.png` (2508², PIL Lanczos x2 — no neural upscaler in env). See live2d/BASE.md.
4. Cubism 5 FREE (.moc3); runtime swaps the Cubism 2 core for the official Cubism 4 core. Verified in Phase 1.0 Task 1.
5. Background is OUT of the model (character-only, transparent). Particle drift deferred.
6. Flat-rig discipline: reactivity on flat channels (gaze, blink, breath, tilt, physics, smile); head turn (AngleX/Y) tiny + planar + lag only, NO pseudo-3D parallax.
7. Tier-1 restraint: most life from auto-blink/breath + physics; cursor reaction small + damped; occasional eye-contact smile; start under-animated.
8. Source-of-truth durability: locked base raster committed/checksummed (see live2d/source/SHA256SUMS).
9. **W3 part set (user decision, 2026-05-31):** 19 parts. **Bangs are baked into `face_base`** (no separate bangs sway layer; forehead patch NOT applied so the fringe stays visible). **Hair merged to one mass per side** — `hair_L`/`hair_R` are the front side locks; back hair is baked into `face_base`. Rationale: color-based hair/skin separation is infeasible (skin ≈ bangs RGB), so spatial columns + the spec §7 merge escape hatch. Matte = rembg **isnet-anime** (default u2net kept the bokeh/halo bg). See live2d/PIPELINE.md (W3) + RIG_GUIDE.md "Full Build (W4)".
