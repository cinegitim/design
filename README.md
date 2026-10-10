# AI Brand Studio

**OpenCode and ChatGPT Work/Codex can both design and produce; GitHub is their shared source and independent audit layer.**

- [Operating instructions](AGENTS.md)
- [ChatGPT Work capability map, branch workflow and handoffs](studio/work/README.md)
- [Cloud architecture and production commands](studio/cloud/README.md)
- [One-time ChatGPT/Codex account activation](studio/cloud/ACTIVATION.md)
- [OpenCode without a user-machine project checkout: remote execution boundary](studio/cloud/REMOTE-OPENCODE.md)
- [Chosen setup: temporary OpenCode + cloud Codex, verified task cleanup](studio/work/EPHEMERAL.md)
- [Live cloud handover guide](https://cinegitim.github.io/design/cloud/)
- [Latest launch experiment — human review pending](https://cinegitim.github.io/design/instagram/launch-creative-02/)

`brands/`, `studio/`, `docs/`, `.agents/` and `.opencode/` adapters are
durable project sources. CI is audit-only: no render, model/image calls or
OpenAI API key. Existing Pages serves committed review assets.

The repository configuration does not activate a cloud account or prove an
image connector is available. Complete the activation checklist and first
actual cloud test before retiring local working folders. No local files are
deleted by this migration. Technical CI success is never creative approval.

GitHub is not an execution host by itself. The chosen setup uses one temporary
disk root locally for OpenCode, with isolated disposable task clones; Work/Codex
uses its own cloud workspace. Sources/exports remain on GitHub, then verified
task clones (and their Git object stores) can be removed without merging the PR.
This needs no paid VM, is not a RAM disk and does not erase legacy folders,
OpenCode sessions or installed tool caches. Remote execution is optional.

Every new production uses a separate branch/checkout and ends in an open PR.
Merge only after explicit user authorization; existing GitHub Pages publication
remains unchanged. Work reads repository skills explicitly when they are not
auto-discovered; connecting GitHub alone does not install OpenCode commands.
