# Asya’da Eğitim — Launch Carousel Experiment 02 / placement revision 02

Five 1080×1350 PNGs are at the ZIP root: 01-cover.png … 05-invitation.png. They are also in `final/` so all manifest paths resolve.

- `originals/`: unmodified generated artwork; initial slide-05 version retained.
- `source/`: editable SVG and HTML sources; Jost is embedded in SVG, canonical marks linked unchanged.
- `assets/`: Jost, canonical manifest, verbatim SVG lockups and transparent, separately editable paper/contrast cleanup layers.
- `render-validation.json`: actual Chromium font loading and glyph/complete-mark collision/clearspace metrics.

Rebuild: Python 3 + Pillow, Node.js + playwright-core and Chrome. Install with `npm install playwright-core`, set CHROME_PATH if not on macOS; `python3 build.py && python3 verify_and_package.py`. In a temporary install, set PLAYWRIGHT_MODULE to the absolute playwright-core directory.

AI people/places are illustrative. Human review pending; not published to Instagram.
