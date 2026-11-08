# Production notes

- **Campaign:** Asya'da Eğitim — Rotanı Seç #001 / Tokyo mu, Seul mü?
- **Status:** Human campaign review pending; not published to social media; campaign grammar is not a canonical brand system.
- **Production:** Licensed Wikimedia Commons photography + deterministic HTML/CSS/SVG composition + Chromium export.
- **Image-model calls:** 0 generations, 0 edits. No AI scene is presented as documentary photography.
- **Typography:** Exact supplied Turkish copy, typeset with local Jost VF. No text or logo is baked by an image model.
- **Identity:** D-04/light is used at 220–238 px on paper/light signature fields; H-02/dark is used at 548 px on the dark finale. Both exceed manifest minimums. Geometry and colours are unchanged.
- **Visual grammar:** Cyan distinguishes Tokyo, pink distinguishes Seoul, acid-lime carries questions/interaction; red, ink and paper remain brand anchors. This is a campaign-local, review-only decision.
- **Photography:** Downloaded source bytes are preserved in `assets/photos/originals/`; source pages, authors, licences, hashes and modification disclosure are in `photography-sources.json` and `photography-attributions.md`.
- **Build environment note:** The pinned setup script requires Python 3.12, unavailable on this macOS host. Rendering used repository-pinned Playwright 1.56.1 with installed Google Chrome and the local repository font. No dependency is committed.
