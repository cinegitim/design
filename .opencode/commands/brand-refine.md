---
description: Refine the currently selected creative direction
agent: brand-director
---

Act as brand-director using the brand-studio skill. Refine the CURRENTLY SELECTED creative direction.

Refinement intent:
$ARGUMENTS

Steps: locate the current brand-system.md (brands/*/brand-system.md; if multiple, pick the most recently modified and say which), read it, apply the refinement intent in place (if empty, fix the weakest point from your last visual-quality critique), update brand-system.md first, then affected SVGs and boards, re-critique, preview, and present the delta. Never redesign from scratch unless explicitly asked.

**Locked logo gate:** if `brands/<slug>/brand.json` has `canonicalLogo.locked`, `/brand-refine` does **not** touch the logo. The canonical asset is immutable — not re-traced, not re-fitted, not smoothed, not simplified, not re-typeset. If the refinement intent targets the logo itself, say so plainly, refuse, and point at what can be refined instead (application, layout, colour use, typography). Changing a canonical logo requires an explicit new human decision and a new record in `brands/<slug>/decisions/`. Run `studio/tools/verify-canonical-logo.sh` to confirm it is untouched.

Finish via the standing GitHub delivery workflow in AGENTS.md (procedure: studio/workflow/PUBLISHING.md) and verify the affected live Pages URL before reporting completion.
