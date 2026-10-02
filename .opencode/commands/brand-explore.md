---
description: Run a ChatGPT Image exploration round for a specific brand
agent: brand-director
---

Act as brand-director using the brand-studio skill. Run an image-exploration round:

$ARGUMENTS

Format: `<brand-slug> <round/instruction>`. Steps: resolve `brands/<brand-slug>/`, read its `brand-brief.md`, `status.md`, and selected creative territories. Use ChatGPT Image as the primary exploration medium (one call per interpretation, no auto-retries). Preserve every original output untouched under `brands/<brand-slug>/explorations/<round>/`. Never auto-select a winner, never auto-convert results to SVG, never canonicalize. All directions remain CLIENT VISUAL SELECTION PENDING until explicitly approved and recorded in `decisions/`.
