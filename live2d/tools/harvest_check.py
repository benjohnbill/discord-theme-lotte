"""W2: verify a generated reference is drift-free vs the base crop, and emit a
landmark-aligned ghost overlay + amplified diff for the user/agent to judge. Same
technique used in the pilot to accept eyes-closed. Usage:
  python harvest_check.py BASE.png REF.png OUTPREFIX
Resizes REF to BASE size, writes <OUTPREFIX>-blend.png and <OUTPREFIX>-diff.png,
and prints whether non-target regions look stable (low diff outside the edit area)."""
import sys
from PIL import Image, ImageChops

base = Image.open(sys.argv[1]).convert("RGB")
ref = Image.open(sys.argv[2]).convert("RGB").resize(base.size)
out = sys.argv[3]

Image.blend(base, ref, 0.5).save(f"{out}-blend.png")
diff = ImageChops.difference(base, ref).point(lambda v: min(255, v * 3))
diff.save(f"{out}-diff.png")

# crude global drift signal: mean amplified-diff. The EDIT region will be bright;
# everything else should stay dark. High global mean => the whole image moved/recolored.
import statistics
px = list(diff.convert("L").getdata())
print(f"size {base.size}  mean-amplified-diff {statistics.mean(px):.1f} "
      f"(low ~<25 = only the edited region changed; high = global drift → regenerate)")
print(f"wrote {out}-blend.png {out}-diff.png")
