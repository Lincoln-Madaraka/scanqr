"""Split the gridded image into 4 quadrants for readable Read views."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
src = Image.open(ROOT / "source" / "menu.jpg").convert("RGB")
W, H = src.size
draw = ImageDraw.Draw(src)
try:
    font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 28)
except OSError:
    font = ImageFont.load_default()

STEP = 50
for x in range(0, W + 1, STEP):
    color = (255, 0, 255) if x % 100 == 0 else (255, 200, 255)
    draw.line([(x, 0), (x, H)], fill=color, width=1)
    if x % 100 == 0:
        draw.text((x + 3, 3), str(x), fill=(180, 0, 180), font=font)
for y in range(0, H + 1, STEP):
    color = (0, 200, 0) if y % 100 == 0 else (180, 240, 180)
    draw.line([(0, y), (W, y)], fill=color, width=1)
    if y % 100 == 0:
        draw.text((3, y + 3), str(y), fill=(0, 130, 0), font=font)

# Save each quadrant at full resolution (~512 x ~768)
mid_x, mid_y = W // 2, H // 2
quads = {
    "q-TL.png": (0, 0, mid_x, mid_y),
    "q-TR.png": (mid_x, 0, W, mid_y),
    "q-BL.png": (0, mid_y, mid_x, H),
    "q-BR.png": (mid_x, mid_y, W, H),
}
for name, box in quads.items():
    src.crop(box).save(ROOT / "source" / name)
    print(f"  {name} {box}")
