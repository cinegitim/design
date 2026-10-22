# Production Bootstrap: activation and live smoke-test checklist

This document separates **discovery readiness** from **observed activation**.
Repository rules do not run a process by themselves. The repo is not a globally
installed ChatGPT plugin, and a GitHub connection does not synchronize sessions.

## Zero-write diagnostic (any local checkout)

```sh
python3 studio/production/activation_probe.py
python3 -m unittest discover -s studio/production/tests -v
python3 studio/production/router.py --executor codex \
  --brand asyada-egitim --category instagram-carousel \
  --capability filesystem --capability terminal
```

The probe establishes file-layout readiness only. Its executable inventory
is not proof of the **currently running model** or of tool access by the agent.
The last command simulates a Codex capability set: those capabilities must
be established in the real execution environment before an actual run.

## Repository-local agents: no global installation required

- **Codex (repo checkout):** Start in the repository worktree. Codex reads the
  repository-root AGENTS.md and exposes .agents/skills/production-router.
  Try the ordinary request: "Asya'da Eğitim için beş slaytlık Instagram
  karuseli üret; başlamadan önce hangi production route'u seçtiğini ve
  bunu hangi runtime kanıtına dayandırdığını söyle." Check that Bootstrap
  is read, the canonical brand is selected and an actual route is reported.
  Do not create assets in this *smoke test*.
- **OpenCode (repo checkout):** Start within the same Git worktree and use the
  same prompt. OpenCode discovers repo-local .agents/skills and AGENTS.md.
  Check available skills using the native skill tooling; do not infer the
  active model from configured defaults. Do not install a version-specific
  plugin until the installed OpenCode version and hook API are verified.
- **Antigravity (repo workspace):** Open the repository as an Antigravity
  workspace. Its current Rules system reads root AGENTS.md and its Skills
  system discovers .agents/skills. Use the same prompt and inspect skill
  invocation/which files were read. Do not use legacy Workflows: those
  were retired on 2026-10-19 in favor of Agent Skills.

## Ordinary ChatGPT: separate activation

A ChatGPT chat is not a repository checkout. Repo AGENTS.md/skills are not
implicitly installed by adding GitHub. For a dedicated ChatGPT Project, paste
the short text in `CHATGPT_PROJECT_INSTRUCTIONS.md` into Project Instructions
using the ChatGPT UI. Ensure access to the GitHub account/repository, then
use a natural-language request and explicitly inspect which files were read.
In a chat without Python/file execution, the agent can apply routes.json
manually, but must not claim to have run router.py.

## Acceptance evidence for *each* real host

Record only factual observations, without storing private prompts or secrets:

- Executor and where its identity was observed.
- Actual model identifier from host/provider metadata, or "unavailable".
- Whether AGENTS.md and the production-router skill were loaded.
- Whether Bootstrap and exact brand.json were read.
- Selected route, capabilities with supporting evidence, and fallback reason.
- "No design generation" for the smoke test.
- If anything did not activate, note the step and version; do not mark PASS.

These fields are a manual activation checklist in v1.1. Host-native model hooks,
automatic usage/latency instrumentation, ChatGPT Project installation and
end-to-end creation are **not yet implemented**. Do not claim this diagnostic
has validated them.

## Source of truth

Existing root `AGENTS.md` and publishing/brand rules remain authoritative.
A route cannot override canonical logos, approved lockups or human decisions.
Any real production belongs on an isolated publish branch with exact-head
GitHub checks. Do not run a creative generation as part of discovery testing.
