# Brandstudio — Publication Tracker (serverless candidate)

**Purpose:** On-demand publication discovery without a powered-on Mac, a browser MCP connection, paid social APIs, background polling or creative source changes.

## Status / release gate

Source-only implementation. **NOT connected, NOT deployed and NOT a production-ready automatic publication proof.** Do not show an enabled “Güncelle” control until service health, admin authentication, D1 migration and real Meta/LinkedIn account authorizations are tested. Never claim a platform was checked merely because a source file exists.

This module deliberately avoids editing `docs/visual-editor/browser/product-groups.json`, any prior human publication decisions or historical assets. Its `publication_posts` table is supplemental and cannot silently supersede the existing `socialPublication.posts` proof. To show new records in a product card, add a separate reviewed UI integration after auth.

## Service design

- **Meta:** Free official Facebook Page `/{page-id}/posts` plus Instagram Professional `/{ig-user-id}/media`. Create a Meta developer app and authorize an admin of the managed Page; obtain the minimum Page-read/Instagram-read scopes. Requires a Professional Instagram account and Page linkage for Facebook Login. This account-owner authorization must be performed by a person with the permissions. Store access tokens as **Cloudflare Worker secrets**, never in a browser bundle, public repository or ChatGPT message. Review token expiry and refresh before production.
- **LinkedIn:** Community Management API, **if approved** for `r_organization_social`. Development tier is free, but not automatic access. OAuth by a Company Page admin is mandatory. Add `LINKEDIN_ORG_ID` and short-lived `LINKEDIN_TOKEN` as secure runtime config; implement safe token renewal before production.
- **X:** Optional best-effort public RSS mirror (allowlisted hosts only) if one remains available; it is **not** an official X API, can break without notice and is not reliable enough to prove absence. Existing real X permalinks captured at publishing time are more dependable. Do not depend on paying for the X API or guarantee RSS access.
- **Cloudflare:** Workers Free and a dedicated D1 database; **no cron**. POST `/api/refresh` is intentionally blocked without an administrator secret and only retrieves selected platforms on request. Free-tier limits are hard caps; never automatically upgrade.
- **Match policy:** Text-title family suggestions are candidates, not proofs of an exact revision. `product_id` stays null and uncertain matches stay `needs_review`. The existing exact Instagram revision confirmations must be preserved separately until an explicit reconciliation review.
- **Data policy:** Never automatically delete prior discovered posts when a platform is blocked, returns errors or has no new results. Avoid a platform “not published” label if scanning was incomplete.

## D1 database

Provision new database `brandstudio-publications`, run `studio/publication-tracker/schema.sql`. Bind it to the Worker as `DB`. Isolate from current Brandstudio editor D1 databases. Keep the known `brandstudio-edge` and `brandstudio-editor-store` Workers untouched.

## Worker configuration

Worker name: `brandstudio-publications`. Deploy `worker.mjs` as a module alongside `match.mjs` using a compatible bundler (Wrangler). Set:
- required `PUBLICATION_REFRESH_TOKEN` as a secret and D1 binding `DB`
- Meta: `META_IG_ID`, `META_PAGE_ID`, `META_PAGE_TOKEN` (and optional `META_IG_TOKEN`)
- LinkedIn: `LINKEDIN_ORG_ID`, `LINKEDIN_TOKEN`, `LINKEDIN_VERSION` (e.g. `202609`)
- optional X: `X_RSS_URL` (a permitted public mirror only; not a credential)

Read-only `GET /health`, `GET /api/status`, `GET /api/posts?groupId=...`; authenticated `POST /api/refresh` with `Authorization: Bearer <refresh secret>` and optional `{"platforms":["instagram","facebook","linkedin","x"]}`. This secret must not be embedded in the public webpage: integrate with existing Brandstudio admin authentication or use a server-side administrator workflow before enabling a public UI button. The first deploy must use test-only connection credentials, not live ones. A request failure must not mark a post as removed.

## Tests and remaining tasks

Run `node --test studio/publication-tracker/match.test.mjs`.

Before connecting to the live Brandstudio UI:
1. Verify the three connected accounts and granted access; ensure read scopes are valid and token renewal is safely implemented.
2. Execute D1 schema migration and create secret/config bindings. Verify unauthorized refresh returns 401.
3. E2E test fetching 10 real posts per provider, timestamps and permalink validity. In particular check LinkedIn URN-based links in the actual browser.
4. Test X mirror availability from Cloudflare; if blocked, leave it disabled and use publishing-time permalink receipts.
5. Audit actual family matching against canonical source artwork; never infer the published revision from a text-only similarity score.
6. Build a reviewed, logged-in UI button and a read-only public post display. Confirm exact-head CI, PR merge and an explicit Cloudflare Pages deployment.

No source-only PR or CI result constitutes credentials approval, live post discovery or successful deployment.
