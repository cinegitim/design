---
description: Refine the currently selected creative direction
agent: brand-director
---

Act as brand-director using the brand-studio skill. Refine the CURRENTLY SELECTED creative direction.

Refinement intent:
$ARGUMENTS

Steps: resolve the exact brand from the brief and metadata/decisions, never modification time. Read its system and apply the refinement intent (if empty, fix the weakest point from the last critique). If the system is missing, disclose it and refine only the selected application spec/brief against approved identity sources per AGENTS.md. Update the relevant system/spec before derived SVGs and boards, re-critique, preview, and present the delta. Never redesign from scratch unless explicitly asked.

**Locked logo gate:** if `brands/<slug>/brand.json` has `canonicalLogo.locked`, `/brand-refine` does **not** touch the logo. The canonical asset is immutable — not re-traced, not re-fitted, not smoothed, not simplified, not re-typeset. If the refinement intent targets the logo itself, say so plainly, refuse, and point at what can be refined instead (application, layout, colour use, typography). Changing a canonical logo requires an explicit new human decision and a new record in `brands/<slug>/decisions/`. Run `studio/tools/verify-canonical-logo.sh` to confirm it is untouched.

Finish via `studio/workflow/PUBLISHING.md`: a new branch and open PR. Wait for explicit authorization to merge that PR; verify Pages only after an authorized publication.
