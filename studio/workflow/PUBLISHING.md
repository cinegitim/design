# Publishing workflow (procedure)

Authority: `AGENTS.md` → Delivery rule. This file is the reusable procedure behind it.

One user request = one clean logical publish cycle (not many tiny commits/PRs):

1. Work locally in the repo on a `publish/<topic>` branch.
2. Make the complete logical change (files + assets + gallery updates together).
3. Commit and push the branch.
   - If the request touches Asya'da Eğitim branded production, run `python3 studio/tools/verify_asyada_canonical_lockups.py` before committing. A failure stops the publish.
4. Open a PR against `main` (concise title/body, no identity claims beyond the change).
5. Merge to `main`, pull locally.
6. Wait for the GitHub Pages build; check build status via API.
7. Verify the affected live Pages URL serves the change (HTTP 200 + content check).
8. Only then report completion.

Rules:
- Quick Tunnels (`/brand-preview`) are instant previews only — never the deliverable, never proof.
- Read-only work (status reads, reviews without edits) creates no commits.
- Never report done before the live site proves it.
