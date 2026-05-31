# Lotte Cubism Tier-1 Rig Guide

Written as we learn (building while learning). Tier-1 scope only: blink, breath, gaze
(EyeBall X/Y), head tilt (AngleZ), tiny flat head turn, hair/ribbon physics, occasional
eye-contact smile (MouthForm + the standard `EyeL/R Smile` param — INV-8). Flat-rig discipline: no
pseudo-3D parallax (`DECISIONS.md` §6).

The Phase 1.0 **pilot** section below is the first, smallest pass — a crude 6-part face
slice that proves the art -> rig -> runtime chain. It was authored against the current
Live2D Cubism documentation (verified May 2026); links are inline so you can follow the
official tutorial alongside each step.

---

## Phase 1.0 Pilot — rig the 6-part slice

**Goal:** a deliberately rough Cubism 4 model of the face slice that blinks, gazes,
smiles a little, and has one hair sway. This proves the chain; polish is NOT the goal.

**Inputs the pilot prepared for you:**
- `live2d/pilot/lotte-pilot.psd` — 6 aligned layers, 803×690, RGB, 8 bit/channel
  (already in the format Cubism wants). Layers, back → front:
  `face_base` (matted character), `hair_side`, `eye_sclera`, `eye_iris`,
  `eye_upperlid` (closed-eye art for blink), `mouth`.
- `live2d/pilot/lotte-pilot-preview.png` — what the stack looks like flattened (the
  visible "wink" is only because the closed-eye lid sits on top in the static stack; the
  rig morphs between open and closed, so both never show at once).

> **Known pilot roughness (recorded in `pilot/RESULT.md`, do not be surprised):** parts
> are rectangular crops over the matte (only `face_base` has true alpha); the eyes/mouth
> on `face_base` still show *under* the overlay parts (no hole inpainting in the pilot);
> the mouth is small and slightly clipped at the bottom edge. All fine for a crude rig —
> the full build (W3/W4) fixes these. If a part is too rough to rig, **merging it into a
> simpler rig is an allowed pilot outcome**, not a failure (`DECISIONS.md` §6, spec §4).

### Step 0 — Install Cubism 5 FREE

Download and install the editor (FREE tier is enough for a Tier-1 bust):
https://www.live2d.com/en/cubism/download/editor/ — launch in **FREE** mode.

### Step 1 — Import the PSD

File ▸ Open (or drag the PSD into the View area). Choose `live2d/pilot/lotte-pilot.psd`.
Each PSD layer becomes an **ArtMesh**, placed on the canvas in register; the layer names
appear in the **Parts** palette (top-left).
Manual: https://docs.live2d.com/en/cubism-editor-manual/reimport-psd/ ·
Tutorial: https://docs.live2d.com/4.2/en/cubism-editor-tutorials/import/

> Import format note (already satisfied by our PSD): save format PSD, color mode RGB,
> 8 bit/channel. If a mesh imports with holes, raise the "alpha value to be considered
> transparent" slightly.

### Step 2 — Auto-mesh every part

Select all (Ctrl+A) ▸ click **Automatic Mesh generator** on the toolbar (Ctrl+Shift+A) ▸
in the dialog, accept the default preset (click the Setting text box and press Enter).
Then hand-clean only the eyes and mouth meshes if they look coarse.
Manual: https://docs.live2d.com/en/cubism-editor-manual/mesh-edit/ ·
Manual edit: https://docs.live2d.com/en/cubism-editor-manual/mesh-edit-manual/

### Step 3 — Split the eyes L/R and set clipping masks

The pilot ships both eyes as one band (`eye_sclera`/`eye_iris`/`eye_upperlid`). For the
rig, duplicate each into Left and Right ArtMeshes and trim each to one eye (the head is
tilted, so the right eye sits a little lower).

Clipping: set `eye_sclera_L/R` as the **mask**, and clip `eye_iris_L/R` to it so the
iris can move without leaving the eye white. The upper-eyelid rides above both.
Concept: https://docs.live2d.com/4.2/en/cubism-editor-manual/concept-of-artmesh/

### Step 4 — Deformer hierarchy (not auto-flat)

Build a rotation/warp deformer nest so parameters cascade naturally
(`DECISIONS.md` §6 — flat discipline):

```
root
└─ body (warp)            ← ParamBodyAngleX, ParamBreath
   └─ head (rotation)     ← ParamAngleX / Y / Z
      ├─ face (warp)      ← holds face_base
      │  ├─ eyes (warp)   ← ParamEyeLOpen/ROpen, ParamEyeBallX/Y, eye-smile
      │  └─ mouth (warp)  ← ParamMouthForm, ParamMouthOpenY
      └─ hair_side (rotation/physics input)
```
Auto-deformer helper: https://docs.live2d.com/en/cubism-editor-manual/auto-generation-of-deformer/

### Step 5 — Bind the Tier-1 parameters (verified IDs + ranges)

Add keys on these standard parameters (Standard Parameter List:
https://docs.live2d.com/en/cubism-editor-manual/standard-parameter-list/). **Values
verified against the current manual:**

| Parameter | Range (default) | Meaning | Pilot use |
|---|---|---|---|
| `ParamEyeLOpen` / `ParamEyeROpen` | 0..1 (1) | 1 = open, 0 = closed | **blink** — closed keyform uses `eye_upperlid`; runtime auto-blink drives it |
| `ParamEyeBallX` | −1..1 (0) | + = look right | **gaze** — iris moves in sclera; runtime `model.focus()` drives it |
| `ParamEyeBallY` | −1..1 (0) | + = look up | gaze |
| `ParamMouthForm` | −1..1 (0) | + = smile, − = frown | **smile** form |
| `ParamMouthOpenY` | 0..1 (0) | 0 = closed, 1 = open | mouth open amount (keep small) |
| `ParamAngleZ` | −30..30 (0) | + = tilt right | **head tilt** — the charm channel; keep gentle |
| `ParamAngleX` / `ParamAngleY` | −30..30 (0) | turn R / up | **FLAT ONLY**: planar offset + tiny rotation + hair/body lag. **No cheek/nose parallax** (`DECISIONS.md` §6) |
| `ParamBodyAngleX` | −10..10 (0) | + = lean right | subtle body lean |
| `ParamBreath` | 0..1 (0) | + = inhale | runtime auto-breath drives it |

> ⚠️ SUPERSEDED → see Full Build **W4 Step 6** + registry **INV-8**: the rig uses the standard `EyeL Smile` / `EyeR Smile`; there is no `ParamEyeForm`. The pilot text below is history (kept for the chain record), not a rig instruction.

**Eye-smile crease — important correction:** the spec §5 named `ParamEyeForm`, but **there
is no standard `ParamEyeForm`** (the standard list only has `ParamEyeBallForm`, which is
eyeball *scaling*, not an eye-smile). For the pilot either (a) **skip** the eye-smile, or
(b) add a **custom parameter** named `ParamEyeForm` (−1..1, default 0) and key the upper
lids into a soft upward crescent at +1. Flagged back to the spec; the W4 rig decides the
final id. Facial-expression system:
https://docs.live2d.com/en/cubism-editor-manual/facial-expression-system/

Blink keying walkthrough (open ▸ closed keyforms):
https://docs.live2d.com/en/cubism-editor-tutorials/eye-blink/

### Step 6 — One hair physics chain

Add a Physics setting that takes head/body angle as input and sways `hair_side` (a simple
1–2 link pendulum is enough). Start with a low output scale so it reads as a *flat 2D*
sway, not a 3D flop. Physics is under the editor manual's Physics/Scene Blend section
(editor manual top: https://docs.live2d.com/en/cubism-editor-manual/top/).

### Step 7 — Export the Cubism 4 model

> ⚠️ SUPERSEDED → see Full Build **W4 Step 10–11** + registry **INV-6/INV-7** for the settled atlas (single 2048) and moc3 export (**5.0**, never the v6 default) procedure. The pilot text below is history.

File ▸ **Export embedded file** ▸ **Export as moc3 file**. In the Export settings dialog,
include: `.moc3`, `.model3.json`, **textures** (atlas **2048** — Cubism FREE cap; the original "4096" here was wrong), and **`physics3.json`**.
Export into `live2d/pilot/model/` as `lotte-pilot.model3.json` (+ companions).
Manual: https://docs.live2d.com/en/cubism-editor-manual/export-moc3-motion3-files/

> **moc3 version — READ THIS (verified runtime constraint).** The runtime loads the
> official Cubism Core + `pixi-live2d-display@0.4.0`. A `.moc3` exported at **Cubism 5
> version cannot be read by an older Core** — it errors with
> `csmReviveMocInPlace ... The Core unsupport later than moc3 ver:[4]. This moc3 ver is [5]`.
> Tier-1 needs **no** Cubism-5-only features (blend shapes, new deformers, ArtMesh draw
> order/opacity/color), so in the export settings set the **.moc3 file version to the most
> backward-compatible option** (target SDK 4.2 / moc3 v4 if offered). If the dialog says a
> higher version is required, you used a 5.x-only feature — remove it for the pilot.
> Compatibility ref: https://docs.live2d.com/en/cubism-sdk-manual/compatibility-with-cubism-5/
>
> **Fallback (recorded for Task 6, verify-and-decide):** if the model still will not load
> in the runtime, either (a) re-export at a lower moc3 version, or (b) swap the runtime to
> the `pixi-live2d-display-lipsyncpatch` fork, which explicitly supports Cubism 5 models.

### Step 8 — Sanity-check the export (agent will run)

The agent runs a checker that the `.model3.json` references an existing `.moc3`,
`physics3.json`, and texture(s). Then Task 6 loads it in the runtime under SwiftShader and
confirms blink / gaze / smile / sway. Keep the rig rough — this proves the chain.

---

## Full Build (W4) — the real Tier-1 rig

This is the production rig. Do it in **Cubism 5.3 FREE**. It carries the pilot's learnings and
the W3 separation decisions. Keep everything **Tier-1 restrained** — start under-animated; you
can always add motion later. The param IDs/ranges are the verified table in **Pilot Step 5** above
(unchanged); the steps below are the full-build deltas, web-verified against the current manual
(May 2026).

**Inputs W3 prepared for you:**
- `live2d/lotte.psd` — **19 full-canvas aligned layers** (2508²), depth-ordered back→front. These are
  the ArtMesh / Part names you will rig:
  `body, scarf, neck, face_base, brow_L, brow_R, sclera_L, iris_L, sclera_R, iris_R, upperlid_L,
  upperlid_R, lowerlid_L, lowerlid_R, mouth_inner, mouth_outer, hair_L, hair_R, ribbon`.
- `live2d/lotte-preview.png` — flattened preview (the static "closed-eye + closed-mouth on top" look is
  EXPECTED; the rig morphs between keyforms so both states never show at once).
- (PSD/preview are gitignored — if missing, regenerate: `live2d/pilot/.venv/bin/python
  live2d/tools/full_segment.py` then `… build_psd_full.py`.)

**What changed from the pilot — read before you start:**
- **Bangs are baked into `face_base`** (W3.2 user decision). There is NO separate bangs part; the fringe
  deforms with the head/face, not as its own physics chain.
- **Hair = two front side locks**, `hair_L` / `hair_R`. Back hair is baked into `face_base`. So hair
  physics = 2 chains + the ribbon (not the 6 the early plan listed).
- **`face_base` already has cheek/jaw skin reconstructed under the side hair** (W2 cheekjaw patch), so
  when `hair_L/R` sway they reveal skin, not a hole. (No forehead reconstruction — bangs are baked in.)
- **Blink is MESH DEFORMATION, not opacity** (the pilot crude-faded opacity; the real rig deforms the
  eye closed).
- **Eye-smile uses `EyeL Smile` / `EyeR Smile`** — there is NO standard `ParamEyeForm` (the pilot Step 5
  flagged this; it is now settled).

### W4 Step 1 — Import + auto-mesh
File ▸ Open `live2d/lotte.psd`. Each layer → an ArtMesh in register; names appear in the Parts palette.
Select all (Ctrl+A) ▸ **Automatic Mesh generator** (Ctrl+Shift+A) ▸ accept the default preset. Then
hand-clean the **eye, lid, and mouth** meshes (they deform the most).
Manual: https://docs.live2d.com/en/cubism-editor-manual/reimport-psd/ ·
https://docs.live2d.com/en/cubism-editor-manual/mesh-edit/

### W4 Step 2 — Deformer hierarchy (flat discipline, `DECISIONS.md` §6)
Build this nest so parameters cascade (do NOT leave parts auto-flat). Parent each part into the right
deformer by dragging in the Parts/Deformer palette:
```
root
└─ body (warp)            ← ParamBodyAngleX, ParamBreath        [body, scarf, neck]
   └─ head (rotation)     ← ParamAngleX / Y / Z                 [face_base + everything on the face]
      ├─ face (warp)      ← holds face_base
      │  ├─ eyes (warp)   ← brow_L/R, sclera_L/R, iris_L/R, upperlid_L/R, lowerlid_L/R
      │  └─ mouth (warp)  ← mouth_inner, mouth_outer
      └─ hair (physics)   ← hair_L, hair_R, ribbon
```
Auto-deformer helper: https://docs.live2d.com/en/cubism-editor-manual/auto-generation-of-deformer/

### W4 Step 3 — Clipping masks (eyes)
Set `sclera_L` and `sclera_R` as **masks**; clip `iris_L` → `sclera_L` and `iris_R` → `sclera_R` so the
iris can gaze without leaving the white. Upper + lower lids ride ABOVE the sclera (not clipped).
Manual: https://docs.live2d.com/en/cubism-editor-manual/clipping-mask/

### W4 Step 4 — Blink via MESH DEFORMATION (verified procedure)
Replaces the pilot's opacity crossfade. For each eye (do L and R independently — the head tilt puts them
at different heights, so do NOT copy one onto the other):
1. Select `ParamEyeLOpen` (then `ParamEyeROpen`) ▸ click **[Add 2 Keyforms]** → value **1 = open**,
   **0 = closed**.
2. At **value 0 (closed)**: with the **Deform Path tool**, deform the open-eye mesh (sclera + iris) down
   into a closed slit — pull the inner/outer corners and the lid line into the closed shape — and bring
   `upperlid_L/R` DOWN over the eye (the upperlid art is the harvested *closed-eye* shape, already
   correct). Deform Path: https://docs.live2d.com/en/cubism-editor-manual/deformpath/
3. Because `iris` is clipped to `sclera` and the sclera mesh collapses, the eyeball won't poke through
   when closed (clipping does the occlusion).
4. Leave value 1 (open) as the neutral import shape.
Keyform tutorial: https://docs.live2d.com/en/cubism-editor-tutorials/eye-blink/ — runtime auto-blink
drives `ParamEyeLOpen/ROpen` 1→0→1.

### W4 Step 5 — Gaze
On `ParamEyeBallX` (−1..1, + = right) and `ParamEyeBallY` (−1..1, + = up): add keys that **translate
`iris_L/R`** within the sclera clip — only a few px at the extremes (small, Tier-1). Runtime
`model.focus(x,y)` drives these from the cursor.

### W4 Step 6 — Eye-smile (lower lids)
Add `EyeL Smile` / `EyeR Smile` (0..1). At 1, raise `lowerlid_L/R` into a soft upward crescent (the
harvested eyes-smile lid art) — the "soft creased smile" eyes. **There is no `ParamEyeForm`.**

### W4 Step 7 — Mouth (open↔closed + form)
- `ParamMouthOpenY` (0..1): 0 shows `mouth_outer` (closed-lip art); opening reveals `mouth_inner`
  (cavity). Keep the open amount small.
- `ParamMouthForm` (−1..1, + = smile): gently curve the lip line up at +1; the closed-smile keyform uses
  the `mouth_outer` closed art.

### W4 Step 8 — Head + body (FLAT only)
- `ParamAngleZ` (−30..30, + = tilt right): the charm channel — keep gentle; deforms the head deformer.
- `ParamAngleX / ParamAngleY` (−30..30): **FLAT ONLY** — planar offset + a tiny rotation + hair/body lag.
  **Do NOT build cheek/nose/mouth parallax** (the easiest way to accidentally get the 3D look —
  `DECISIONS.md` §6).
- `ParamBodyAngleX` (−10..10): subtle body lean (the body warp). `ParamBreath` (0..1): gentle rise;
  runtime auto-breath drives it.

### W4 Step 9 — Physics (hair + ribbon sway)
Add Physics settings with pendulum chains driven by head/body angle:
- `hair_L`, `hair_R` — 1–2 link pendulums each, **low output scale** so it reads as flat 2D sway (not a
  3D flop).
- `ribbon` — a short, light pendulum.
Bangs/back hair are in `face_base` and move with the head deformer (no separate chain).
Editor manual top: https://docs.live2d.com/en/cubism-editor-manual/top/

### W4 Step 10 — Texture atlas (FREE = ONE 2048 atlas)
**[Edit Texture Atlas]** ▸ New, size **2048×2048** ▸ **Auto Layout** ▸ enable **"Set magnification
automatically"** (1–100%) so all 19 parts scale down to fit ONE atlas.
> **Verified (May 2026):** Cubism **FREE allows only a single texture atlas** (max 2048×2048) and ≤100
> pieces (we have 19). **Multiple atlases are PRO-only** — so everything MUST fit this one atlas; the
> auto-magnification is how it fits (≈0.5× effective). The hi-res `assets/lotte_base.png` master is
> untouched. Manual: https://docs.live2d.com/en/cubism-editor-manual/texture-atlas-edit/

### W4 Step 11 — Export (moc3 ≤ v5 — CRITICAL)
File ▸ **Export embedded file** ▸ moc3. Include `.moc3`, `.model3.json`, **textures**, `physics3.json`,
`.cdi3.json`. **Set `.moc3 file version` to 5.0 (or 4.2) — NOT the v6 default**, or the runtime Core
rejects it (pilot-confirmed: the pinned Core reports `csmGetLatestMocVersion()=5`). Export to
`live2d/model/` as `lotte.model3.json` (+ companions); save the project as `live2d/lotte.cmo3`. Then the
agent runs `check_model.py` (W4.3) to assert the version + populate the EyeBlink group.
Compatibility ref: https://docs.live2d.com/en/cubism-sdk-manual/compatibility-with-cubism-5/

### Tier-1 restraint cheat-sheet (start here; loosen only if it feels dead)
- Gaze: a few px of iris travel. Tilt (`ParamAngleZ`): ±10–15° in normal idle, not the full ±30.
  Breath/lean: subtle. Smile: occasional, gentle. Hair: low physics scale.
- Most of the life is FREE from runtime auto-blink + auto-breath + physics. The cursor only drives a
  small damped gaze + slight head, plus the occasional eye-contact smile (the W5.1 state machine).
- If a part is too rough to rig cleanly, **merging it is an allowed outcome** (`DECISIONS.md` §6, spec
  §4) — and the W3↔W4 loop lets you re-cut: edit `live2d/tools/full_segment.py` (`BOXES` / `col_layer`)
  and re-run `full_segment.py` + `build_psd_full.py`.
