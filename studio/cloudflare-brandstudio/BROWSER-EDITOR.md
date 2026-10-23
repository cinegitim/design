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
