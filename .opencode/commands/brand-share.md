---
description: Share a brand's review material via local server + Cloudflare Quick Tunnel
agent: brand-director
---

Act as brand-director. Share review material for a brand:

$ARGUMENTS

Format: `<brand-slug>` or `<brand-slug> stop`. Resolve `brands/<brand-slug>/` (if empty and exactly one brand exists, use it; otherwise ask which).

- If arguments contain `stop`: read PIDs from `brands/<slug>/share-runtime/` (server.pid, cloudflared.pid) and terminate ONLY those two processes. Report stopped PIDs. Do nothing else.
- Otherwise (start/share): 1. identify the brand's latest review board + referenced original images, 2. rebuild ONLY that brand's isolated `brands/<slug>/share/` (index.html + assets/ only; no prompts, credentials, .env, OpenCode config, source files, notes, keys), 3. verify every image path exists, 4. start/reuse `python3 -m http.server <port> --directory <share>` in background (per-brand port; log to `brands/<slug>/share-runtime/server.log`, record PID), 5. start `cloudflared tunnel --url http://localhost:<port>` in background (log to `brands/<slug>/share-runtime/cloudflared.log`, record PID), 6. extract the https://*.trycloudflare.com URL, verify index + one asset return HTTP 200 through it, 7. return the public URL.
- Never expose anything outside that brand's `share/`. Never expose the studio root or another brand. Never invent team emails; `--allowed-mail <addr>` is documented for a future account-based Access setup (plain Quick Tunnels do not support email gating without a Cloudflare account — do not claim otherwise).
