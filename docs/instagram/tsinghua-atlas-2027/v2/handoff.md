# Studio task handoff

- **Request / scope:** Remove two unsolicited footnotes from the Tsinghua Atlas V2 carousel and clean matching descriptive text in its gallery/captions. Keep factual-source and photo-license reports separate; preserve V1 slide artwork and editable sources.
- **Executor:** OpenCode, manager-owned isolated local task clone.
- **Brand slug and application sources:** `asyada-egitim`; use existing approved identity metadata and canonical lockup SVGs with the campaign application spec. No identity artwork changed.
- **Task branch / base SHA / current head:** `publish/opencode-tsinghua-copy-cleanup-20261010` / `6b4538d9ee2293d662a231065bede356214e5de8` / pending commit.
- **Changed paths:** V2 build/render sources, exports, package, gallery and QA/source reports; descriptive copy on the existing gallery and V1 caption/source notes. V1 PNG, SVG/HTML slide artwork, and manifest remain unchanged; the earlier V2 delivery remains in Git history.
- **Generation/edit calls:** no image-generation/editing model used. Rebuilt editable SVG/HTML and rendered the same seven campaign slides and previews with Node 22.23.3, Playwright, Chromium 141.0.7390.37, Python 3.12/Pillow 12.0.0. Re-used existing photos and canonical lockups. Removed two appended slide footnotes; preserved the seven first-render PNGs under `originals/`, and retained citations and required photo credits in separate files.
- **Outputs:** seven 1080×1350 sRGB PNGs, editable SVG/HTML, mobile previews, contact sheets, gallery, manifest and ZIP under `docs/instagram/tsinghua-atlas-2027/v2/`.
- **Checks:** preflight PASS; environment doctor PASS after sparse checkout was expanded to the registered bundles and lockup/preservation assets; Chromium render and package verification PASS; canonical-lockup verifier PASS (15 records); full audit PASS; cloud tests PASS (14); work tests PASS (81); gallery/resource browser smoke PASS (7 pages); disclaimer-copy grep returned no matches in the active gallery/source/report paths. Exact-head CI remains to be run.
- **Human decisions:** V-01 and lockup approvals remain recorded in their existing decision files. No new identity decision made.
- **Remaining:** publish this update through a PR, pass exact-head CI, merge per repository policy, and verify Pages hashes. No Instagram publishing is part of this request.
- **Delivery:** PR and exact-head review state are tracked in GitHub; this handoff records the production state before publication.
- **After merge:** verify the live gallery, updated exports, and ZIP against the merged commit.
