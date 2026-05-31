# Lotte Cubism Tier-1 Rig Guide

Written as we learn (building while learning). Tier-1 scope only: blink, breath, gaze
(EyeBall X/Y), head tilt (AngleZ), tiny flat head turn, hair/ribbon physics, occasional
eye-contact smile (MouthForm + a custom eye-smile param). Flat-rig discipline: no
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

File ▸ **Export embedded file** ▸ **Export as moc3 file**. In the Export settings dialog,
include: `.moc3`, `.model3.json`, **textures** (atlas 4096), and **`physics3.json`**.
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

## Full build (W4) — extends this guide after the pilot gate

The full Tier-1 rig (≈20 parts, full deformer hierarchy, restrained value ranges, the
eye-contact-smile state machine, complete physics) is detailed in the W4 plan and written
into this guide after the Task 7 gate, carrying the pilot's learnings.
