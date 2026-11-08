# Asya'da Eğitim — canonical lockup approval (human final)

**Date:** 2026-10-08
**Status:** APPROVED / CANONICAL (human approval granted, recorded here)
**Scope:** Unified logo family only. No redesign, refit, retypeset, smoothing, optical adjustment, or alternative font.

## Approved inputs

- Turkish: Jost 550 (outlined paths from `tr550-en350-wordmark.svg`)
- English: Jost 350 (outlined paths from same source)
- Apostrophe: original approved red vector apostrophe from selected outlined source
- Common measure: 881 units for bilingual three-line wordmarks (P-01, H-02, C-03, F-05)
- Seal: `brands/asyada-egitim/assets/v01-canonical.svg`
- Seal SHA-256: `8f5d46f0302c4cc7e3765d3bfce9445f842dbd92f1e0f8fbe99f9f509c77e11a`
- Alignment approved: 0 (horizontal) / 0 (stacked-vertical). Alternatives retained as historical, not production.
- Source wordmark SHA-256: `668c0026043cf6ab2496c67feca152da37ad8348d2b6641a354a841b58e375f3`

## Approved variants (15 canonical SVGs)

- P-01 Primary stacked — light / dark / monochrome — min 352px / 75mm
- H-02 Primary horizontal — light / dark / monochrome — min 528px / 110mm
- C-03 Compact — light / dark / monochrome — min 448px / 95mm
- D-04 Small-use / digital — light / dark / monochrome — min 200px / 45mm — TURKISH ONLY
- F-05 Formal bilingual — light / dark / monochrome — min 352px / 75mm

All promoted from exact `*-0.svg` approved review assets with only title/metadata replaced. No artwork change.

## Manifest and verification

- Manifest: `brands/asyada-egitim/assets/lockups/canonical-lockups.json`
- Verifier: `studio/tools/verify_asyada_canonical_lockups.py` — must pass before any Asya'da Eğitim production publish; failure stops publishing.
- Gallery: `docs/asyada-seal/canonical-lockups/`
- Every final branded output records `canonical_lockup_id`, `canonical_lockup_sha256`, `canonical_seal_sha256`.

## Archive rule

W1/W2/W3, WU, smooth, A/B, weight-study, alternative alignments, and final-review assets are EXPERIMENTAL / NOT FOR PRODUCTION. Preserved for history; never selected by production workflows.

## Config enforcement

- `AGENTS.md`, `.opencode/commands/brand-apply.md`, `.opencode/agents/brand-director.md`, `.opencode/skills/brand-studio/SKILL.md`, `.opencode/skills/brand-studio/references/applications.md`, `studio/workflow/PUBLISHING.md` updated to require manifest-listed complete SVGs.
- CI: `.github/workflows/asyada-canonical-lockups.yml` runs seal + lockup verification on relevant changes.
