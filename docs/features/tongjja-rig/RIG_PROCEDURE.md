# 통짜 re-rig — Cubism walkthrough (CD-1..9)

The current rigging procedure under the pivot (ADR-0001): one whole-image `base` + opacity-swap bands,
replacing the W4 mesh-deform of face parts. **Strategy-level** — it belongs to the 통짜 strategy, is reused
across investigations (`cd4-blink`, future expression bands, re-exports), and is archived only when ADR-0001
itself is superseded by a strategy pivot — **not** when any single investigation closes. Strategy-*invariant*
editor facts (Replace-not-Add, re-mesh on Enter, the single-2048 atlas, moc3 ≤ 5, the SwiftShader CDP recipe)
are **not restated here** — they live in `live2d/DOMAIN_MAP.md`; this file references them.

> **Live blink state — read `cd4-blink/RESEARCH.md` §2 first.** CD-4 (blink) **hit a warp/distortion wall**
> (06-03); root cause (pixi-vs-model) is `❓` and gated behind the localization test, to be re-run cleanly
> post-restructure. The steps below are the procedure; they are **not** a claim that blink currently works.

**Inputs (Phase C+D agent-prep, 2026-06-02):** `live2d/lotte.psd` — **7 full-canvas aligned layers** (2508²),
back→front: `base, mouthband_closed, eyeband_smile, eyeband_closed, hair_L, hair_R, ribbon`. `base` is the
WHOLE character with **open eyes + open mouth baked in**; the three bands are feathered baked alternate-state
art revealed by **opacity**, not deform. (PSD is gitignored — regenerate via
`live2d/pilot/.venv/bin/python live2d/tools/full_segment.py` then `… build_psd_full.py`.)

**What is DIFFERENT from the W4 mesh-deform rig (read first):**
- `base` is ONE ArtMesh — no face cuts, **no clipping masks**, no mesh-deform blink.
- Tilt / turn / breath / lean = **whole-image WARP** over `base` (+ bands), not part deform.
- Blink / smile / mouth = a band drawable's **opacity** keyed to a param (frame-swap), not geometry.
- Gaze = **head-lean only** (the runtime probe drives Angle/Body with eyeball weight 0, ADR-0001) → **NO**
  `ParamEyeBallX/Y` or iris keys. One less thing to rig.

> **Two corrections that OVERRIDE any older rectangle/import wording (now also in `DOMAIN_MAP`):**
> 1. **Swap bands are FULL-SILHOUETTE frame-swaps, not feathered rectangles** — a band's Cubism **mesh must
>    cover the WHOLE character** (a box mesh re-creates the premultiplied-alpha dark line). `cd4-blink/RESEARCH.md` §1.2.
> 2. **PSD reimport = "Replace [lotte.psd]", NEVER "Add all layers as new ArtMesh"** (Add triplicates parts
>    + destroys the warp rig). `DOMAIN_MAP.md` (machine-ops) + `cd4-blink/RESEARCH.md` §1.3.

### CD-1 Import + auto-mesh
File ▸ Open `live2d/lotte.psd`. 7 layers → 7 ArtMeshes in register; names in the Parts palette. Select all
(Ctrl+A) ▸ **Automatic Mesh generator** (Ctrl+Shift+A) ▸ default preset. Give `base` a **fairly dense mesh**
(more control points → a smoother warp tilt with no creasing); bands can stay light.
Manual: https://docs.live2d.com/en/cubism-editor-manual/reimport-psd/

### CD-2 Deformer nest (two nested warps)
Build with **[Create Warp Deformer]**, then drag each part into its deformer:
```
root
└─ body_warp  (Warp, ~6×6, covers the WHOLE character)   ← ParamBreath, ParamBodyAngleX
   ├─ head_warp (Warp, ~5×5, covers head→shoulders)      ← ParamAngleX, ParamAngleY, ParamAngleZ
   │    ├─ base              (the 통짜 character mesh)
   │    ├─ eyeband_closed    (opacity-swap — blink)
   │    ├─ eyeband_smile     (opacity-swap — ^^)
   │    └─ mouthband_closed  (opacity-swap — closed mouth)
   ├─ hair_L   (Rotation/Warp, physics-driven)           ← ParamHairSide
   ├─ hair_R   (Rotation/Warp, physics-driven)           ← ParamHairSide
   └─ ribbon   (Warp, physics-driven)                    ← ParamHairFront
```
The bands sit INSIDE `head_warp` next to `base` so they stay registered over the face when the head tilts.
**Cubism FREE caps a deformer at 2 params → rig one param per warp** (Angle X / Y / Z each on its own
warp); this also removes the diagonal corner-blend distortion (`DOMAIN_MAP.md`).
Warp-deformer help: https://docs.live2d.com/en/cubism-editor-manual/deformer-warp/

### CD-3 Head tilt/turn = warp the HEAD ROWS only (the key 통짜 trick)
Because `base` is one mesh, the warp must move the head WITHOUT dragging the body.
1. On `ParamAngleZ` (−30..30) ▸ **[Add 2 Keyforms]**. At +30, in `head_warp` move only the **upper (head)
   control points** to rotate the head a little — **leave the bottom (neck/shoulder) rows at default** so the
   body stays put. Mirror for −30. Keep it gentle (Tier-1: ±8 is the live-tuned Phase-A feel, not ±30).
2. `ParamAngleX` / `ParamAngleY` (−30..30): the same head-rows-only idea but a tiny **planar** shift + slight
   rotation. **FLAT ONLY — no cheek/nose parallax** (ADR-0004, flat discipline).
> Tip: anchor the neck row first (don't move it across any AngleZ/X/Y keyform). If the shoulders tilt with
> the head, you moved a row too low.

### CD-4 Blink = opacity-swap (the new mechanism) — see `cd4-blink/RESEARCH.md` §2 for the warp wall
1. Select **`eyeband_closed`** (the drawable, in the Parts palette).
2. Select `ParamEyeLOpen` (0..1; 1 = open, 0 = closed) ▸ **[Add 2 Keyforms]**.
3. At param **= 1 (open)** set this drawable's **Opacity = 0** (hidden → base's open eyes show). At param
   **= 0 (closed)** set **Opacity = 100** (the closed-eye band covers the open eyes).
4. That's the whole blink. Runtime auto-blink drives `ParamEyeLOpen` 1→0→1, fading the band in/out. *2-state
   first*; both eyes blink together (one band over both) — an independent wink needs the band split L/R (a
   re-cut, out of scope). **The band mesh must cover the WHOLE character** (`cd4-blink/RESEARCH.md` §1.2).
Opacity keying: https://docs.live2d.com/en/cubism-editor-manual/facial-expression-system/

### CD-5 (optional, decide on-screen) eye-smile ^^ + closed-mouth
Same opacity pattern; wire only if wanted. Draw order already gives blink priority (`eyeband_closed` is above
`eyeband_smile`).
- **`eyeband_smile`** opacity on a smile param (`EyeL Smile` 0..1, or a custom `ParamSmile`): 0 → Opacity 0,
  1 → Opacity 100. (No runtime smile driver yet — for a manual/expression preset.)
- **`mouthband_closed`** opacity for a closed-mouth SNAP: bind to `ParamMouthOpenY` **inverted** (OpenY 0 →
  Opacity 100 = looks closed; OpenY 1 → Opacity 0 = base's open mouth shows), OR a custom `ParamMouthClose`.
  This also sets the **resting mouth**: opaque-at-rest = gentle closed; off-at-rest = the baked open smile.
  Pick what reads calmer. (Smooth/talking mouth is INFEASIBLE on flat — that's the speech-bubble's job.)

### CD-6 Breath + lean (whole-character warp)
On `body_warp`: `ParamBreath` (0..1) → a gentle vertical rise/scale of the whole grid; `ParamBodyAngleX`
(−10..10) → a subtle horizontal lean. Runtime auto-breath drives `ParamBreath`; the Phase-A probe drives
`ParamBodyAngleX` for the head-lean gaze.

### CD-7 Physics (hair + ribbon) — reuse the validated feel
`hair_L`/`hair_R` on a low-scale pendulum → `ParamHairSide`; `ribbon` on its own warp → `ParamHairFront`
(Delay ~0.7, lighter/faster — it should trail the head ~5 frames; the liveness is the **lag**, not the
amplitude — CDP-verified, W4 Step 9B). Reuse `live2d/model/lotte.physics3.json` as the starting physics file.

### CD-8 Atlas (single 2048 — now roomy)
**[Edit Texture Atlas]** ▸ size **2048×2048** ▸ **Auto Layout** ▸ **"Set magnification automatically."** Only
**7 parts** now (vs 19) → far more room, so the auto-magnification can stay **higher = sharper** than the old
~0.5×. FREE = one atlas, ≤100 pieces (`DOMAIN_MAP.md`).

### CD-9 Export (moc3 5.0) + verify
File ▸ **Export embedded file** ▸ moc3. Include `.moc3`, `.model3.json`, **textures**, `physics3.json`,
`.cdi3.json`. **Set `.moc3 file version` to 5.0** (NOT the v6 default — `DOMAIN_MAP.md`). Export to
`live2d/model/` as `lotte.model3.json`; save the project as `live2d/pilot/lotte-good.cmo3` (the working
master). Then ping the agent — it runs `tools/check_model.py` (asserts v≤5 + populates the EyeBlink group)
and renders it over `gen/scene-plate.png` at real Discord scale to gate the blink + the seam.

### Tier-1 restraint (unchanged — ADR-0004)
Tilt ±8 (Phase-A feel), not ±30. Breath/lean subtle. Hair low scale. Most life is FREE from auto-blink +
auto-breath + physics + the head-lean gaze. If a band sits wrong at real scale, it's a one-line fix in
`full_segment.py` (band coords / `FEATHER`) → re-run → re-import (the W3↔W4 loop).
