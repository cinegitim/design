# P2 KAIST OpenCode output — recovered and corrected

**Local source:** OpenCode ephemeral clone `publish/opencode-opencode-p2-kaist-20261102` (reported local HEAD `e1893e2c1d214eb50ee6b949642ca0d2d5bb36b3`), inspected using Chrome's local file response. GitHub write was unavailable to local `iakfirat` account.

**Authenticated GitHub recovery:** ChatGPT's `cinegitim/design` GitHub connector copied **byte-identical** original HTML into `original/brand-system-demo.html` and imported the submitted metadata under `original/`. This GitHub commit is NEW and must **not** be presented as the original local OpenCode git commit.

- Original HTML length: **7186 UTF-8 bytes**, SHA-256: `5c29a53d8b42c89fda5ab118127afb91fd9ef066b7d291576e0624097dfc843d`, matches local `.sha256`.
- In the original HTML, all three images and one CSS link were broken because the relative paths went through the wrong directory. The corrected `brand-system-demo.html` changes **only** these four `href/src` attributes. Chrome loaded all three canonical images and the CSS with these corrected paths in a temporary DOM check.
- Corrected HTML SHA-256: `5b6e54b60ea0bfe1c50df9fc3d569e22332e2ca70687f291959ee3882528fce3`.
- H-02 uses the existing Git-identical published `docs/instagram/kaist-tech-track-2027-001/assets/h02-primary-horizontal-dark.svg`; V-01 uses the existing Git-identical published `docs/instagram/basvuru-rehberi-china-001/assets/v01-canonical.svg`. Approved logo bytes were **not** edited.
- The archived local TaskReceipt has `base_sha=f503...` rather than original TaskSpec's `base_sha=f44...` and reports stale `head_sha=206b...` rather than local branch HEAD `e189...`. The local handoff's `output_ref` points to an HTML file instead of the output directory; `received` was not remotely verifiable at time of local creation. Both are archived for forensic accuracy, **not valid normative protocol receipts**.
- The normalized receipt/envelope should be generated **outside this artifact commit** (e.g. in PR #196's coordinator branch), referencing the actual new GitHub commit: a file within its own commit cannot truthfully embed the enclosing commit SHA.
- No generated raster image, pixel QA or human creative approval has been completed. This is an **experimental source artifact** and must remain outside published social exports; original KAIST V2 sources are unchanged.

**Provenance:** Original design authored by local OpenCode per supplied agent logs; ChatGPT performed only credentialed recovery, broken-path repair and metadata audit. Do not assign work done by ChatGPT to OpenCode.
