"""W3: composite every live2d/layers/*.png over magenta into one labeled sheet so alpha cutouts
are visible (generalizes the pilot's inspector). Run after each full_segment.py tweak."""
import glob
from PIL import Image, ImageDraw

MAG = (255, 0, 255, 255); TH = 230; COLS = 6; GAP = 6
cells = []
for p in sorted(glob.glob("live2d/layers/*.png")):
    im = Image.open(p).convert("RGBA")
    comp = Image.alpha_composite(Image.new("RGBA", im.size, MAG), im)
    w = max(1, int(comp.width * TH / comp.height)); comp = comp.resize((w, TH))
    lab = Image.new("RGBA", (comp.width, 20), (0, 0, 0, 255))
    ImageDraw.Draw(lab).text((3, 4), p.split("/")[-1], fill=(255, 255, 0, 255))
    cell = Image.new("RGBA", (comp.width, TH + 20), (40, 40, 40, 255))
    cell.paste(lab, (0, 0)); cell.paste(comp, (0, 20)); cells.append(cell)

rows = [cells[i:i + COLS] for i in range(0, len(cells), COLS)]
cw = max(c.width for c in cells); ch = TH + 20
W = COLS * (cw + GAP) + GAP; H = len(rows) * (ch + GAP) + GAP
sheet = Image.new("RGBA", (W, H), (20, 20, 20, 255))
for r, row in enumerate(rows):
    x = GAP
    for c in row:
        sheet.paste(c, (x, GAP + r * (ch + GAP))); x += cw + GAP
sheet.convert("RGB").save("/tmp/layers_contact.png")
print("wrote /tmp/layers_contact.png", sheet.size, "—", len(cells), "layers")
