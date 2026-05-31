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
```
(paste prompt here)
```

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

```
(to be filled — e.g. "brown long hair, lilac eyes, purple ribbon, navy sailor
uniform, soft anime shading, lilac bokeh background, ...")
```

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
