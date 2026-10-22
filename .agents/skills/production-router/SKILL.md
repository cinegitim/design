---
name: production-router
description: Routes Brandstudio design production for Instagram carousels, social graphics, print catalogs, website visuals, logos, new brand identities and brand applications. Use at the start of a natural-language design or branding request to identify runtime tools, resolve the approved brand, select a capability-aware production route and load the relevant skills.
---

# Brandstudio Production Router

When the user requests a visual brand, carousel, social post, identity
application, print asset or web-design production in this repository:

1. Read `studio/production/BOOTSTRAP.md`. For setup or test requests, read `studio/production/ACTIVATION.md` and use `activation_probe.py` without generating art.
2. Detect the actual executor, model metadata and available tools before
   selecting a production strategy. Never invent model/version/capabilities.
3. Resolve exact brand and task category. Preserve original request unchanged.
4. Run the read-only `studio/production/router.py` when Python execution is
   available, or apply `studio/production/routes.json` manually.
5. Load the route's referenced existing Brand Studio skills, canonical assets
   and publishing rules. Respect locked identity and human approval gates.
6. Use a candidate strategy only as a production **method**, never as a new
   source of brand authority. Do not claim tokens/telemetry were collected.
7. For `instagram-carousel`, enforce the `production_policies` contract in
   `routes.json`: editable HTML/CSS/SVG → exact canonical SVG placement →
   actual browser render → visual inspection/manifest. Do not use ImageGen to
   generate a finished branded slide by default, even when image tools exist.
   Image generation is limited to optional background/photo/illustration layers;
   the full-slide image experiment requires an explicit user choice.

## Optional style layer
Category and visual style are independent. When given an explicit style, resolve the exact brand/category-scoped manifest with `studio/production/style_catalog.py` or verify it manually from connected GitHub; presets and variation overrides are bounded by `variation_axes`. An unselected style remains null. Do not turn a review-only style into brand approval or bypass fixed SVG/HTML/Chromium production rules.

This skill does not install tools, switch models, override `AGENTS.md`, create
a production output by itself or auto-activate in ordinary ChatGPT conversations.
