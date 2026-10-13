---
description: Run a ChatGPT Image exploration round for a specific brand
agent: brand-director
---

Act as brand-director using the brand-studio skill. Run an image-exploration round:

$ARGUMENTS

Format: `<brand-slug> <round/instruction>`. Steps: resolve `brands/<brand-slug>/`, read its `brand-brief.md`, `status.md`, and selected creative territories. Use ChatGPT Image as the primary exploration medium (one call per interpretation, no auto-retries). Preserve every original output untouched under `brands/<brand-slug>/explorations/<round>/`. Never auto-select a winner, never auto-convert results to SVG, never canonicalize. All directions remain CLIENT VISUAL SELECTION PENDING until explicitly approved and recorded in `decisions/`.

**Locked logo gate:** if `brands/<brand-slug>/brand.json` has `canonicalLogo.locked`, the logo is excluded from every exploration prompt and image model call. Exploration covers territories, textures, scenes and compositions only; the canonical SVG is composited afterward per references/image-production.md. Never let a model redraw, imitate or typeset a locked logo, and never let a generated result overwrite the canonical asset.

Finish via `studio/workflow/PUBLISHING.md`: new branch → PR → exact-head required checks → lossless technical corrections → rerun checks → checked merge without another confirmation → verify Pages. Honor explicit PR holds; creative/identity approval remains human-only.
