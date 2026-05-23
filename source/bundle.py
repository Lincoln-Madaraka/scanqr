"""Bundle the DStv MOTD Word Hunt into a single self-contained HTML file.

Reads the modular game files (index.html, styles.css, data.js, app.js),
inlines everything as <style> / <script> blocks, and writes the result to
DSTV-MOTD-HUNT.html at the project root. The output runs from file:// on
any modern browser — no server, no internet, no service worker.

Re-run any time the modular files change:

    python3 source/bundle.py
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_NAME = "DSTV-MOTD-HUNT.html"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def bundle() -> Path:
    html = read(ROOT / "index.html")
    css = read(ROOT / "styles.css")
    data_js = read(ROOT / "data.js")
    app_js = read(ROOT / "app.js")

    # 1. Replace the stylesheet link with an inline <style> block.
    html = re.sub(
        r'<link rel="stylesheet" href="styles\.css">',
        f"<style>\n{css}\n</style>",
        html,
    )

    # 2. Collapse the two <script defer> tags into a single inline <script>.
    html = re.sub(
        r'\s*<script defer src="data\.js"></script>\s*<script defer src="app\.js"></script>',
        f"\n  <script>\n{data_js}\n{app_js}\n  </script>",
        html,
    )

    # 3. Drop the PWA manifest reference — meaningless from file://.
    html = re.sub(r'\s*<link rel="manifest" href="manifest\.webmanifest">\s*', "\n  ", html)

    # 4. Stamp the offline title.
    html = re.sub(
        r"<title>[^<]*</title>",
        "<title>DStv MOTD Word Hunt — Offline Edition</title>",
        html,
        count=1,
    )

    out = ROOT / OUT_NAME
    out.write_text(html, encoding="utf-8")
    size_kb = out.stat().st_size / 1024
    print(f"Wrote {OUT_NAME} ({size_kb:.1f} KB)")
    return out


if __name__ == "__main__":
    bundle()
