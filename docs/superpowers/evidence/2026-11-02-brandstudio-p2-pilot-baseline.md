# P2 Pilot Baseline — 2026-11-02

**Status:** read-only intake verified; real OpenCode → Work handoff **NOT RUN**.

| Signal | Observed |
| --- | --- |
| Repository | `cinegitim/design`, `main` |
| Source SHA (pinned) | `2d0e36aeabeb147d8ec6c5a284d9d3cdad8cf9cd` |
| Pilot | `docs/instagram/kaist-tech-track-2027-001/v2/` |
| Pilot manifest Git blob SHA-1 | `d4893dbb5f226d01d00bb57414ab67ea88fe3a99` |
| Editable source 03 Git blob SHA-1 | `c81d962850bfcaaf7da97179b05724f6538ba997` |
| Editable source 06 Git blob SHA-1 | `66d45715c882a60098f2139b760e1b2af52580c0` |
| Render JPEG 03 Git blob SHA-1 | `6748eca73ab6d1dfcdff214ac0da2f1c230f5f02` |
| Render JPEG 06 Git blob SHA-1 | `c35ab23d042463aa5bbc00c90ced0ad4e8c36e91` |
| Existing brand H-02 SVG Git blob SHA-1 | `0469f6cab3ec46c93c1d4494aa725ae7432e1cb7` |
| Canonical H-02/dark SHA-256 claimed in existing KAIST manifest | `c9eb55f95a60924f34e6f7b043e81216963441833a4f158ff882d710cc8dd1e7`; not re-hashed during this read-only observation |
| Source format | 6 HTML files, 6 JPEG exports |
| Approval | in-review; creative_approved=false; social_published=false |
| Prior local handoff coverage | `studio/work/tests/test_ephemeral.py::test_executor_handoff_uses_explicit_parent_branch_and_new_clone` is a **simulation**, not live agent proof |
| GitHub host | Connector GitHub read+write capability observed in this ChatGPT conversation |
| OpenCode host | Not available as an executable tool in this session; no real-run receipt |
| Dedicated ChatGPT Work host | Not confirmed; ordinary ChatGPT with GitHub connector cannot be relabeled as Work |
| Browser origin | `https://studio.asyadaegitim.com/` in isolated Chrome context redirects to access-protected admin login; no post-login editor audit |
| Cloudflare actions | None |
| Paid model/API calls | None from this P2 intake |

**Boundary:** Git's 40-character blob SHA-1 and content SHA-256 are different. This table only proves remote repository metadata observed through GitHub; not screenshot/pixel equality, working OpenCode agent status, approved publication or completed design.

**Next gates:** P2 design review → test-first handoff adapter → real independent source and receiving host evidence → exact-head CI → creative review for any new output. No historical KAIST assets will be overwritten.
