# Publishing workflow (procedure)

Authority: `AGENTS.md` → Delivery rule. This file is the reusable procedure behind it.

One user request = one clean logical publish cycle (not many tiny commits/PRs):

1. Start from current `main` in an isolated checkout/worktree. Create a new, unique `publish/<topic>` branch for this request before production (Work: `publish/work-<topic>-<id>`; OpenCode: `publish/opencode-<topic>-<id>` recommended). Never reuse another executor's checkout or overwrite its branch.
2. Make the complete logical change (files + assets + gallery updates together).
3. Commit and push the branch.
   - If the request touches Asya'da Eğitim branded production, run `python3 studio/tools/verify_asyada_canonical_lockups.py` before committing. A failure stops the publish.
4. Open a PR against `main` (concise title/body, no identity claims beyond the change).
5. Run the independent submitted-file audit and inspect CI for the exact PR head. Attach review evidence and handoff context. Leave the PR open and report **PR ready; publication pending**. This applies to infrastructure as well as creative work.
6. Only after the user explicitly authorizes merging this PR: recheck current main/head, resolve conflicts without losing others' work, rerun affected checks and merge. An approval of visuals does not itself authorize a merge.
7. After authorized merge, wait for the existing GitHub Pages deployment; check its status via API.
8. Verify the affected live Pages URL serves the change (HTTP 200 + content/hash check), then report published. Repository-only infrastructure has no new public URL; verify its merged files instead.

Rules:
- Quick Tunnels (`/brand-preview`) are instant previews only — never the deliverable, never proof.
- Read-only work (status reads, reviews without edits) creates no commits.
- Never claim an unmerged branch is live on Pages. PR delivery and authorized publication are distinct states.
- Never force-push, reset/clean someone else's checkout, auto-enable merging or publish to social media.
- With connector-only access, pin reads to the base SHA, create a new branch, use explicit branch arguments for writes and expected-head leases. Re-read a changed head before retrying; never write to the default branch implicitly.
