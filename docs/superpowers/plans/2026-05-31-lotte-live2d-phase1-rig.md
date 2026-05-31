# Lotte Live2D — Phase 1.0 Vertical-Slice Pilot Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
>
> **Plan type note:** This is a **pilot / feasibility gate**, not a pure-TDD code feature. It mixes (a) agent-written scripts (testable where there is real logic), (b) user actions in external tools (ChatGPT/GPT-image-2, Cubism Editor — verified by handoff artifact), and (c) browser render checks (verified by run/observe/screenshot, not unit tests, because the project's headless `bh-chrome` has no WebGL — use a throwaway SwiftShader Chrome, per memory `bh-chrome-no-webgl`). Honor the bite-sized, concrete, no-placeholder spirit throughout.

**Goal:** Prove the entire hardest Phase 1 chain end-to-end on a 6-part face slice (Cubism 4 runtime → AI hidden-pixel harvest → scripted part separation → Cubism rig → runtime behavior) cheaply, before committing days to the full W1–W5 build.

**Architecture:** Front-load the cheapest, highest-information checks. First prove the Cubism 4 runtime loads in the proven plumbing (de-risks the core swap with zero art work). Then take a temporary face crop of the locked source, harvest one hidden-state reference via GPT-image-2, separate ~6 parts with agent scripts, hand the user a guided Cubism rig of just those parts, export, and load the crude model back in the runtime. End with an explicit go / adjust gate that decides whether (and how) to detail the full W1–W5 plan.

**Tech Stack:** PIXI.js v6, pixi-live2d-display@0.4.0 (Cubism 4 build), official Live2D Cubism 4 Core, Cubism 5 FREE editor, Python (Pillow + a segmentation tool: rembg / OpenCV), throwaway SwiftShader Chrome for headless WebGL.

**Source spec:** `docs/superpowers/specs/2026-05-31-lotte-live2d-phase1-rig-design.md` (§6 Phase 1.0; §2 locked decisions; §7 workstreams; §12 execution-time checks).

---

## Scope of THIS plan

**Phase 1.0 pilot only.** The full build (W1 base lock, W2 source pack, W3 separation, W4 rig, W5 integrate) is captured as a **roadmap** at the end. Its bite-sized detail genuinely depends on pilot findings (which segmentation tool actually delivers clean alpha here; whether ×2 upscale packs a 4096 atlas; the real Cubism workflow the user learns in the pilot). Detailing it now would force placeholders. Expand W1–W5 into its own plan after the pilot gate (Task 7) passes.

All pilot artifacts live in `live2d/pilot/` and `live2d/` docs — outside the theme build pipeline (not in `src/`, not in `theme.manifest.yaml`). Work stays on the `live2d-spike` branch. `master` is never touched.

---

## File Structure

| File | Responsibility |
|---|---|
| `live2d/PIPELINE.md` | Master tracker (authority): workstream/pilot status, interfaces, current-state / next-action. Read first every session. |
| `live2d/DECISIONS.md` | The locked decisions (spec §2), to prevent re-litigation. |
| `live2d/RIG_GUIDE.md` | Cubism Tier-1 walkthrough; the pilot writes its first section against current Cubism 5 docs. |
| `live2d/pilot/runtime-check.html` | Standalone page: PIXI + pixi-live2d-display Cubism 4 build + official Cubism 4 core, loads a free Cubism 4 sample, tracks the cursor. Proves the runtime core swap. |
| `live2d/pilot/crop_face.py` | Crop a face/bust slice from `live2d/source/lotte-discord-original.png`. |
| `live2d/pilot/segment.py` | Separate the slice into ~6 alpha parts (tool-availability check + segmentation + alpha-union sanity check). |
| `live2d/pilot/layers/` | Output per-part PNGs (face base, eye sclera+iris, upper eyelid, mouth, hair piece). |
| `live2d/pilot/gen/` | The one GPT-image-2 hidden-state reference (eyes-closed) the user provides. |
| `live2d/pilot/model/` | Cubism 4 export of the rigged slice. |
| `live2d/pilot/RESULT.md` | Pilot outcome: PASS/FAIL per gate + screenshots + the go/adjust decision. |

---

## Task 0: Scaffold the pipeline docs

**Files:**
- Create: `live2d/PIPELINE.md`
- Create: `live2d/DECISIONS.md`
- Create: `live2d/RIG_GUIDE.md`

- [ ] **Step 1: Create `live2d/DECISIONS.md` (extract spec §2)**

```markdown
# Lotte Live2D — Locked Decisions

Source: docs/superpowers/specs/2026-05-31-lotte-live2d-phase1-rig-design.md §2. Do not re-litigate without new information.

1. Technique = Live2D mesh deformation (not frame/sprite).
2. Scope = Discord bust only; mobile stays static.
3. Base locked, not regenerated. Character source likely `original` (more facial px); background from `version` (its outpaint, pixel-aligned). Confirm in W1. See live2d/BASE.md.
4. Cubism 5 FREE (.moc3); runtime swaps the Cubism 2 core for the official Cubism 4 core. Verified in Phase 1.0 Task 1.
5. Background is OUT of the model (character-only, transparent). Particle drift deferred.
6. Flat-rig discipline: reactivity on flat channels (gaze, blink, breath, tilt, physics, smile); head turn (AngleX/Y) tiny + planar + lag only, NO pseudo-3D parallax.
7. Tier-1 restraint: most life from auto-blink/breath + physics; cursor reaction small + damped; occasional eye-contact smile; start under-animated.
8. Source-of-truth durability: locked base raster committed/checksummed (see live2d/source/SHA256SUMS).
```

- [ ] **Step 2: Create `live2d/PIPELINE.md` (tracker)**

```markdown
# Lotte Live2D — Pipeline Tracker (authority)

Read this FIRST every session. Pipeline state lives here, not in handoffs or memory.

## Current state / next action
- Phase 1.0 pilot: NOT STARTED. Next: Task 1 (Cubism 4 runtime pre-flight).

## Phase 1.0 — Vertical-Slice Pilot
| Task | Status | Artifact |
|---|---|---|
| 0 Scaffold docs | | PIPELINE.md, DECISIONS.md, RIG_GUIDE.md |
| 1 Cubism 4 runtime pre-flight | | live2d/pilot/runtime-check.html + screenshot |
| 2 Face crop | | live2d/pilot/face-crop.png |
| 3 GPT eyes-closed ref | | live2d/pilot/gen/eyes-closed.png |
| 4 Scripted 6-part separation | | live2d/pilot/layers/*.png |
| 5 Cubism rig (user) | | live2d/pilot/model/*.model3.json |
| 6 Runtime verify | | live2d/pilot/RESULT.md + screenshot |
| 7 Gate decision | | RESULT.md decision |

## Full build (W1–W5) — roadmap, detailed AFTER the pilot gate
See the plan's roadmap section.
```

- [ ] **Step 3: Create `live2d/RIG_GUIDE.md` (stub)**

```markdown
# Lotte Cubism Tier-1 Rig Guide

Written as we learn (building while learning). The pilot fills the first section
(Task 5) against current Cubism 5 FREE documentation. Tier-1 scope only:
blink, breath, gaze (EyeBallX/Y), tilt (AngleZ), tiny flat head turn, hair/ribbon
physics, occasional eye-contact smile (MouthForm + EyeForm). Flat-rig discipline:
no pseudo-3D parallax (DECISIONS.md §6).
```

- [ ] **Step 4: Commit**

```bash
git add live2d/PIPELINE.md live2d/DECISIONS.md live2d/RIG_GUIDE.md
git commit -m "docs(live2d): scaffold pipeline tracker, decisions, rig guide"
```

---

## Task 1: Cubism 4 runtime pre-flight (de-risk the core swap, spec §6 step 0 / §12.1)

**Goal:** Prove the official Cubism 4 core + the pixi-live2d-display Cubism 4 build render a Cubism 4 `.model3.json` and track the cursor in the proven plumbing — before any Lotte art exists. This is the cheapest, highest-value de-risk Codex flagged.

**Files:**
- Create: `live2d/pilot/runtime-check.html`

- [ ] **Step 1: Write the Cubism 4 runtime check page**

Create `live2d/pilot/runtime-check.html`:
```html
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <style>
    html, body { margin: 0; height: 100%; background: #1e1f3a; overflow: hidden; }
    #c { display: block; width: 100vw; height: 100vh; }
    #status { position: fixed; top: 8px; left: 8px; color: #fff; font: 14px monospace; }
  </style>
</head>
<body>
  <div id="status">loading…</div>
  <canvas id="c"></canvas>
  <!-- Official Live2D Cubism 4 Core (replaces the Phase 0 Cubism 2 core). -->
  <script src="https://cubism.live2d.com/sdk-web/cubismcore/live2dcubismcore.min.js"></script>
  <!-- PIXI v6 (unchanged from Phase 0). -->
  <script src="https://cdn.jsdelivr.net/npm/pixi.js@6.5.10/dist/browser/pixi.min.js"></script>
  <!-- pixi-live2d-display Cubism 4 build (NOT cubism2.min.js). -->
  <script src="https://cdn.jsdelivr.net/npm/pixi-live2d-display@0.4.0/dist/cubism4.min.js"></script>
  <script>
    (async () => {
      const status = document.getElementById('status');
      try {
        const app = new PIXI.Application({
          view: document.getElementById('c'), resizeTo: window,
          backgroundAlpha: 0, autoStart: true,
        });
        // Free Cubism 4 sample model from the pixi-live2d-display test assets.
        const model = await PIXI.live2d.Live2DModel.from(
          'https://cdn.jsdelivr.net/gh/guansss/pixi-live2d-display/test/assets/haru/haru_greeter_t03.model3.json'
        );
        app.stage.addChild(model);
        const fit = () => {
          const s = Math.min(window.innerWidth / model.width, window.innerHeight / model.height) * 0.9;
          model.scale.set(s); model.anchor.set(0.5, 0.5);
          model.position.set(window.innerWidth / 2, window.innerHeight / 2);
        };
        fit(); window.addEventListener('resize', fit);
        window.addEventListener('mousemove', e => model.focus(e.clientX, e.clientY));
        status.textContent = 'Cubism 4 model rendered — move mouse, gaze should track. ' + PIXI.VERSION;
      } catch (e) {
        status.textContent = 'ERROR: ' + (e && e.message ? e.message : e);
        console.error(e);
      }
    })();
  </script>
</body>
</html>
```

- [ ] **Step 2: Serve it locally**

Run:
```bash
cd live2d/pilot && python3 -m http.server 8124
```
Expected: server on `http://localhost:8124`.

- [ ] **Step 3: Render it in a WebGL-capable headless Chrome and screenshot**

The project's `bh-chrome` has no WebGL (memory `bh-chrome-no-webgl`). Launch a throwaway SwiftShader Chrome (same approach the Phase 0 spike used) pointed at the page, and capture `live2d/pilot/1-runtime-check.png`:
```bash
google-chrome --headless=new --enable-unsafe-swiftshader --use-gl=angle --use-angle=swiftshader \
  --window-size=1280,800 --screenshot=$PWD/live2d/pilot/1-runtime-check.png \
  --virtual-time-budget=8000 http://localhost:8124/runtime-check.html
```
(If `google-chrome` is not the binary name, use the one the Phase 0 spike used.)

- [ ] **Step 4: Verify and record (GATE)**

Open `live2d/pilot/1-runtime-check.png`. Expected: the Haru sample renders (status line reads "Cubism 4 model rendered…", NOT "ERROR:"). 

- **PASS** → the Cubism 4 runtime path works; proceed.
- **FAIL** (model3.json 404 / core not found / empty `PIXI.live2d`) → record the exact error in `RESULT.md`. Common fixes (verify-and-record, mirroring Phase 0): pin a different `pixi-live2d-display` version that ships a Cubism 4 build; use a different free Cubism 4 sample `.model3.json` if the Haru path moved; confirm `live2dcubismcore.min.js` loaded (`window.Live2DCubismCore` defined). **Do not start any rigging until this is PASS** — the whole rig targets this runtime.

Update `PIPELINE.md` Task 1 row with PASS/FAIL.

- [ ] **Step 5: Stop the server and commit**

```bash
git add live2d/pilot/runtime-check.html live2d/pilot/1-runtime-check.png live2d/PIPELINE.md
git commit -m "pilot(live2d): Cubism 4 runtime pre-flight in proven plumbing"
```

---

## Task 2: Prepare the pilot face crop

**Goal:** A small working slice of the real character to rig — not the full bust.

**Files:**
- Create: `live2d/pilot/crop_face.py`
- Output: `live2d/pilot/face-crop.png`

- [ ] **Step 1: Write the crop script**

Create `live2d/pilot/crop_face.py`:
```python
from PIL import Image
import pathlib

SRC = "live2d/source/lotte-discord-original.png"  # the parent; most facial pixels
OUT = "live2d/pilot/face-crop.png"

img = Image.open(SRC).convert("RGBA")
W, H = img.size  # 1254 x 1254
# Generous head+upper-face box (fractions of the square). Adjust after inspecting.
box = (int(W * 0.18), int(H * 0.05), int(W * 0.82), int(H * 0.60))
crop = img.crop(box)
pathlib.Path("live2d/pilot").mkdir(parents=True, exist_ok=True)
crop.save(OUT)
print("crop box", box, "-> size", crop.size)
```

- [ ] **Step 2: Run and inspect**

Run: `python3 live2d/pilot/crop_face.py`
Expected: prints the box and a crop size near `(800, 690)`. Open `live2d/pilot/face-crop.png` and confirm it contains the full face (eyes, mouth, some bangs, one side-hair lock). If the crop cuts the face, adjust the `box` fractions and re-run.

- [ ] **Step 3: Commit**

```bash
git add live2d/pilot/crop_face.py live2d/pilot/face-crop.png
git commit -m "pilot(live2d): face crop from locked source (original)"
```

---

## Task 3: Harvest one hidden-state reference (USER — GPT-image-2)

**Goal:** Test the hidden-pixel harvest path with a single edit: an eyes-closed version, used later to build the upper-eyelid blink art.

**Files:**
- Output (user provides): `live2d/pilot/gen/eyes-closed.png`

- [ ] **Step 1: Generate the eyes-closed reference**

User action in ChatGPT (GPT-image-2). Attach `live2d/pilot/face-crop.png` and use the style-vocabulary prefix from `live2d/gen/PROMPTS.md` §2, e.g.:
```
Reference image attached. Keep the character EXACTLY the same — same face, hair,
ribbon, lighting, line weight, colors, framing, and pixel alignment — change ONLY
the eyes: draw them gently closed in a soft, natural relaxed-eyelid shape. Do not
move or restyle anything else. Output the same size, character pixel-aligned to the
reference.
```
Save the result as `live2d/pilot/gen/eyes-closed.png`.

- [ ] **Step 2: Verify presence and rough alignment**

Run:
```bash
python3 - <<'PY'
from PIL import Image
a = Image.open("live2d/pilot/face-crop.png")
b = Image.open("live2d/pilot/gen/eyes-closed.png")
print("base", a.size, "eyes-closed", b.size, "match" if a.size == b.size else "RESIZE NEEDED")
PY
```
Expected: same dimensions (or note that it must be resized/aligned to the crop in Task 4). If badly drifted (face moved, recolored), regenerate — only the eyes should differ. This is the W2 drift-reject discipline in miniature (spec §7).

- [ ] **Step 3: Commit**

```bash
git add live2d/pilot/gen/eyes-closed.png
git commit -m "pilot(live2d): eyes-closed hidden-state reference (GPT-image-2)"
```

---

## Task 4: Scripted 6-part separation (the load-bearing test, spec §7 W3 / §12.3)

**Goal:** Separate the slice into ~6 alpha parts with agent scripts, respecting the no-hand-paint constraint. This is the riskiest link; the pilot exists mainly to test it. The code below is a concrete **starting point** — Step 2 is an explicit inspect-and-iterate loop, because production-clean anime part alpha is exactly what we are here to measure.

**Files:**
- Create: `live2d/pilot/segment.py`
- Output: `live2d/pilot/layers/{face_base,eye_sclera,eye_iris,eye_upperlid,mouth,hair_side}.png`

- [ ] **Step 1: Write the segmentation scaffold (with tool-availability check first)**

Create `live2d/pilot/segment.py`:
```python
"""Pilot part separation. Tool-availability check first (spec rule: verify before relying).
Strategy: rembg for the character silhouette/alpha; box+matte crops for sub-parts at
approximate coordinates of the crop; eyelid art harvested from the eyes-closed ref.
All boxes are FRACTIONS of the crop so they are easy to tweak by inspection."""
import sys, pathlib
from PIL import Image

CROP = "live2d/pilot/face-crop.png"
CLOSED = "live2d/pilot/gen/eyes-closed.png"
OUT = pathlib.Path("live2d/pilot/layers"); OUT.mkdir(parents=True, exist_ok=True)

# --- tool availability ---
try:
    from rembg import remove          # U2Net matting; pip install rembg
    HAVE_REMBG = True
except Exception as e:
    HAVE_REMBG = False
    print("rembg NOT available:", e, "-> falling back to full-frame alpha", file=sys.stderr)

img = Image.open(CROP).convert("RGBA")
W, H = img.size

def box(l, t, r, b):
    return (int(W*l), int(H*t), int(W*r), int(H*b))

def cut(name, frac_box, source=img):
    part = source.crop(frac_box)
    part.save(OUT / f"{name}.png")
    print("wrote", name, part.size)

# Whole-character matte (silhouette alpha) as the face_base source.
if HAVE_REMBG:
    matted = remove(img)              # RGBA with background removed
else:
    matted = img
matted.save(OUT / "face_base.png")

# Approximate sub-part boxes (fractions of the crop) — TWEAK after inspecting.
cut("eye_sclera",   box(0.30, 0.34, 0.70, 0.50))   # both-eyes band (split L/R later)
cut("eye_iris",     box(0.34, 0.36, 0.66, 0.49))
cut("mouth",        box(0.40, 0.58, 0.60, 0.72))
cut("hair_side",    box(0.04, 0.10, 0.30, 0.95))
# upper eyelid art comes from the eyes-closed reference, same band as the eyes:
closed = Image.open(CLOSED).convert("RGBA").resize((W, H))
cut("eye_upperlid", box(0.30, 0.34, 0.70, 0.50), source=closed)
print("done")
```

- [ ] **Step 2: Run, inspect, iterate**

Run: `python3 live2d/pilot/segment.py`
Expected: six PNGs in `live2d/pilot/layers/`. Open them. The goal of the pilot is to judge **separation quality**, so record honestly in `RESULT.md`:
- Does `face_base.png` have a clean character alpha (rembg) or a hard rectangle (fallback)?
- Do the eye / mouth / hair crops isolate the right region? Adjust the fraction boxes and re-run until each part roughly contains its feature.
- If rembg is missing, try `pip install rembg onnxruntime` once; if it still cannot run in this env, record that and proceed with rectangular parts for the pilot (the pilot only needs *riggable* parts, not production-clean alpha — production fallback ladder is spec §7 W3).

- [ ] **Step 3: Alpha-union sanity check**

Run:
```bash
python3 - <<'PY'
from PIL import Image, ImageChops
import glob
base = Image.open("live2d/pilot/face-crop.png").convert("RGBA")
acc = Image.new("L", base.size, 0)
for p in glob.glob("live2d/pilot/layers/*.png"):
    a = Image.open(p).convert("RGBA")
    # paste each part's alpha into a full-frame accumulator is non-trivial for crops;
    # here we just confirm every part file is non-empty and has alpha variation.
    ex = a.getextrema()
    print(p, "alpha range", ex[3])
PY
```
Expected: every part reports a non-degenerate alpha/content range (not fully transparent, not a flat block). Anything fully empty means that box missed its feature — fix and re-run.

- [ ] **Step 4: Record the verdict and commit**

Append a "Task 4 — separation" section to `live2d/pilot/RESULT.md`: which tool ran (rembg vs fallback), per-part quality (clean / rectangular / poor), and whether this is good enough to rig. Update `PIPELINE.md`.
```bash
git add live2d/pilot/segment.py live2d/pilot/layers live2d/pilot/RESULT.md live2d/PIPELINE.md
git commit -m "pilot(live2d): scripted 6-part separation + quality record"
```

---

## Task 5: Rig the 6-part slice in Cubism (USER, guided)

**Goal:** A crude but real Cubism 4 model of the slice: blink, gaze, a tiny smile, one hair sway. The rig guide is authored at execution time against **current** Cubism 5 documentation (not pre-guessed), then the user follows it.

**Files:**
- Modify: `live2d/RIG_GUIDE.md` (add the pilot walkthrough)
- Output (user provides): `live2d/pilot/model/lotte-pilot.model3.json` (+ `.moc3`, textures, `physics3.json`)

- [ ] **Step 1: Author the pilot rig walkthrough**

Agent: web-search the current **Cubism 5 FREE** Tier-1 workflow and official tutorials (mesh / deformer / parameter / physics / export to `.moc3` + `.model3.json`). Write a concrete, verified step list into `live2d/RIG_GUIDE.md` covering exactly the pilot scope:
- import the `live2d/pilot/layers/` parts as a layered source,
- auto-mesh each part + clean up eyes/mouth,
- bind `ParamEyeLOpen/ROpen` (blink, using `eye_upperlid` from the eyes-closed art), `ParamEyeBallX/Y` (iris move), `ParamMouthForm`+`ParamMouthOpenY` (smile), `ParamEyeForm` (eye-smile), one `ParamAngleZ` tilt, and one hair physics chain on `hair_side`,
- keep `ParamAngleX/Y` flat (planar offset only — no parallax; DECISIONS.md §6),
- export Cubism 4 (`.moc3` + `.model3.json` + `physics3.json` + texture atlas, 4096).
Include the official tutorial links inline so the user can follow along.

- [ ] **Step 2: User rigs the slice**

User action in Cubism 5 FREE, following `RIG_GUIDE.md`. Export into `live2d/pilot/model/` as `lotte-pilot.model3.json` and its companion files. Keep it deliberately rough — this proves the chain, not polish.

- [ ] **Step 3: Sanity-check the export**

Run:
```bash
python3 - <<'PY'
import json, glob, os
m = glob.glob("live2d/pilot/model/*.model3.json")
print("model3:", m)
assert m, "no .model3.json exported"
d = json.load(open(m[0]))
refs = d.get("FileReferences", {})
print("moc:", refs.get("Moc"), "textures:", refs.get("Textures"), "physics:", refs.get("Physics"))
for t in refs.get("Textures", []):
    p = os.path.join(os.path.dirname(m[0]), t)
    print(t, "exists" if os.path.exists(p) else "MISSING")
PY
```
Expected: a `.model3.json` referencing an existing `.moc3` and texture(s). Missing files mean the export was incomplete — re-export.

- [ ] **Step 4: Commit**

```bash
git add live2d/RIG_GUIDE.md live2d/pilot/model live2d/PIPELINE.md
git commit -m "pilot(live2d): rig guide + crude 6-part Cubism 4 model of the slice"
```

---

## Task 6: Load the pilot model in the runtime and verify the chain

**Goal:** Confirm the rigged slice renders and behaves (blink / gaze / smile / sway) in the proven plumbing.

**Files:**
- Create: `live2d/pilot/model-check.html` (copy of `runtime-check.html` pointed at the local model)

- [ ] **Step 1: Point the runtime at the local model**

Create `live2d/pilot/model-check.html` identical to `runtime-check.html` except the model URL:
```js
const model = await PIXI.live2d.Live2DModel.from('./model/lotte-pilot.model3.json');
```

- [ ] **Step 2: Serve and screenshot under SwiftShader**

Run:
```bash
cd live2d/pilot && python3 -m http.server 8124
google-chrome --headless=new --enable-unsafe-swiftshader --use-gl=angle --use-angle=swiftshader \
  --window-size=1280,800 --screenshot=$PWD/live2d/pilot/6-model-check.png \
  --virtual-time-budget=8000 http://localhost:8124/model-check.html
```
(Run the chrome command from the repo root so `$PWD` resolves; or use an absolute output path.)

- [ ] **Step 3: Verify behaviors (run/observe)**

Open `live2d/pilot/6-model-check.png`: the Lotte slice renders (not blank, not ERROR). For motion (blink/gaze/smile/sway), the static screenshot is not enough — also open `http://localhost:8124/model-check.html` in the throwaway Chrome (or the real client) and confirm: gaze follows the cursor, auto-blink fires, the hair lock sways when the head moves. Record observations in `RESULT.md`.

- [ ] **Step 4: Commit**

```bash
git add live2d/pilot/model-check.html live2d/pilot/6-model-check.png live2d/pilot/RESULT.md
git commit -m "pilot(live2d): load rigged slice in runtime + behavior check"
```

---

## Task 7: Pilot gate decision

**Files:**
- Modify: `live2d/pilot/RESULT.md`, `live2d/PIPELINE.md`

- [ ] **Step 1: Summarize the chain**

In `RESULT.md`, answer each link: (1) Cubism 4 runtime loads? (Task 1) (2) hidden-pixel harvest usable? (Task 3) (3) scripted separation quality? (Task 4) (4) riggable in Cubism + exports? (Task 5) (5) renders + behaves in runtime? (Task 6).

- [ ] **Step 2: Decide and record**

State one:
- **GO** → the chain works at acceptable quality. Proceed to detail the full W1–W5 plan (next writing-plans pass), carrying any pilot learnings (e.g., the segmentation tool that worked, real upscale/atlas numbers, the parts that needed splitting).
- **ADJUST** → the chain works but a link is weak. Name the change (simpler rig, fewer parts, a different segmentation tool, more conservative motion) before the full build.
- **NO-GO on this approach** → a link is infeasible (e.g., no usable segmentation in this env AND clean alpha is unreachable without manual painting). Re-open the relevant locked decision with the user (it is theirs to change).

- [ ] **Step 3: Commit**

```bash
git add live2d/pilot/RESULT.md live2d/PIPELINE.md
git commit -m "pilot(live2d): Phase 1.0 gate decision"
```

---

## Roadmap — Full build W1–W5 (high-level; detailed AFTER the pilot gate)

Detail these into their own bite-sized plan once Task 7 is GO/ADJUST, informed by pilot findings. From spec §7:

- **W1 — Base lock + upscale.** Compare `version` vs `original` facial resolution; lock the character source (`original` per BASE.md) and the background source (`version` extended); waifu2x ×2 → ~2508 px; verify ~20 parts pack a 4096 atlas; write `assets/lotte_base.png` + fill `BASE.md` result fields + checksum.
- **W2 — Generative source pack.** Produce the remaining hidden-state references (forehead, cheek/jaw, smiling-eyes, closed-mouth) with the §7 drift discipline (harvest hidden pixels only, landmark-align, color-match, reject gate); store accepted patches + masks; grow `gen/PROMPTS.md`.
- **W3 — Full part separation.** ~20–23 parts with the §7 fallback ladder (agent mask candidates + previews → user coarse keep/remove → CV refine → merge/simplify if needed). Output `layers/*.png` + layered PSD.
- **W4 — Cubism rig.** Full Tier-1 rig with deformer hierarchy, restrained parameter ranges, physics; export `model/lotte.model3.json`. Extend `RIG_GUIDE.md`.
- **W5 — Integrate + verify.** Swap the model into the Phase 0 standalone page and the Discord console probe; implement the eye-contact smile state machine (spec §3.1); verify in SwiftShader then the real Discord client; checkpoint screenshots.

---

## Self-Review

- **Spec coverage (Phase 1.0):** spec §6 steps 0–5 map to Tasks 1 (step 0 runtime), 2 (temp base), 3 (one reference), 4 (minimal layers), 5 (Cubism), 6 (runtime load); the §6 gate is Task 7. Execution-time checks §12.1 (runtime core swap) = Task 1; §12.3 (segmentation availability) = Task 4 Step 1; §12.4 (smile derivation) is deferred to W2/W4 (out of pilot scope, noted in roadmap). Doc spine §8/§9 (PIPELINE, DECISIONS, RIG_GUIDE, RESULT, checkpoints) = Task 0 + per-task records. W1–W5 are intentionally roadmap-only (their detail depends on pilot findings — detailing now would force placeholders).
- **Placeholder scan:** every script and HTML page is complete and runnable. The two genuine unknowns — the segmentation quality (Task 4) and the Cubism workflow (Task 5) — are handled as explicit verify-and-iterate / author-against-live-docs steps with named fallbacks, not hand-waved TODOs.
- **Consistency:** file paths are stable across tasks (`live2d/pilot/face-crop.png`, `live2d/pilot/layers/*`, `live2d/pilot/model/lotte-pilot.model3.json`). The runtime triplet (official Cubism 4 core + PIXI v6 + `pixi-live2d-display@0.4.0/dist/cubism4.min.js`) is identical in Tasks 1 and 6. `model.focus(x, y)` is the tracking call in both. Parameter names (`ParamEyeLOpen/ROpen`, `ParamEyeBallX/Y`, `ParamEyeForm`, `ParamMouthForm/OpenY`, `ParamAngleZ`) match the spec §5 set.
