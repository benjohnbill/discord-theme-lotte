# Lotte — source rasters (source-of-truth)

These are the original, irreplaceable Lotte illustrations. The base **cannot be
regenerated** (it came from iterative revision, no single reproducible prompt), so
these files are committed as source-of-truth per the Phase 1 design spec
(`docs/superpowers/specs/2026-05-31-lotte-live2d-phase1-rig-design.md`, §2.8 / §8).

Full checksums: see `SHA256SUMS` in this directory.

## Lineage

`lotte-discord-original.png` is the **parent**. The other three were derived from it
via GPT-image-2 "bridge" edits (the prompts the user can provide — see
`live2d/gen/PROMPTS.md`):

```
lotte-discord-original  ──┬──► lotte-discord-version   (Discord background)
                          ├──► lotte-discord-banner    (Discord Nitro banner)
                          └──► lotte-mobile-background  (phone wallpaper)
```

## Files

| File | Dimensions | Actual use | Role for the rig |
|---|---|---|---|
| `lotte-discord-version.png` | 1586 × 992 (16:10) | **Current Discord background (in active use).** Derived from `original`. | The look Phase 1 must preserve → **locked-base candidate (target look).** |
| `lotte-discord-original.png` | 1254 × 1254 (1:1) | Parent source of the other three. | Canonical character; tighter framing, likely most facial resolution → **locked-base candidate.** W1 compares the two and locks one. |
| `lotte-discord-banner.png` | 2110 × 745 (wide) | **Discord Nitro profile banner (in active use).** | Reference only — hair flow / alternate framing for occluded-region inpainting. |
| `lotte-mobile-background.png` | 841 × 1870 (tall) | **User's phone wallpaper (in active use).** | Reference only — the one view showing the full upper body (shoulders/arms/torso); reference for what the bust occludes, and the future (deferred) mobile surface. |

## Base selection (W1)

W1 (base lock + upscale) compares `version` vs `original` for facial resolution,
locks one, upscales it with waifu2x, and writes the result to
`live2d/assets/lotte_base.png` with its rationale in `live2d/BASE.md`. Because
`version` is itself a derivation of `original`, their faces should be close; the
choice is mostly about which gives cleaner, higher-resolution facial pixels while
keeping the Discord look. These four files stay here as the untouched originals.

**Provenance:** copied from the user's Windows assets folder
`C:\Users\benjohnbill\OneDrive\바탕 화면\Life_System\04_System_Assets\` on 2026-05-31.
Generated with GPT-image-2 (iterative revision). Filenames normalized to kebab-case.
