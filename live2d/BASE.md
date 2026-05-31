# Base lock + resolution decisions (W1)

This file records the base-image lock and upscale decisions. The **target/display
inputs and the planned approach are decided now** (from the 2026-05-31 brainstorm);
the **result fields are filled when W1 actually runs**.

## Target displays (the user's environment — author for the densest)

Discord usually runs on one of the two external monitors. All three are in regular use:

| Display | Resolution | Aspect |
|---|---|---|
| Laptop panel | 1920 × 1200 | 16:10 |
| External (QHD) | 2560 × 1440 | 16:9 |
| External (WQXGA) | 2560 × 1600 | 16:10 |

**Author-for = 2560 × 1600** (the densest). One rig serves all three: Phase 0's
`fit()` scales the model to the window, and a texture crisp on the biggest display
downscales cleanly on the smaller ones. The rig is **aspect-agnostic** (character
only, transparent background); the 16:10 vs 16:9 difference only affects the
background layer, which the theme renders with `background-size: cover`, so a 16:10
background source adapts to the 16:9 QHD without distortion.

## Planned approach (confirm in W1 / Phase 1.0)

- **Character source = `lotte-discord-original.png`** (1254², the parent; more native
  facial pixels than `version`, which is its side-extension — see
  `source/README.md` and `gen/PROMPTS.md` §1).
- **Background source = `lotte-discord-version.png`** extended bokeh (the live Discord
  look; aligns with the original character because version is pixel-aligned to it).
- **Upscale = waifu2x ×2** on the locked character source → ~2508 px, giving ~1.4–1.5×
  headroom over a 1600 px display plus deformation headroom.
- **Texture atlas budget = 4096** (Cubism). Confirm the ~20 parts pack into 4096 during
  Phase 1.0 / W1; if not, reduce upscale or merge parts.
- **Order:** lock → upscale the whole base once → then separate parts (never per-part
  upscale).

## Result (W1 fills)

- Locked base file: _(W1)_
- sha256: _(W1)_
- Upscale applied: _(W1)_
- Atlas packing verified: _(Phase 1.0 / W1)_
