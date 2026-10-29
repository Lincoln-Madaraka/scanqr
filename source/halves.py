"""Split the gridded image into top half and bottom half (each 1024 x 768)."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
src = Image.open(ROOT / "source" / "menu.jpg").convert("RGB")
W, H = src.size
draw = ImageDraw.Draw(src)
font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 26)

STEP = 50
for x in range(0, W + 1, STEP):
    c = (255, 0, 255) if x % 100 == 0 else (255, 210, 255)
    draw.line([(x, 0), (x, H)], fill=c, width=1)
    if x % 100 == 0:
        draw.text((x + 3, 3), str(x), fill=(180, 0, 180), font=font)
        draw.text((x + 3, H // 2 + 3), str(x), fill=(180, 0, 180), font=font)
for y in range(0, H + 1, STEP):
    c = (0, 200, 0) if y % 100 == 0 else (180, 240, 180)
    draw.line([(0, y), (W, y)], fill=c, width=1)
    if y % 100 == 0:
        draw.text((3, y + 3), str(y), fill=(0, 130, 0), font=font)

src.crop((0, 0, W, H // 2)).save(ROOT / "source" / "h-top.png")
src.crop((0, H // 2, W, H)).save(ROOT / "source" / "h-bot.png")
print("h-top and h-bot saved")
