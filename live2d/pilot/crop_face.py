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
