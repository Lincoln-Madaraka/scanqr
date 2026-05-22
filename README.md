# scanqr — Kenchic UCL Word Hunt

A mobile-first **UEFA Champions League word-hunt** mini-game, dressed in the Kenchic brand. Built around the Arsenal vs PSG fixture but the puzzle pool spans the wider football world so players can run game after game without seeing repeats.

## Live site

<http://scanthisqr.redgiant.co.ke/>

## How the game plays

- A category prompt appears at the top of every round (e.g. *"Find 6 Arsenal players"*, *"Find 6 Champions League winning clubs"*).
- A 12 × 12 letter grid hides **6 valid answers** somewhere inside — horizontally, vertically, or diagonally, forward or backward.
- Press-and-drag across letters in a straight line to commit a word. Correct → cells lock in **green**. Wrong → cells flash **red** and clear.
- A **30-second** countdown ring runs in the corner and never pauses.
- Find all 6 in time → "Champion!" modal, session score increments, *Next puzzle* loads a fresh one.
- Time runs out → "Oopsie!" modal shows your score and a mini-grid with all 6 answers revealed.
- Puzzles are procedurally generated, so the supply is effectively endless.

## What's in this repo

| Path | What it is |
|---|---|
| `index.html` | Game shell — header, prompt + timer, grid container, modal. Inline SVG icons (no emoji). |
| `styles.css` | Layout (upper-3/4 play area, lower-1/4 score strip), cell states, modal styling, Kenchic palette. |
| `app.js` | Game logic — puzzle generator, drag selection, timer, win / timeout modals, session score. |
| `data.js` | Category word pools (Arsenal & PSG squads, UCL winners, Ballon d'Or, stadiums, managers, etc.). |
| `manifest.webmanifest` | PWA manifest — "Add to Home Screen" installs as *UCL Hunt*. |
| `assets/icon-*.png`, `favicon-*.png`, `apple-touch-icon.png` | Kenchic logo set, reused as the app icon. |
| `assets/og-image.jpg` | 1200 × 630 social share card. |
| `source/` | Offline Python tooling that originally generated the asset images. Not used at runtime. |

## Stack

- Plain HTML + CSS + JavaScript. No framework, no bundler, no build step.
- Runtime is three small files: `index.html`, `styles.css`, `app.js` (+ `data.js`).
- No database, no localStorage — each session starts fresh.

## Run it locally

```bash
python3 -m http.server 8765
```

Open <http://localhost:8765> on the Mac. To test on a phone on the same Wi-Fi, open `http://<your-Mac-LAN-IP>:8765` (find the IP with `ipconfig getifaddr en0`).

## Adding new puzzles

Edit `data.js`. Each entry is a category with a prompt and a pool of at least 8 uppercase words (so a 6-word puzzle still has variety run-to-run):

```js
{
  prompt: "Find 6 Bundesliga clubs",
  pool: ["BAYERN", "DORTMUND", "LEVERKUSEN", "LEIPZIG", "FRANKFURT", "STUTTGART", "WOLFSBURG", "UNION"]
}
```

Words must be 12 letters or shorter (grid is 12 × 12). No spaces, no hyphens.

## Deployment

The site is hosted on **Red Giant** infrastructure at `scanthisqr.redgiant.co.ke`. Pure static — `index.html`, `styles.css`, `app.js`, `data.js`, `manifest.webmanifest`, and `assets/` are all the web server needs.

```bash
rsync -avz --delete \
  --exclude '.git' --exclude 'source' --exclude '.DS_Store' \
  /Users/lincoln/scanqr/  user@server:/var/www/scanthisqr/
```

## Credits

- Brand: Kenchic
- Built with [Claude Code](https://claude.com/claude-code)
