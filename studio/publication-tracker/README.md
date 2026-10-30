# Brandstudio — Instagram Publication Tracker (production; future providers opt-in)

**Purpose:** On-demand Instagram publication discovery and read-only live Brandstudio proof display without a powered-on Mac, Chrome MCP, or paid social APIs. Facebook, LinkedIn and X remain optional and disconnected.

## Verified deployment (2026-10-30)

- **Production Instagram:** Meta Graph API Professional account via secure Cloudflare Worker secrets; the existing D1 records include **8 real posts: 6 uniquely anchored design-family proofs, 2 unmatched needs-review posts**. Old human-verified exact revision claims remain in the canonical GitHub registry and always take precedence.
- **Worker:** `brandstudio-publications` in Cloudflare account `5f90104db6f24a941c04e974e250cb67`. D1 `brandstudio-publications` (`397061ae-723c-4070-b6f8-a332e179cd78`) bound as `DB`.
- **No automatic trigger:** All Cron schedules are disabled. The authenticated dashboard's **Yayınları denetle** button calls `/admin/publications/refresh` on `brandstudio-edge`, which forwards only an Instagram refresh over a private service binding. The official Instagram API is queried **only on explicit click**. A normal page load only reads stored proof.
- **Dynamic UI:** Design workspace, Visual Editor and gallery pages augment the published GitHub registry with `GET /api/proofs`. Only `family_verified` Instagram posts from the official API with a unique natural-language caption anchor appear. No browser token, browser-side API writes, version guessing or automatic canonical-registry commits.
- **Source of truth:** The GitHub `socialPublication.posts` log continues to be immutable human-verified historical proof; D1 is an additive runtime discovery layer and must never overwrite exact historical decisions.
- **Safety:** Missing/expired Meta access or network errors never erase old proof. Dashboard can inspect `GET /api/status` and D1 `publication_runs` for last run. Do not declare a scan healthy solely because a Worker is deployed.

## Service design

- **Meta:** Free official Facebook Page `/{page-id}/posts` plus Instagram Professional `/{ig-user-id}/media`. Create a Meta developer app and authorize an admin of the managed Page; obtain the minimum Page-read/Instagram-read scopes. Requires a Professional Instagram account and Page linkage for Facebook Login. This account-owner authorization must be performed by a person with the permissions. Store access tokens as **Cloudflare Worker secrets**, never in a browser bundle, public repository or ChatGPT message. Review token expiry and refresh before production.
- **LinkedIn:** Community Management API, **if approved** for `r_organization_social`. Development tier is free, but not automatic access. OAuth by a Company Page admin is mandatory. Add `LINKEDIN_ORG_ID` and short-lived `LINKEDIN_TOKEN` as secure runtime config; implement safe token renewal before production.
- **X:** Optional best-effort public RSS mirror (allowlisted hosts only) if one remains available; it is **not** an official X API, can break without notice and is not reliable enough to prove absence. Existing real X permalinks captured at publishing time are more dependable. Do not depend on paying for the X API or guarantee RSS access.
- **Cloudflare:** Workers Free and a dedicated D1 database; **no cron, no background polling**. POST `/api/refresh` remains blocked without an administrator secret and retrieves selected platforms on demand. Free-tier limits are hard caps; never automatically upgrade.
- **Match policy:** Only a unique pre-registered caption anchor (or sufficiently distinctive complete title) on an official Instagram post can create a `family_verified` record. This remains **family-level**, never exact-revision proof; `product_id` stays null. Fuzzy candidates stay `family_candidate`/ `needs_review`, invisible to the public proof overlay. New Instagram designs should register a unique 16+ character natural caption phrase under `publicationAnchors` in `docs/visual-editor/browser/product-groups.json`.

- **Data policy:** Never automatically delete prior discovered posts when a platform is blocked, returns errors or has no new results. Avoid a platform “not published” label if scanning was incomplete.

## D1 database

Provision new database `brandstudio-publications`, run `studio/publication-tracker/schema.sql`. Bind it to the Worker as `DB`. Isolate from current Brandstudio editor D1 databases. Keep the known `brandstudio-edge` and `brandstudio-editor-store` Workers untouched.

## Worker configuration

Worker name: `brandstudio-publications`. Deploy `worker.mjs` as a module alongside `match.mjs` using a compatible bundler (Wrangler). Set:
- required `PUBLICATION_REFRESH_TOKEN` as a secret and D1 binding `DB`
- Meta: `META_IG_ID`, `META_PAGE_ID`, `META_PAGE_TOKEN` (and optional `META_IG_TOKEN`)
- LinkedIn: `LINKEDIN_ORG_ID`, `LINKEDIN_TOKEN`, `LINKEDIN_VERSION` (e.g. `202609`)
- optional X: `X_RSS_URL` (a permitted public mirror only; not a credential)

Read-only `GET /health`, `GET /api/status`, `GET /api/posts?groupId=...` and public **filtered** `GET /api/proofs`; authenticated `POST /api/refresh` with `Authorization: Bearer <refresh secret>` and optional `{"platforms":["instagram","facebook","linkedin","x"]}`. This secret must not be embedded in the public webpage: integrate with existing Brandstudio admin authentication or use a server-side administrator workflow before enabling a public UI button. The first deploy must use test-only connection credentials, not live ones. A request failure must not mark a post as removed.

## Future providers and remaining tasks

Run `node --test studio/publication-tracker/match.test.mjs`.

Before connecting to the live Brandstudio UI:
1. Verify the three connected accounts and granted access; ensure read scopes are valid and token renewal is safely implemented.
2. Execute D1 schema migration and create secret/config bindings. Verify unauthorized refresh returns 401.
3. E2E test fetching 10 real posts per provider, timestamps and permalink validity. In particular check LinkedIn URN-based links in the actual browser.
4. Test X mirror availability from Cloudflare; if blocked, leave it disabled and use publishing-time permalink receipts.
5. Audit actual family matching against canonical source artwork; never infer the published revision from a text-only similarity score.
6. Build a reviewed, logged-in UI button and a read-only public post display. Confirm exact-head CI, PR merge and an explicit Cloudflare Pages deployment.

No source-only PR or CI result constitutes credentials approval, live post discovery or successful deployment.

## Reproducible production configuration

See `wrangler.toml` in this directory. It pins the account, Worker name, D1 database and cron trigger. Secrets `META_IG_ID`, `META_IG_TOKEN` and `PUBLICATION_REFRESH_TOKEN` live in Cloudflare **secret bindings**, not in the repository. For routine uploads, ensure these existing bindings are inherited strictly (the Workers API `bindings_inherit=strict`) and confirm D1/secret bindings survive and Cron schedules remain **empty**. Do not replace tokens or enable a paid plan.

For release checks: `node --test studio/publication-tracker/match.test.mjs docs/instagram/publication-bridge.test.mjs`; verify Worker deployments include `fetch` and no `scheduled` handler, confirm Cron schedules are **empty**, inspect last `publication_runs` row, and confirm custom-domain Cloudflare Pages deploy is on the exact merged Git commit. Browserless smoke tests do not authorize publishing content to social networks.

## Admin-only manual check

- Dashboard route: `POST https://studio.asyadaegitim.com/admin/publications/refresh` (existing trusted-device admin session, `Origin` checked). The browser never sees an API token. Only this button triggers Meta API reads; closing the page or not clicking triggers none.
- Backend: `brandstudio-edge` has a `PUBLICATION_TRACKER` service binding to `brandstudio-publications` and a private `BRANDSTUDIO_PUBLICATION_BRIDGE_TOKEN` secret. The tracker Worker has the matching secret and retains its other existing bindings. Never commit or log the shared value. The forwarder always uses `platforms: ['instagram']` and ignores client choices.
- `GET /admin/publications/status` returns last-scan metadata from D1 (no Instagram request). A successful click refreshes the gallery to display newly verified family links. Candidate matches remain review-only.
- Cloudflare Workers Free + D1 Free; no automation, webhook, chargeable provider or recurring schedule. Confirm `GET /api/status` says `on_demand_only` and `/schedules` is `[]` after any Worker deployment.
