# Brand Status (operational state — updated only on explicit human decisions)

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
