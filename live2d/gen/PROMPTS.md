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

- [ ] forehead revealed (hair pushed back) — for face base under bangs
- [ ] cheek / jaw line (side hair tucked) — for face base under side hair
- [ ] eyes closed — for the upper-eyelid blink art
- [ ] smiling (softly creased) eyes — for `ParamEyeForm`
- [ ] closed mouth — unlocks tight-closed + closed-smile via `ParamMouthForm`
- [ ] (optional) gentle closed smile — only if deriving from closed + form looks off

```
(prompts added here as W2 proceeds, each tagged with which output it produced)
```
