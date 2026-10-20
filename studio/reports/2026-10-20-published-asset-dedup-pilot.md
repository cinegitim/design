# Brandstudio | Duplicate PNG pilot — no-deletion gate

**Issue:** #110  
**Read-only baseline:** \`main\` @ \`773771172b4a840bc66fc2c2d0da9ccc4f4c42a3\` (2026-10-20)  
**Scope:** \`docs/instagram/\` four historical carousels; no locked logo, font or production-manifest edits.  
**Outcome:** Reference audit and feasibility decision, **not** a file migration or claimed space saving.

## Confirmed four-file group

The following 4 public PNG paths point to the exact same Git blob SHA-1 \`22dde98f383bc6998ff74c54c12f8044ac9e371b\` (3,281,287 bytes each):

- \`docs/instagram/carousel-01-v2/assets/photo-3.png\`
- \`docs/instagram/carousel-01-v3/assets/photo-3.png\`
- \`docs/instagram/carousel-02/assets/photo-3.png\`
- \`docs/instagram/discovery-01/assets/study-worlds.png\`

Current combined uncompressed bytes: **13,125,148** (12.52 MiB). If three copies actually disappeared from published assets, theoretical savings would be **9,843,861 bytes (9.39 MiB)**.

The assets are referenced by the current source layouts:
- \`carousel-01-v2/source/03.html\` → \`../assets/photo-3.png\`
- \`carousel-01-v3/source/03.html\` → \`../assets/photo-3.png\`
- \`carousel-02/source/03.html\` → \`../assets/photo-3.png\`
- \`discovery-01/source/02.html\` → \`../assets/study-worlds.png\`

These source HTML pages are still part of the historical design archive. The original 4 URLs and source pixels are currently retained.

## Important GitHub Pages limitation

Git may store identical blobs once in its object database, but GitHub Pages publishes independent paths. **Rewriting the HTML references to a shared image while keeping all four original files yields exactly 0 bytes of published-site size reduction.** Removing three original paths immediately makes those historical direct image URLs return 404 on a static site.

Therefore **do not** claim a 9.39 MiB saving, delete the three historical files, substitute symlinks, or silently change approved/source images in this pilot. A safe deletion needs an agreed URL compatibility policy (or an explicit acceptance that some raw-image deep links expire). GitHub Pages alone does not provide per-file 301 rewrites while preserving the old response.

## Supported ways forward, in order

1. **Read-only evidence:** Use \`python3 studio/tools/audit_asset_dedup_pilot.py --root . --json\` and run \`python3 -m unittest discover -s studio/tools/tests -p 'test_audit_asset_dedup_pilot.py'\`. The script confirms all four files are byte-identical and maps HTML/CSS references. It does not alter files. Old external links cannot be ruled out.
2. **URL-preserving optimization trial:** On a throwaway copy, benchmark lossless PNG recompression; require pixel-perfect decoding, ICC/gamma/alpha compatibility, correct thumbnails and previews, then calculate actual byte savings. Unlike duplication removal, this preserves paths but changes image binary hashes. Approved canonical files are excluded, and source copies must be preserved. Do not apply absent results and approval.
3. **Single-source URLs:** Update source layouts to one shared asset then remove duplicates **only** if raw-image URL compatibility is explicitly waived, or a separate redirect/storage route is independently verified. A free quota is not unlimited; do not provision R2 or redirect Workers without approval.
4. **Separate publish from source:** Longer-term, build a small site artifact from an explicit publication manifest while retaining full editable sources and original packages outside that artifact. Must keep historical gallery HTML navigation and downloads functional and stay within GitHub usage rules.

## Delivery and acceptance guard

- [x] Four Git SHA matches and path sizes independently verified.
- [x] Four source layout dependencies identified.
- [x] Read-only analyzer and local fixture tests added in this PR (run on a real checkout to confirm exact SHA-256 and all text references).
- [ ] Byte-identical external/download URL compatibility has a decided policy.
- [ ] Lossless size trial proves a positive, measured, visual-safe saving.
- [ ] Any eventual asset move/deletion gets a **separate PR**, original/old URL checks, SHA evidence, and exact-head CI.
- [ ] Compare actual GitHub Pages artifact size before and after; **never** equate apparent duplicate paths with Git packfile saving.

This proposal adds no new image, ZIP, workflow, external service, polling, or scheduled job.
