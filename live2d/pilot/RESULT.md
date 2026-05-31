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
