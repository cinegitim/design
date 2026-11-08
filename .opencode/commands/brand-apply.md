---
description: Propagate the established identity into requested applications
agent: brand-director
---

Act as brand-director using the brand-studio skill. Propagate the ESTABLISHED identity into requested applications.

Requested applications:
$ARGUMENTS

Steps: resolve the exact brand from the user's brief and metadata/decisions, never modification time. Read its brand-system.md; if missing, disclose the gap and follow the identity-source exception in AGENTS.md, without borrowing a sibling system or declaring campaign templates canonical. Derive assets from these sources with correct sizes/safe zones per references/applications.md, build outputs in a unique brands/<slug>/applications/<task>/ directory, self-critique, preview, and present. Never invent orphan colors, fonts, or devices. If vague, choose valuable real touchpoints for that brand's category.

## Locked logo gate — run before any raster work

Check `brands/<slug>/brand.json` for `canonicalLogo.locked`. If it is locked:

1. Run `studio/tools/verify-canonical-logo.sh`. If it fails, stop and restore from git — do not continue.
2. **Never** ask an image model to draw the logo. Image models generate background / composition / texture only.
3. Composite the exact repo-root-relative `canonicalLogo.path` from `brand.json` onto every output that shows the logo.
4. Only placement may change: position, size, clearspace, approved variant. Geometry never changes.
5. Logo inside a flat design → reserve a clean logo-safe area during generation, composite the SVG after.
6. Logo on a perspective or physical surface → do not regenerate. Flag it for the perspective/mockup workflow, which warps the same canonical asset.
7. Write `canonical_logo_sha256` into the output's manifest before reporting completion.

## Canonical lockup gate — Asya'da Eğitim

If `brands/<slug>/brand.json` has `canonicalLockups.locked`:

1. Run `python3 studio/tools/verify_asyada_canonical_lockups.py`. If it fails, stop publishing.
2. Use only complete SVGs listed in `brands/<slug>/assets/lockups/canonical-lockups.json`, or the existing locked seal when seal-only use is appropriate.
3. Do **not** reconstruct a lockup from separate seal and wordmark geometry. Do **not** typeset the brand name, substitute fonts, recolour outside approved variants, crop, distort or perspective-transform.
4. For Asya'da Eğitim, D-04 is Turkish-only. Never add English to it.
5. If the layout cannot accommodate an approved lockup at minimum size and clearspace, flag the constraint or use a different approved variant; do not modify the design.
6. Every final branded output manifest must record `canonical_lockup_id`, `canonical_lockup_sha256`, and `canonical_seal_sha256`.

If the logo is not locked, follow references/image-production.md normally.

Finish via `studio/workflow/PUBLISHING.md`: new branch → PR → exact-head required checks → lossless technical corrections → rerun checks → checked merge without another confirmation → verify Pages. Honor explicit PR holds; creative/identity approval remains human-only.
