# Burs Dosyası / 001 — GKS 2027 · Asya'da Eğitim Instagram campaign

Six-slide 1080×1350 (4:5) Instagram carousel about the 2027 GKS-UIC university-track
scholarships, produced deterministically from HTML/CSS/SVG.

## Reproduce

```bash
cd brands/asyada-egitim/applications/burs-dosyasi-gks-2027-001
python3 build.py           # renders export/01..06.png, runs geometry + copy QA
python3 deliver.py         # manifest, docs, gallery copy, contact sheet, ZIP
```

Requirements: Python 3 with Pillow; Google Chrome (headless Chromium also works —
`CHROME` in build.py points at the macOS Chrome binary). Fonts and lockups are bundled
under `assets/`; no network access is needed at render time.

## Layout

- `source/01..06.html` — editable slide sources (self-contained; open in a browser)
- `export/01..06.png` — final 1080×1350 sRGB PNGs
- `assets/` — Jost variable font (+OFL), canonical lockup SVGs, graded photos
- `assets/photos-original/` — unmodified downloads + `credits.json`
- `qa/geometry-report.json` — measured bounds/safe-area/overlap/clip QA per slide
- `copy-manifest.json` — the locked on-slide copy (validation target)
- `contact-sheet.png`, `mobile-preview/` — review artifacts (375px width)
- `manifest.json` — delivery manifest with SHA-256 hashes and lockup IDs
- `verification-notes.md`, `photo-credits.md` — sources and licences
- `instagram-feed-preview.html`, `index.html` — review pages
- `package/` — ZIP bundle

## Quality gates

Copy, geometry and visual QA statuses are recorded in `manifest.json`.
Status: HUMAN CREATIVE APPROVAL PENDING. Not published to social media.
