"""Slice product photos out of the source menu image.

Coordinates are in source pixels (1024 x 1536). Adjust the dicts below if a
crop is off. Re-run: python3 source/slice.py
"""
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
src = Image.open(ROOT / "source" / "menu.jpg")
W, H = src.size  # 1024 x 1536
out_dir = ROOT / "assets"
out_dir.mkdir(exist_ok=True)

# Each crop: (left, top, right, bottom) in pixels of the 1024x1536 source.
crops = {
    "logo.png":           (760,   10,  1020,  195),
    "burger.png":         (610,  280,   970,  580),
    "chicken.png":        ( 55,  620,   500,  850),
    "nuggets.png":        ( 80,  790,   500, 1010),
    "chips-medium.png":   (525,  760,   770,  930),
    "chips-large.png":    (770,  760,  1015,  945),
    "drinks.png":         (  0, 1180,   490, 1420),
    "combo-snacks.png":   (795, 1000,  1015, 1140),
    "combo-homeland.png": (795, 1135,  1015, 1295),
    "combo-muthamaki.png":(795, 1305,  1015, 1465),
    # OpenGraph share image: top masthead band (title + logo)
    "og-cover.png":       (  0,    0,  1024,  205),
}

for name, box in crops.items():
    src.crop(box).save(out_dir / name, optimize=True)
    print(f"  {name:24s} {box}")

# Favicon: square crop of just the round Kenchic chicken badge (top of logo)
fav = src.crop((805, 10, 985, 145)).resize((512, 512), Image.LANCZOS)
fav.save(out_dir / "icon-512.png", optimize=True)
fav.resize((192, 192), Image.LANCZOS).save(out_dir / "icon-192.png", optimize=True)
fav.resize((180, 180), Image.LANCZOS).save(out_dir / "apple-touch-icon.png", optimize=True)
fav.resize((32, 32), Image.LANCZOS).save(out_dir / "favicon-32.png", optimize=True)
fav.resize((16, 16), Image.LANCZOS).save(out_dir / "favicon-16.png", optimize=True)
print("favicon set generated")
