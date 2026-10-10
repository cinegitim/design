# Publishing workflow (procedure)

Authority: `AGENTS.md` → Delivery rule. This file is the reusable procedure behind it.

One user request = one clean logical publish cycle (not many tiny commits/PRs):

1. Start from current `main` in an isolated checkout/worktree. Create a new, unique `publish/<topic>` branch for this request before production (Work: `publish/work-<topic>-<id>`; OpenCode: `publish/opencode-<topic>-<id>` recommended). Never reuse another executor's checkout or overwrite its branch.
2. Make the complete logical change (files + assets + gallery updates together).
3. Commit and push the branch.
   - If the request touches Asya'da Eğitim branded production, run `python3 studio/tools/verify_asyada_canonical_lockups.py` before committing. A failure stops the publish.
4. Open a PR against `main` (concise title/body, no identity claims beyond the change).
5. Run the independent submitted-file audit and inspect every required GitHub check for the exact PR head. Attach review evidence and handoff context. Failed/pending checks, unresolved substantive review blockers, unfinished work or an explicit user hold leave the PR open; report the blocker. A passing file audit is never visual/identity approval.
6. Under the standing repository policy, no additional merge confirmation is requested. Recheck current main/head; resolve technical conflicts and corrections without losing others' work, run affected local tests and await required checks on the new head. Do not blindly accept suggestions that alter creative decisions or locked artwork; those keep their existing human gates. Merge only the exact checked head when branch protection allows it, e.g. `gh pr merge <number> --merge --match-head-commit <checked-head-sha>`. Never force-push, bypass required checks, auto-approve aesthetics or enable an unconditional merge bot.
7. After merge, wait for the existing GitHub Pages deployment; check its status via API.
8. Verify the affected live Pages URL serves the change (HTTP 200 + content/hash check), then report published. Repository-only infrastructure has no new public URL; verify its merged files instead.
   - If shared instruction/tool sources changed, run the installed `ephemeral.py calibrate` against current main to refresh the private local baseline and launcher. This reads committed sources only; it never edits another task, regenerates imagery, or rewrites legacy checkouts. See `studio/work/BASELINE.md`.
9. For new manager-owned disposable clones, follow `studio/work/EPHEMERAL.md`: stop writers, leave/move the session out, dry-run `cleanup`, then `cleanup --pr <number> --apply`. Exact remote SHA, independent blob verification and passing exact-head PR CI gate deletion. Cleanup supports OPEN (for a held, safely archived PR) or MERGED PRs; it does not perform the merge itself. Preserve the source branch until cleanup has verified it. Do not clean legacy/platform checkouts.

Rules:
- Quick Tunnels (`/brand-preview`) are instant previews only — never the deliverable, never proof.
- Read-only work (status reads, reviews without edits) creates no commits.
- Never claim an unmerged branch is live on Pages. PR delivery and authorized publication are distinct states.
- Never force-push, reset/clean someone else's checkout, bypass branch protection or publish to social media.
- With connector-only access, pin reads to the base SHA, create a new branch, use explicit branch arguments for writes and expected-head leases. Re-read a changed head before retrying; never write to the default branch implicitly.
