---
name: brand-studio
description: Create, refine or apply visual brand identities and campaign assets. Follow the existing Brand Studio methodology and human approval gates; use Codex Cloud for production and GitHub for durable delivery.
---

# Brand Studio — Codex adapter

Read `AGENTS.md` at the repository root first. Then read the complete
`.opencode/skills/brand-studio/SKILL.md` and its required `references/` files.
These files remain the **single methodology source**, not a second copied skill.
All paths here are repository-root-relative.

Map user requests to the existing workflows:
- New identity → three different visual worlds → human A/B/C choice → fidelity transfer → human logo approval.
- Refinement → preserve direction; update the system before derived assets.
- Applications → approved system and exact canonical marks; required formats and safe zones.
- Explicit senior review → advisory, never automatic approval; don't assume legacy models are available.
- Other studio commands → read the matching `.opencode/commands/*.md` as guidance, not installed Codex commands.

Tool availability is environment-specific. OpenCode plugin names are not Codex
tool registrations. Never claim generation or visual inspection without actually
running the tool / reading the image. No automatic paid/API fallback. If an image
connector is absent, work vector-first or disclose the blocked raster step.
Headless rendering uses the pinned Playwright recipe, not a desktop browser tool.

For production/delivery also read `.agents/skills/cloud-delivery/SKILL.md`.
Never merge creative work without the human's acceptance of the actual visuals.
