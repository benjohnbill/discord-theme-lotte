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
    # Full-canvas ALIGNED layer (Live2D layer format): the part sits at its true
    # position on a transparent 803x690 canvas, so all layers stack into register
    # on import. (box() returns pixel coords, so paste at its top-left.)
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    region = source.crop(frac_box)
    canvas.paste(region, (frac_box[0], frac_box[1]))
    canvas.save(OUT / f"{name}.png")
    print("wrote", name, "contentbox", frac_box, "-> canvas", canvas.size)

# Whole-character matte (silhouette alpha) as the face_base source.
if HAVE_REMBG:
    matted = remove(img)              # RGBA with background removed
else:
    matted = img
matted.save(OUT / "face_base.png")

# Sub-part boxes (fractions of the crop). Calibrated from a 10%-grid read of THIS
# crop: eyes sit at v~0.53–0.74 / h~0.25–0.73; mouth at v~0.80–0.92 / h~0.42–0.62.
cut("eye_sclera",   box(0.23, 0.53, 0.74, 0.80))   # both-eyes band (split L/R later)
cut("eye_iris",     box(0.26, 0.56, 0.71, 0.78))
cut("mouth",        box(0.52, 0.87, 0.74, 1.00))   # head-tilt puts the smile right-of-center, near the bottom edge
cut("hair_side",    box(0.03, 0.18, 0.28, 0.96))
# upper eyelid art comes from the eyes-closed reference, same band as the eyes:
closed = Image.open(CLOSED).convert("RGBA").resize((W, H))
cut("eye_upperlid", box(0.23, 0.53, 0.74, 0.80), source=closed)
print("done")
