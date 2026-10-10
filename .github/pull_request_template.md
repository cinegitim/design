## Request / change

Describe the human's request. Infrastructure change or creative delivery?

## Production and durable files

- [ ] Executor, brand, task branch/base SHA and changed paths recorded; isolated from concurrent OpenCode/Work tasks.
- [ ] Production environment and actually available tools recorded (or mark infrastructure-only; no production build).
- [ ] Originals, editable sources, recipe/dependency versions, exports and ZIP are committed / durably archived.
- [ ] New bundles registered in `studio/cloud/policy.json`; prior work preserved.
- [ ] Exact canonical SVGs used unchanged, required provenance hashes recorded.
- [ ] No secrets, sessions, runtime servers, caches or installed dependencies added.

## Actual checks / evidence

- [ ] `python3 studio/cloud/audit.py --root .` passed.
- [ ] GitHub's independent `submitted-files` check passed.
- [ ] Actual visual inspection + source/final or old/new comparison linked (if creative).

Image/model calls and available connectors:

Known limits / unresolved compromises:

## Human gate

Technical checks do NOT approve aesthetics, a logo or Instagram publication.
Creative work: leave PR open until the human accepts the shown visuals.
All work: leave PR open until the user explicitly authorizes merging this PR.
Implementation authorization, visual acceptance and merge authorization are separate.

## After authorized merge

- [ ] Pages deployment and live URLs/hashes verified.
