# Brand Status (operational state — updated only on explicit human decisions)

## Language-specific canonical logos — current (2026-11-04)

The user approved the complete English-only **Education in Asia V9** on 2026-11-04.
Both languages share the same approved V-01 seal and **one canonical source directory**, `assets/lockups/`, but are separate lockup families:

- **Türkçe (tr):** existing H-02, P-01 and F-05 bilingual/Turkish brand signatures, Jost 550/350, approved 2026-10-08. Original `assets/lockups/canonical-lockups.json` and hashes remain unchanged.
- **English (en):** H-EN-02 horizontal (default) and P-EN-01 stacked, light/dark/monochrome, Jost 450 main and 350 five-country subtitle, approved 2026-11-04. Authority: `assets/lockups/canonical-english-lockups.json`, checksum `f8379cfc30602121d2fd773edd7297cf0d576c4cdd262c71077b504db95f9c7d`.
- Choose the intended language before selecting a complete, unchanged canonical SVG. The English line within a bilingual Turkish logo is not the approved English-only logo.
- Brandstudio presents both language families on `docs/identity/index.html` and `docs/workspaces/asyada-egitim/logos-and-covers/index.html` under distinct headings. No separate review gallery or active older English logo versions remain.
- Old English V6–V8.1/V9 review **SVG copies** were removed from the working repository; historic Git commits and decision records remain auditable. Do not restore obsolete review SVGs to production or generation workflows.


- Workflow stage: **canonical seal and complete lockup family locked** (human approval 2026-10-08; metadata reconciled 2026-10-10)
- Client-approved territory: the seal. Territory/world exploration closed.
- Client-approved visual direction: **V-01**
- Canonical identity status: **CANONICAL**
- Production work allowed: **YES**, within the locked-asset rules below
- Current next action: apply the canonical logo to applications; every output
  records the canonical hash
- Lockup system: **APPROVED / CANONICAL**, P-01 / H-02 / C-03 / D-04 / F-05,
  light / dark / monochrome, alignment 0. D-04 is Turkish-only.
  Authority: `decisions/2026-10-08-canonical-lockup-approval.md`, `brand.json`,
  `assets/lockups/canonical-lockups.json`. Complete SVGs only.
- Full `brand-system.md`: **not present**. Approved identity is defined by the
  sources above; application specifications and Instagram templates remain
  review-only. Never use the separate `brands/asya-egitim/brand-system.md`.

## Historical proposals (superseded by 2026-10-08 approval)

The following describes the earlier review stage, not the current production state:

- Lockup system: **PROPOSED, 5 variants, human selection pending**
  (`brands/asyada-egitim/decisions/2026-10-07-lockup-system-proposal.md`,
  review page `docs/asyada-seal/lockups/`). Not canonical. No variant selected.
- Wordmark: **PROPOSED, 3 fidelity levels (W1/W2/W3), human selection pending**
  (`brands/asyada-egitim/decisions/2026-10-08-wordmark-reference-rebuild.md`,
  review page `docs/asyada-seal/wordmark/`). Rebuilt against the approved
  typographic reference. Not canonical. No candidate selected.
  The 2026-10-07 lockup family is NOT rebuilt on these yet — the wordmark is
  approved first, then the lockup family follows.

## Locked assets

| Asset | Path | SHA-256 |
|---|---|---|
| V-01 logo (canonical) | `brands/asyada-egitim/assets/v01-canonical.svg` | `8f5d46f0302c4cc7e3765d3bfce9445f842dbd92f1e0f8fbe99f9f509c77e11a` |

Decision record: `brands/asyada-egitim/decisions/2026-10-07-v01-canonical-lock.md`

Verify before any production work:

```sh
studio/tools/verify-canonical-logo.sh
python3 studio/tools/verify_asyada_canonical_lockups.py
```

## Generation rules for this brand

1. **Never** ask an image model to draw, recreate, imitate or typeset the logo.
2. **Always** composite the exact canonical SVG.
3. Image models generate visual / background / composition only.
4. Allowed logo placement changes: position, size, clearspace, approved
   colour variant. **Geometry never changes.**
5. Flat design with branding inside: reserve a clean logo-safe area during
   generation, then composite the canonical SVG afterward.
6. Perspective or physical surfaces: **do not** regenerate the logo. Flag for
   the separate perspective/mockup workflow, which also uses the canonical asset.
7. Every final branded output records `canonical_logo_sha256` in its manifest.

## Superseded (history, not canonical)

- `brands/asyada-egitim/assets/v01-seal.svg` — earlier contour trace
- `brands/asyada-egitim/assets/v01-seal-favicon.svg` — earlier 16px variant
- `brands/asyada-egitim/assets/v01-lockup-primary.svg` — earlier lockup
- `docs/asyada-seal/v01-micro/assets/micro-A{1,2,3}.svg` — comparison candidates
- `docs/asyada-seal/v01-audit/assets/a2.svg` — audited pre-fix candidate

None of these may be used as a production logo asset.
