---
name: production-router
description: Start Brandstudio design production from a natural-language request by detecting the execution environment, selecting a capability-aware route, and loading only the required brand and production skills.
---

# Brandstudio Production Router

When the user requests a visual brand, carousel, social post, identity
application, print asset or web-design production in this repository:

1. Read `studio/production/BOOTSTRAP.md`.
2. Detect the actual executor, model metadata and available tools before
   selecting a production strategy. Never invent model/version/capabilities.
3. Resolve exact brand and task category. Preserve original request unchanged.
4. Run the read-only `studio/production/router.py` when Python execution is
   available, or apply `studio/production/routes.json` manually.
5. Load the route's referenced existing Brand Studio skills, canonical assets
   and publishing rules. Respect locked identity and human approval gates.
6. Use a candidate strategy only as a production **method**, never as a new
   source of brand authority. Do not claim tokens/telemetry were collected.

This skill does not install tools, switch models, override `AGENTS.md`, create
a production output by itself or auto-activate in ordinary ChatGPT conversations.
