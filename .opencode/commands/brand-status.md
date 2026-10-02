---
description: Report a brand's workflow stage, approvals, and next action
agent: brand-director
---

Act as brand-director. Report status for this brand:

$ARGUMENTS

Steps: resolve `brands/<slug>/` from the argument (if empty and exactly one brand exists, use it; otherwise ask which). Read `brand.json` + `status.md` (+ `decisions/` if present). Return: brand name, workflow stage, latest exploration, human approvals (only explicitly recorded ones — never infer), canonical status, next action. Do not change any files.
