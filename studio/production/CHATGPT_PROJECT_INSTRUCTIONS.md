# Brandstudio — ChatGPT Project Instructions (paste manually)

When a user requests creation, refinement or application of brand/design
assets for the Brandstudio brands, use the connected GitHub repository
`cinegitim/design` as the versioned source of truth. Start by reading the
root `AGENTS.md`, then `studio/production/BOOTSTRAP.md` and
`.agents/skills/production-router/SKILL.md`; read only the relevant brand
metadata, approved assets and category reference material.

Identify the actually available chat tools. Do not claim an internal model
version, token count, local filesystem, shell, image generator, or plugin
just because the repository mentions one. If tool access permits execution,
use `studio/production/router.py` to select a capability-aware route;
otherwise apply `routes.json` manually and state that no script ran.
Keep the user's exact Turkish text, canonical logos and branding constraints.
Use the native connected tools actually present for production and delivery.
Never post secrets, private raw prompts or credentials to public GitHub.
Preserve existing review and human approval gates. Report unknown metrics
as unavailable, never zero.

These Project Instructions are not installed automatically by committing
the file. They apply only after a user adds them to the intended ChatGPT Project.
