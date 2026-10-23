# Brandstudio — personal Cloudflare account, isolated staging

Account: iakfiratt@gmail.com (Cloudflare account ID b462aa1499215378fe7f671a788c8a3c).
Never configure this project under info@asyadaegitim.com. Never touch its
existing website or preview Workers; leave personal chat-handoff-v1 untouched.

Current **staging bridge** only, not the final migrated production site:

- Worker \`brandstudio-stage\` on personal workers.dev: proxies **read-only** static
  paths from the original \`https://cinegitim.github.io/design/\`.
  This deliberately preserves all existing galleries and relative URLs during migration.
  It is **not** static-asset migration: the GitHub Pages origin remains required.
- D1 database \`brandstudio-stage\` has a separate private/public product catalog,
  append-only version schema, but API only exposes public product metadata reads.
- All API writes are **disabled** until a real authentication/authorization mechanism
  and appropriate durable image/source storage are connected. No generated output is
  marked approved merely because it is listed or saved.
- \`/api/health\`: read-only app/database check; \`/api/products\`: *public* catalog.
- No domain/DNS cutover. This stage is a test URL only and carries \`X-Robots-Tag: noindex\`.

## Intended final Cloudflare topology (not yet deployed)

1. Wrangler Workers Static Assets upload the **actual** \`docs/\` tree into Cloudflare,
   removing the upstream proxy dependence. Avoid wholesale removal or renaming of URLs.
2. Access (or a comparably secure server-side authentication service) protects editor
   and write endpoints, with origin/CSRF controls, per-user authorization and audit logs.
3. D1 stores product metadata, append-only editor states, version sequence and render
   job status. Never treat D1 as unlimited media file storage.
4. R2 stores source/raster packages and immutable render artifacts when enabled.
5. A trusted production builder with Chromium executes renders, validates canonical
   P-01 SVG and hash, and stores outputs. Workers do **not** silently render native
   local Python builds, nor can they reach an unconnected Mac.
6. GitHub keeps canonical assets and reviewed source, PR/CI controls and audit trail;
   publishing approved versions remains explicit, with a checked PR.
7. Only after source and media are independently mirrored and routed/tested should
   a custom domain be selected and switched. Existing GitHub Pages remains available
   throughout. \`asyadaegitim.com\` is a separate website and is not changed here.

## Verification

\`\`\`sh
cd studio/cloudflare-brandstudio
node --test tests/worker.test.mjs
python3 -m sqlite3 :memory: ".read migrations/0001_initial.sql"
npx wrangler d1 migrations apply brandstudio-stage --remote
npx wrangler deploy
\`\`\`

The last two commands require actual authorized credentials in the personal
Cloudflare account. This repo does not contain credentials, private drafts,
Cloudflare API tokens or secret login links.

Status:
- Staging D1: created in personal account.
- Staging Worker: not proven deployed merely by this repository's files.
- R2: dashboard activation required.
- Access: dashboard activation required.
- Source-assets migration and private editor saves: not complete.

No private personal briefs, source images, generated final exports or passwords
are committed by this infrastructure PR.
