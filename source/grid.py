"""Overlay a coordinate grid on the source image so positions are readable."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
src = Image.open(ROOT / "source" / "menu.jpg").convert("RGB")
W, H = src.size
draw = ImageDraw.Draw(src)
try:
    font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 22)
except OSError:
    font = ImageFont.load_default()

STEP = 50
for x in range(0, W, STEP):
    color = (255, 0, 255) if x % 100 == 0 else (255, 180, 255)
    draw.line([(x, 0), (x, H)], fill=color, width=1)
    if x % 100 == 0:
        draw.text((x + 2, 2), str(x), fill=(255, 0, 255), font=font)
for y in range(0, H, STEP):
    color = (0, 200, 0) if y % 100 == 0 else (180, 230, 180)
    draw.line([(0, y), (W, y)], fill=color, width=1)
    if y % 100 == 0:
        draw.text((2, y + 2), str(y), fill=(0, 130, 0), font=font)

# Save halved so it fits in one Read view
src.resize((W // 2, H // 2), Image.LANCZOS).save(ROOT / "source" / "menu-grid.png")
print(f"grid saved (orig {W}x{H}, preview {W//2}x{H//2})")
