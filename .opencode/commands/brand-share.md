---
description: Publish a brand's review gallery through GitHub Pages and return the verified live URL
agent: brand-director
---

Act as brand-director. Publish review material for a brand:

$ARGUMENTS

Format: `<brand-slug>`. Resolve `brands/<brand-slug>/` (if empty and exactly one brand exists, use it; otherwise ask which).

Steps: 1. identify the brand's current gallery pages + referenced original images, 2. update ONLY that brand's public review files under `docs/<brand-slug>/` (never another brand, never studio root), 3. preserve original high-quality images, expose no internal notes/prompts/configuration/credentials, 4. follow `studio/workflow/PUBLISHING.md` (`publish/<topic>` branch → PR → required checks on exact HEAD → lossless technical corrections → rerun checks → checked merge without another confirmation), 5. honor explicit PR holds and unresolved substantive review blockers; after merge, wait for Pages and verify the live URL/hashes. Review-page delivery is not creative/identity approval or social publication.

Quick Tunnel is NOT this command's path — for temporary previews use `/brand-preview` instead.
