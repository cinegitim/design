---
description: Temporary instant preview of a brand gallery via Cloudflare Quick Tunnel (not delivery)
agent: brand-director
---

Act as brand-director. Temporary preview only:

$ARGUMENTS

Format: `<brand-slug>` or `<brand-slug> stop`. Resolve `brands/<brand-slug>/` (if empty and exactly one brand exists, use it; otherwise ask which).

- If arguments contain `stop`: read PIDs from `brands/<slug>/share-runtime/` (server.pid, cloudflared.pid, plus `server-seal.pid`/`cloudflared-seal.pid` where present) and terminate ONLY those processes. Report stopped PIDs. Do nothing else.
- Otherwise: 1. verify the brand's gallery files exist locally, 2. start/reuse `python3 -m http.server <port> --directory <gallery-dir>` in background (per-brand port; record PID), 3. start `cloudflared tunnel --url http://localhost:<port>` in background (record PID), 4. extract the https://*.trycloudflare.com URL, verify index returns HTTP 200 through it, 5. return the temporary URL with the warning that it dies with the tunnel.
- This command is OPTIONAL preview only. It must never count as delivery and never replaces GitHub Pages. Never expose anything outside that brand's gallery directory. Never invent team emails.
