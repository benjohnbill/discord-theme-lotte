"""W3: separate live2d/assets/lotte_base.png into ~22 full-canvas aligned PNG layers (spec §4).

Extends the pilot's segment.py. Corrections vs the plan's literal starting script, applied per the
PIPELINE.md "W3 prep findings" plus W3 empirical calibration (see /tmp/face_zoom.png grid read):

  (1) Boxes are recalibrated against the FULL 2508^2 base via a 10%-grid read. The plan's fraction
      boxes were pilot-CROP coordinates (face crop = (0.18,0.05,0.82,0.60) of the 1254^2 original).
      The base has a real HEAD TILT, so the L (viewer-left / character's-right, LOWER) and
      R (viewer-right, HIGHER) eyes/brows/lids sit at different heights.
  (2) The eyes-closed blink source is base-ALIGNED, not stretched: the pilot art is 803x690 aligned to
      the face crop, so it is re-placed onto the 2508^2 canvas at the crop box (no full-canvas stretch).
  (3) The mouth + lower-lid sources are the full-opaque base-aligned REFS (live2d/gen/refs/*), NOT the
      W2 patches: the patches' feathered bands were miscalibrated BELOW the mouth (closed-mouth band
      v0.76-0.98 vs the true mouth v0.62-0.69), so a box crop of the patch returns transparency.
      The refs are full-opaque + base-aligned (harvest_check verified), so a box crop yields real pixels.
      This is the sanctioned W2<->W3 iterative core (PROMPTS.md / spec §7).
  (4) Every layer is intersected with the rembg character matte so no part carries bokeh background.

face_base = rembg matte + the forehead/cheekjaw patches (their bands ARE correct) so deformation under
bangs/side-hair reveals skin, not holes. Every layer is full-canvas so they stack in register on import.
"""
import sys, pathlib
from PIL import Image, ImageChops

BASE = "live2d/assets/lotte_base.png"
PATCH = pathlib.Path("live2d/gen/patches")
REFS = pathlib.Path("live2d/gen/refs")
PILOT_CLOSED = "live2d/pilot/gen/eyes-closed.png"
OUT = pathlib.Path("live2d/layers"); OUT.mkdir(parents=True, exist_ok=True)

try:
    from rembg import remove, new_session
    # isnet-anime: anime-specialized matte. The default u2net keeps the circular bokeh/halo/clover
    # background as foreground; isnet-anime cuts the GIRL clean (bg is a separate ambient layer, spec §4).
    REMBG_SESSION = new_session("isnet-anime")
    HAVE_REMBG = True
except Exception as e:
    HAVE_REMBG = False
    REMBG_SESSION = None
    print("rembg NOT available:", e, file=sys.stderr)

img = Image.open(BASE).convert("RGBA")
W, H = img.size
matte = remove(img, session=REMBG_SESSION) if HAVE_REMBG else img   # character silhouette/alpha
matte_a = matte.getchannel("A")

# --- (2) base-aligned closed-eye source: pilot face-crop = (0.18,0.05,0.82,0.60) of the original;
#         base = original x2, so the same fractions map directly onto the 2508^2 canvas. ---
cl, ct, cr, cb = int(W * 0.18), int(H * 0.05), int(W * 0.82), int(H * 0.60)
closed = Image.new("RGBA", (W, H), (0, 0, 0, 0))
closed.paste(Image.open(PILOT_CLOSED).convert("RGBA").resize((cr - cl, cb - ct)), (cl, ct))

# --- (3) full-opaque base-aligned refs for mouth + lower-lid sources ---
def ref_src(name, fallback=img):
    p = REFS / name
    return Image.open(p).convert("RGBA").resize((W, H), Image.LANCZOS) if p.exists() else fallback
mouth_src = ref_src("closed-mouth.png")
smile_src = ref_src("eyes-smile.png")

def box(l, t, r, b):
    return (int(W * l), int(H * t), int(W * r), int(H * b))

def layer(name, frac_box, source=img, mask_to_matte=True):
    """Full-canvas aligned layer: crop `source` at the box, place at the box origin.
    Intersect with the character matte unless the part is not in the matte silhouette."""
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    canvas.paste(source.crop(frac_box), (frac_box[0], frac_box[1]))
    if mask_to_matte:
        canvas.putalpha(ImageChops.multiply(canvas.getchannel("A"), matte_a))
    canvas.save(OUT / f"{name}.png")
    print("wrote", name, frac_box)

# --- face_base = matte + the cheekjaw skin patch only ---
# The cheekjaw patch fills cheek/jaw skin UNDER the side hair (hair_L/hair_R sway away to reveal it).
# The forehead patch is intentionally NOT applied: per the W3.2 user decision the bangs are baked into
# face_base (fixed, not a separate moving layer), so the forehead must show the BANGS, not bare skin —
# compositing the forehead patch would erase the visible fringe.
face = matte.copy()
fp = PATCH / "cheekjaw.png"
if fp.exists():
    face.alpha_composite(Image.open(fp).convert("RGBA"))
face.save(OUT / "face_base.png"); print("wrote face_base")

# --- (1) calibrated fraction boxes (base coords). L = canvas-left (viewer-left, LOWER due to tilt). ---
# Face-interior + body parts cropped straight from the base.
# W3.2 USER decisions (2026-05-31): (a) BANGS merged into face_base — no separate bangs layer;
# (b) hair MERGED to one mass per side — back hair is baked into face_base (static), only the front
# side locks sway as hair_L / hair_R (below). Color-based hair/skin separation is unreliable here
# (skin ~RGB(170,130,128) vs bangs ~RGB(163,118,123) overlap), per spec §7 — so this uses spatial
# columns + the merge escape hatch rather than a hair matte.
RIBBON = box(0.67, 0.15, 0.90, 0.37)
BOXES = {
    "body":        box(0.08, 0.73, 0.94, 1.00),   # uniform shoulders/chest (breath/lean)
    "scarf":       box(0.38, 0.79, 0.64, 0.97),   # sailor neckerchief
    "neck":        box(0.41, 0.68, 0.61, 0.79),
    "brow_L":      box(0.27, 0.37, 0.47, 0.46),
    "brow_R":      box(0.52, 0.31, 0.72, 0.41),
    "sclera_L":    box(0.29, 0.46, 0.47, 0.61),
    "iris_L":      box(0.32, 0.49, 0.44, 0.60),
    "sclera_R":    box(0.53, 0.39, 0.70, 0.54),
    "iris_R":      box(0.56, 0.42, 0.68, 0.53),
    "mouth_inner": box(0.45, 0.62, 0.58, 0.70),   # open-mouth interior from the base
    "ribbon":      RIBBON,
}
for name, bx in BOXES.items():
    layer(name, bx)

# --- hair: front side locks, one mass per side. Cut to the OUTER columns so they clear the eyes and
# the central face (h<0.27 / h>0.73); the ribbon is carved out of hair_R so it stays its own layer. ---
def col_layer(name, l, r, carve=None):
    colmask = Image.new("L", (W, H), 0)
    colmask.paste(255, (int(W * l), 0, int(W * r), H))
    a = ImageChops.multiply(matte_a, colmask)
    if carve is not None:
        cut = Image.new("L", (W, H), 255); cut.paste(0, carve)
        a = ImageChops.multiply(a, cut)
    canvas = matte.copy(); canvas.putalpha(a)
    canvas.save(OUT / f"{name}.png"); print("wrote", name, "(column %.2f-%.2f)" % (l, r))
col_layer("hair_L", 0.00, 0.27)
col_layer("hair_R", 0.73, 1.00, carve=RIBBON)

# blink upper lids from the base-aligned closed-eye art (split L/R):
layer("upperlid_L", box(0.29, 0.45, 0.47, 0.61), source=closed)
layer("upperlid_R", box(0.53, 0.38, 0.70, 0.54), source=closed)
# eye-smile lower lids from the eyes-smile ref:
layer("lowerlid_L", box(0.29, 0.55, 0.47, 0.63), source=smile_src)
layer("lowerlid_R", box(0.53, 0.48, 0.70, 0.56), source=smile_src)
# closed-mouth outer keyform from the closed-mouth ref:
layer("mouth_outer", box(0.42, 0.60, 0.60, 0.71), source=mouth_src)

print("done —", len(list(OUT.glob("*.png"))), "layers")
