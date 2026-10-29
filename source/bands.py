"""Slice the source into horizontal bands so we can map vertical Y ranges."""
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
src = Image.open(ROOT / "source" / "menu.jpg")
W, H = src.size
out = ROOT / "source" / "bands"
out.mkdir(exist_ok=True)

BAND = 200  # px tall per strip
for i, y in enumerate(range(0, H, BAND)):
    src.crop((0, y, W, min(y + BAND, H))).save(out / f"band-{i:02d}-y{y}.png", optimize=True)
    print(f"band-{i:02d}: y={y}..{min(y+BAND, H)}")
