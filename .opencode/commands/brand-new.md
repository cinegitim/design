---
description: Scaffold a new independent brand directory (no design, no images)
agent: brand-director
---

Act as brand-director using the brand-studio skill. Scaffold a NEW brand from this name:

$ARGUMENTS

Steps: derive a kebab-case slug, create `brands/<slug>/` with subdirectories (`explorations/`, `boards/`, `decisions/`, `assets/`, `applications/`, `share/`, `archive/`), copy `studio/templates/brand-manifest.json` → `brand.json` (fill name/slug, status `brief`, approvals null/false), `studio/templates/brand-status.md` → `status.md`, `studio/templates/brand-brief.md` → `brand-brief.md` (leave unfilled), plus `decisions/README.md` and `explorations/README.md`. Then ask the user to provide the brief (the next step is `/brand`, not auto-started). Do NOT generate a logo, image, colors, or visual direction. Do NOT inherit styling, palette, typography, or logic from any other brand.

Finish via `studio/workflow/PUBLISHING.md`: a new branch and open PR. Wait for explicit authorization to merge that PR; verify Pages only after an authorized publication.
