# Portable Brandstudio versions — browser-only, zero charges

The prompt-based producer remains authoritative. The optional browser editor
works on the selected product's publicly available source HTML and does not
upload any state to Cloudflare, GitHub or R2.

## Move between computers

1. Open a product's **Tarayıcıda düzenle** view.
2. Click **Sürüm arşivini indir** to export a validated portable JSON archive
   containing the existing v2/v3 versions plus current edits.
3. Transfer that file yourself to the other computer.
4. Open the **same product** and click **Arşivi içe aktar**.
5. Confirm: imports append as fresh vN versions without overwriting local
   versions or changing the source v1. Invalid brands/products, CSS, colors,
   archive format and out-of-range slide references fail closed.
6. Existing per-device version backups are **not synchronized** or stored in
   any cloud account. The user must consciously move the file. Browser data
   clearance can otherwise erase changes.

## Reproducible exports

Optionally choose the **product root folder** with the native browser file
picker. On approved save vN, write:

    versions/vN/editor-state.json
    versions/vN/manifest.json
    versions/vN/slides/01.html
    versions/vN/slides/01.css
    ... one source-based HTML/CSS pair per carousel slide.

HTML snapshots preserve original source text, typography, images and approved
lockup references; apply editor overrides on top, and include a base
link to the published source asset path for correct relative media loading.
CSS rules use deterministic structural selectors, not interactive-only
data attributes. Each exported HTML/CSS pair can be reopened independently
while external source media URLs remain available.

Saved previews and HTML are **not** independently verified PNGs or an approved
published deliverable. Never report real browser render parity based only on
HTML source export. This flow does not change Github production source, logos,
approved typography rules, existing publication URLs or the core prompt pipeline.

## Zero-cost and safety

- Every state is strictly validated and capped to 32 KiB.
- At most 25 user versions per product; import is additive only.
- Supports only a known safe subset of CSS properties and scalar pixel values.
- Writing to an already-existing versions/vN folder is rejected.
- Folder writing is a local browser action requiring native folder permission;
  browsers without File System Access can still download individual files and
  portable archives.
- JSON import does not evaluate code, load custom remote media or contact APIs.
- No Cloudflare Access, D1 writes, R2 or billable image rendering.
