# Visual QA — Rotanı Seç #001 / V2

Every slide was rendered at 1080×1350, inspected at full size, and re-inspected
at 375×469 after each revision. The inspections below record what was actually
seen in the PNGs, not what the source implies.

## Stage 1 — first full render

The contact sheet showed six clearly different compositions and the geometry
audit was mostly clean, but inspection found two real defects that no
collision test had caught:

- **Slide 01 carried a detached red comma** floating in dark space beside the
  signature. Zooming to 3× revealed the cause: the `D-04/light` lockup has an
  **ink** wordmark, and on the dark cinematic ground only the red seal and the
  red apostrophe were visible — the wordmark was rendering invisibly.
- **Slide 06's H-02 sat at 330px**, below its approved 528px minimum.

Both were fixed by measurement, and an automated contrast gate plus a minimum-size
assertion were added so the same defect classes now fail the build.

## Stage 2 — final render, inspected per slide

| Slide | What was verified in the PNG |
|---|---|
| 01 | Headline `TOKYO MU, SEUL MÜ?` dominant and unclipped; secondary question clearly smaller; four-category strip on one line and clear of the signature; `TOKYO` city tag legible; D-04/dark wordmark now fully visible on the dark ground |
| 02 | Two-column band reads YONSEI UIC first; route diagram anchored to the Songdo label; Waseda/Shinjuku and WISH/Nakano labels sit with the Tokyo column; footer note legible |
| 03 | All six university names legible at full size; one dominant photo per city, two supporting; labels separate from imagery; no label over a noisy area |
| 04 | Question headline dominant; `6 fakültede` and `Tamamen İngilizce` emphasised in the two cards; red qualification note legible at the base |
| 05 | Local prices dominant and on one line; EUR values visibly smaller and directly beneath; accommodation type directly under its price group; both footnotes readable; photos read as labelled interiors |
| 06 | Question headline dominant; TOKYO and SEUL equally weighted and each tied to its photograph; comment CTA larger than the consultation line; H-02/dark signature legible inside the dark finale |

## Stage 3 — mobile review

All six 375×469 previews were inspected. The binding categories are the two
price strings and the six university names. Local currency remains the largest
element on slide 05, and EUR stays secondary as required. On slide 03 the longest
name, `Seoul National University`, stays readable because labels sit on paper
panels rather than over photography.

## Remaining limitations

- Slide 05's housing photographs are **disclosed illustrative AI generations**,
  not documentary photography of WISH or a real Seoul apartment; they are labelled
  as examples in `photography-attributions.md` and in the manifest. Documentary
  interiors of those specific buildings were not available under a usable licence.
- The 2026-10-12 `/tvÄ±` exchange-rate figures are supplied by the brief and were
  not independently re-derived.
- Campaign aesthetic approval and any social publication remain pending human
  decision. A passing technical audit is not a visual approval.
