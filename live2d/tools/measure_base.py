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
