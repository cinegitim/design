---
description: Propagate the established identity into requested applications
agent: brand-director
---

Act as brand-director using the brand-studio skill. Propagate the ESTABLISHED identity into requested applications.

Requested applications:
$ARGUMENTS

Steps: read the canonical brands/*/brand-system.md (if none exists, say so and run /brand first; if multiple, pick the most recently modified and say which), derive every asset strictly from system tokens with correct sizes/safe zones per references/applications.md, build HTML/SVG outputs under brands/<slug>/applications/, self-critique, preview, and present. Never invent orphan colors, fonts, or devices. If the request is vague, choose the most valuable real touchpoints for the brand's category.

## Locked logo gate — run before any raster work

Check `brands/<slug>/brand.json` for `canonicalLogo.locked`. If it is locked:

1. Run `studio/tools/verify-canonical-logo.sh`. If it fails, stop and restore from git — do not continue.
2. **Never** ask an image model to draw the logo. Image models generate background / composition / texture only.
3. Composite `brands/<slug>/assets/<canonicalLogo.filename>` onto every output that shows the logo.
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

Finish via the standing GitHub delivery workflow in AGENTS.md (procedure: studio/workflow/PUBLISHING.md) and verify the affected live Pages URL before reporting completion.
