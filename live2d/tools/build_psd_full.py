"""W3/Phase C+D: assemble live2d/layers/*.png into live2d/lotte.psd (psd-tools), depth-ordered
back->front. Each layer is full-canvas (2508^2) so they import in register. Cubism's documented
import path is a layered PSD; loose PNGs are not. Mirrors the pilot's build_psd.py (PixelLayer.frompil).

Part set = the 통짜 (whole-image) re-cut (ADR-0001, 2026-06-02): one feathered `base` (open eyes +
open mouth baked in) + three feathered opacity-SWAP bands + the moving hair/ribbon physics locks.
NO face-interior cuts -> no patchwork. See full_segment.py for how each layer is built. 7 layers.

Draw order rationale: bands sit OVER the base (they swap over the open eyes/mouth) but UNDER the
hair locks (hair frames the face over the outer eye corner); eyeband_closed is above eyeband_smile
so a blink wins visually if both ever open (param priority: blink overrides smile)."""
import pathlib
from PIL import Image
from psd_tools import PSDImage
from psd_tools.api.layers import PixelLayer

LAYERS = pathlib.Path("live2d/layers")
OUT = "live2d/lotte.psd"
# back -> front. Names must match files in live2d/layers/ (full_segment.py output).
DEPTH = [
    "base",
    "mouthband_closed",
    "eyeband_smile", "eyeband_closed",
    "hair_L", "hair_R", "ribbon",
]
size = Image.open(LAYERS / "base.png").size
psd = PSDImage.new(mode="RGBA", size=size)
for name in DEPTH:
    f = LAYERS / f"{name}.png"
    if not f.exists():
        print("skip missing", name); continue
    psd.append(PixelLayer.frompil(Image.open(f).convert("RGBA"), psd, name, top=0, left=0))
psd.save(OUT)

chk = PSDImage.open(OUT)
print("wrote", OUT, "size", chk.size, "layers(bottom->top):", [l.name for l in chk])
chk.composite().convert("RGB").save("live2d/lotte-preview.png")
print("preview -> live2d/lotte-preview.png")
