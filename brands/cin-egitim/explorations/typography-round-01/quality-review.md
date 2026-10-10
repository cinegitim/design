# Visual quality review — typography round 01

## Scope / fidelity

- Three real HTML wordmark renderings use the same canonical logo asset by path. No logo shapes, colors, or dimensions inside the source SVG are changed; no raster was generated.
- The typographic grammars differ beyond font choice: A is left-aligned horizontal serif / two lines; B is centered vertical sans / one line; C is horizontal condensed uppercase / ruled type block.
- Palette, paper field, test copy, and exact symbol remain constant across directions. Swapping color cannot erase their distinction.
- The A/B/C preview is not production-ready logo art. Spacing, optical correction, small-size survival, licensing, dark-field variants, and full wordmark approval remain unresolved until one direction is selected.

## Risks / fixes

- **High if treated as final:** HTML text is not outlined production artwork and hosted fonts may fail offline. Keep all three labelled exploratory; only outline/type-test the human-selected direction later.
- **Medium:** C's uppercase/condensed form may feel too institutional or reduce warmth. Evaluate after actual browser inspection at 16–24 px; do not assume from font name alone.
- **Medium:** A's serif + wordmark may be too bookish for a service identity. Compare the narrow horizontal header specimen against B before selecting.
- **Low:** Google Fonts network dependence and system fallbacks can shift line breaks. Verify selected font file/licence and approved production renderer later.

## Actual checks / limits

- Opened the comparison board and all three detail pages in the available browser at 1000 px viewport width. All board/detail mark images and Google Fonts reported loaded; no horizontal document overflow was reported. Accessible names, card headings, Turkish glyph specimen and local page links appeared in the browser accessibility snapshot.
- Browser screenshot capture failed because the desktop tab was not available to the screenshot tool. Therefore **visual screenshot inspection is unavailable**; DOM/render checks are not a substitute for human visual approval.
- No mobile device emulation or 16–24 px legibility review was performed. Mobile CSS exists but needs a real narrow viewport check.
- Exact canonical logo SHA is independently verified by `verify.py`.
