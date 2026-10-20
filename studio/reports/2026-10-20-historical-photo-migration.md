# Brandstudio — First byte-identical historical photo migration

**Issue:** #110 · **Consent:** Existing deep links to *historical raw PNG files* may change; historic galleries and Git history must remain intact.  
**Starting main:** `98feb9a69d62e649ea1dd1e67a812dae970ff503` · **Scope:** Asya'da Eğitim historical Instagram drafts only.

## Exact migration

The original 4 published image paths all point to the **same Git blob SHA-1** `22dde98f383bc6998ff74c54c12f8044ac9e371b`. Image bytes: **3,281,287** per path. SHA-256 of the unchanged original byte stream: `c9e22040515021cfa5014b51426cf63ba3ded488370ae347edba77632c4e63ed`.

A Git tree move reuses that precise blob, without PNG encoding, stripping caBX provenance chunks, touching ICC/alpha metadata, or editing creative identity.

**New shared public path:** `docs/instagram/_shared/assets/study-worlds-22dde98f.png`

**Removed from published tree (retained in Git history):**
- `docs/instagram/carousel-01-v2/assets/photo-3.png`
- `docs/instagram/carousel-01-v3/assets/photo-3.png`
- `docs/instagram/carousel-02/assets/photo-3.png`
- `docs/instagram/discovery-01/assets/study-worlds.png`

**Changed source HTML:**
- `docs/instagram/carousel-01-v2/source/03.html`: `../assets/photo-3.png` → `../../_shared/assets/study-worlds-22dde98f.png`
- `docs/instagram/carousel-01-v3/source/03.html`: `../assets/photo-3.png` → `../../_shared/assets/study-worlds-22dde98f.png`
- `docs/instagram/carousel-02/source/03.html`: `../assets/photo-3.png` → `../../_shared/assets/study-worlds-22dde98f.png`
- `docs/instagram/discovery-01/source/02.html`: `../assets/study-worlds.png` → `../../_shared/assets/study-worlds-22dde98f.png`

**Current total for the 4 paths:** 13,125,148 bytes.  
**New shared path:** 3,281,287 bytes.  
**Net published-tree reduction:** **9,843,861 bytes (9.39 MiB)**. This is a tracked-tree calculation, not a claim of reduced Git pack storage or a measured GitHub Pages deployment artifact.

## Deep-link policy

The **four old direct PNG URLs will return HTTP 404** once the new Pages deployment completes. This is intentional and authorized **only for historical source image URLs**; their galleries, source HTML, manifest JSON, final rendered slide PNGs and the Git commit history remain reachable. No direct-image URL redirects are claimed, and no Cloudflare R2/Worker service is provisioned.

## Preflight evidence

- Full main tree: all 4 old paths share the same Git SHA and size.
- Live original SHA-256 computed via the browser and compared to the retained Git blob pointer.
- 503/503 text-based published-site documents checked, no fetch errors; the **only 4 resolved HTML/CSS references** to deleted URLs are the 4 source pages changed above.
- `studio/archive/local-preservation.json` contains no preservation entries for these four published URLs.
- `studio/cloud/policy.json` explicitly registers other production bundles; **none** of these 4 paths is listed as an invariant.
- The full source page output and all historical pre-rendered PNGs remain unchanged apart from those four source refs.

## Post-migration required checks

Run locally in an existing checkout or disposable CI runner, **no daemon**:

```sh
python3 -m unittest discover -s studio/tools/tests -p test_audit_asset_dedup_pilot.py
python3 studio/tools/audit_asset_dedup_pilot.py --root . --mode after --json
```

The read-only verifier stops on modified shared SHA-256, wrong length, remaining old paths, stale source links, or missing expected references. The fixture tests exercise both before and after states.

After the independent PR audit passes and the approved PR merges, wait for GitHub Pages deploy; validate 4 galleries and 4 historical source HTML pages, their shared PNG HTTP 200 and SHA-256, 4 old raw URLs HTTP 404, and ensure unaffected final PNG, logo and gallery links still work. Do **not** assert live savings based on Git tree alone.

## Revert

Use a new revert PR against the migration commit: restore four identical image paths from the original Git blob SHA, restore four legacy source references and revert verifier default to the before state. Do not rewrite Git history or force-push.