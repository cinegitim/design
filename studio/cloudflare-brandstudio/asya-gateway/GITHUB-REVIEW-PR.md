# Brandstudio — Visual Editor → GitHub review PR (stage-1)

## Scope

The authorized administrator may submit a **saved Cloudflare Durable Object revision** of one design from Visual Editor to the public \`cinegitim/design\` repository as a **draft review PR**.

- This is an **explicit** button click, never triggered by autosave or publication syncing.
- Submission uses the exact \`product + version + expectedSha\` of a persisted cloud record. The server reads state from the Durable Object, ignores client-supplied state, and fails with 409 if a concurrent save changed its revision.
- A new branch named \`studio/editor-<product>-v<version>-<revision>\` is created from current \`main\`. The PR changes only \`studio/production/editor-proposals/<product>/v<version>-<revision>.json\`.
- The JSON stores a portable \`savedState\` overlay, linked to the original source HTML/CSS/SVG. It does **not** claim that edited HTML was generated, rendered, published, or creatively approved.
- Existing branches/PRs are never overwritten. Repeated submission of the same revision returns the existing PR; an abandoned branch without a verifiable PR requires manual reconciliation.
- PRs default to **draft**; human review, source/brand checks, rendering and CI are independent prerequisites to merging or publication.

## Security and free-only operation

The browser has no GitHub API key. The Cloudflare gateway handles the same-origin authenticated API \`POST /visual-editor/api/github-pr\` and requires an explicit public-repository confirmation. The request includes only identifiers and consent, not arbitrary files or script. On GitHub failure it does not claim a PR was made.

**Deployment prerequisite:** Provision \`GITHUB_PR_TOKEN\` as a **Cloudflare Worker secret** for \`brandstudio-edge\` on the corporate Asya'da Eğitim Cloudflare account. Use a GitHub fine-grained token limited to **\`cinegitim/design\` only**, with **Contents: read/write** and **Pull requests: read/write**; do not add the token to GitHub, frontend source, chat, commit history, or Cloudflare plaintext vars. Prefer an equivalent short-lived GitHub App installation credential in a future hardening phase. Rotate/revoke credentials when staff access changes.

Until the secret exists, endpoint returns **503** and no repository changes are made. The PR is not live until the reviewed code is merged and the \`brandstudio-edge\` Worker is deployed, with binding and secret confirmed.

Use Cloudflare Workers Free and GitHub's normal REST API; there is no recurring Cron, background agent, automatic paid deployment, Workers AI, or new storage service. API use and GitHub workflow quotas still count under provider free-tier limits; monitor them.

**Privacy:** The repository is *public*. Embedded edited image bytes or draft copy in the selected editor state become publicly accessible on the PR branch. The UI asks for an explicit, informed confirmation; do not submit confidential or unlicensed material.

## Verification before enabling

1. Run \`node --test studio/cloudflare-brandstudio/tests/github-pr.test.mjs\` plus existing editor/style/gateway regression tests.
2. Inspect the new branch and draft PR for accidental secrets or changes outside the review JSON.
3. Deploy only to the intended Cloudflare Worker after an explicit review; leave current admin login and Durable Object bindings untouched.
4. From an authenticated editor, save a non-sensitive test revision; submit it; verify exactly one draft PR, matching product/version/sha, correct \`savedState\`, and no \`main\` change.
5. Confirm no-token 503, unauthenticated 401, cross-origin 403, unsaved/stale 409, repeat-click idempotency and GitHub permission failures.
6. Revoke test credentials if no longer needed.

## Remaining phases

This first stage records the precise editable overlay as a reviewable PR artifact. A future source-materialization phase must produce and browser-render updated HTML/CSS/SVG and pass official logo/render regression checks before any reviewed design is promoted to a published source. Social-media post/version reconciliation remains independent and must be evidence-based.
