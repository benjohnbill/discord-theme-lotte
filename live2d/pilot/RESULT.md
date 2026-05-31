# Lotte Live2D — Phase 1.0 Pilot RESULT

Per-gate outcome + evidence. Authority for status is `live2d/PIPELINE.md`; this file
holds the verdict detail and screenshots.

## Task 1 — Cubism 4 runtime pre-flight: **PASS**

Official Cubism 4 core (`live2dcubismcore.min.js`) + PIXI 6.5.10 +
`pixi-live2d-display@0.4.0/dist/cubism4.min.js` loaded a Cubism 4 `.model3.json`
(Haru sample) and rendered under throwaway SwiftShader Chrome. Status line read
`Cubism 4 model rendered … 6.5.10` (not `ERROR:`). Screenshot:
`live2d/pilot/1-runtime-check.png`. All four CDN deps returned 200. The Phase-0
Cubism 2 → Phase-1 Cubism 4 core swap is de-risked before any art work.

## Task 3 — hidden-pixel harvest (eyes-closed reference): **USABLE, drift noted**

GPT-image-2 edit of the 803×690 face crop. Canonical `gen/eyes-closed.png` is the
crop-aligned 803×690 copy; raw 1353×1163 archived. Ghost-overlay + amplified-diff vs
the crop: hair / ribbon / face outline **pixel-aligned** (no doubling); closed eyes
land on the open-eye position → eyelid band harvest aligns. **Drift:** GPT widened the
mouth into a fuller smile despite the "change ONLY the eyes" instruction. Harmless for
the pilot (only the eye band is harvested) but confirms the spec §7 W2 discipline:
production edits need landmark-align + tight conservative masks, not full-region paste.

## Task 4 — scripted 6-part separation

**Tool that ran:** `rembg` 2.0.75 + `onnxruntime` 1.26.0 (U2Net), installed into the
pilot venv on Python 3.14 — **available, no fallback needed**. Crop source alpha was
fully opaque (255,255), so matting was genuinely required. Sub-parts are cut as
fraction boxes of the crop, calibrated from a 10%-grid read of this specific crop
(its head-tilt puts features off the nominal centers).

| Part | Size | Alpha | Quality | Notes |
|---|---|---|---|---|
| `face_base` | 803×690 | (0,255) | **clean matte** | rembg cut the character off the halo background; real per-pixel alpha |
| `eye_sclera` | 410×145 | opaque | good | both-eyes band; split L/R in Cubism |
| `eye_iris` | 362×110 | opaque | good | violet irises isolated → gaze |
| `eye_upperlid` | 410×145 | opaque | good | from the eyes-closed ref, same band → blink art, aligned |
| `hair_side` | 200×538 | opaque | good | clean left side-hair lock → sway |
| `mouth` | 177×90 | opaque | **marginal** | smile is right-of-center near the crop's bottom edge and slightly **clipped** by it |

**Honest verdict (the load-bearing W3 question — "does AI-assisted layering yield a
riggable asset?"): YES.**
- rembg delivers a **clean character silhouette/alpha** with no manual painting — the
  single most important pilot signal. W3's load-bearing risk is materially reduced.
- Fraction-box sub-parts are **opaque rectangles**, not per-part mattes — expected for
  the box method; Cubism masks/clips them at rig time, which is fine for a Tier-1 rig.
- The **eyes-closed harvest aligns** to the eye band → the blink-art path works.

**Findings that feed W1/W2 (the minor "adjust" signals):**
1. **Crop set too high.** The mouth/chin sits at the crop's bottom edge and is partly
   clipped. The full-bust W1 crop must extend lower so the mouth/chin is fully inside.
   (Not fixed in the pilot: re-cropping would cascade to regenerating the user's
   eyes-closed asset; the clipped mouth is still riggable as a crude `ParamMouthForm`.)
2. **Mouth wants a dedicated source.** A small feature near an edge is the weakest box
   cut — this is exactly what the W2 "closed-mouth" hidden-state reference is for.
3. **Head-tilt offsets features** from nominal centers; production separation should
   key boxes off detected landmarks, not fixed fractions.

Nothing here is a NO-GO. The chain so far is GO-leaning with a minor crop adjust for W1.

### Task 5 prep — layered source for Cubism

- **Layers re-emitted as full-canvas aligned PNGs** (803×690, part-in-place, transparent
  elsewhere) so they stack in register on import — the proper Live2D layer format. The
  per-part sizes in the table above are the *content boxes*; the files are full-canvas.
- **Eye band extended** (bottom 0.74 → 0.80) so the closed-eye art covers *both* tilted
  eyes (the right eye sits lower); verified by overlaying `eye_upperlid` on `face_base`.
- **Layered PSD built** (`build_psd.py`, psd-tools): `live2d/pilot/lotte-pilot.psd` — 6
  layers, RGB/8-bit, depth-ordered face_base→…→mouth. Reopen + flatten verified
  (`lotte-pilot-preview.png`). pytoshop was tried first but its RLE/packbits extension is
  unbuilt on this Python (raw-mode merged image came out black) — psd-tools is the writer.
- **Spec correction flagged:** spec §5 / `DECISIONS` reference `ParamEyeForm` for the
  eye-smile, but **there is no standard `ParamEyeForm`** (the standard list has
  `ParamEyeBallForm` = eyeball scaling). The pilot rig guide treats the eye-smile as a
  custom parameter or skips it; the W4 plan should reconcile the parameter id in spec §5.
- **moc3 compatibility recorded** as the Task 6 verify-and-decide risk: a Cubism-5-version
  `.moc3` cannot load on an older Core (`csmReviveMocInPlace` error). Export the most
  backward-compatible moc3 version; fallback = re-export lower or use the
  `pixi-live2d-display-lipsyncpatch` fork. (See `RIG_GUIDE.md` Step 7.)

## Task 5 (user) — Cubism rig: DONE

User rigged the slice in Cubism 5.3.02 FREE (guided, screenshot loop). Built: auto-mesh
all 6 parts → one `head` rotation deformer parenting all parts → **head tilt** keyed on
`ParamAngleZ` (±8° at ±30) → **blink** via `eye_upperlid` opacity keyed on `ParamEyeLOpen`
(0% open / 100% closed) → texture atlas (2048) → moc3 export. Source project committed as
`live2d/pilot/lotte-pilot.cmo3`. Gaze / mouth-smile / hair-physics were intentionally
deferred to W4 (the chain was proven without them; see gate).

**FREE-tier finding (feeds BASE.md):** Cubism FREE caps the texture atlas at **2048×2048**,
not the 4096 that BASE.md assumed. 2048 is ample for the 6-part slice. The full ~20-part
build must plan for this: multiple atlases, a lower upscale, or Cubism PRO.

## Task 6 — runtime verify: **PASS**

Loaded the exported model in the proven plumbing (PIXI 6.5.10 + `pixi-live2d-display@0.4.0`
cubism4 build + official web Core) under SwiftShader.

**The moc3 version risk REPRODUCED and resolved (the pilot's headline finding):**
- Cubism Editor **5.3.02 exports moc3 version 6 by default**.
- The pinned runtime Core (`cubism.live2d.com/sdk-web/cubismcore/live2dcubismcore.min.js`)
  reports `csmGetLatestMocVersion() = 5`. So **v6 failed to load** (`ERROR: Unknown error`,
  blank canvas — see `6-model-check.png` first run).
- **Fix:** re-export with the `.moc3 file version` set to **5.0** (≤ Core max). The v5 moc3
  **loads and renders** — `MODEL LOADED ok`, full character, correct textures.
- Evidence: `live2d/pilot/6-model-check.png` (open-eye render + "MODEL LOADED ok"),
  `live2d/pilot/6-model-check-blink.png` (forced eyes-closed + tilt).

**Behaviors confirmed in-runtime:**
- **Render**: full character, correct atlas, no errors.
- **Head tilt**: `model.focus()` drives `ParamAngleZ` → head visibly tilts (the focus
  controller maps cursor → head angles).
- **Blink art**: forcing `ParamEyeLOpen = 0` shows the **harvested eyes-closed lid art** in
  the runtime → the GPT-image-2 → separation → rig → runtime **blink chain works**.

**Two model3.json hand-fixes were needed after export (record for W4 export hygiene):**
1. `Groups.EyeBlink.Ids` exported **empty** → runtime auto-blink had no target. Populated
   with `["ParamEyeLOpen","ParamEyeROpen"]`. (W4: set the eye-blink group inside Cubism.)
2. Texture path: model3.json referenced `lotte-pilot.2048/texture_00.png` but the file
   shipped as `texture_00.png`. Repointed. (W4: keep the export folder structure intact.)

**Roughness (expected, → W4):** only one eye fully closes (both-eyes band + tilt + lid
bound to a single param → reads as a wink); opacity-fade blink, not mesh-deformation;
eyebrows baked into `face_base`.

## Task 7 — Pilot gate decision: **GO**

The entire hardest Phase-1 chain runs end to end at acceptable pilot quality:

1. **Cubism 4 runtime core swap** (Task 1) — PASS.
2. **Hidden-pixel harvest** (eyes-closed, Task 3) — usable; mouth-drift recorded.
3. **Scripted separation** (Task 4) — rembg matte clean (the load-bearing W3 question = YES);
   sub-parts riggable; mouth marginal.
4. **Riggable in Cubism + exports** (Task 5) — YES; a first-timer built mesh + deformer +
   2 parameter binds + atlas + moc3 export via the guide.
5. **Renders + behaves in runtime** (Task 6) — PASS; loads, tilts, shows the harvested
   blink art.

**Decision: GO** — proceed to detail the full W1–W5 plan, carrying these pilot learnings:
- **moc3 export must target ≤ v5** for the pinned runtime (Cubism 5.3 default v6 is too new),
  or bump the runtime Core / use the lipsyncpatch fork. **Confirmed, not theoretical.**
- **Atlas:** Cubism FREE = 2048 cap → plan multi-atlas / lower upscale / PRO for ~20 parts
  (update BASE.md's 4096 assumption).
- **Segmentation:** rembg works in-env for the silhouette; sub-parts need landmark-keyed
  boxes (not fixed fractions) and L/R eye splits; mouth needs a lower crop + the W2
  closed-mouth reference.
- **Rig:** W4 = mesh-deformation blink (not opacity), split L/R eyes, separate eyebrows/lids,
  gaze (`ParamEyeBallX/Y`), restrained smile (`ParamMouthForm` + standard `EyeL/R Smile`),
  hair physics, ~20 parts. `ParamEyeForm` is non-standard — use the template's `EyeL/R Smile`.
- **Export hygiene:** set the EyeBlink group in Cubism; keep the texture-folder path intact.
