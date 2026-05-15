# scanqr — The Kenchic x Ngemi Experience

A single-page mobile menu for **The Kenchic x Ngemi Experience**, built to be reached by scanning a QR code at the venue. Lightweight, fast, and renders identically on every phone.

> 🐔 *Cîna Mûrio!!*

## Live site

<http://scanthisqr.redgiant.co.ke/>

## What's in this repo

| Path | What it is |
|---|---|
| `index.html` | The single page. Loads the menu image with proper meta tags. |
| `styles.css` | Mobile-first CSS. Caps the layout at 600 px on phones and adds a soft shadow on desktop. |
| `manifest.webmanifest` | PWA manifest — lets visitors "Add to Home Screen" with the Kenchic icon. |
| `assets/menu.jpg` + `assets/menu.webp` | The menu image. WebP is served to modern browsers, JPG is the fallback. |
| `assets/favicon-*.png`, `icon-*.png`, `apple-touch-icon.png` | Full favicon set generated from the Kuku Mfalme badge. |
| `assets/og-image.jpg` | 1200 × 630 share-card image used by WhatsApp, Twitter, iMessage, Slack, etc. |
| `source/` | Original full-resolution menu image + the Python scripts used to generate everything in `assets/`. |

## Stack

- Plain HTML + CSS. No framework, no build step, no JavaScript.
- ~550 KB total page weight (the menu image is the bulk; everything else is < 100 KB).
- Single-file mental model: edit `index.html` and you're editing the whole site.

## Run it locally

```bash
python3 -m http.server 8765
```

Open <http://localhost:8765> on the Mac. To test on a phone on the same Wi-Fi, open `http://<your-Mac-LAN-IP>:8765` (find the IP with `ipconfig getifaddr en0`).

## Updating the menu

When prices, items, or artwork change:

```bash
cp ~/Downloads/new-menu.jpg source/menu.jpg
python3 source/build_assets.py     # rebuilds menu.jpg, menu.webp, favicons, og-image
git add source/menu.jpg assets/
git commit -m "Update menu — <what changed>"
git push
```

GitHub Pages redeploys automatically (about a minute).

## Deployment

The site is hosted on **Red Giant** infrastructure at `scanthisqr.redgiant.co.ke`. It's a pure static site — `index.html`, `styles.css`, `manifest.webmanifest`, and the `assets/` folder are the only files the web server needs.

To deploy a new version, upload the working tree (excluding `source/` and `.git/`) to the server's web root, e.g.:

```bash
rsync -avz --delete \
  --exclude '.git' --exclude 'source' --exclude '.DS_Store' \
  /Users/lincoln/scanqr/  user@server:/var/www/scanthisqr/
```

Or zip and upload via cPanel / File Manager — same files, same result.

## QR code

Generate a QR pointing at the live URL:

```
http://scanthisqr.redgiant.co.ke/
```

Print it at restaurant-sized resolution — the page is already optimised for the phone that will scan it.

## Credits

- Menu artwork: Kenchic x Ngemi
- Built with [Claude Code](https://claude.com/claude-code)
