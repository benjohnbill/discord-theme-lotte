"""Assemble the 6 full-canvas aligned layers into one layered PSD for Cubism import.
Cubism's documented import path is a layered PSD (RGB, 8 bit/channel); loose PNGs are
not a documented import format. Each layer is full-canvas 803x690 so they import in
register. Depth order (back->front) follows the spec §4 layer map for this slice.

Uses psd-tools (PixelLayer.frompil) which writes a valid layered PSD with a correct
merged preview. (pytoshop's RLE/packbits extension is unbuilt on this Python and its
raw-mode merged image came out black.)"""
import pathlib
from PIL import Image
from psd_tools import PSDImage
from psd_tools.api.layers import PixelLayer

LAYERS_DIR = pathlib.Path("live2d/pilot/layers")
OUT = "live2d/pilot/lotte-pilot.psd"

# back -> front. Appended in this order so face_base is at the bottom of the stack.
DEPTH_BACK_TO_FRONT = ["face_base", "hair_side", "eye_sclera", "eye_iris", "eye_upperlid", "mouth"]

psd = PSDImage.new(mode="RGBA", size=(803, 690))
for name in DEPTH_BACK_TO_FRONT:
    pil = Image.open(LAYERS_DIR / f"{name}.png").convert("RGBA")
    layer = PixelLayer.frompil(pil, psd, name, top=0, left=0)
    psd.append(layer)

psd.save(OUT)

# self-check: reopen, list layers, flatten preview
chk = PSDImage.open(OUT)
print("wrote", OUT, "size", chk.size, "layers(bottom->top):", [l.name for l in chk])
chk.composite().convert("RGB").save("live2d/pilot/lotte-pilot-preview.png")
print("preview -> live2d/pilot/lotte-pilot-preview.png")
