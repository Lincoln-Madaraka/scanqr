"""Build the Kenchic Myth or Fact page art from the board mockup.

Everything is cut straight from source/myth-or-fact-board.jpg (1600 x 1282) so the
branding stays exactly as designed:

- header.webp   the top band of the board: pattern + Kenchic logo + MYTH OR FACT title
                (the "pick a card and stick it..." line is painted out — the page sets
                its own instruction in HTML)
- pattern.webp  the same band with logo/title painted out, stacked with a mirrored copy
                so it tiles seamlessly below the header
- myth-label.png / fact-label.png
                the card wordmarks as alpha masks (the page colours them with CSS, so
                they still work when a card turns green or red)
- og-image.jpg  share preview

Run: python3 source/build_myth_or_fact.py
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
src = np.asarray(Image.open(ROOT / "source" / "myth-or-fact-board.jpg").convert("RGB")).astype(np.float32)
OUT = ROOT / "assets" / "myth-or-fact"
OUT.mkdir(parents=True, exist_ok=True)

NAVY = np.array([29, 46, 92], np.float32)   # the two pattern colours, sampled
BLUE = np.array([25, 69, 134], np.float32)
RED = np.array([223, 54, 51], np.float32)   # card red
WHITE = np.array([255, 255, 255], np.float32)

# Band = rows 4..549: below the white frame line at the very top, above the cards (row 551).
Y0, Y1 = 4, 550
band = src[Y0:Y1]
H, W = band.shape[:2]

# Bounding boxes in source pixels (x0, y0, x1, y1), measured off the mockup.
LOGO = (683, 12, 903, 225)
TITLE = (386, 244, 1199, 337)
INSTR = (320, 422, 1267, 455)


def box(b, pad=0):
    x0, y0, x1, y1 = b
    return slice(max(y0 - Y0 - pad, 0), y1 - Y0 + pad + 1), slice(x0 - pad, x1 + pad + 1)


def dilate(m, r):
    p = np.pad(m, r)
    out = m.copy()
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            if dx * dx + dy * dy <= r * r:
                out |= p[r + dy:r + dy + m.shape[0], r + dx:r + dx + m.shape[1]]
    return out


def fill_holes(m):
    """Mark everything not reachable from the border as foreground (PIL flood fill)."""
    img = Image.fromarray(np.pad(m, 1).astype(np.uint8) * 255)
    ImageDraw.floodfill(img, (0, 0), 128)
    return (np.asarray(img) != 128)[1:-1, 1:-1]


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def blur(a, radius):
    from PIL import ImageFilter
    img = Image.fromarray(np.clip(a * 255, 0, 255).astype(np.uint8))
    return np.asarray(img.filter(ImageFilter.GaussianBlur(radius))).astype(np.float32) / 255


# ---- content masks ----
dist_bg = np.minimum(np.linalg.norm(band - NAVY, axis=2), np.linalg.norm(band - BLUE, axis=2))
content = dist_bg > 40

logo = np.zeros_like(content)
sl = box(LOGO, 2)
logo[sl] = fill_holes(content[sl])  # the badge's blue disc sits close to the pattern blue
title = np.zeros_like(content)
sl = box(TITLE, 3)
title[sl] = content[sl]
instr = np.zeros_like(content)
sl = box(INSTR, 4)
instr[sl] = content[sl]

# ---- pattern as a single 0..1 value (0 = navy, 1 = blue) ----
axis = BLUE - NAVY
t = np.clip(((band - NAVY) @ axis) / (axis @ axis), 0, 1)


def inpaint(values, hole, levels=7, iters=60):
    """Multi-scale diffusion fill of `values` inside `hole`."""
    v = np.where(hole, 0, values)
    w = (~hole).astype(np.float32)
    if levels == 0 or min(v.shape) < 8:
        mean = (v * w).sum() / max(w.sum(), 1)
        return np.where(hole, mean, values)
    h2, w2 = v.shape[0] // 2 * 2, v.shape[1] // 2 * 2
    vs = (v * w)[:h2, :w2].reshape(h2 // 2, 2, w2 // 2, 2).sum((1, 3))
    ws = w[:h2, :w2].reshape(h2 // 2, 2, w2 // 2, 2).sum((1, 3))
    coarse_hole = ws == 0
    coarse = inpaint(np.where(coarse_hole, 0, vs / np.maximum(ws, 1e-6)), coarse_hole, levels - 1, iters)
    up = np.repeat(np.repeat(coarse, 2, 0), 2, 1)
    up = np.pad(up, ((0, v.shape[0] - h2), (0, v.shape[1] - w2)), mode="edge")
    out = np.where(hole, up, values)
    for _ in range(iters):
        p = np.pad(out, 1, mode="edge")
        avg = (p[:-2, 1:-1] + p[2:, 1:-1] + p[1:-1, :-2] + p[1:-1, 2:]) / 4
        out = np.where(hole, avg, values)
    return out


def render(tv):
    """Re-draw the pattern crisply: two flat colours with a 1px anti-aliased edge."""
    a = blur((tv > 0.5).astype(np.float32), 0.6)[..., None]
    return NAVY * (1 - a) + BLUE * a


def save_webp(arr, name, **kw):
    Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).save(OUT / name, "WEBP", method=6, **kw)


# ---- header.webp: clean pattern, original pixels for logo + title ----
keep = dilate(logo | title, 2)
keep_soft = blur(keep.astype(np.float32), 0.8)[..., None]
t_top = inpaint(t, dilate(instr, 3) | keep)  # pattern continues under the kept art's halo
header = render(t_top) * (1 - keep_soft) + band * keep_soft
save_webp(header, "header.webp", quality=88)

# ---- pattern.webp: band with everything painted out, mirrored so it tiles ----
# Order is [flipped, normal]: the first row under the header must match the header's
# last row, and the tile's last row matches its own first row, so repeat-y is seamless.
# The logo hole is too big to diffuse convincingly, so it borrows the pattern from the
# same rows further along — whichever offset best matches the hole's surroundings — and
# feathers it in so strokes join up instead of stopping at a straight cut. The thin text
# holes diffuse fine.
logo_hole = dilate(logo, 4)
ring = dilate(logo_hole, 10) & ~logo_hole
ys, xs = np.nonzero(ring)
rows = slice(ys.min(), ys.max() + 1)
best = min(
    (s for s in range(-460, 461, 4)
     if abs(s) > 240 and not content[rows, max(xs.min() + s, 0):xs.max() + s + 1].any()),
    key=lambda s: np.abs(t[ys, xs] - t[ys, xs + s]).mean(),
)
shifted = np.roll(t, -best, axis=1)
w = np.maximum(blur(dilate(logo_hole, 6).astype(np.float32), 5), logo_hole)
t_clean = t * (1 - w) + shifted * w
clean = render(inpaint(t_clean, dilate(title | instr, 4) & ~logo_hole))
tile = np.vstack([clean[::-1], clean])
save_webp(tile, "pattern.webp", quality=80)


# ---- card wordmarks as alpha masks ----
def label(bbox, ink, paper, name, pad=6, scale=3):
    x0, y0, x1, y1 = bbox
    crop = src[y0 - pad:y1 + pad + 1, x0 - pad:x1 + pad + 1]
    axis = ink - paper
    a = np.clip(((crop - paper) @ axis) / (axis @ axis), 0, 1)
    # Upscale then re-sharpen: the letters are flat shapes, so this gives crisp edges
    # on 3x phone screens instead of a soft 1x crop.
    big = Image.fromarray((a * 255).astype(np.uint8)).resize(
        (a.shape[1] * scale, a.shape[0] * scale), Image.BICUBIC)
    a = smoothstep(0.3, 0.7, np.asarray(big).astype(np.float32) / 255)
    rgba = np.zeros(a.shape + (4,), np.uint8)
    rgba[..., :3] = 255
    rgba[..., 3] = (a * 255).astype(np.uint8)
    Image.fromarray(rgba).save(OUT / name, optimize=True)
    return rgba.shape[1], rgba.shape[0]


# ---- og-image.jpg: link preview when the page is shared (top of the board, 1200x630) ----
Image.fromarray(src[Y0:Y0 + 840].astype(np.uint8)).resize((1200, 630), Image.LANCZOS).save(
    OUT / "og-image.jpg", quality=85, optimize=True, progressive=True)

print("myth-label", label((292, 579, 498, 633), WHITE, RED, "myth-label.png"))
print("fact-label", label((1068, 588, 1237, 646), RED, WHITE, "fact-label.png"))

for f in sorted(OUT.iterdir()):
    print(f.name, f.stat().st_size)
