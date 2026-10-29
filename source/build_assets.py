"""Build the assets needed by the live site.

- favicon set (from a square crop of the Kenchic chicken badge)
- OpenGraph share image (1200x630, the menu fit into a wide canvas)
- web-ready menu jpg (compressed) + webp version
"""
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
src = Image.open(ROOT / "source" / "menu.jpg").convert("RGB")
W, H = src.size  # 1024 x 1536
ASSETS = ROOT / "assets"
ASSETS.mkdir(exist_ok=True)

# ---- 1. Optimised menu image for the page ----
src.save(ASSETS / "menu.jpg", quality=82, optimize=True, progressive=True)
src.save(ASSETS / "menu.webp", quality=82, method=6)

# ---- 2. Favicon set ----
# Crop a square containing just the navy circle badge (chicken). Center is ~ (885, 80),
# circle radius ~55 in source pixels. Pad a touch for breathing room.
cx, cy, r = 885, 80, 62
badge = src.crop((cx - r, cy - r, cx + r, cy + r))
bw, bh = badge.size
side = max(bw, bh)
square = Image.new("RGB", (side, side), (13, 46, 92))  # navy palette
square.paste(badge, ((side - bw) // 2, (side - bh) // 2))
square.resize((512, 512), Image.LANCZOS).save(ASSETS / "icon-512.png", optimize=True)
square.resize((192, 192), Image.LANCZOS).save(ASSETS / "icon-192.png", optimize=True)
square.resize((180, 180), Image.LANCZOS).save(ASSETS / "apple-touch-icon.png", optimize=True)
square.resize((32, 32), Image.LANCZOS).save(ASSETS / "favicon-32.png", optimize=True)
square.resize((16, 16), Image.LANCZOS).save(ASSETS / "favicon-16.png", optimize=True)

# ---- 3. OpenGraph 1200 x 630 share card ----
og = Image.new("RGB", (1200, 630), (255, 255, 255))
# Place the menu image centered, scaled to fit within 630px height while preserving aspect
scale = 630 / H
new_w = int(W * scale)
menu_for_og = src.resize((new_w, 630), Image.LANCZOS)
og.paste(menu_for_og, ((1200 - new_w) // 2, 0))
og.save(ASSETS / "og-image.jpg", quality=85, optimize=True, progressive=True)

print("Built:")
for f in sorted(ASSETS.iterdir()):
    size = f.stat().st_size
    print(f"  {f.name:24s} {size//1024} KB")
