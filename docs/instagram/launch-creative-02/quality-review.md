# Placement revision 02 — critical review

**Human experimental campaign review pending.** The first implementation was rejected by the user for weak logo/copy integration; the initial optimistic scores were not a reliable aesthetic gate. Its PNGs, sources, manifest and review are preserved under `history/v1/`.

## What was actually corrected

| Slide | Previous problem | Revised placement |
|---|---|---|
| 01 | Small edge-hugging signature; headline/body did not follow the narrowing paper shape. | Larger D-04 at a 62px top inset, natural Jost 550/720 weights, stepped headline and indented support wholly inside the cream sweep. |
| 02 | Printed strokes crossed letterforms; large seal sat on the student/backpack. | Strokes are removed by a separate original-paper-texture cleanup layer. Narrower headline clears the passage; compact D-04 moves entirely off the person into the lower-right architectural floor, protected by a soft ink shade. |
| 03 | Added note rectangle and scattered labels competed with the atlas. | Extra rectangle removed. Logo and headline are separated within the original paper crest; supporting line moves away from the ink blot. Country captions use original annotation fields, not new tags. |
| 04 | Upper-right bilingual mark was cramped; added body card covered academic/social imagery. | D-04 sits within the ink aperture with larger edge clearance. Body returns to the main paper panel; program names fill the original annotations. No new lower card. |
| 05 | Headline and red accent competed with city lights; bilingual mark overlapped the silhouette; destinations crossed red print. | Headline is Paper and clears the skyline. Whole H-02 sits to the right of the person, fully inside the cream wave at 560px (minimum 528px). A separate textured cleanup layer protects destinations. CTA/contact are grouped on the existing dark diagonal; redundant button removed. |

## Self-critique, based on full-size and reduced-image inspection

| Slide | Hierarchy | Consistency | Aesthetics | Usability |
|---|---:|---:|---:|---:|
| 01 | 8 | 9 | 8 | 8 |
| 02 | 8 | 9 | 8 | 8 |
| 03 | 8 | 9 | 8 | 7.5 |
| 04 | 8 | 9 | 8 | 8 |
| 05 | 9 | 9 | 8 | 8 |

- **Closed Critical:** unreliable font rendering. PNGs are now exported through actual Chromium with embedded Jost, variable weights, no text stretching and no synthetic font substitutions. Font readiness and metrics are recorded in `render-validation.json`.
- **Closed High:** copy/mark collisions and edge constraints. Glyph-ink bounds—not a generic font line box—and complete SVG mark viewports are checked for collision and clipping. All five exports pass.
- **Closed High:** slide-05 brand/person collision. H-02 is wholly to the right of the figure; its embedded clearspace remains intact.
- **Closed High:** low-contrast support on print strokes. Slide-02 title-area strokes and slide-05 destination-area branches are cleaned using texture sampled from their own original paper. These are separately editable transparent layers; original generation bytes are untouched.
- **Remaining Medium:** the Japan/Korea labels occupy narrow, source-native annotation fields. They are clearly read at full export size but secondary at phone size. The fine approved English line on H-02 is likewise secondary at 375px; no retyping/enlarging individual logo parts is permitted.
- **Remaining Low:** the slide-04 support block uses a stepped last line to follow the torn-paper edge. This is deliberate rather than a mechanical shared alignment.

## Fidelity

No new image generation was performed. All original composition hashes stay identical to v1. Faces, campus perspective, atlas fragments, cut-paper density and red interventions remain; only copy, lockup placement, tiny paper cleanups and local contrast shading change. New transparent layers slightly suppress print detail behind copy, consciously trading incidental texture for actual readability. Pixel-difference percentage is a technical diagnostic, not an aesthetic approval.

The campaign remains an irregular photographic/editorial series, not a five-card template, uniform photo strip or empty corporate brochure. The original-vs-current and v1-vs-v2 contact sheets expose any loss instead of hiding it. Final judgement remains with the human.

## Delivery checks

The gallery was exercised at 375 / 768 / 1440px in Chromium: five images, five comparisons, archive/current switching, next/previous navigation, no page overflow or JavaScript errors. The ZIP was extracted outside the repository and rebuilt using only its supplied sources/assets plus documented dependencies: all five rebuilt PNG SHA-256 hashes match the reviewed exports exactly. Archived v1 PNGs and all original generated-image hashes also match the first delivered manifest.
