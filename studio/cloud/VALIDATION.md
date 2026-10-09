# Migration validation / boundaries

This infrastructure migration was bootstrapped from the existing OpenCode
environment; **it did not run inside an activated Codex Cloud account**. No image
generation or campaign rebuild occurred. Existing canonical marks, launch sources,
five final PNGs and delivery ZIP remain unchanged.

Verified before publishing:
- Read-only audit passes for 15 canonical lockups and the current five-slide bundle.
- All preserved creative/documentary files match source bytes; the 291 duplicate
  archive/ZIP entries match the recorded baseline Git blobs.
- 14 checker tests cover actual delivery, wrong PNG dimensions, altered visible
  copy with a recomputed hash, unapproved logo hash, stale ZIP manifest, path escape,
  symlink escape, hash/CRC corruption, unsafe geometry, credential detection,
  retained bundle policy and Python import-shadow isolation.
- Production dependencies resolve as compatible Python 3.12 Linux binary wheels.
- Playwright 1.56.1 lockfile integrity checked against published registry metadata;
  CLI location uses the exported package.json, not an unexported subpath.
- Handover guide viewed at 375 and 1440px; no horizontal overflow. Actual screenshots
  inspected: clear status notice and readable installation steps. Hierarchy 9,
  consistency 9, aesthetics 8, usability 9 (documentation, not a new brand board).
- Independent infrastructure review fixed two High issues before publication:
  unsupported Playwright CLI export and Python PR-directory import shadowing.

GitHub CI is a separate Linux execution of the **audit only**, not a production
rebuild. Its run/check links are visible from the PR and workflow page. Passing it
does not prove the Codex account install, native image tools, Linux raster fidelity,
actual OCR or aesthetic acceptance. Complete ACTIVATION.md and save a real cloud
test PR before declaring cutover or removing any local working folder.
