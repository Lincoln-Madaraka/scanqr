"""Auto-detect the navy circle's bounding box in the top-right of the menu."""
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
src = Image.open(ROOT / "source" / "menu.jpg").convert("RGB")
W, H = src.size
# Search region: top-right quadrant only
region = src.crop((600, 0, W, 250))
rw, rh = region.size
px = region.load()

# A pixel is "navy" if it's dark blue
def is_navy(r, g, b):
    return r < 50 and g < 70 and b > 60 and b < 130

min_x, min_y, max_x, max_y = rw, rh, 0, 0
for y in range(rh):
    for x in range(rw):
        r, g, b = px[x, y]
        if is_navy(r, g, b):
            if x < min_x: min_x = x
            if y < min_y: min_y = y
            if x > max_x: max_x = x
            if y > max_y: max_y = y

# Translate back to source coords
abs_min_x = min_x + 600
abs_min_y = min_y
abs_max_x = max_x + 600
abs_max_y = max_y
print(f"Navy bounding box in source: ({abs_min_x}, {abs_min_y}) -> ({abs_max_x}, {abs_max_y})")
print(f"Width:  {abs_max_x - abs_min_x}, Height: {abs_max_y - abs_min_y}")
