"""W2 harvest (consolidates the per-reference inline snippets from the plan).

For each ACCEPTED reference in live2d/gen/refs/, produce a hidden-state PATCH and MASK in
live2d/gen/patches/. Geometry decision (deviates from the plan's literal small-crop code):
patches are FULL-CANVAS (base-sized) RGBA, because W3 full_segment.py consumes them
full-canvas — forehead/cheekjaw are alpha_composited onto the rembg matte to fill skin
under hair, and eyes-smile/closed-mouth are used as full-canvas layer() sources that get
re-cropped at base-relative fraction boxes. A small crop would land at the wrong origin /
out of bounds in W3. Full-canvas also matches the plan's "every layer full-canvas so they
stack in register" philosophy.

Each patch carries the (resized-to-base) reference pixels with alpha = a feathered band
mask: opaque only inside the target region, transparent elsewhere. The bands are generous
enough to contain the W3 layer boxes that crop these sources.

Refs are 1254^2 (GPT output); base is 2508^2 — resize ref to base before banding so the
patch is pixel-aligned to the master (alignment was verified at base size by harvest_check)."""
import pathlib
from PIL import Image, ImageFilter

BASE = "live2d/assets/lotte_base.png"
REFS = pathlib.Path("live2d/gen/refs")
OUT = pathlib.Path("live2d/gen/patches"); OUT.mkdir(parents=True, exist_ok=True)
FEATHER = 20  # GaussianBlur radius on the 2508^2 mask (~40px rim) — soft skin blends

W, H = Image.open(BASE).size

# name -> (ref filename, band as l,t,r,b fractions). Bands are STARTING POINTS — inspect
# the contact sheet (live2d/tools/contact_sheet.py over /tmp) and tweak if a band clips or
# includes the wrong feature.
BANDS = {
    "forehead":     ("forehead.png",     (0.28, 0.18, 0.72, 0.42)),  # revealed forehead skin band
    "cheekjaw":     ("cheekjaw.png",     (0.10, 0.45, 0.90, 0.85)),  # cheek + jawline band
    "eyes-smile":   ("eyes-smile.png",   (0.22, 0.50, 0.78, 0.82)),  # both eyes (covers W3 lid boxes)
    "closed-mouth": ("closed-mouth.png", (0.40, 0.76, 0.66, 0.98)),  # mouth + chin (covers W3 mouth box)
}

def band_mask(box):
    m = Image.new("L", (W, H), 0)
    l, t, r, b = box
    px = (int(W * l), int(H * t), int(W * r), int(H * b))
    Image.Image.paste(m, Image.new("L", (px[2] - px[0], px[3] - px[1]), 255), (px[0], px[1]))
    return m.filter(ImageFilter.GaussianBlur(FEATHER)), px

for name, (fn, box) in BANDS.items():
    ref = Image.open(REFS / fn).convert("RGBA").resize((W, H), Image.LANCZOS)
    mask, px = band_mask(box)
    patch = ref.copy()
    patch.putalpha(mask)  # opaque only inside the feathered band
    patch.save(OUT / f"{name}.png")
    mask.save(OUT / f"{name}_mask.png")
    print(f"{name}: band px={px}  patch+mask -> {OUT}/{name}.png")
print("done — full-canvas patches written")
