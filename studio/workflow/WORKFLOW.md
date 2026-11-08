# Brand Studio workflow (15 stages)

01 Brief — natural-language brief → `brands/<slug>/brand-brief.md` (from `studio/templates/brand-brief.md`, inferred, never a questionnaire)
02 Research if requested — market/cultural context via web tools
03 Creative Territories — distinct worlds (`studio/templates/creative-territories.md`)
04 Human Territory Selection — recorded in `decisions/` (gate)
05 ChatGPT Image Exploration — round folders, originals untouched, comparison board
06 Human Visual Selection — recorded (gate)
07 Deeper Exploration if needed — further rounds, same rules
08 Human Direction Approval — recorded (gate)
09 Visual DNA Extraction — Layer A from the source image
10 Fidelity Reconstruction — toward the source, essential vs incidental
11 Source-vs-Reconstruction Review — side by side, "same brand?"
12 Human Identity Approval — recorded (gate; AI review advisory only)
13 Canonicalization — `brand-system.md` (Layer A + B), production assets
14 Application Grammar — 12-rule system grammar per brand
15 Production Applications — derived only from the canonical system

Human approval is mandatory at 04, 06, 08, 12. No LOCKED/CANONICAL/APPROVED status without it.
Methodology: `.opencode/skills/brand-studio/` (authoritative). Templates: `studio/templates/`.
