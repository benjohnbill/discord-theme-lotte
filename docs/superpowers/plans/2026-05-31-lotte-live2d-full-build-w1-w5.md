# Lotte Live2D — Full Build (W1–W5) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans (recommended for this plan — it interleaves agent scripts with user GUI work in ChatGPT/Cubism) or superpowers:subagent-driven-development. Steps use checkbox (`- [ ]`) syntax for tracking.
>
> **Plan type note:** Like the Phase 1.0 pilot plan, this mixes (a) agent-written Python/JS (testable where there is real logic), (b) user actions in external tools (ChatGPT/GPT-image-2, Cubism 5 FREE — verified by handoff artifact + agent sanity scripts), and (c) browser render checks (run/observe/screenshot under a SwiftShader Chrome, because `bh-chrome` has no WebGL — memory `bh-chrome-no-webgl`). The genuinely exploratory links (segmentation refinement, generative drift, rig posing) are written as **explicit inspect-and-iterate loops with complete starting-point code and named fallbacks**, not vague TODOs — this is the same style the pilot plan used and is intentional (spec §7 declares W2/W3/W4 an iterative core).

**Goal:** Turn the locked Lotte illustration into a full ~20-part Tier-1 Cubism 4 rig (blink, breath, gaze, head tilt, hair/ribbon physics, occasional eye-contact smile) and swap it into the proven Phase-0 plumbing, verified in a SwiftShader standalone page and the real Discord client.

**Architecture:** Five workstreams seeded by the Phase 1.0 pilot (gate = GO). W1 locks + upscales the base. W2 harvests the remaining hidden-state references (USER, GPT-image-2) with a drift-reject gate. W3 separates ~20 parts with agent scripts (extending the pilot's `segment.py`) + user preview review, then assembles the layered PSD. W4 is the full guided Cubism rig (USER) exporting a moc3 **≤ v5**. W5 integrates into a standalone page + the Discord console probe, adds the eye-contact-smile state machine, and verifies. **W2→W3→W4 is an iterative core** (spec §7): expect one full pass then targeted re-runs; `PIPELINE.md` records the loop state.

**Tech Stack:** Python 3.14 in `live2d/pilot/.venv` (Pillow, rembg/onnxruntime, psd-tools, numpy); waifu2x (or a verified upscaler fallback); Cubism 5.3 FREE; PIXI.js v6.5.10 + `pixi-live2d-display@0.4.0` (cubism4 build) + official web Cubism Core; throwaway SwiftShader Chrome.

**Source spec:** `docs/superpowers/specs/2026-05-31-lotte-live2d-phase1-rig-design.md` (§2 decisions, §3.1 smile state machine, §4 layer map, §5 params, §7 workstreams, §8 layout, §12 checks).

**Pilot learnings carried in (confirmed, see `live2d/pilot/RESULT.md`):**
1. **moc3 export must target ≤ v5.** Cubism 5.3 default = v6; the pinned web Core reports `csmGetLatestMocVersion()=5` and rejects v6. Export at moc3 **5.0** (or 4.2). Fallback: bump the Core / use the `pixi-live2d-display-lipsyncpatch` fork.
2. **Cubism FREE caps the texture atlas at 2048×2048** (not 4096). Keep hi-res masters in `assets/`, but scale the Cubism source so ~20 *tight-bounded* parts pack into a single 2048 atlas (verify in W3.4/W4); fall back to 2 atlases or a lower factor if not.
3. **`ParamEyeForm` is not standard;** the 5.3 template provides `EyeL Smile`/`EyeR Smile`. Use those (or whatever IDs the model exposes — W5 sets defensively).
4. **Export hygiene:** set the EyeBlink group *inside* Cubism; keep the texture-folder path intact (W4.3 still re-checks).
5. rembg matte is clean in-env; sub-parts need **landmark-keyed boxes + L/R splits**, not fixed fractions; mouth needs a lower crop + the W2 closed-mouth reference.

---

## Scope & File Structure

All artifacts live under `live2d/` (outside the theme build — not in `src/`, not in `theme.manifest.yaml`). Work stays on the `live2d-spike` branch; `master` is never touched.

| File | Responsibility |
|---|---|
| `live2d/PIPELINE.md` | Authority tracker. Update the W-row + "current state / next action" at the end of every task. |
| `live2d/BASE.md` | W1 fills the Result fields (locked file, sha256, upscale, atlas decision). |
| `live2d/source/SHA256SUMS` | Checksums of the locked source rasters (already present; W1 verifies). |
| `live2d/assets/lotte_base.png` | W1 output: the upscaled hi-res character master (committed). |
| `live2d/assets/SHA256SUMS` | W1 output: checksum of `lotte_base.png`. |
| `live2d/gen/PROMPTS.md` | W2 audit log (grows per reference). |
| `live2d/gen/refs/*.png` | W2: raw GPT-image-2 outputs (provenance). |
| `live2d/gen/patches/*.png`, `live2d/gen/patches/*_mask.png` | W2: accepted hidden-state patches + masks. |
| `live2d/tools/harvest_check.py` | W2: reusable alignment-overlay + amplified-diff drift checker. |
| `live2d/tools/full_segment.py` | W3: ~20-part separation (extends the pilot's `segment.py`). |
| `live2d/tools/contact_sheet.py` | W3: build labeled magenta contact sheets for review. |
| `live2d/tools/build_psd_full.py` | W3: assemble the ~20-layer `lotte.psd` (extends `build_psd.py`). |
| `live2d/tools/check_model.py` | W4: model3.json sanity + EyeBlink/texture fix + moc3-version assert. |
| `live2d/layers/*.png` | W3 output: per-part full-canvas aligned PNG layers. |
| `live2d/lotte.psd` | W3 output: the layered Cubism import source. |
| `live2d/model/lotte.model3.json` (+ `.moc3`, `texture_00.png`, `physics3.json`, `.cdi3.json`) | W4 output: the full rig export (moc3 ≤ v5). |
| `live2d/RIG_GUIDE.md` | W4 extends with the full Tier-1 walkthrough. |
| `live2d/integrate/lotte.html` | W5: production standalone page (Cubism 4 triplet + local model + auto-blink/breath + focus + smile state machine). |
| `live2d/integrate/smile-state-machine.js` | W5: the eye-contact-smile behavior (spec §3.1), shared by the page and the probe. |
| `live2d/integrate/discord-probe-v5.js` | W5: Cubism-4 Discord console probe (bg takeover + local model + smile). |
| `live2d/checkpoints/2026-..-<gate>/` | Per-gate screenshot + short note (evidence). |

**Pilot reuse:** `live2d/pilot/.venv` is the Python; `live2d/pilot/segment.py`, `build_psd.py`, `runtime-check.html`, `model-check.html` are the proven starting points to copy/extend into `live2d/tools/` and `live2d/integrate/`.

**Convention for every task below:** run Python with `live2d/pilot/.venv/bin/python`; serve pages with `cd <dir> && python3 -m http.server 8124`; screenshot with the SwiftShader command from W5.2 Step 2; commit with a `feat(live2d):`/`asset(live2d):` message; update `PIPELINE.md`.

---

# Workstream W1 — Base lock + upscale

**Goal:** Confirm the locked base, produce the committed hi-res master, and DECIDE the upscale/atlas strategy under the FREE-tier 2048 cap.

## Task W1.1: Confirm + checksum the locked base

**Files:** Create `live2d/tools/measure_base.py`; Modify `live2d/BASE.md`, `live2d/source/SHA256SUMS`.

- [ ] **Step 1: Write the measurement script**

Create `live2d/tools/measure_base.py`:
```python
"""W1: confirm the locked base (decision §2.3). Measures both source rasters and
reports which carries more facial pixels, and writes/updates source checksums."""
import hashlib, pathlib
from PIL import Image

SRC = pathlib.Path("live2d/source")
FILES = ["lotte-discord-original.png", "lotte-discord-version.png"]

def sha256(p):
    h = hashlib.sha256()
    h.update(pathlib.Path(p).read_bytes())
    return h.hexdigest()

for f in FILES:
    im = Image.open(SRC / f)
    print(f"{f}: size={im.size} mode={im.mode} sha256={sha256(SRC / f)[:16]}…")

# Write a fresh SHA256SUMS for the source dir (all pngs).
lines = []
for p in sorted(SRC.glob("*.png")):
    lines.append(f"{sha256(p)}  {p.name}")
(SRC / "SHA256SUMS").write_text("\n".join(lines) + "\n")
print("\nwrote", SRC / "SHA256SUMS", f"({len(lines)} files)")
```

- [ ] **Step 2: Run and read the result**

Run: `live2d/pilot/.venv/bin/python live2d/tools/measure_base.py`
Expected: `lotte-discord-original.png: size=(1254, 1254)` and `lotte-discord-version.png: size=(1586, 992)` (or similar). Confirm `original` is the square parent with more vertical facial pixels (1254 vs 992 tall for the same crop) — this re-confirms decision §2.3 (character = `original`). If `version` were unexpectedly taller in the face region, STOP and raise with the user (it would reopen a locked decision).

- [ ] **Step 3: Fill BASE.md Result fields**

Edit the `## Result (W1 fills)` section of `live2d/BASE.md` to:
```markdown
## Result (W1 fills)

- Locked character source: `live2d/source/lotte-discord-original.png` (1254×1254) — confirmed more facial px than `version` (992 tall).
- Background (ambient layer, OUT of model): `live2d/source/lotte-discord-version.png`.
- sha256 (character source): _(paste the full hash from measure_base.py output)_
- Upscale applied: _(W1.2 fills)_
- Atlas packing decision: _(W3.4 / W4 fills)_
```

- [ ] **Step 4: Commit**

```bash
git add live2d/tools/measure_base.py live2d/BASE.md live2d/source/SHA256SUMS
git commit -m "asset(live2d): W1 confirm locked base + source checksums"
```

## Task W1.2: Produce the hi-res character master (upscale, verify-and-decide)

**Files:** Create `live2d/tools/upscale_base.py`; Output `live2d/assets/lotte_base.png`, `live2d/assets/SHA256SUMS`.

- [ ] **Step 1: Check upscaler availability (tool-availability rule)**

Run, in order, and note which succeeds:
```bash
command -v waifu2x-ncnn-vulkan && echo "have waifu2x-ncnn-vulkan"
command -v realesrgan-ncnn-vulkan && echo "have realesrgan"
live2d/pilot/.venv/bin/python -c "import cv2; print('have opencv', cv2.__version__)" 2>&1 | tail -1
```
Decision ladder (record the chosen tool in BASE.md):
- If `waifu2x-ncnn-vulkan` exists → use it (`-s 2 -n 2`).
- Else if `realesrgan-ncnn-vulkan` exists → use it (`-s 2`).
- Else fall back to high-quality Lanczos (`opencv`/Pillow) — softer than a neural upscaler but adequate for a soft-focus anime background; record this as a quality note.

- [ ] **Step 2: Write the upscale script (with the Lanczos fallback inline)**

Create `live2d/tools/upscale_base.py`:
```python
"""W1.2: produce the hi-res character master. Prefers a neural upscaler if one was
found in Step 1; otherwise high-quality Lanczos (Pillow). FACTOR=2 per BASE.md, but
the ATLAS decision (W3.4/W4) may scale the *Cubism source* down to fit a 2048 atlas —
this master stays hi-res regardless."""
import shutil, subprocess, hashlib, pathlib
from PIL import Image

SRC = "live2d/source/lotte-discord-original.png"
OUT = pathlib.Path("live2d/assets/lotte_base.png")
OUT.parent.mkdir(parents=True, exist_ok=True)
FACTOR = 2

def have(cmd):
    return shutil.which(cmd) is not None

if have("waifu2x-ncnn-vulkan"):
    subprocess.run(["waifu2x-ncnn-vulkan", "-i", SRC, "-o", str(OUT),
                    "-s", str(FACTOR), "-n", "2"], check=True)
    tool = "waifu2x-ncnn-vulkan -s2 -n2"
elif have("realesrgan-ncnn-vulkan"):
    subprocess.run(["realesrgan-ncnn-vulkan", "-i", SRC, "-o", str(OUT),
                    "-s", str(FACTOR)], check=True)
    tool = "realesrgan-ncnn-vulkan -s2"
else:
    im = Image.open(SRC).convert("RGBA")
    im = im.resize((im.width * FACTOR, im.height * FACTOR), Image.LANCZOS)
    im.save(OUT)
    tool = "PIL Lanczos x2 (fallback; no neural upscaler in env)"

h = hashlib.sha256(OUT.read_bytes()).hexdigest()
(OUT.parent / "SHA256SUMS").write_text(f"{h}  {OUT.name}\n")
print("upscaled with:", tool)
print("output:", OUT, Image.open(OUT).size, "sha256", h[:16], "…")
```

- [ ] **Step 3: Run and verify**

Run: `live2d/pilot/.venv/bin/python live2d/tools/upscale_base.py`
Expected: `live2d/assets/lotte_base.png` at ~2508×2508 (FACTOR×1254). Open it; confirm no artifacts/halos around hair edges (neural) or acceptable softness (Lanczos fallback). If a neural tool produced ringing, re-run the fallback branch and keep the cleaner result.

- [ ] **Step 4: Record the upscale in BASE.md + commit**

In `live2d/BASE.md` set `- Upscale applied:` to the tool string + output size from the script. Then:
```bash
git add live2d/tools/upscale_base.py live2d/assets/lotte_base.png live2d/assets/SHA256SUMS live2d/BASE.md
git commit -m "asset(live2d): W1 hi-res character master (upscaled) + checksum"
```
Update `PIPELINE.md`: W1 = DONE, note the upscale tool + that the atlas decision is pending W3.4.

---

# Workstream W2 — Generative source pack (USER + agent verify)

**Goal:** Harvest the hidden-state references the rig needs, applying the drift-reject discipline (spec §7). References (spec / `gen/PROMPTS.md` §3): **forehead-revealed**, **cheek/jaw (side hair tucked)**, **smiling (creased) eyes**, **closed mouth**. Each is generated by the user ON the locked base, then the agent verifies alignment + drift and stores an accepted patch + mask. The pilot's eyes-closed reference already exists as the template.

## Task W2.1: Reusable harvest drift-checker

**Files:** Create `live2d/tools/harvest_check.py`.

- [ ] **Step 1: Write the checker (generalizes the pilot's overlay/diff)**

Create `live2d/tools/harvest_check.py`:
```python
"""W2: verify a generated reference is drift-free vs the base crop, and emit a
landmark-aligned ghost overlay + amplified diff for the user/agent to judge. Same
technique used in the pilot to accept eyes-closed. Usage:
  python harvest_check.py BASE.png REF.png OUTPREFIX
Resizes REF to BASE size, writes <OUTPREFIX>-blend.png and <OUTPREFIX>-diff.png,
and prints whether non-target regions look stable (low diff outside the edit area)."""
import sys
from PIL import Image, ImageChops

base = Image.open(sys.argv[1]).convert("RGB")
ref = Image.open(sys.argv[2]).convert("RGB").resize(base.size)
out = sys.argv[3]

Image.blend(base, ref, 0.5).save(f"{out}-blend.png")
diff = ImageChops.difference(base, ref).point(lambda v: min(255, v * 3))
diff.save(f"{out}-diff.png")

# crude global drift signal: mean amplified-diff. The EDIT region will be bright;
# everything else should stay dark. High global mean => the whole image moved/recolored.
import statistics
px = list(diff.convert("L").getdata())
print(f"size {base.size}  mean-amplified-diff {statistics.mean(px):.1f} "
      f"(low ~<25 = only the edited region changed; high = global drift → regenerate)")
print(f"wrote {out}-blend.png {out}-diff.png")
```

- [ ] **Step 2: Smoke-test on the pilot's accepted eyes-closed reference**

Run:
```bash
live2d/pilot/.venv/bin/python live2d/tools/harvest_check.py \
  live2d/pilot/face-crop.png live2d/pilot/gen/eyes-closed.png /tmp/ec
```
Expected: prints a low-ish mean (the eyes region dominates the diff) and writes `/tmp/ec-blend.png` + `/tmp/ec-diff.png`. Open them: hair/ribbon/outline single (aligned), eyes bright. This confirms the checker reproduces the pilot's accept decision.

- [ ] **Step 3: Commit**

```bash
git add live2d/tools/harvest_check.py
git commit -m "feat(live2d): W2 reusable harvest drift-checker"
```

## Tasks W2.2–W2.5: Harvest each reference (USER generates, agent verifies)

> Repeat this 4-step cycle for each reference. The full-base master `live2d/assets/lotte_base.png` is the attach target for face-wide edits; for tight edits (mouth/eyes) the user may attach a crop of it. Use the §2 style-vocabulary CHARACTER prefix from `gen/PROMPTS.md` so the character stays on-model.

- [ ] **W2.2 forehead-revealed** (for the face base under the bangs)
  1. **User (ChatGPT / GPT-image-2):** attach `live2d/assets/lotte_base.png`. Prompt:
     ```
     Reference image attached: long brown hair, large violet eyes, a violet ribbon on
     top of the head, navy sailor uniform, gentle expression, slight head-tilt.
     Keep the character EXACTLY the same — same face, eyes, ribbon, lighting, line
     weight, colors, framing, pixel alignment. Change ONLY the hairline: push the front
     bangs up/back to reveal the full forehead skin underneath, drawn in the same soft
     shading as the visible face. Do not move or restyle anything else. Same size,
     pixel-aligned to the reference.
     ```
     Save to `live2d/gen/refs/forehead.png`.
  2. **Agent verify:** `live2d/pilot/.venv/bin/python live2d/tools/harvest_check.py live2d/assets/lotte_base.png live2d/gen/refs/forehead.png /tmp/fh` → open `/tmp/fh-blend.png`/`/tmp/fh-diff.png`. ACCEPT only if face/eyes/ribbon are single (aligned) and the change is localized to the forehead. If global drift → user regenerates.
  3. **Agent harvest the patch + mask:** create `live2d/gen/patches/forehead.png` (the forehead skin region, landmark-aligned) and `live2d/gen/patches/forehead_mask.png` (a conservative, feathered alpha of just the newly-revealed forehead). Use the W3 box helper (Step pattern from `full_segment.py`) to crop the forehead band and feather its mask:
     ```bash
     live2d/pilot/.venv/bin/python - <<'PY'
     from PIL import Image, ImageFilter
     ref = Image.open("live2d/gen/refs/forehead.png").convert("RGBA")
     W,H = ref.size
     box = (int(W*0.28), int(H*0.20), int(W*0.72), int(H*0.40))  # forehead band — TWEAK by inspecting
     patch = ref.crop(box); patch.save("live2d/gen/patches/forehead.png")
     m = Image.new("L", patch.size, 255).filter(ImageFilter.GaussianBlur(8))  # feather edges
     m.save("live2d/gen/patches/forehead_mask.png")
     print("patch", patch.size)
     PY
     ```
     Inspect `forehead.png`; adjust the `box` fractions until it tightly contains the revealed forehead.
  4. **Commit:** `git add live2d/gen/refs/forehead.png live2d/gen/patches/forehead*.png && git commit -m "asset(live2d): W2 forehead-revealed patch"`. Tick the box in `gen/PROMPTS.md` §3 and append the prompt + drift note (mirror the pilot's eyes-closed entry).

- [ ] **W2.3 cheek/jaw (side hair tucked)** — same cycle. Prompt change: *"Change ONLY the side hair: tuck the left and right side-hair locks behind the ears to reveal the full cheek and jawline skin underneath."* Save `refs/cheekjaw.png`; patch `patches/cheekjaw.png` (+ mask) over the cheek/jaw band (`box ≈ (0.10,0.45,0.90,0.85)` — TWEAK).

- [ ] **W2.4 smiling (creased) eyes** — for the eye-smile keyform. Prompt change: *"Change ONLY the eyes: give them a soft, gentle smiling crease (lower lids raised slightly, a content 'soft smile' eye shape), eyes still mostly open."* Save `refs/eyes-smile.png`; patch the eye band (reuse the pilot's eye box `(0.23,0.53,0.74,0.80)` scaled to the master).

- [ ] **W2.5 closed mouth** — unlocks tight-closed + closed-smile via `ParamMouthForm` (and fixes the pilot's clipped/marginal mouth). Prompt change: *"Change ONLY the mouth: draw it gently closed (a soft closed-lip line, relaxed), keeping the same lip color and the same position."* Save `refs/closed-mouth.png`; patch the mouth region. **Use a crop that includes the full chin** (the pilot finding: don't clip the mouth at the bottom).

## Task W2.6: Reject-gate summary

- [ ] **Step 1:** In `gen/PROMPTS.md`, confirm all four §3 boxes are ticked with their drift notes, and that each accepted patch composites invisibly at the patch location (spot-check by pasting a patch onto `lotte_base.png` via its mask and eyeballing the seam). Record any reference that needed >1 regeneration (informs the W2 cookbook).
- [ ] **Step 2: Commit** `git add live2d/gen && git commit -m "asset(live2d): W2 generative source pack complete (4 hidden-state patches + masks)"`. Update `PIPELINE.md` W2 = DONE.

---

# Workstream W3 — Full part separation (agent scripts + user review)

**Goal:** Separate the upscaled master into ~20 depth-ordered parts (spec §4 layer map), using rembg for the silhouette + landmark-keyed boxes + L/R splits + the W2 patches for hidden regions, then assemble the layered `lotte.psd`. **This is the load-bearing workstream** — favor merging parts over a bad cut (spec §7 escape hatch).

## Task W3.1: The ~20-part separation script

**Files:** Create `live2d/tools/full_segment.py` (extends `live2d/pilot/segment.py`).

- [ ] **Step 1: Write `full_segment.py`**

Create `live2d/tools/full_segment.py`:
```python
"""W3: separate live2d/assets/lotte_base.png into ~20 full-canvas aligned PNG layers
(spec §4). rembg gives the character matte; sub-parts are fraction boxes CALIBRATED by
inspection (run live2d/tools/contact_sheet.py + a 10%-grid read, exactly as the pilot
did); L/R parts are split at the face midline; hidden regions (forehead/cheek/jaw under
hair, closed-mouth/eyelid art) come from the W2 patches. Every layer is full-canvas so
they stack in register on PSD import."""
import sys, pathlib
from PIL import Image

BASE = "live2d/assets/lotte_base.png"
PATCH = pathlib.Path("live2d/gen/patches")
OUT = pathlib.Path("live2d/layers"); OUT.mkdir(parents=True, exist_ok=True)

try:
    from rembg import remove
    HAVE_REMBG = True
except Exception as e:
    HAVE_REMBG = False
    print("rembg NOT available:", e, file=sys.stderr)

img = Image.open(BASE).convert("RGBA")
W, H = img.size
matte = remove(img) if HAVE_REMBG else img  # character silhouette/alpha

def box(l, t, r, b):
    return (int(W*l), int(H*t), int(W*r), int(H*b))

def layer(name, frac_box, source=img):
    """Full-canvas aligned layer: crop `source` at the box, place at the box origin."""
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    canvas.paste(source.crop(frac_box), (frac_box[0], frac_box[1]))
    canvas.save(OUT / f"{name}.png")
    print("wrote", name, frac_box)

def patch_layer(name, patch_png):
    """A hidden-state part sourced from a W2 patch, kept full-canvas at its origin."""
    p = Image.open(PATCH / patch_png).convert("RGBA")
    # patches were cropped from the master at known boxes; re-place onto full canvas.
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    canvas.alpha_composite(p, (0, 0))  # if a patch was saved full-canvas; else adjust origin
    canvas.save(OUT / f"{name}.png")
    print("wrote", name, "(from patch", patch_png + ")")

# face_base = matte with forehead + cheek/jaw filled from W2 patches (so deformation
# under bangs/side-hair reveals skin, not holes). Composite patches onto the matte:
face = matte.copy()
for pp in ["forehead.png", "cheekjaw.png"]:
    fp = PATCH / pp
    if fp.exists():
        face.alpha_composite(Image.open(fp).convert("RGBA"))
face.save(OUT / "face_base.png")

# --- Depth-ordered ~20 parts (spec §4). Fraction boxes are STARTING POINTS — calibrate. ---
# back hair L/R, body, scarf, neck handled as their own boxes off the matte:
layer("backhair_L", box(0.00, 0.10, 0.30, 0.95))
layer("backhair_R", box(0.70, 0.10, 1.00, 0.95))
layer("body",       box(0.10, 0.78, 0.90, 1.00))   # body + collar (breath/lean)
layer("scarf",      box(0.40, 0.80, 0.60, 0.95))
layer("neck",       box(0.40, 0.74, 0.60, 0.84))
# eyebrows L/R (now separated from face_base — pilot finding):
layer("brow_L",     box(0.26, 0.48, 0.46, 0.55))
layer("brow_R",     box(0.54, 0.48, 0.74, 0.55))
# eyes, split L/R (sclera mask, iris, upper lid from eyes-closed art, lower lid):
layer("sclera_L",   box(0.26, 0.55, 0.47, 0.74))
layer("iris_L",     box(0.29, 0.57, 0.44, 0.72))
layer("sclera_R",   box(0.53, 0.55, 0.74, 0.78))
layer("iris_R",     box(0.56, 0.57, 0.71, 0.76))
# blink lids from the pilot's eyes-closed art (resized to the master); split L/R:
closed = Image.open("live2d/pilot/gen/eyes-closed.png").convert("RGBA").resize((W, H))
layer("upperlid_L", box(0.26, 0.53, 0.47, 0.74), source=closed)
layer("upperlid_R", box(0.53, 0.53, 0.74, 0.78), source=closed)
# eye-smile lower lids from the W2 smiling-eyes ref if present:
sm = PATCH / "eyes-smile.png"
sm_src = Image.open(sm).convert("RGBA") if sm.exists() else img
layer("lowerlid_L", box(0.26, 0.66, 0.47, 0.76), source=sm_src)
layer("lowerlid_R", box(0.53, 0.66, 0.74, 0.80), source=sm_src)
# mouth outer + inner; outer from the W2 closed-mouth ref for the closed keyform:
cm = PATCH / "closed-mouth.png"
cm_src = Image.open(cm).convert("RGBA") if cm.exists() else img
layer("mouth_outer", box(0.44, 0.80, 0.62, 0.95), source=cm_src)
layer("mouth_inner", box(0.46, 0.83, 0.60, 0.93))
# front: side hair L/R, bangs, ribbon:
layer("sidehair_L", box(0.03, 0.18, 0.30, 0.96))
layer("sidehair_R", box(0.70, 0.18, 0.97, 0.96))
layer("bangs",      box(0.20, 0.20, 0.80, 0.58))
layer("ribbon",     box(0.55, 0.06, 0.85, 0.30))
print("done — ~", len(list(OUT.glob('*.png'))), "layers")
```

- [ ] **Step 2: Run it**

Run: `live2d/pilot/.venv/bin/python live2d/tools/full_segment.py`
Expected: ~21 PNGs in `live2d/layers/`, all full-canvas (master size). rembg downloads its model on first run (already cached from the pilot).

## Task W3.2: Inspect-and-iterate the boxes (the real work)

**Files:** Create `live2d/tools/contact_sheet.py`.

- [ ] **Step 1: Write the contact-sheet tool (generalizes the pilot's)**

Create `live2d/tools/contact_sheet.py`:
```python
"""W3: composite every live2d/layers/*.png over magenta into one labeled sheet so
alpha cutouts are visible. Run after each full_segment.py tweak."""
import glob
from PIL import Image, ImageDraw
MAG = (255, 0, 255, 255); TH = 220; cells = []
for p in sorted(glob.glob("live2d/layers/*.png")):
    im = Image.open(p).convert("RGBA")
    comp = Image.alpha_composite(Image.new("RGBA", im.size, MAG), im)
    w = max(1, int(comp.width * TH / comp.height)); comp = comp.resize((w, TH))
    lab = Image.new("RGBA", (comp.width, 20), (0, 0, 0, 255))
    ImageDraw.Draw(lab).text((3, 4), p.split("/")[-1], fill=(255, 255, 0, 255))
    cell = Image.new("RGBA", (comp.width, TH + 20), (40, 40, 40, 255))
    cell.paste(lab, (0, 0)); cell.paste(comp, (0, 20)); cells.append(cell)
# wrap into rows of ~6
import math
COLS = 6; rows = [cells[i:i+COLS] for i in range(0, len(cells), COLS)]
gap = 6; cw = max(c.width for c in cells); ch = TH + 20
W = COLS*(cw+gap)+gap; H = len(rows)*(ch+gap)+gap
sheet = Image.new("RGBA", (W, H), (20, 20, 20, 255))
for r, row in enumerate(rows):
    x = gap
    for c in row:
        sheet.paste(c, (x, gap + r*(ch+gap))); x += cw + gap
sheet.convert("RGB").save("/tmp/layers_contact.png")
print("wrote /tmp/layers_contact.png", sheet.size)
```

- [ ] **Step 2: The iteration loop**

Run `live2d/pilot/.venv/bin/python live2d/tools/contact_sheet.py`; open `/tmp/layers_contact.png`. For each part that misses its feature (the master's head-tilt offsets features from nominal centers — pilot finding), adjust that part's `box(...)` fractions in `full_segment.py` and re-run both scripts. Use a 10%-grid render (copy the pilot's grid snippet) on `lotte_base.png` to read exact coordinates. **Acceptance per part:** the magenta cell shows the right feature, reasonably isolated. `face_base` must show a clean character matte (rembg). Iterate until all ~20 cells are right.

- [ ] **Step 3: User review (preview-only, spec §7 constraint — no hand-painting)**

Send the contact sheet to the user. The user marks any part that is mis-cut or should be **merged** (e.g., if two parts can't be cleanly separated, merge them — an allowed outcome). Apply merges by deleting the surplus `layer(...)` calls and widening the survivor's box. Re-run.

- [ ] **Step 4: Alpha-union + commit**

Run the pilot's alpha-union check adapted to `live2d/layers/*.png` (every part non-empty, `face_base` alpha range `(0,255)`, sub-parts opaque). Then:
```bash
git add live2d/tools/full_segment.py live2d/tools/contact_sheet.py live2d/layers
git commit -m "asset(live2d): W3 ~20-part separation (calibrated)"
```

## Task W3.3: Assemble the layered PSD

**Files:** Create `live2d/tools/build_psd_full.py` (extends `live2d/pilot/build_psd.py`).

- [ ] **Step 1: Write it**

Create `live2d/tools/build_psd_full.py`:
```python
"""W3: assemble live2d/layers/*.png into live2d/lotte.psd (psd-tools), depth-ordered
back->front per spec §4. Each layer is full-canvas so they import in register."""
import pathlib
from PIL import Image
from psd_tools import PSDImage
from psd_tools.api.layers import PixelLayer

LAYERS = pathlib.Path("live2d/layers")
OUT = "live2d/lotte.psd"
# back -> front (spec §4). Names must match files in live2d/layers/.
DEPTH = [
    "backhair_L", "backhair_R", "body", "scarf", "neck", "face_base",
    "brow_L", "brow_R", "sclera_L", "iris_L", "sclera_R", "iris_R",
    "upperlid_L", "upperlid_R", "lowerlid_L", "lowerlid_R",
    "mouth_inner", "mouth_outer", "sidehair_L", "sidehair_R", "bangs", "ribbon",
]
size = Image.open(LAYERS / "face_base.png").size
psd = PSDImage.new(mode="RGBA", size=size)
for name in DEPTH:
    f = LAYERS / f"{name}.png"
    if not f.exists():
        print("skip missing", name); continue
    psd.append(PixelLayer.frompil(Image.open(f).convert("RGBA"), psd, name, top=0, left=0))
psd.save(OUT)
chk = PSDImage.open(OUT)
print("wrote", OUT, "layers:", [l.name for l in chk])
chk.composite().convert("RGB").save("live2d/lotte-preview.png")
print("preview -> live2d/lotte-preview.png")
```

- [ ] **Step 2: Run + verify the preview**

Run: `live2d/pilot/.venv/bin/python live2d/tools/build_psd_full.py`
Open `live2d/lotte-preview.png`: it should reconstruct the full character (the closed-eye/closed-mouth overlays sit on top in the static preview — expected; the rig morphs between them). If a layer is missing or misplaced, fix `full_segment.py`/`DEPTH` and re-run.

## Task W3.4: Atlas-packing pre-check (the FREE 2048 decision)

- [ ] **Step 1: Estimate tight-bounded packing**

Run:
```bash
live2d/pilot/.venv/bin/python - <<'PY'
import glob
from PIL import Image
total = 0
for p in glob.glob("live2d/layers/*.png"):
    bb = Image.open(p).convert("RGBA").getbbox()  # tight content bounds
    if bb: total += (bb[2]-bb[0]) * (bb[3]-bb[1])
import math
print(f"sum of tight part areas = {total:,} px²  ~= a {int(math.sqrt(total)):,}px square")
print("single 2048 atlas area = 4,194,304 px². Fits one atlas if sum (×~1.4 packing slack) < that.")
PY
```
Decision (record in BASE.md `Atlas packing decision:`):
- If the slack-adjusted sum fits **one 2048 atlas** → keep the upscaled master resolution for Cubism.
- If not → in W4's atlas step, either (a) let Cubism use **2 atlases** (if FREE allows multiple — verify in W4), or (b) scale the Cubism import down (Cubism's atlas tool can downscale on layout; or pre-scale the layers) until it fits. The hi-res `assets/lotte_base.png` master is preserved either way.

- [ ] **Step 2: Commit + update PIPELINE**

```bash
git add live2d/tools/build_psd_full.py live2d/lotte.psd live2d/lotte-preview.png live2d/BASE.md
git commit -m "asset(live2d): W3 layered lotte.psd + atlas-packing decision"
```
Update `PIPELINE.md` W3 = DONE. **Note the W3↔W4 loop:** if W4 rigging reveals a part needs splitting/merging, return here.

---

# Workstream W4 — Cubism rig (USER, agent-guided)

**Goal:** The full Tier-1 rig: deformer hierarchy, clipping masks, **mesh-deformation** blink (not opacity), L/R eyes, gaze, restrained head tilt + flat turn, body lean, breath, hair/ribbon physics, and a restrained smile — exported as a moc3 **≤ v5**.

## Task W4.1: Author the full rig walkthrough

**Files:** Modify `live2d/RIG_GUIDE.md` (add a "Full Build (W4)" section).

- [ ] **Step 1: Web-check current Cubism 5.3 specifics, then write the section**

Agent: re-verify against current docs the steps that differ from the pilot (clipping mask setup, mesh-deformation blink keying, physics pendulum setup, multi-atlas behavior in FREE). Then append a **Full Build (W4)** section to `RIG_GUIDE.md` covering, in order, with the verified param IDs/ranges from the pilot guide's table:
  1. Import `live2d/lotte.psd`; auto-mesh all; hand-clean eyes/mouth/hair meshes.
  2. **Deformer hierarchy** (spec §4): `root → body(warp) → head(rotation) → {face(warp) → {eyes, mouth}, hair parts}`. Parent the parts accordingly.
  3. **Clipping masks:** set `sclera_L/R` as masks; clip `iris_L/R` to them; lids ride above.
  4. **Blink (mesh deformation, not opacity):** key `ParamEyeLOpen`/`ParamEyeROpen` (1=open,0=closed) by deforming the open-eye mesh closed AND bringing `upperlid_L/R` down — use the eyes-closed art as the closed keyform shape. This replaces the pilot's opacity crossfade.
  5. **Gaze:** key `ParamEyeBallX` (−1..1, +right) / `ParamEyeBallY` (−1..1, +up) by translating `iris_L/R` within the sclera clip.
  6. **Eye-smile:** key the template's `EyeL Smile`/`EyeR Smile` (raise lower lids via `lowerlid_L/R`). (No `ParamEyeForm`.)
  7. **Mouth:** key `ParamMouthForm` (−1..1, +smile) using `mouth_outer` closed-art at the closed end; small `ParamMouthOpenY`.
  8. **Head:** `ParamAngleZ` (−30..30) tilt; `ParamAngleX/Y` **FLAT only** — planar offset + tiny rotation + hair/body lag, NO cheek/nose parallax (DECISIONS §6). `ParamBodyAngleX` (−10..10) lean; `ParamBreath` (0..1).
  9. **Physics:** pendulum chains driven by head/body angle for `backhair_L/R`, `sidehair_L/R`, `bangs`, `ribbon` — low output scale (flat 2D sway).
  10. **Texture atlas:** create at **2048** (FREE cap; W3.4 decision). If parts don't fit one, add a second atlas or downscale on layout.
  11. **Export:** File ▸ Export embedded file ▸ moc3; include textures + `physics3.json`; **set `.moc3 file version` to 5.0 (or 4.2)** — NOT the v6 default; export to `live2d/model/lotte.model3.json`.
  Keep all ranges restrained (Tier-1, spec §5/§7): small gaze, gentle tilt, subtle breath.

- [ ] **Step 2: Commit** `git add live2d/RIG_GUIDE.md && git commit -m "docs(live2d): W4 full Tier-1 rig walkthrough"`.

## Task W4.2: User rigs the full model

- [ ] **Step 1 (USER):** Follow the W4 section of `RIG_GUIDE.md` in Cubism 5.3 FREE. Save the project to `live2d/lotte.cmo3`. Export to `live2d/model/` as `lotte.model3.json` (+ `.moc3` at version 5.0, `texture_00.png`, `physics3.json`, `.cdi3.json`). Keep ranges restrained; this is the real rig, but Tier-1 (start under-animated). Expect to interleave with the agent (screenshot loop) as in the pilot.
- [ ] **Step 2 (USER):** Provide the exported `live2d/model/` files (paste into the worktree path, as in the pilot).

## Task W4.3: Sanity-check + repair the export

**Files:** Create `live2d/tools/check_model.py`.

- [ ] **Step 1: Write the checker/repairer**

Create `live2d/tools/check_model.py`:
```python
"""W4: validate live2d/model/lotte.model3.json — moc3 version <= 5 (runtime Core max),
all referenced files exist, and populate/fix the EyeBlink group + LipSync if Cubism
exported them empty (pilot fix). Run after every (re)export."""
import json, pathlib, sys

MODEL = pathlib.Path("live2d/model/lotte.model3.json")
d = json.loads(MODEL.read_text())
base = MODEL.parent
refs = d["FileReferences"]

moc = base / refs["Moc"]
ver = moc.read_bytes()[4]
print(f"moc3 magic ok, version_byte = {ver}", "(<=5 OK)" if ver <= 5 else "(>5 — WILL NOT LOAD; re-export at moc3 5.0)")
assert ver <= 5, "moc3 version > 5: the pinned Core rejects it. Re-export at .moc3 version 5.0."

for t in refs.get("Textures", []):
    assert (base / t).exists(), f"missing texture {t}"
if refs.get("Physics"):
    assert (base / refs["Physics"]).exists(), "missing physics3.json"
print("textures + physics present:", refs.get("Textures"), refs.get("Physics"))

changed = False
for g in d.get("Groups", []):
    if g.get("Name") == "EyeBlink" and not g.get("Ids"):
        g["Target"] = "Parameter"; g["Ids"] = ["ParamEyeLOpen", "ParamEyeROpen"]; changed = True
if changed:
    MODEL.write_text(json.dumps(d, indent=2, ensure_ascii=False))
    print("populated empty EyeBlink group")
print("OK")
```

- [ ] **Step 2: Run it**

Run: `live2d/pilot/.venv/bin/python live2d/tools/check_model.py`
Expected: `version_byte <= 5`, textures/physics present, `OK`. If it asserts on the moc3 version, the user re-exports at moc3 **5.0** (W4.2) and you re-run. If a texture path is wrong (pilot saw `.2048/` vs root mismatch), fix `FileReferences.Textures` to the actual filename.

- [ ] **Step 3: Commit**

```bash
git add live2d/lotte.cmo3 live2d/model live2d/tools/check_model.py
git commit -m "asset(live2d): W4 full Tier-1 Cubism rig (moc3 v5) + export check"
```
Update `PIPELINE.md` W4 = DONE.

---

# Workstream W5 — Integrate + verify

**Goal:** Render the full model in the proven plumbing with auto-blink/breath + cursor gaze + the eye-contact-smile state machine; verify under SwiftShader, then in the real Discord client.

## Task W5.1: The eye-contact-smile state machine

**Files:** Create `live2d/integrate/smile-state-machine.js`.

- [ ] **Step 1: Write it (spec §3.1, conservative tunables)**

Create `live2d/integrate/smile-state-machine.js`:
```javascript
// Eye-contact smile behavior (spec §3.1). idle → glance → eye-contact → smile-hold →
// relax → idle. Gaze/tilt come from model.focus() (autoInteract); this module adds the
// occasional smile by ramping ParamMouthForm + EyeL/R Smile. Defensive setter: unknown
// param IDs are no-ops in the Cubism core, so we try the standard smile IDs.
// Hook = app.ticker (proven in the pilot's forced-blink test): it runs after the model's
// own auto-update, so our values win for that frame's draw.
// Usage:  attachSmileBehavior(app, model, () => lastCursor)   // lastCursor = {x,y} or null
window.attachSmileBehavior = function (app, model, getCursor) {
  const T = {                      // tunables — start conservative (spec §3.1)
    triggerMinMs: 9000, triggerMaxMs: 22000, // how often an eye-contact smile may fire
    proximityPx: 220,              // cursor within this of the face can also trigger
    rampMs: 700,                   // smile ramp in/out
    holdMs: 1500,                  // smile hold
    cooldownMs: 12000,             // min gap between smiles (keeps it rare)
  };
  const rand = (a, b) => a + Math.random() * (b - a);   // browser JS: Math.random is fine
  const cx = () => model.x, cy = () => model.y - model.height * 0.15; // ~face center
  const setP = (id, v) => { try { model.internalModel.coreModel.setParameterValueById(id, v); } catch (e) {} };
  let state = "idle", t0 = performance.now(), nextAt = t0 + rand(T.triggerMinMs, T.triggerMaxMs), lastEnd = 0, amp = 0;
  const near = () => {
    const c = getCursor && getCursor(); if (!c) return false;
    return Math.hypot(c.x - cx(), c.y - cy()) < T.proximityPx;
  };
  app.ticker.add(() => {
    const now = performance.now();
    if (state === "idle") {
      if ((now >= nextAt || near()) && now - lastEnd > T.cooldownMs) { state = "ramp_in"; t0 = now; }
    } else if (state === "ramp_in") {
      amp = Math.min(1, (now - t0) / T.rampMs); if (amp >= 1) { state = "hold"; t0 = now; }
    } else if (state === "hold") {
      amp = 1; if (now - t0 > T.holdMs) { state = "ramp_out"; t0 = now; }
    } else if (state === "ramp_out") {
      amp = Math.max(0, 1 - (now - t0) / T.rampMs);
      if (amp <= 0) { state = "idle"; lastEnd = now; nextAt = now + rand(T.triggerMinMs, T.triggerMaxMs); }
    }
    if (amp > 0) {                 // restrained smile: gentle mouth + eye-smile crease
      setP("ParamMouthForm", 0.7 * amp);
      setP("ParamEyeLSmile", amp); setP("ParamEyeRSmile", amp);
      setP("ParamEyeForm", amp);   // harmless if the model lacks it
    }
  });
  return T; // expose for tuning from the console
};
```

- [ ] **Step 2: Lint-check (node parse)**

Run: `node --check live2d/integrate/smile-state-machine.js`
Expected: no output (parses). If `node` is absent, skip (the browser will surface syntax errors in W5.2).

## Task W5.2: Standalone page + SwiftShader verify

**Files:** Create `live2d/integrate/lotte.html`.

- [ ] **Step 1: Write `lotte.html`** (Cubism 4 triplet from the pilot + local model + smile module)

Create `live2d/integrate/lotte.html`:
```html
<!doctype html>
<html><head><meta charset="utf-8" />
<style>html,body{margin:0;height:100%;background:#1e1f3a;overflow:hidden}#c{display:block;width:100vw;height:100vh}
#status{position:fixed;top:8px;left:8px;color:#fff;font:13px monospace}</style></head>
<body><div id="status">loading…</div><canvas id="c"></canvas>
<script src="https://cubism.live2d.com/sdk-web/cubismcore/live2dcubismcore.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/pixi.js@6.5.10/dist/browser/pixi.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/pixi-live2d-display@0.4.0/dist/cubism4.min.js"></script>
<script src="./smile-state-machine.js"></script>
<script>
(async () => {
  const status = document.getElementById('status');
  try {
    const app = new PIXI.Application({ view: document.getElementById('c'), resizeTo: window, backgroundAlpha: 0, autoStart: true });
    const model = await PIXI.live2d.Live2DModel.from('../model/lotte.model3.json');
    app.stage.addChild(model);
    let frames = 0;
    const fit = () => { const s = Math.min(innerWidth/model.width, innerHeight/model.height)*0.9;
      model.scale.set(s); model.anchor.set(0.5,0.5); model.position.set(innerWidth/2, innerHeight/2); };
    const refit = () => { fit(); if (++frames < 30) requestAnimationFrame(refit); }; refit();
    addEventListener('resize', fit);
    let cursor = null; addEventListener('mousemove', e => { cursor = {x:e.clientX,y:e.clientY}; model.focus(e.clientX,e.clientY); });
    window.attachSmileBehavior(app, model, () => cursor);   // auto-blink/breath are on by default
    window.__lotte = { app, model };
    status.textContent = 'lotte loaded — blink/breath auto; move mouse for gaze; smile fires occasionally.';
  } catch (e) { status.textContent = 'ERROR: ' + (e&&e.message?e.message:e); console.error(e); }
})();
</script></body></html>
```

- [ ] **Step 2: Serve + screenshot under SwiftShader**

Run (server in one shell, screenshot in another):
```bash
cd live2d/integrate && python3 -m http.server 8124 &
SRV=$!; sleep 1
google-chrome --headless=new --enable-unsafe-swiftshader --use-gl=angle --use-angle=swiftshader \
  --no-sandbox --user-data-dir=/tmp/live2d-w5-chrome --window-size=1280,800 \
  --screenshot="$PWD/../checkpoints/w5-standalone.png" --virtual-time-budget=15000 \
  http://localhost:8124/lotte.html 2>/dev/null
kill $SRV
```
(Create `live2d/checkpoints/` first.) Open `live2d/checkpoints/w5-standalone.png`: the full Lotte renders (not blank, not ERROR), status reads `lotte loaded`.

- [ ] **Step 3: Behavior check (run/observe)**

A static shot can't show motion. Also load `http://localhost:8124/lotte.html` in the throwaway Chrome (or the real client) and confirm over ~30 s: auto-blink fires (now a real lid-down deform), breath rises subtly, gaze + head tilt follow the cursor, and an eye-contact smile fires occasionally then relaxes. Capture a forced-smile frame for evidence by running in the console: `__lotte.model.internalModel.coreModel.setParameterValueById('ParamMouthForm',0.7)`. Record in `live2d/checkpoints/w5-standalone-NOTES.md`.

- [ ] **Step 4: Commit**

```bash
git add live2d/integrate/lotte.html live2d/integrate/smile-state-machine.js live2d/checkpoints
git commit -m "feat(live2d): W5 standalone page + smile state machine + SwiftShader verify"
```

## Task W5.3: Discord console probe (Cubism 4) + real-client verify

**Files:** Create `live2d/integrate/discord-probe-v5.js`.

- [ ] **Step 1: Write the probe** (the proven v4 bg-takeover from `experiments/live2d-spike/discord-console-probe.js`, swapped to the Cubism 4 triplet + local model + smile)

Create `live2d/integrate/discord-probe-v5.js` by copying `experiments/live2d-spike/discord-console-probe.js` and making exactly these changes:
  1. Replace the `SCRIPTS` array (Cubism 2 triplet) with the Cubism 4 triplet:
     ```javascript
     const SCRIPTS = [
       "https://cubism.live2d.com/sdk-web/cubismcore/live2dcubismcore.min.js",
       "https://cdn.jsdelivr.net/npm/pixi.js@6.5.10/dist/browser/pixi.min.js",
       "https://cdn.jsdelivr.net/npm/pixi-live2d-display@0.4.0/dist/cubism4.min.js",
     ];
     ```
  2. Replace `MODEL` with the locally served model (run `cd live2d && python3 -m http.server 8124` so Discord can fetch it):
     ```javascript
     const MODEL = "http://localhost:8124/model/lotte.model3.json";
     ```
  3. After `app.stage.addChild(model);` and the `fit`/`onMove` setup, inject the smile module and attach it: load `smile-state-machine.js` via the existing `loadScript` helper (`await loadScript("http://localhost:8124/integrate/smile-state-machine.js")`) and call `window.attachSmileBehavior(app, model, () => lastCursor)`, tracking `lastCursor = {x:e.clientX,y:e.clientY}` in the existing `onMove`.
  Keep the bg-image auto-detect + base-color-clear logic verbatim (it is what made the character visible in Phase 0).

- [ ] **Step 2: Lint-check** `node --check live2d/integrate/discord-probe-v5.js` (skip if no node).

- [ ] **Step 3 (USER): verify in real Discord**

User: run `cd live2d && python3 -m http.server 8124` (so the model + module are reachable). In Discord: Ctrl+Shift+I → Console → `allow pasting` → paste `discord-probe-v5.js` → Enter. Confirm: the full Lotte renders as the background behind the translucent UI, gaze follows the cursor, auto-blink/breath, and the occasional smile. Cleanup: `__lotteSpikeStop()`. Capture a screenshot to `live2d/checkpoints/w5-discord.png`.

- [ ] **Step 4: Commit**

```bash
git add live2d/integrate/discord-probe-v5.js live2d/checkpoints/w5-discord.png
git commit -m "feat(live2d): W5 Cubism-4 Discord probe + real-client verify"
```

## Task W5.4: Final pass

- [ ] **Step 1:** Update `PIPELINE.md`: W5 = DONE, all W1–W5 complete, Phase 1 success criteria (spec §13) met. Note the remaining out-of-scope item: **Phase 2 production delivery** (turning the console probe into a persistent Vencord userplugin — needs a self-built dev Vencord; tracked as a Phase-2 cost in `experiments/live2d-spike/FINDINGS.md`).
- [ ] **Step 2:** Write `live2d/checkpoints/2026-..-phase1-complete/RESULT.md` summarizing the success criteria vs evidence (standalone render, Discord render, blink/breath/gaze/tilt/physics/smile, flat-rig preserved, master untouched).
- [ ] **Step 3: Commit** `git add live2d/PIPELINE.md live2d/checkpoints && git commit -m "docs(live2d): W1-W5 complete — Phase 1 success criteria met"`.
- [ ] **Step 4:** Use **superpowers:finishing-a-development-branch** to decide integration of the `live2d-spike` branch (it carries Phase 0 + Phase 1 + the pilot). `master` is the theme; the Live2D artifacts live under `live2d/` outside the build, so a merge is low-risk — but present the options to the user; do not merge unilaterally.

---

## Self-Review

- **Spec coverage:** §2 decisions seed `DECISIONS.md` (done in pilot) and constrain W4 (flat-rig, moc3, bg-out). §3 reactive behaviors → W4 (params) + W5 (auto-blink/breath/gaze + the §3.1 state machine, written complete in W5.1). §4 ~20-part layer map → W3.1 `DEPTH` + `full_segment.py` parts. §5 parameter set → W4.1 walkthrough table (verified IDs, with the `EyeL/R Smile` correction). §7 workstreams → W1–W5; the W2/W3/W4 iterative core is called out (W3.4 + W4 loop-back notes). §7 W2 drift discipline → `harvest_check.py` + per-reference reject gate. §7 W3 fallback ladder → contact-sheet review + the merge escape hatch (W3.2 Step 3). §8 repo layout → File Structure table. §12 checks → W1.1 (base confirm), W1.2 (upscaler availability), W3.4 (atlas), W4.3 (moc3 version assert). §13 success criteria → W5.4 RESULT.
- **Placeholder scan:** every script (`measure_base`, `upscale_base`, `harvest_check`, `full_segment`, `contact_sheet`, `build_psd_full`, `check_model`, `smile-state-machine`, `lotte.html`) is complete and runnable. The genuinely exploratory steps — segmentation box calibration (W3.2) and the rig posing (W4.2) — are explicit inspect-and-iterate / guided-GUI loops with complete starting code, concrete prompts/settings, and named fallbacks (rembg→fallback, neural→Lanczos, single→multi atlas, split→merge parts, moc3 v6→v5). The four W2 prompts are written out verbatim.
- **Type/name consistency:** layer names are identical across `full_segment.py`, `build_psd_full.py`'s `DEPTH`, and the W4 clipping/binding steps (`sclera_L/R`, `iris_L/R`, `upperlid_L/R`, `lowerlid_L/R`, `mouth_outer/inner`, `sidehair_L/R`, `backhair_L/R`, `bangs`, `ribbon`, `brow_L/R`, `body`, `scarf`, `neck`, `face_base`). The runtime triplet (official Core + PIXI 6.5.10 + `pixi-live2d-display@0.4.0/dist/cubism4.min.js`) and `model.focus(x,y)` are identical across `lotte.html` and `discord-probe-v5.js` and match the pilot. moc3 ≤ v5 is asserted in `check_model.py` and set in W4.1 Step 11 / W4.2. Param IDs match spec §5 + the pilot's verified table.
