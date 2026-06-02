# Lotte — prompt audit log

**What this is.** An audit log and a **style-vocabulary reference**, NOT a
reproducibility guarantee. The base illustration cannot be regenerated, and
GPT-image-2 edits are stochastic (per the Phase 1 spec). These prompts are kept
because their *descriptive language* (how Lotte is described) is the reusable part:
it seeds the W2 hidden-state edit prompts so generated references stay on-model.

---

## 0. Original creation — NOT RECOVERABLE

`lotte-discord-original.png` was built by iterative revision, so there is no single
prompt that reproduces it. Left intentionally blank. Do not try to reconstruct it.

---

## 1. Bridge prompts (original → variant)

The prompts fed to GPT-image-2 to derive each variant from
`lotte-discord-original.png`. **User to paste** what is recoverable.

### original → discord-version (1586×992, current Discord background)

Provided to GPT-image-2 with `lotte-discord-original.png` attached as the reference.
This is a **side-extension (outpaint)**: the character is preserved and pixel-aligned;
only the left/right background is newly generated.

```
Reference image attached: a 1:1 anime portrait of a girl with long brown hair, large
violet eyes, a violet ribbon on the top of her head, wearing a navy blue sailor
uniform. The background features a soft dreamy purple-and-beige bokeh, with a subtle
clover pattern motif and a soft circular halo behind her head.

Generate a single image in 16:10 aspect ratio (1920×1200 pixels) that meets ALL of
the following requirements:

1. CHARACTER PRESERVATION (highest priority)
Preserve the character exactly as she appears in the reference — same face, same
hair color and style, same violet eyes, same ribbon, same sailor uniform, same
gentle expression, same head-tilt and pose. The character must be centered
horizontally in the new canvas, with the same crop (top of the head down to the
upper chest visible) and the same proportional size as in the reference. Do not
redraw, restyle, age, or alter the character in any way.

2. SIDE EXTENSION
The new pixels to the LEFT and RIGHT of the character must:
- Match the existing background's dreamy, soft anime aesthetic
- Use the same muted purple, warm beige, and soft pink palette
- Naturally continue and extend the clover pattern motif across both sides
- Continue the soft circular halo / frame structure outward beyond the character
- Scatter, sparingly, a few small kawaii motifs across both sides: tiny twinkling
stars, small hearts, and gentle flower petals — all in muted pastel tones, light
and unobtrusive, never dominating the character
- Maintain the same soft-focus, bokeh-like depth of field as the reference
- Contain NO additional characters, NO text, NO sharp or harsh elements

3. OUTPUT
A single PNG at 1920×1200, with the character pixel-aligned to the reference.
```

**Observation (informs W1):** because the character is pixel-aligned and only the
sides were extended, `version`'s character == `original`'s character. `version` is
992 tall vs `original`'s 1254 for the same crop, so `original` carries more facial
pixels. Likely base plan: rig the character from `original`, borrow `version`'s
extended background as the ambient layer (they align).

### original → discord-banner (2110×745, Nitro profile banner)
```
(paste prompt here)
```

### original → mobile-background (841×1870, phone wallpaper)
```
(paste prompt here)
```

---

## 2. Style vocabulary (extracted)

Distilled from the prompts above once pasted — the recurring descriptors that keep
Lotte on-model (hair, eyes, ribbon, uniform, palette, rendering style). Filled in
during W1/W2 and reused as the prefix for every W2 edit prompt.

Extracted from the discord-version bridge prompt (the canonical character + scene
description). Reuse the CHARACTER block as the prefix for every W2 edit prompt.

**Character:** long brown hair; large violet eyes; a violet ribbon on the top of the
head; navy blue sailor uniform; gentle expression; slight head-tilt; crop = top of
head down to upper chest.

**Scene / palette:** soft dreamy purple-and-beige bokeh; subtle clover pattern motif;
soft circular halo behind the head; muted purple + warm beige + soft pink palette;
sparse muted-pastel kawaii motifs (tiny twinkling stars, small hearts, gentle flower
petals); soft-focus / bokeh depth of field; soft anime aesthetic. No text, no extra
characters, no sharp elements.

---

## 3. W2 hidden-state edit prompts (cookbook)

Built during W2. Each is an edit applied ON the locked base to harvest hidden /
interior pixels (NOT a fresh generation). Discipline (spec §7): harvest hidden
pixels only, landmark-align, color-match, reject unless it composites invisibly and
survives the deformation test.

- [x] eyes closed — for the upper-eyelid blink art **(Phase 1.0 pilot, on the face crop, not the full base)**
- [x] forehead revealed (hair pushed back) — for face base under bangs **(W2, full base)**
- [x] cheek / jaw line (side hair tucked) — for face base under side hair **(W2, full base)**
- [x] smiling (softly creased) eyes — for `EyeL Smile`/`EyeR Smile` (NOT `ParamEyeForm`; see spec §5 correction / pilot learning #3) **(W2)**
- [x] closed mouth — unlocks tight-closed + closed-smile via `ParamMouthForm` **(W2)**
- [ ] (optional) gentle closed smile — only if deriving from closed + form looks off

### eyes-closed (pilot) — produced `live2d/pilot/gen/eyes-closed.png`

Input: `live2d/pilot/face-crop.png` (803×690 crop of the locked `original`). Tool: GPT-image-2.

```
Reference image attached: a 1:1 anime portrait — long brown hair, large violet
eyes, a violet ribbon on the top of the head, navy blue sailor uniform, gentle
expression, slight head-tilt.

Keep the character EXACTLY the same — same face, same hair, same ribbon, same
lighting, same line weight, same colors, same framing, and the same pixel
alignment. Change ONLY the eyes: draw them gently closed in a soft, natural,
relaxed-eyelid shape (a calm, content closed-eye look, not a hard squint). Do not
move, recolor, or restyle anything else — not the hair, not the mouth, not the
background. Output the same size as the reference, character pixel-aligned to it.
```

**Result / drift observation (W2 evidence):** Output came back at 1353×1163 (archived
as `eyes-closed-raw-1353x1163.png`); user downscaled a copy to 803×690 = the crop
size. Ghost-overlay + amplified-diff vs the crop: **hair / ribbon / face outline are
pixel-aligned** (no doubling), and the closed eyes land exactly on the open-eye
position — good for harvesting the eyelid band. **BUT GPT widened the mouth into a
fuller open smile despite the "change ONLY the eyes" instruction** — confirmed mouth
drift. Harmless for the pilot (only the eye band is harvested in Task 4), but it
validates the spec §7 W2 discipline: production edits need landmark-align + tight,
conservative masks; a naive full-region paste would import the drift.

### W2 full-base harvest (2026-05-31) — all 4 accepted

Generated by the user on `live2d/assets/lotte_base.png` (refs returned 1254² → resized
×2 to the 2508² base for alignment). Verified with `live2d/tools/harvest_check.py`
(ghost-overlay + amplified-diff vs base) and harvested into full-canvas patches + masks
by `live2d/tools/harvest_patches.py`. **Harvest geometry note:** patches are FULL-CANVAS
(not the plan's literal small crops) because W3 `full_segment.py` consumes them
full-canvas — forehead/cheekjaw are `alpha_composite`d onto the rembg matte for the skin
base; eyes-smile/closed-mouth are full-canvas `layer()` sources re-cropped at base-relative
boxes. Each patch = the resized ref with alpha = a feathered band mask (FEATHER=20).

| ref | mean-amplified-diff | accept rationale |
|---|---|---|
| `forehead` | 35.6 | large but localized to hairline/forehead (bangs lifted, skin revealed); face/eyes/ribbon/mouth aligned. High mean = hair-strand edge shimmer, harvested band is forehead-only. |
| `cheekjaw` | 31.1 | localized to side-hair → cheek/jaw reveal; aligned. High mean = side-hair repositioning + minor collar edge variance, outside the harvest band. |
| `eyes-smile` | 13.2 | tight to both eyes (smile crease) + slight brow raise; everything else dark. |
| `closed-mouth` | 11.9 | mouth open→closed (soft closed-lip line), **chin in frame, not clipped** (fixes the pilot's clipped mouth); aligned. |

**Skin-fill seam check (W2.6):** forehead + cheekjaw `alpha_composite`d onto the base
blend with feathered edges, no hard rectangular seams — confirms the patches fill skin
invisibly for the W3 `face_base`. Bands are starting points (`harvest_patches.py BANDS`)
and the W2↔W3 iterative core may re-tweak during W3 calibration.

Prompts used (canonical CHARACTER prefix from §2 + the proven §3 "EXACTLY the same /
ONLY" framing):
- **forehead-revealed:** *"…Change ONLY the hairline: push the front bangs up and back
  to reveal the full forehead skin underneath, drawn in the same soft shading as the
  rest of the visible face.…"*
- **cheek/jaw (side hair tucked):** *"…Change ONLY the side hair: tuck the left and
  right side-hair locks behind the ears to reveal the full cheek and jawline skin
  underneath, drawn in the same soft shading.…"*
- **smiling (creased) eyes:** *"…Change ONLY the eyes: give them a soft, gentle smiling
  crease (lower lids raised slightly, a content 'soft smile' eye shape), eyes still
  mostly open.…"*
- **closed mouth:** *"…Change ONLY the mouth: draw it gently closed (a soft, relaxed
  closed-lip line), keeping the same lip color and the same position. Keep the full chin
  and jaw in frame, not cropped.…"*

**Regenerations needed:** none — all 4 accepted on the first generation (informs the W2
cookbook: this CHARACTER-prefix + "change ONLY X" framing is reliable on GPT-image-2 for
localized hidden-state edits; only the pilot's eyes-closed showed mouth drift, which the
explicit "not the mouth" / "ONLY the eyes" wording here avoided).

---

## 4. Phase B — scene plate (character removed, background only)

Built for the rig-strategy pivot (ADR-0001 / ROI.md Phase B). The rigged character
(from `original`) composites OVER this plate; the plate must contain the lavender scene,
the completed halo ring, and the bokeh/clover/motifs of `version` with the girl removed —
so the rig sits on a congruent backdrop and never exposes a pixel-aligned static twin
(no **doubling**; see CONTEXT.md). This is the INVERSE of the §3 edits: remove the
character, keep + complete the background.

Input: `live2d/source/lotte-discord-version.png` (1586×992 — the wallpaper WITH the girl,
made by side-outpainting `original`). Tool: GPT-image-2. Output target: `live2d/gen/scene-plate.png`.

```
Reference image attached: a 16:10 anime wallpaper (1586x992) — a girl with long brown
hair, large violet eyes, a violet ribbon, and a navy sailor uniform, centered against a
soft dreamy purple-and-beige bokeh background with a soft circular halo behind her head,
a subtle clover pattern, and sparse pastel kawaii motifs (tiny twinkling stars, small
hearts, gentle flower petals).

Generate a single image, the SAME dimensions and SAME 16:10 framing as the reference,
that is the BACKGROUND ONLY — with the girl completely removed:

1. REMOVE THE CHARACTER (highest priority)
Completely remove the girl — her hair, face, ribbon, body, and uniform. Leave NO trace:
no silhouette, no ghost, no faint outline, no stray hair strands, no shadow of her shape.
The result must contain NO characters and NO people at all.

2. RECONSTRUCT THE BACKGROUND where she was
Fill the area she occupied with the same background that surrounds it, continued
naturally and seamlessly:
- the same soft dreamy purple-and-beige bokeh and muted purple + warm beige + soft pink palette
- COMPLETE the soft circular halo into a full, unbroken glowing ring/oval behind where
  she stood (the arc that was hidden by her head and hair, now visible)
- continue the subtle clover pattern across the whole frame
- keep the existing scattered pastel motifs (tiny twinkling stars, small hearts, gentle
  flower petals, soft falling petals); a few may drift across the center too, sparingly
- maintain the soft-focus, bokeh depth of field everywhere; smooth, even, dreamy

3. PRESERVE the existing background pixels
Keep the left/right/top/bottom background as in the reference wherever the girl is NOT —
do not restyle, recolor, or re-light it. Only the region she occupied is newly filled.

4. OUTPUT
A single PNG at the reference's exact pixel size (1586x992), 16:10, background only.
NO text, NO characters, NO sharp or harsh elements, NO watermark.
```

**Result / drift observation:** _pending generation (USER → GPT-image-2)._ Watch for: GPT
resizing/restyling the whole frame (the eyes-closed edit came back 1353x1163 — accept any
16:10 and realign on composite); residual ghost where the hair was; halo left as an open
arc instead of a full ring. Save the accepted plate as `live2d/gen/scene-plate.png`.
