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
