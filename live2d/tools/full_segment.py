"""Phase C+D 통짜 (whole-image) re-cut: collapse the W3 22-layer face-box separation into a
patchwork-free part set. Replaces the brow/sclera/iris/lid/mouth box crops -- the source of the
rectangular seams seen at Discord scale (ADR-0001) -- with ONE feathered whole-character `base`
plus three feathered opacity-SWAP bands (blink / eye-smile / closed-mouth) and the moving
hair/ribbon physics locks. NO face-interior cuts -> no patchwork.

Part set (back -> front), 7 layers:
  base             통짜 whole character (open eyes + open mouth baked in); the front hair-locks +
                   ribbon are carved out (feathered) over a soft blurred UNDER-FILL backing, so a
                   physics sway reveals soft local colour, never a hole -- a flat source has no
                   under-drawing behind the hair/ribbon. Real cheek/jaw skin (the W2 cheekjaw patch)
                   is baked under the side-locks where the sway is largest.
  mouthband_closed feathered band over the mouth; opacity-swap to the closed-mouth ref (snap).
  eyeband_smile    feathered band over both eyes; opacity-swap to the eyes-smile ref (^^).
  eyeband_closed   feathered band over both eyes; opacity-swap to the closed-eye art (blink).
  hair_L / hair_R  front side-locks, physics; feathered column edges.
  ribbon           hair ribbon, physics; feathered box edge.

All expression is a baked-art opacity frame-swap (ROI.md feasibility decided 2026-06-02: blink /
eye-smile ^^ / closed-mouth-SNAP are cheap on a flat source; smooth/talking mouth is INFEASIBLE
-> speech-bubble). Every band + carve edge is feathered (soft alpha falloff) -- this IS the
deferred W5(c) seam-fix: a soft rim has no rectangular outline to read.

Band coords calibrated 2026-06-02 from a 2508^2 grid read (/tmp/calib_face.png), NOT lore:
  eyeband   x0.27-0.72  y0.36-0.56   (both open eyes + brows; stops above the nose)
  mouthband x0.42-0.60  y0.575-0.68  (open smile mouth; below the eyeband)
The 0.56 -> 0.575 gap between the eyeband bottom and the mouthband top keeps the two opacity-swaps
from ever co-painting the same pixels.

Open implementation choice resolved (AGENT call, per the 통짜 handoff): a SINGLE `base`, no
head/body PSD split. Head-tilt + body-lean are whole-image WARP deformers placed over regions of
the one base in Cubism at re-rig time -- a PSD neckline cut would only ADD a horizontal seam, the
exact artefact this re-cut removes.

Run: live2d/pilot/.venv/bin/python live2d/tools/full_segment.py  then  ... build_psd_full.py
(layers/ + lotte.psd are gitignored + regenerable; the committed artefact is this script.)
"""
import sys
import pathlib
from PIL import Image, ImageChops, ImageFilter

BASE = "live2d/assets/lotte_base.png"
PATCH = pathlib.Path("live2d/gen/patches")
REFS = pathlib.Path("live2d/gen/refs")
PILOT_CLOSED = "live2d/pilot/gen/eyes-closed.png"
OUT = pathlib.Path("live2d/layers"); OUT.mkdir(parents=True, exist_ok=True)

FEATHER = 30          # GaussianBlur radius on the 2508^2 masks (~60px soft rim) -> no hard edges
UNDERFILL_BLUR = 60   # soft backing so a sway reveal shows blurred local colour, not a hole

try:
    from rembg import remove, new_session
    # isnet-anime: anime-specialised matte. The default u2net keeps the circular bokeh/halo/clover
    # background as foreground; isnet-anime cuts the GIRL clean (the bg is a separate scene plate).
    REMBG_SESSION = new_session("isnet-anime")
    HAVE_REMBG = True
except Exception as e:
    HAVE_REMBG = False
    REMBG_SESSION = None
    print("rembg NOT available:", e, file=sys.stderr)

img = Image.open(BASE).convert("RGBA")
W, H = img.size
matte = remove(img, session=REMBG_SESSION) if HAVE_REMBG else img   # character silhouette/alpha
matte = matte.convert("RGBA")
matte_a = matte.getchannel("A")


def box(l, t, r, b):
    return (int(W * l), int(H * t), int(W * r), int(H * b))


def feather_rect(l, t, r, b):
    """Opaque inside the box, GaussianBlur soft falloff on every edge (kills the rectangle)."""
    m = Image.new("L", (W, H), 0)
    m.paste(255, box(l, t, r, b))
    return m.filter(ImageFilter.GaussianBlur(FEATHER))


def feather_col(l, r, ytop=0.0, ybot=0.72):
    """Feathered column mask for a front hair side-lock. Bounded above the body line (~0.72) so the
    carve never touches the shoulders; the lock's lower tip stays static in base (small-amplitude
    physics, liveness from lag not amplitude)."""
    m = Image.new("L", (W, H), 0)
    m.paste(255, box(l, ytop, r, ybot))
    return m.filter(ImageFilter.GaussianBlur(FEATHER))


def with_alpha(src, a):
    c = src.copy(); c.putalpha(a); return c


# --- region masks (each intersected with the character matte) ---
RIBBON = (0.67, 0.15, 0.90, 0.37)
hair_mask_L = ImageChops.multiply(matte_a, feather_col(0.00, 0.27))
hair_mask_R = ImageChops.multiply(matte_a, feather_col(0.73, 1.00))
ribbon_mask = ImageChops.multiply(matte_a, feather_rect(*RIBBON))
hair_mask_R = ImageChops.subtract(hair_mask_R, ribbon_mask)   # ribbon owns its box
move_mask = ImageChops.lighter(ImageChops.lighter(hair_mask_L, hair_mask_R), ribbon_mask)

# --- moving physics layers (the only sharp copies of the front locks + ribbon) ---
with_alpha(matte, hair_mask_L).save(OUT / "hair_L.png"); print("wrote hair_L (column 0.00-0.27)")
with_alpha(matte, hair_mask_R).save(OUT / "hair_R.png"); print("wrote hair_R (column 0.73-1.00, ribbon carved)")
with_alpha(matte, ribbon_mask).save(OUT / "ribbon.png"); print("wrote ribbon", RIBBON)

# --- base (통짜): soft under-fill backing + real cheek skin + sharp character MINUS the moving locks ---
# 1) under-fill: a heavily blurred copy of the matte, bounded to the silhouette. Hidden entirely at
#    rest; only a hair/ribbon sway reveals it, as soft local colour instead of a transparent hole.
underfill = matte.filter(ImageFilter.GaussianBlur(UNDERFILL_BLUR))
underfill.putalpha(matte_a)
base = underfill.copy()
# 2) real cheek/jaw skin under the side-locks (the W2 cheekjaw patch band is correct as harvested).
fp = PATCH / "cheekjaw.png"
if fp.exists():
    base.alpha_composite(Image.open(fp).convert("RGBA"))
# 3) the sharp character everywhere EXCEPT the moving-lock regions (so no doubling on sway).
sharp_static = with_alpha(matte, ImageChops.multiply(matte_a, ImageChops.invert(move_mask)))
base.alpha_composite(sharp_static)
base.putalpha(ImageChops.multiply(base.getchannel("A"), matte_a))   # stay inside the silhouette
base.save(OUT / "base.png"); print("wrote base (통짜 whole character, hair/ribbon carved + under-filled)")

# --- opacity-swap bands: baked alt-expression art, feathered, masked to the silhouette ---
# closed-eye source is base-ALIGNED: pilot crop box (0.18,0.05,0.82,0.60) of the original; base =
# original x2, so the same fractions map straight onto the 2508^2 canvas.
cl, ct, cr, cb = box(0.18, 0.05, 0.82, 0.60)
closed = Image.new("RGBA", (W, H), (0, 0, 0, 0))
closed.paste(Image.open(PILOT_CLOSED).convert("RGBA").resize((cr - cl, cb - ct)), (cl, ct))


def ref(name):
    p = REFS / name
    return Image.open(p).convert("RGBA").resize((W, H), Image.LANCZOS) if p.exists() else img


EYEBAND = (0.27, 0.36, 0.72, 0.56)
MOUTHBAND = (0.42, 0.575, 0.60, 0.68)


def band(name, src, frac_box):
    a = ImageChops.multiply(feather_rect(*frac_box), matte_a)
    with_alpha(src, a).save(OUT / f"{name}.png")
    print("wrote", name, frac_box)


band("eyeband_closed", closed, EYEBAND)
band("eyeband_smile", ref("eyes-smile.png"), EYEBAND)
band("mouthband_closed", ref("closed-mouth.png"), MOUTHBAND)

print("done —", len(list(OUT.glob("*.png"))), "layers:", sorted(p.stem for p in OUT.glob("*.png")))
