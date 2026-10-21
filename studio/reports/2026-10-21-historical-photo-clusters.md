# Brandstudio — Historical photo reuse, phase 2

**Issue:** #110  
**Base commit:** `fa24e5612ca3317696f2c52727add60d0391b755`  
**Scope:** four **historical, not human-approved** Asya'da Eğitim Instagram carousel experiments only.

## Three new single-source groups

| Shared public file under `docs/instagram/_shared/assets/` | Original Git blob SHA | Exact PNG bytes | Old published copies | Asset-only bytes saved |
|---|---|---:|---:|---:|
| `students-53a42641.png` | `53a426414549164bc30e3e59512068c3e4e8fce5` | 2,644,250 | 4 | 7,932,750 |
| `campus-1bebf73c.png` | `1bebf73c28d0a5eb7e7a0a2614cd29762c332f36` | 2,248,887 | 4 | 6,746,661 |
| `photo-2-031a795c.png` | `031a795c7745cba6ab2c23350513007092786291` | 2,552,934 | 3 | 5,105,868 |

**Old paths removed:** eleven PNG paths: `carousel-01-v2`, `carousel-01-v3` and `carousel-02` each retire `assets/photo-1.png`, `photo-2.png`, and `photo-4.png`; `discovery-01` retires `assets/students.png` and `assets/campus.png`. These are exactly the same bytes as the retained Git blobs, not recompressed.

**Changed source layouts:** ten `source/*.html` pages point to one of these shared images; no rendered slide PNG, manifesto, font, approved SVG, identity, active delivery or user-facing gallery page is modified. This follows the previously accepted policy that historical *raw PNG* deep links can end, provided galleries and Git history survive.

**Exact SHA-256 checksums** of the unchanged originals (measured on the previous live Pages deployment):
- `students`: `9018a8239c23e3dde39b448d79ce441ecdcc14f7e95dfe375f71169df2663761`
- `campus`: `5e0d818fcece01758b60c6a767b4e3d40b121586a312985531b67ff7f046b91b`
- `photo-2`: `d0b3667953d8c8754d2a06f056dd222ef647702f1e67053a11d01c935a157625`

**Net published file-tree saving:** **19,785,076 bytes (18.87 MiB)** after adding 203 bytes of longer `src` strings. PNG-only saving is 19,785,279 bytes. These are *uncompressed current tree* measurements; neither Git `.git` object storage nor billed Pages artifact size is claimed to have changed by the same number.

**Previous phase 1 already verified on the live site**: original shared `study-worlds-22dde98f.png` HTTP 200 and exact SHA-256; 4/4 historic raw image URLs 404; 4/4 source HTML and 4/4 overview gallery pages HTTP 200.

## Reproducibility and no-repeat rule

The old `build.py` producer programs previously copied the same raw photos to every gallery folder, **including the already deduplicated phase 1 photo**. The three affected source producers now invoke the *same* post-render normalizer when rendering finishes:
- `instagram-carousel-01-v2/build.py`: `carousel-01-v2`
- `instagram-carousel-01-v3/build.py`: `carousel-01-v3` and `carousel-02`
- `instagram-discovery-01/build.py`: `discovery-01`

`studio/tools/normalize_historical_carousel_build.py` is **dry-run by default** and `--apply` is explicit. Before touching files it validates source HTML references, exact original image bytes and existing shared images; a regenerated, different creative image **stops** rather than silently overwriting provenance or deleting originals. After the already-complete render/manifest, it rewrites historic source `src` URLs and unpublishes duplicate raw copies. Independent unit tests cover dry-run, apply, idempotence, wrong bytes and broken source markup. No render or image generation is performed by CI.

`studio/tools/audit_asset_dedup_pilot.py --mode after` also verifies all **four** shared groups, all historical references and retired originals. The historical source HTML remains at the same URL. Old raw image URL compatibility is intentionally waived for these experiments **only**.

## Check gates

1. Ensure exact-head PR independent technical audit passes and there are no unresolved substantial code review findings.
2. Run stdlib-only fixture unit tests for both verifier and normalizer, and check their byte safety controls.
3. Verify new head tree: three new shared files have exact original Git blob SHA; all eleven old raw paths absent; ten source HTML references updated; final render files and manifests byte-identical to the base.
4. After squash merge wait for GitHub Pages deploy; verify three shared PNG URLs return HTTP 200 + original SHA-256, all ten source HTML URLs HTTP 200 and load; eleven intentionally removed deep links return 404. Check four galleries and one final PNG per series.
5. Document actual measured new `docs/` tree size; do not equate it with GitHub storage billing. Rollback via a new revert PR, never history rewriting.

No extra paid Cloudflare services, schedules, background polling, or standalone production runners.