# Free browser Visual Editor (no cloud writes)

The optional **browser-only** Visual Editor is published as
`docs/visual-editor/browser/index.html`.
It reads the approved *published source HTML* from
`docs/instagram/<product>/source/NN.html`, preserving original artwork and
canonical logo SVGs, and applies non-destructive layout/style overrides.

- First-party site UI only. **No Cloudflare Access, billing authorization,
  R2, D1 writes, or external paid rendering.**
- User can edit coordinates, dimensions, font size, palette tokens and direct
  colors; changes are held in-memory until explicitly **New version → Confirm**.
- Saves append-only `v2`, `v3` ... in this browser's localStorage (at most 25).
  The user can optionally choose a folder via File System Access API:
  `versions/vN/editor-state.json` and `overrides.css`.
- Can export the active slide as an HTML snapshot with original external asset
  dependencies. PNG or independent local image packages are **not** produced by
  the static editor; prompt-based verified render remains authoritative.
- No multi-device synchronization. Clearing browser data can erase unexported
  revisions. The static site doesn't claim remote permanence.
- When a given public product has no numbered source HTML pages, the UI reports
  **source unavailable** rather than inventing layers.
- Users see the browser editor as a first option; the existing local companion
  remains a separate second option for source + verified image re-rendering.
- Do not interpret these local browser revisions as approved by a human,
  posted to Instagram, committed to GitHub or render validated.

## Deployment

GitHub Pages serves it immediately after the normal reviewed deployment.
The temporary personal Cloudflare Worker stages it via *public proxy* as
`/visual-editor/browser/?product=carousel-01-v3`.

The personal Cloudflare Pages project `brandstudio-migration` exists but direct
asset upload is currently blocked by the Pages asset JWT API returning
HTTP 403. Do not claim independent static hosting until the actual uploads and
live asset parity can be confirmed.

The Cloudflare Pages Git installation is independently blocked with
HTTP 401 even though the cinegitim GitHub app is installed. Never enable
paid features or Cloudflare Access Free when its checkout requires agreeing
to bill usage above free limits: user's absolute preference is zero charges.


## Visual editing UX (browser-only)

- Accordion layer list groups each photo with overlapping or nearby text; other
  headings, logos and footers are separate sections. The grouping is a visual
  convenience and never rewrites the canonical source DOM or approved copy.
- Logo and folio can be inspected but are read-only in the browser editor.
- A five-slide navigator and Alt+ArrowLeft/ArrowRight allow direct slide change.
  Selected editable layers can move 1px with arrow keys or 10px with Shift.
- Undo/redo buttons and Cmd/Ctrl+Z, Cmd/Ctrl+Shift+Z and Ctrl+Y cover editor
  state changes with a 40-checkpoint in-memory history. One drag contributes
  one checkpoint; after switching saved versions, history resets. History is
  *not* written to exported JSON or the cloud; approved vN saves still use
  the existing explicit confirmation dialog.
- Photo/type group proximity is based on actual preview element rectangles;
  it is not a semantic image classifier. For designs with no nearby overlap,
  the copy remains in the text section instead of being inaccurately grouped.
- Undo affects uncommitted editor state only and does not change previously
  saved versions or the immutable v1 source.


## Flexible canvas / inspector (October 2026)

Browser Editor now uses a viewport-sized editing shell and a responsive canvas:
zoom-to-fit, 25–125% explicit zoom, Ctrl/Command+wheel zoom inside preview,
hand-pan over the canvas, and a focus mode that hides both inspectors.
Direct manipulation includes 8 px optional drag snapping, the resize grip
on the selection border, and quick alignment to the 1080×1350 slide.

The richer object inspector stores safe, portable CSS state for: width, height,
font size/weight (existing approved Jost only), letter spacing, line height,
text alignment, opacity, border radius, stacking order, image object-fit,
and X/Y crop positions. These values are audited in portable.js and remain
strictly bounded. Photo crops only change display geometry, never source bytes.
The canonical logo and folio remain locked for editing.

All gestures participate in local undo/redo and the same explicit vN save.
Neither imported snapshots nor CSS exports can use arbitrary CSS expressions,
remote URLs, JavaScript, or unapproved font substitution. No paid Cloudflare
service, remote state write, server render or synchronization is enabled.
