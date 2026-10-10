# AI Brand Studio — ChatGPT Work adapter

One repository, one methodology, two executors. OpenCode keeps its agents,
commands and plugins. Work reads the same sources and uses tools exposed in its
current conversation. This adapter neither installs a plugin nor changes models.
The existing `docs/` panel and GitHub Pages deployment remain intact.

Current workspace choice: [EPHEMERAL.md](EPHEMERAL.md). OpenCode produces locally
in a single owned temporary root; Work/Codex produces in its own cloud temporary
root. Important bytes and handoff records go to GitHub, then verified task clones
can be removed without merging. No paid remote VM is required. Cleanup is only
for new manager-owned clones, never the platform's existing checkout or legacy files.

## Start a Work request

1. Read root `AGENTS.md`, `.agents/skills/brand-studio/SKILL.md`, the shared
   `.opencode/skills/brand-studio/SKILL.md`, required reference files, and
   `.agents/skills/cloud-delivery/SKILL.md`. Read them explicitly through GitHub
   when repository skills are not automatically discovered.
2. Resolve the brand from the request, `brand.json`, status and decision records.
   Never select by mtime. `asyada-egitim` is the approved seal/Jost identity;
   `asya-egitim` is a separate older exploration, not a fallback system.
3. Inspect current main and open PRs. Create a unique branch from that main SHA
   in a separate checkout/worktree before any production. Recommended name:
   `publish/work-<topic>-<date-or-id>`; OpenCode uses
   `publish/opencode-<topic>-<date-or-id>`. Existing `publish/<topic>` names remain
   valid. Never reuse another active task's branch or working directory.
4. Run `python3 studio/work/preflight.py --root . --brand <slug>`.
   This is read-only: branch check, exact locked source hashes, missing system
   warning and local runtime inventory. Use `--read-only` for an audit on main.
   Session connector availability must be checked in the conversation separately.
5. Translate the brief to the workflow below. Preserve originals in unique
   exploration/application folders. Maintain sources, exact-copy manifests,
   exports and evidence; register supported delivery bundles in cloud policy.
6. Audit and open a PR. Follow PUBLISHING.md: inspect required checks on exact HEAD,
   resolve technical conflicts/corrections, rerun checks and merge without another
   confirmation when no substantive blocker remains. Honor an explicit user hold.
   Pages serves main, so unmerged branch work is not live there. After checked merge,
   verify deployment and live files; then verified task cleanup. No social posting.

Example request (no OpenCode command installation needed):

> Asya'da Eğitim için yeni bir carousel hazırla. AGENTS.md ve Work adapter'ını
> oku; güncel onaylı kimlik ve belirttiğim uygulama referansını kullan. Ayrı bir
> branch'te çalış, orijinalleri koru, denetle ve PR aç. PUBLISHING.md'deki exact-head
> denetim ve teknik düzeltme kapılarından sonra ek onay istemeden merge et; yayını doğrula.

## Workflow mapping

| Intent / OpenCode command | Work action | Human gate |
|---|---|---|
| `/brand-new` | Scaffold an independent brand; no borrowed identity | Brief before design |
| `/brand` | Three distinct territories/boards using the existing methodology | Human territory choice; no auto-development |
| `/brand-explore` | Authorized native image exploration; untouched originals and comparison | Visual/direction selection |
| `/brand-refine` | Update the selected system/spec, then derived applications | Locked logo remains untouched; exact-head required checks |
| `/brand-apply` | Exact approved identity + system/selected application spec → exact-size assets | New campaign output remains review-only |
| `/brand-status` | Read metadata and actual decisions; no changes | No commit/PR for read-only status |
| `/brand-review` | Explicit advisory review of the named stage/artifact | No automatic model switch or approval |
| `/brand-share` | Prepare existing `docs/` gallery in a new branch and PR | Exact-head checked merge, then Pages verification; not identity approval |
| `/brand-preview` | Available temporary preview; source-only if browser unavailable | Preview is not publication |

## Capability and backend routing

| Capability | Work route | Boundary |
|---|---|---|
| Repo reads, branch, files/commits, PR, CI | Connected GitHub plugin; Git checkout where available | Pin reads; explicit target branch; compare current SHA before writes |
| Research and factual copy | Available web search/retrieval | Verify current claims with primary sources; preserve source links |
| HTML/CSS/SVG, copy, manifests | Workspace editing and existing templates | Typography/layout/approved marks stay deterministic |
| New raster / image edits | Exposed native Work image-generation tool, when the user request or workflow authorizes images | Not the `.opencode/plugins/gpt-image` credential adapter; no private endpoint calls |
| Raster inspection | Actual image input / available image viewer | Never infer quality from a prompt, filename or hash |
| PNG/export/package | Existing pinned cloud recipe, after setup/doctor succeeds | Setup does not create artwork; not every historical recipe is portable |
| Browser/preview | Exposed preview tools or pinned headless Chromium | Source checks do not prove visual quality |
| Figma | Separate `figma/` rules and any actually available connector | Do not activate or change the isolated Figma layer in this migration |
| Model routing | Current conversation model | OpenCode model names/config do not switch Work or establish cost/quota |

Native image tools are not automatically installed by repo files. Check the
actual tool set each task. This migration performs no test generations or image
calls. If no native tool is available, continue with authorized existing imagery
and vector assets; disclose a blocked raster step. Never silently call a paid API,
assume free quotas, import local OpenCode auth files, or change provider settings.

Keep the shared raster budget (normally 0–3, maximum 6 for initial three-direction
exploration, one targeted correction per direction). A requested larger campaign
needs an explicit campaign budget; do not infer it from historical generation
counts. No automatic retries. Keep exact Turkish copy and wordmarks outside the
image model. Locked logos are never image-model inputs to be redrawn: composite
complete approved SVGs afterward, using manifest min size/clearspace and hashes.

When native generation returns a repository deliverable, use its actual returned
file/path or supported download mechanism to preserve original bytes in the task
branch, then inspect and checksum them. A chat image alone is not a GitHub studio
delivery. If byte retrieval/upload is unavailable, mark that step blocked; never
claim it was committed. Preserve tool/model provenance actually returned by the
tool; do not infer a hidden model version or expose temporary signed URLs/secrets.

## Rendering versus preparation

Read/edit/audit do not need the production dependency install. For requested
rendering, the existing recipe needs Python 3.12, Node 22, librsvg, a pinned
`.venv` and pinned Playwright/Chromium:

```sh
bash studio/cloud/setup.sh
bash studio/cloud/doctor.sh
python3 studio/work/preflight.py --root . --brand asyada-egitim --require-render
bash studio/cloud/build.sh launch-creative-02
```

Run the build only for that requested bundle revision and on its task branch;
for a portability comparison, use a separate test checkout and preserve the old
delivery. Node 24 or a global Pillow installation does not prove the pinned recipe
is ready. Do not weaken pinned dependencies to make a capability report pass.
Cloud-account activation is separate: `studio/cloud/ACTIVATION.md` remains the
Codex Cloud environment checklist, not a prerequisite for every Work repo read.

## Existing identity gap and approval authority

The current approved Asya'da Eğitim identity is backed by `brand.json`, the
2026-10-07 seal decision, the 2026-10-08 canonical-lockup approval and the canonical
lockup manifest. Its `status.md` is reconciled to those existing human records.
The full `brand-system.md` is absent. Use these identity sources plus the user's
selected application spec/brief (e.g. `docs/instagram/phase-2b/production-notes.md`
or the requested launch experiment); keep that campaign's rules review-only.
Do not transfer the old sibling's Fraunces/bronze identity or fabricate missing
tokens/grammar as approved. Developing a full system is a separate creative task
with the original human gates. Technical hashes do not establish aesthetics.

## OpenCode ↔ Work handoff

Use [handoff-template.md](handoff-template.md) for a production task's record,
saved with its sources or in the PR. The handoff identifies branch/base SHA,
exact changed paths, actual tools, inputs, output hashes and decisions. Do not
rewrite historical manifests just to add executor metadata.

Continue another executor's task only when explicitly requested: fetch its branch,
inspect its changes and record a handoff before editing. Otherwise start a fresh
branch; unrelated outputs use unique directories. When target files overlap,
re-read current branch/file SHAs and resolve the change without losing the other
task. No force push, automatic reset/clean, broad staging or unconditional merge.

New carousel bundles can use the existing checker schema. Other formats require
an explicit checker/schema extension before claiming independent bundle coverage;
adding an unsupported `format` to `policy.json` is not sufficient.

## Validation and limits

Before opening the PR:

```sh
python3 studio/cloud/audit.py --root .
python3 -m unittest discover -s studio/cloud/tests -v
python3 -m unittest discover -s studio/work/tests -v
```

For actual branded production also run its existing canonical verifier and
visually inspect final outputs. The Work preflight is procedural/read-only;
the trusted-base `submitted-files` CI remains unchanged and authoritative for
its existing contracts. No new render/image/model calls run in Actions.

Observed migration evidence and unresolved capabilities:
[2026-10-10-audit.md](2026-10-10-audit.md).

Official environment references, distinct from this session's observed tool set:
- https://learn.chatgpt.com/docs/environments/cloud-environments
- https://learn.chatgpt.com/docs/environments/git-worktrees
