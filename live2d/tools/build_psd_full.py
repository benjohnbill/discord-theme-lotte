"""W3: assemble live2d/layers/*.png into live2d/lotte.psd (psd-tools), depth-ordered back->front
per spec §4. Each layer is full-canvas (2508^2) so they import in register. Cubism's documented
import path is a layered PSD; loose PNGs are not. Mirrors the pilot's build_psd.py (PixelLayer.frompil).

Part set reflects the W3.2 USER decisions (2026-05-31): bangs merged into face_base; hair merged to one
mass per side (hair_L / hair_R, front side locks). 19 layers."""
import pathlib
from PIL import Image
from psd_tools import PSDImage
from psd_tools.api.layers import PixelLayer

LAYERS = pathlib.Path("live2d/layers")
OUT = "live2d/lotte.psd"
# back -> front (spec §4). Names must match files in live2d/layers/.
DEPTH = [
    "body", "scarf", "neck", "face_base",
    "brow_L", "brow_R",
    "sclera_L", "iris_L", "sclera_R", "iris_R",
    "upperlid_L", "upperlid_R", "lowerlid_L", "lowerlid_R",
    "mouth_inner", "mouth_outer",
    "hair_L", "hair_R", "ribbon",
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
print("wrote", OUT, "size", chk.size, "layers(bottom->top):", [l.name for l in chk])
chk.composite().convert("RGB").save("live2d/lotte-preview.png")
print("preview -> live2d/lotte-preview.png")
