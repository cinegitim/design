---
description: Publish a brand's review gallery through GitHub Pages and return the verified live URL
agent: brand-director
---

Act as brand-director. Publish review material for a brand:

$ARGUMENTS

Format: `<brand-slug>`. Resolve `brands/<brand-slug>/` (if empty and exactly one brand exists, use it; otherwise ask which).

Steps: 1. identify the brand's current gallery pages + referenced original images, 2. update ONLY that brand's public review files under `docs/<brand-slug>/` (never another brand, never studio root), 3. preserve original high-quality images, expose no internal notes/prompts/configuration/credentials, 4. publish through the normal GitHub workflow (`publish/<topic>` branch → open PR → explicit user authorization for that PR → merge to `main` per `studio/workflow/PUBLISHING.md`), 5. leave the PR open until merge authorization; only after the authorized merge, wait for the Pages build and verify the resulting GitHub Pages URL serves the change before returning it.

Quick Tunnel is NOT this command's path — for temporary previews use `/brand-preview` instead.
