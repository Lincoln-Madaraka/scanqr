# scanqr — Match Day Special Menu

A single-page, mobile-first **Match Day Special** menu — Geco Cafe × Masshouse × Kenchic. Scan the QR, see the menu. The whole site is one centered, full-width image that fills the screen on a phone and sits as a tidy card on tablet / desktop.

## Live site

<http://scanthisqr.redgiant.co.ke/>

## What's in this repo

| Path | What it is |
|---|---|
| `index.html` | The landing page — **World Cup 26 · Word Hunt** game (self-contained, inline styles). Served at the root domain. |
| `menu.html` | The Match Day Special menu — a single `<picture>` element pointing at the menu artwork. Reachable at `/menu.html`. |
| `styles.css` | ~30 lines used by `menu.html`. Flex-centers the image, full-width on phones, capped at 720 px with a soft shadow on larger screens. |
| `manifest.webmanifest` | PWA manifest — "Add to Home Screen" installs as *Match Day*. |
| `assets/match-day-menu.jpg` | The menu artwork (JPG fallback). |
| `assets/match-day-menu.webp` | The menu artwork (WEBP, served to modern browsers). |
| `assets/` | Icons, favicons, OG image. |
| `source/` | Legacy offline Python tooling (asset-processing scripts). Not used at runtime. |

## Stack

- Plain HTML + CSS. No JavaScript, no framework, no bundler, no build step.
- The whole runtime is two files: `index.html` + `styles.css` + the image in `assets/`.

## Updating the menu artwork

Export the menu (PDF, Figma, etc.) to a JPG and a WEBP and drop both into `assets/`:

- `assets/match-day-menu.jpg` — full-resolution JPG, ~1024–1600 px wide, quality ~85.
- `assets/match-day-menu.webp` — same image, WEBP for smaller payload on modern browsers.

If the aspect ratio of the new artwork differs from the old, update the `width` and `height` attributes on the `<img>` in `menu.html` to match the intrinsic pixel dimensions — this stops Cumulative Layout Shift while the image loads.

## Run it locally

```bash
python3 -m http.server 8765
```

Open <http://localhost:8765> on the Mac. To test on a phone on the same Wi-Fi, open `http://<your-Mac-LAN-IP>:8765` (find the IP with `ipconfig getifaddr en0`).

Checks:
- Phone (375 px viewport): image is edge-to-edge, no horizontal scroll.
- Tablet (768 px): image capped at 720 px, centered, soft shadow card.
- Desktop (1440 px): same as tablet, with breathing room above/below.

## Deployment

The site is hosted on **Red Giant** infrastructure at `scanthisqr.redgiant.co.ke`. Pure static — `index.html`, `styles.css`, `manifest.webmanifest`, and `assets/` are all the web server needs.

```bash
rsync -avz --delete \
  --exclude '.git' --exclude 'source' --exclude '.DS_Store' \
  /Users/lincoln/scanqr/  user@server:/var/www/scanthisqr/
```

## Credits

- Brands: Geco Cafe · Masshouse · Kenchic
- Built with [Claude Code](https://claude.com/claude-code)
