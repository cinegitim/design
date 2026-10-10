---
name: brand-studio
description: Create, refine or apply visual brand identities and campaign assets in ChatGPT Work or Codex. Follow the shared methodology, exact approved assets and human creative gates; deliver via a separate branch, checked PR merge and verified publication.
---

# Brand Studio — Work / Codex adapter

Read `AGENTS.md` and `studio/work/README.md` first. Then read the complete
`.opencode/skills/brand-studio/SKILL.md` and its required `references/` files.
These files remain the **single methodology source**, not a second copied skill.
All paths here are repository-root-relative.

Map user requests to the existing workflows:
- New identity → three different visual worlds → human A/B/C choice → fidelity transfer → human logo approval.
- Refinement → preserve direction; update the system before derived assets.
- Applications → approved system and exact canonical marks; required formats and safe zones.
- Explicit senior review → advisory, never automatic approval; don't assume legacy models are available.
- Other studio commands → read the matching `.opencode/commands/*.md` as guidance, not installed Codex commands.

Resolve the exact brand from the brief and metadata/decision records, never from
mtime. Check that its system exists and its status matches recorded approvals.
Do not transfer the sibling `asya-egitim` system to `asyada-egitim`; for the latter,
use the approved identity sources plus the selected, review-only application spec.
Start each production on its own branch/checkout and run `studio/work/preflight.py`.

Tool availability is environment-specific. OpenCode plugin names are not Codex
tool registrations. Route native Work imagery as described in `studio/work/README.md`;
do not load adapter credentials. Never claim generation or visual inspection without actually
running the tool / reading the image. No automatic paid/API fallback. If an image
connector is absent, work vector-first or disclose the blocked raster step.
Headless rendering uses the pinned Playwright recipe, not a desktop browser tool.

For production/delivery also read `.agents/skills/cloud-delivery/SKILL.md`.
Deliver through `studio/workflow/PUBLISHING.md`: open a PR, inspect required exact-head
checks, resolve technical conflicts/corrections, rerun checks, then merge without
an additional confirmation when all checks pass and no substantive blocker remains.
An explicit user hold leaves that PR open. Creative/identity approval, locked-artwork
changes and social publication remain separate human gates; CI is not aesthetic approval.
