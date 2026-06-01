# W5 Polish — Halo / Vignette Defringe (item a)

Date: 2026-06-01
Status: design (approved direction A3)
Scope: W5 open-polish item **(a)** only. Items (b) eye-smile-too-strong and (c) eye/forehead seam are deferred to their own passes.

## Problem

The runtime render (`live2d/w5-runtime-fullbody.png`) shows a dark/lavender **halo** along the character's outer hair edge and a faint **circular vignette ring** around the figure. Source: the W3 `isnet-anime` matte left a soft, anti-aliased, lavender-tinted fringe at the character silhouette boundary — the original art's bokeh/clover background color bleeding into the matte edge. This fringe is **baked into the exported atlas** `live2d/model/lotte.2048/texture_00.png` (visible as a lavender ring around the `face_base` disc and the `hair_L`/`hair_R` column parts).

## Key structural insight (why this is safe to target)

In `full_segment.py`, every part is built as `paste(source.crop(box))` then `putalpha(multiply(part_alpha, matte_a))` (`full_segment.py:67-69`).

- The **silhouette fringe** (the halo/vignette) is **partial-alpha** (`0 < α < 255`), anti-aliased, lavender-tinted — it comes from `matte_a`'s soft edge.
- The **interior crop-box edges** of face parts (eyes, lids, mouth) are **hard edges** (`α` jumps 255→0, no partial-alpha band) because the crop paste is rectangular and opaque.

Therefore an operation that touches **only partial-alpha pixels** hits the silhouette fringe and automatically skips the hard interior crop edges. This cleanly separates item (a) from item (c) (a seam is a hard crop edge, a different fix).

## Goal / success criteria

- The lavender halo along the outer hair edge and the circular vignette ring are visually gone (or reduced to imperceptible) on a dark Discord-like background, verified in the runtime harness.
- No new seams or gaps introduced at interior part boundaries (eyes, lids, mouth, scarf).
- The fix exists in BOTH the runtime artifact (immediate) and the source pipeline (so a future Cubism re-export stays clean) — no asset-level split-brain.

## Approach A3 (hybrid: fast-verify on atlas, then bake into source)

### Step 1 — Atlas defringe (verifiable now, Pillow only)
Operate on `live2d/model/lotte.2048/texture_00.png`:
1. Identify partial-alpha pixels (`0 < α < 255`).
2. **Alpha erode** the silhouette fringe by a tuned radius (start small, e.g. 1-3 px), removing the outermost translucent band.
3. **RGB decontamination**: bleed the inner opaque color outward into the remaining edge so no lavender tint survives (premultiplied-style edge bleed / nearest-opaque fill).
4. Keep the original atlas backed up (git + a `.orig` copy) for instant revert and A/B.

Verify by loading the model in `runtime-check-full.html` via the SwiftShader throwaway-Chrome recipe (memory `bh-chrome-no-webgl`), screenshot the silhouette regions, montage before/after, save montage to disk for user review. Tune the erode radius / decontamination strength over a small candidate sweep (e.g. 1/2/3 px) chosen by eye.

### Step 2 — Bake the chosen params into the source
Port the same erode/decontamination onto `matte_a` in `full_segment.py` (after `matte_a = matte.getchannel("A")`, `full_segment.py:45`). Because `matte_a` is the single source every layer multiplies by, eroding it fixes the silhouette boundary for every part at once, and — being interior — leaves the eye/mouth/lid crop boxes untouched. This makes any future re-segment → PSD → Cubism re-export halo-free.

Step 2 is **written** this session; its clean-export is **verified later**, whenever the user next re-runs the W3→W4 export (it needs rembg + a Cubism round-trip, out of scope to run now).

## Components

| Unit | Purpose | Depends on |
|---|---|---|
| `live2d/tools/defringe_atlas.py` | Standalone: read atlas PNG, erode partial-alpha fringe + RGB-decontaminate, write cleaned PNG (+ keep `.orig`). Params: erode radius, decontam passes. | Pillow |
| `runtime-check-full.html` (existing) | Render cleaned atlas, screenshot for A/B montage. | SwiftShader Chrome |
| `full_segment.py` matte_a patch | Same erode/decontam on the source matte so re-exports stay clean. | Pillow (+ rembg at re-run time) |

## Verification plan

1. Atlas A/B montage (original vs defringed) on a dark background — halo/ring gone, the silhouette edge clean.
2. Interior-integrity check — eyes/lids/mouth/scarf boundaries unchanged (no gaps, no shrink) by pinning a few param states in the harness and comparing to the pre-fix `w5-runtime-*` evidence.
3. Source patch is a no-op-shaped change recorded for the next re-export (verified on that future export, not now).

## Risks / open questions

- **Vignette may be partly opaque, not pure fringe.** Before committing erode params, zoom into the `face_base` disc boundary in the atlas: if the ring is opaque (a baked circular element of the original art), defringe will not remove it and we adjust (e.g. mask/crop the disc, or revisit the matte). First implementation action: confirm the ring is partial-alpha.
- **Environment**: `.venv` is absent on `master` (gitignored). Restore a minimal venv with Pillow before Step 1; rembg + `isnet-anime` only needed if/when Step 2 is actually re-run.
- **Over-erode** could nibble fine hair wisps. Mitigate with the smallest radius that clears the ring, chosen visually; `.orig` backup makes revert instant.
- **Split-brain**: Step 2 is the explicit mitigation — fix is recorded at the source, not only in the exported texture.

## Out of scope (this pass)
- (b) eye-smile keyform re-tune — Cubism GUI work.
- (c) eye/forehead seam — hard crop-box edge, separate fix (extend box / feather).
- Pushing `master` to origin — unrelated, needs separate sign-off.
