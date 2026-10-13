# Asya'da Egitim - Basvuru Rehberi / 001
# "Cince bilmeden Cin'de okuyabilir miyim?"

Six 1080x1350 PNGs sit at the ZIP root (01-cover.png ... 06-dossier.png) and in
`final/`. Every manifest path resolves to a real file in this archive.

- `final/` - the six exported Instagram carousel slides.
- `originals/` - the copy-free art-direction plates (licensed photography plus
  deterministic Chinese motif geometry) that the typography and canonical
  lockups were composited onto.
- `source/` - editable SVG and HTML sources; Jost and the Songti SC CJK subset are
  embedded, canonical lockups are linked verbatim. `*-plate.svg` are the plates.
- `assets/` - Jost (SIL OFL), the CJK subset, the canonical manifest, the verbatim
  approved lockup SVGs and the licensed photographs in `photos/`.
- `mobile/` - 324x405 and 375x469 previews rendered from the final PNGs.
- `caption-and-credits.md` - photographer, licence and source URL per photograph.
- `exact-copy.json` - the locked copy with a line-by-line fidelity check.

Rebuild: Python 3 + Pillow, Node.js + playwright-core and Chrome.
`python3 build.py && python3 verify_and_package.py`. Set CHROME_PATH off macOS and
PLAYWRIGHT_MODULE to the absolute playwright-core directory in a temporary install.

Image-generation calls: zero. Photography is licensed Wikimedia Commons material;
the Chinese motif geometry is locally generated SVG. Human review pending; not
published to Instagram.
