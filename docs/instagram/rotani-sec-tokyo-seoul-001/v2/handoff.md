# Studio task handoff — Rotanı Seç #001 / V2

- Request / scope: Full visual redesign plus deterministic typography for the six-slide Instagram carousel "Rotanı Seç #001 — Tokyo mu, Seul mü?", with the new locked copy contract.
- Executor: OpenCode in a local macOS temporary task clone (not cloud execution).
- Brand slug and sources: `asyada-egitim`; `brand.json`; canonical lockup manifest; locked V-01 decision; user V2 brief. No full brand system is claimed.
- Branch / base: `publish/opencode-rotani-seoul-001-v2-20261012` / `ececf3f944316432bdc409db55fe6b22ca571d7e`.
- Task head SHA: `ad2dc31bf9b6a595702f35975bee84c1b2a056de`
- Merge SHA: `9d65053b8d9796fa610495663939f9c325082f68`
- Changed paths: `docs/instagram/rotani-sec-tokyo-seoul-001/v2/` (new), `.../v1/index.html` (V1 archive), campaign root `index.html` (now leads with V2), `docs/instagram/index.html`, `studio/cloud/policy.json`.
- Image calls: 2 image generations (disclosed illustrative housing interiors on slide 05), 0 image edits, 0 text/logo generations.
- Sources / exports: `v2/final/*.png`, `v2/source/*.svg|html`, `v2/templates/`, `v2/originals/`, `v2/assets/photos/originals/`, `v2/mobile/`, `v2/contact-sheet.png`, `v2/v1-vs-v2-contact-sheet.jpg`, `v2/source-vs-final-contact-sheet.jpg`, `v2/manifest.json`, `v2/package/rotani-sec-tokyo-seoul-001-v2.zip`.
- Canonical assets: `D-04/dark` slide 01; `D-04/light` slides 02–05; `H-02/dark` slide 06 at 540px (approved minimum 528px). All unmodified, hash-verified.
- Checks: exact copy PASS; geometry audit 6/6 slides zero overlaps/clipping/logo collisions; logo contrast gate PASS; canonical verifier PASS; cloud audit PASS; cloud tests 14 PASS; work tests 81 PASS; CI `submitted-files` PASS on PR #88.
- Human decisions: seal and lockup family are canonical. V2 campaign aesthetic and social publication remain pending human review.
- Live delivery: https://cinegitim.github.io/design/instagram/rotani-sec-tokyo-seoul-001/ (V2 leads; V1 archive at `v1/`). Live HTML, manifest, contact sheet and all four checked PNGs match committed SHA-256 byte-for-byte. No social publication performed.
- Remaining constraints: slide 05 housing interiors are disclosed illustrative AI generations, not documentary photography.
