# Asya'da Eğitim — Başvuru Rehberi / 001
## Çince bilmeden Çin'de okuyabilir miyim?

Six-slide Instagram carousel, 1080×1350, built for the Asya'da Eğitim brand from
the approved V-01 canonical seal and the approved lockup family.

---

## 1. What this is

A production carousel, not a concept round. The copy was supplied locked and is
reproduced verbatim. The art direction was produced in response to the brief's
requirement that the series be *distinctively Chinese* — recognisable even with
the text hidden.

## 2. How it was produced

| Stage | Method |
|---|---|
| Factual check | Every fixed claim checked against official university sources before layout |
| Photography | 12 freely licensed Wikimedia Commons photographs, downloaded once, credited per file |
| Chinese motifs | Locally generated deterministic SVG geometry (`motifs.py`) |
| Typography | Jost embedded from the canonical brand file; Songti SC subset embedded for 17 verified CJK characters |
| Canonical lockups | Verbatim manifest-listed SVGs linked, never redrawn or retypeset |
| Render | One Playwright/Chromium pass at final resolution; copy-free plates rendered separately |
| Geometry audit | `render.mjs` measures every `<text>` box, the lockup box, CJK marks and icons, and throws on any overflow, collision or clipping |
| Visual review | Two full contact-sheet reviews with actual image inspection between them |

No image model was called at any point. No paid backend was used.

## 3. Per-slide art direction

| Slide | Concept | Chinese device | Ground |
|---|---|---|---|
| 01 | Cinematic cover | Circular moon-gate opening + ice-ray lattice panel, gold ring | Deep ink, China-red answer, bright-gold accents |
| 02 | Undergraduate field collage | Lattice geometry interrupting the right-hand photograph | Warm ivory, China-red typography, gold rules |
| 03 | University photo atlas | Flower-window lattice crop frames, red location band | Dominant central photograph + two supporting sections |
| 04 | Master's editorial | Gold editorial rules + small geometric seal-inspired accents | Deep ink, restrained China-red plane |
| 05 | Doctoral research | Large abstracted circular architectural motif + sparse xiangyun contour | Dark research photography, controlled red surface |
| 06 | Application dossier | Red archival-folder form, gold detailing, restrained seal-like accent | Warm paper, vector iconography |

Every slide uses **one or two primary devices only**. No slide repeats the same
ornamental border as another.

## 4. Colour system

Canonical brand values: `#BD2120` red, `#1D2027` ink, `#F7F3E9` paper.
Campaign-only treatments: `#DE2910` China red, `#D9A441` imperial gold,
`#F3C64D` bright gold, `#F4E8D3` warm ivory.

The two reds are never adjacent: brand red carries the canonical signature and
the hero answer word, China red carries campaign graphics (bands, planes, folder
form, kicker rules). Gold appears as large accents (the cover's answer underline,
slide 05's accent bar, the folder's inner rule), not only as hairlines.

## 5. Typography

Jost for all Turkish copy, embedded from
`brands/asyada-egitim/explorations/wordmark-ref/weight-study/sources/Jost-VF.ttf`.
Weights used: 400, 500, 600, 700. No text is rasterised; every line is an
editable `<text>` element inside `#editable-campaign-copy`.

Songti SC (subset to 17 characters) carries the secondary Chinese marks only —
`留学` on the cover and the three verified university names on the atlas slide.
No imitation "Chinese-style" display font is used.

## 6. Copy fidelity

`exact-copy.json` holds the locked copy and a line-by-line check. Multi-line
breaks split only at existing spaces; joining the fragments reproduces the
supplied text exactly. One line, `Asya'da Eğitim` on slide 06, is delivered by
the approved canonical lockup rather than retypeset — see that file for the
explicit record.

## 7. Honest limitations

- Photographs are authentic Commons images of the named institutions, but crops
  and tonal overlays were applied for legibility. They are documentary campus
  imagery, not commissioned campaign photography.
- Programme listings reflect official pages at the time of research (October
  2026) and are subject to the universities' own annual changes. Slide 06's
  document list is illustrative of common requirements, not a guarantee.
- No image model was asked to produce or reproduce any logo, wordmark, seal or
  institution.

## 8. Status

Technical production complete: geometry audit, copy verification, canonical
lockup verification and packaging all pass. **Human creative review pending.**
Not published to Instagram.
