# AI Brand Studio

**OpenCode and ChatGPT Work share one studio; GitHub preserves and independently audits.**

- [Operating instructions](AGENTS.md)
- [ChatGPT Work capability map, branch workflow and handoffs](studio/work/README.md)
- [Cloud architecture and production commands](studio/cloud/README.md)
- [One-time ChatGPT/Codex account activation](studio/cloud/ACTIVATION.md)
- [Live cloud handover guide](https://cinegitim.github.io/design/cloud/)
- [Latest launch experiment — human review pending](https://cinegitim.github.io/design/instagram/launch-creative-02/)

`brands/`, `studio/`, `docs/`, `.agents/` and `.opencode/` adapters are
durable project sources. CI is audit-only: no render, model/image calls or
OpenAI API key. Existing Pages serves committed review assets.

The repository configuration does not activate a cloud account or prove an
image connector is available. Complete the activation checklist and first
actual cloud test before retiring local working folders. No local files are
deleted by this migration. Technical CI success is never creative approval.

Every new production uses a separate branch/checkout and ends in an open PR.
Merge only after explicit user authorization; existing GitHub Pages publication
remains unchanged. Work reads repository skills explicitly when they are not
auto-discovered; connecting GitHub alone does not install OpenCode commands.
