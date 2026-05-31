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
  > **Phase 1.0 finding (2026-05-31): Cubism FREE caps the atlas at 2048×2048, not 4096.**
  > For the full ~20-part build, plan for this: split across **multiple 2048 atlases**
  > (Cubism supports several), **lower the upscale**, or use **Cubism PRO** (paid) for 4096.
  > The 6-part pilot packed into a single 2048 atlas with room to spare.
- **Order:** lock → upscale the whole base once → then separate parts (never per-part
  upscale).

## Result (W1 fills)

- Locked character source: `live2d/source/lotte-discord-original.png` (1254×1254) — confirmed more facial px than `version` (992 tall).
- Background (ambient layer, OUT of model): `live2d/source/lotte-discord-version.png`.
- sha256 (character source): `84175c6721cfe8afab0e2ace90c81cb1951063ecbd69a934bcba0ba94567ffcc`
- Upscale applied: PIL Lanczos x2 (fallback; no neural upscaler in env) → `live2d/assets/lotte_base.png` (2508×2508), sha256 `c0e07b09fc0c4c4e…`. Quality note: softer than a neural upscaler (waifu2x/realesrgan/opencv all absent in env); acceptable for the soft-focus master, but re-upscale with a neural tool before W3 if edge crispness proves insufficient. Master preserved hi-res regardless of the later atlas downscale.
- Atlas packing decision (W3.4, 2026-05-31): at the full 2508² master resolution the 19 tight-bounded
  parts sum to ~12.67M px² ≈ **3.0× a single 2048×2048 atlas** (4.23× with 1.4 packing slack) — does
  **not** fit one FREE atlas. *(Conservative: `face_base`'s bbox is the full canvas because the
  isnet-anime matte leaves faint stray alpha at the corners; real content is smaller.)* **Decision for W4:**
  scale the **Cubism import** down to ~**0.5×** (≈1254² working canvas) so all parts pack into **one 2048
  atlas** with slack — OR let Cubism use **2 atlases** if FREE permits (verify in W4). Either way the hi-res
  `assets/lotte_base.png` master is preserved; only the Cubism source is scaled. Re-decide in W4 against the
  real atlas tool (it can downscale on layout).
