# Explicit legacy Design bulk-file pruning

This is separate from manager-owned task cleanup. It is **not** setup, a timer,
automatic migration or a general permission to delete legacy files. Use only after
the owner explicitly authorizes pruning the exact legacy folder. Current request:
remove space-consuming files from `Design`, retain small working instructions and
necessary infrastructure, and verify GitHub archival before deletion.

## Scope and safe defaults

`legacy_bulk_prune.py plan` does not delete anything. It selects regular raster/
media/package files of at least 1 MiB, not small source files. These are protected:
`.git`, `.opencode`, `.agents`, `.github`, `studio`, `figma`, and active `share`,
`share-seal`, `share-runtime` directories, plus installed dependency/cache roots.
Shared Git history, branches, stash and
linked worktrees remain intact. No other checkout is switched or deleted; active
preview servers are neither stopped nor deprived of their own files.

Candidates must exactly match a blob in a pinned, independently fetched GitHub
main tree. Archive paths may differ when the legacy file is a byte-identical
duplicate. Every selected remote blob is fetched from origin in the independent
task clone and hashed with SHA-256, not inferred from local Git status. Unique or
unverified files are retained. LFS content not present as a normal archived blob
is not eligible. A ZIP with equivalent entries but no exact container blob is
retained; this recipe never uploads runtime/metadata just to claim preservation.

## Procedure

1. Start a fresh isolated task/PR from current main and inspect other open PRs.
2. Confirm the target has no pending tracked/untracked user changes. Inspect linked
   worktrees and live preview paths; protect them. Do not remove the shared `.git`.
3. In the independent task, generate the immutable plan (all paths below are
   examples, not a permission to apply):

   ```sh
   python3 -B studio/work/legacy_bulk_prune.py plan \
     --target /absolute/legacy/Design --source /absolute/independent/task \
     --sha <fetched-main-sha> \
     --manifest studio/archive/<unique-round>/verified-plan.json
   ```

4. Review the exact per-file deletion list, archive locations, byte hashes,
   retained exceptions and total size. Run real-Git rejection/isolation tests.
5. Only under the existing explicit owner authorization, apply that plan:

   ```sh
   python3 -B studio/work/legacy_bulk_prune.py apply \
     --target /absolute/legacy/Design --source /absolute/independent/task \
     --manifest studio/archive/<unique-round>/verified-plan.json \
     --confirm-target /absolute/legacy/Design
   ```

   Apply validates the whole set again before modifying the target. Local hashes,
   file identity/mode, target HEAD, archive paths/blobs and totals must match.
   Dirty targets, existing sparse rules, symlinks, protected paths, shared proof
   object stores and new file changes stop the operation. After preflight, an
   external writer can still cause a partial operation; stop writers before applying
   and inspect any failure rather than blindly retrying.

6. Tracked files are omitted by an exact-file non-cone sparse-checkout pattern.
   This maintains a clean index: a later commit must not accidentally delete the
   GitHub originals. Byte-identical ignored duplicates are unlinked one by one.
   There is no broad recursive delete, branch reset, force push or stash drop.
7. Check clean target status and unchanged linked-worktree statuses; record the
   result, reclaimed logical bytes and retained exceptions. Commit the plan,
   recipe/tests and handoff in the isolated task, not in the sparsified legacy root.
   Required independent CI and standing checked-merge policy still apply.

## Continuing production / undoing local omission

Use the calibrated persistent launcher and new disposable clones for production.
Small boards/copy remain in `Design`, but non-active legacy boards referencing
omitted images may not fully display locally; GitHub/Pages copies are unchanged.
To restore a specific archived input locally, deliberately adjust this root's
sparse rules or use `git sparse-checkout disable` (the latter re-downloads/restores
all tracked material and defeats the disk saving). Never commit removal of the
GitHub archive as a side effect of local cleanup.

No imagery is regenerated, approved or published to social media in this process.
This does not authorize pruning the persistent foundation, global caches/auth,
other worktrees or `.git` after the current task ends.
