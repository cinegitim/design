---
description: Start a new brand identity from a natural-language brief (any brand)
agent: brand-director
---

Act as brand-director using the brand-studio skill. Start a NEW brand identity from this brief:

$ARGUMENTS

If arguments are empty, use the most recent user message describing the brand as the brief. If the brief names an existing brand under `brands/`, work inside that brand's directory; otherwise scaffold via the `/brand-new` pattern first (directories + blank `brand.json`/`status.md`/`brand-brief.md`).

Pipeline (studio/workflow/WORKFLOW.md): 01 Brief (fill `brands/<slug>/brand-brief.md` from `studio/templates/brand-brief.md`, quick market/cultural research) → 02 Research → 03 Creative Territories → 04 HUMAN Territory Selection (stop, record in `decisions/`) → subsequent stages only after approval. This command covers 01–03, then stops for selection. Design genuinely different worlds; build hybrid boards (vector-first + budgeted raster per references/image-production.md); self-critique with actual multimodal inspection of any raster. Do not ask about colors, fonts, logo styles, or grids. Never borrow creative content (palette, type, marks, devices) from another brand — every brand starts blank. Do not build the system or applications yet.

Finish via `studio/workflow/PUBLISHING.md`: a new branch and open PR. Wait for explicit authorization to merge that PR; verify Pages only after an authorized publication.
