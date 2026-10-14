# Studio task handoff

- Request: background-filled social avatar series and browser icons for Çin Eğitim design gallery.
- Executor: Codex desktop, local macOS; isolated clone; no Cloud account/runtime activation claim.
- Brand: cin-egitim; sources brand.json, canonical-lockups.json, 2026-10-10 symbol decision; application-spec.md.
- Base main: 58318c2d0265924c60c0f21a37f233b4c0c71913. Branch: publish/work-cin-egitim-social-avatars-20261015.
- Prerequisite: PR #105 adds the independent avatar contract without weakening existing carousel audit or trusted-base CI. Merged as d9a7a29; this series now registers against that trusted base checker.
- Calls: zero image/edit/model API calls; stdlib SVG composition, rsvg-convert 2.63.0 PNG rasterization. setup.sh rejected local Python 3.14; pinned Linux campaign recipe was not run.
- Original: assets/canonical-symbol.svg exact canonical bytes. Canonical SHA-256: 1cc1808947d8f7f759ebb9956a715d535bb4fcc985d3f85194d4eaf1a85c7381.
- Output: 9 SVG + PNG pairs, editable build.py, application spec, manifest, gallery, fonts/OFL and ZIP.
- Existing approval: canonical symbol and P-01 family selected; applications remain produced/reviewable. No social account upload or whole-system approval claim.
- Validation: file/geometry/hash/PNG/ZIP audit, visual QA documented separately. Main gallery includes direct previews, Downloads and an opaque favicon.
- Delivery: checked PR merge and Pages live hash verification required. Local clone was created directly, not manager-owned; do not adopt/delete it with ephemeral cleanup.
