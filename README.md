# scanqr — The Kenchic x Ngemi Experience

A single-page mobile menu for **The Kenchic x Ngemi Experience**, built to be reached by scanning a QR code at the venue. Lightweight, fast, and renders identically on every phone.

> 🐔 *Cîna Mûrio!!*

## Live site

- Production: _https://&lt;your-domain&gt;_ <!-- update once domain is wired -->
- GitHub Pages: <https://lincoln-madaraka.github.io/scanqr/>

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

The site is hosted on **GitHub Pages** from the `main` branch.

1. Repo Settings → **Pages**
2. Source: *Deploy from a branch*, Branch: `main`, Folder: `/ (root)`
3. Custom domain: set it in the **Custom domain** field — GitHub will commit a `CNAME` file.
4. DNS at your registrar:
   - **Subdomain** (e.g. `menu.example.com`): `CNAME` → `lincoln-madaraka.github.io`
   - **Apex** (e.g. `example.com`): four A records → `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`
5. After DNS resolves (5–30 min), enable **Enforce HTTPS** in Pages settings.

## QR code

Generate a QR pointing at the live URL:

```
https://<your-domain>/
```

Print it at restaurant-sized resolution — the page is already optimised for the phone that will scan it.

## Credits

- Menu artwork: Kenchic x Ngemi
- Built with [Claude Code](https://claude.com/claude-code)
