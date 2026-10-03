---
description: Refine the currently selected creative direction
agent: brand-director
---

Act as brand-director using the brand-studio skill. Refine the CURRENTLY SELECTED creative direction.

Refinement intent:
$ARGUMENTS

Steps: locate the current brand-system.md (brands/*/brand-system.md; if multiple, pick the most recently modified and say which), read it, apply the refinement intent in place (if empty, fix the weakest point from your last visual-quality critique), update brand-system.md first, then affected SVGs and boards, re-critique, preview, and present the delta. Never redesign from scratch unless explicitly asked.

Finish via the standing GitHub delivery workflow in AGENTS.md (procedure: studio/workflow/PUBLISHING.md) and verify the affected live Pages URL before reporting completion.
