# Brandstudio 3.0 — P1 Shared Contracts and Advisory Routing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build versioned, portable Brandstudio task/agent/result contracts and an independent **read-only** readiness evaluator that interoperates with the existing router without changing production, publication, or cloud services.

**Architecture:** Keep the current `studio/production/router.py` and `routes.json` as the unchanged v1 candidate routing engine. Add JSON Schema Draft 2020-12 data contracts, deterministic semantic validation and state transitions, then compose an advisory wrapper that blocks unsupported executors and never invokes a model or writes a task. Reuse the repository's `unittest` style; do not modify existing cloud audit trust boundaries.

**Tech Stack:** Python 3.12; `jsonschema==4.23.0` (open-source Python package, isolated P1 contract checker); Python stdlib `unittest`, `argparse`, `json`, `pathlib`, `re`; JSON Schema Draft 2020-12; GitHub Actions. No paid API, new Cloudflare resource or background agent.

**Spec:** `docs/superpowers/specs/2026-11-02-brandstudio-multi-agent-v3-design.md` (approved 2026-11-02).

**Status:** PLAN-REVIEW — approved architecture, but **no implementation code written** in this PR. Execute only after user confirms this plan; use a **new isolated implementation branch and PR**, not this documentation review branch. The reviewer must merge/land the approved spec/plan on the agreed branch or explicitly pin the two document SHAs for the implementation checkout.

## Global Constraints

- Existing brand policy and authority: `AGENTS.md`, `studio/production/BOOTSTRAP.md`, `studio/workflow/PUBLISHING.md`, and canonical `brands/asyada-egitim` lockups supersede route suggestions. `asya-egitim` is not `asyada-egitim`.
- Python **3.12** for P1 CI, compatible with project's existing CI; keep `studio/cloud/audit.py` and current independent audit workflow unchanged. The existing recorder is stdlib-only; do **not** make its imports depend on `jsonschema`. Dependency stays isolated to `contracts` and advisory CLI.
- `schema_version = 1`; every contract has `$schema: https://json-schema.org/draft/2020-12/schema`, `additionalProperties: false`, and a checked-in fixed known-good test fixture. Reject unknown schema versions, non-finite numeric values, extra fields, malformed types and SHA values.
- All public identifiers/references are safe opaque metadata. **No raw prompt text, secrets, personal details, signed URLs, complete credentials or access tokens in contract fixtures, output, errors or logged CLI input**. Use only `private:<safe-id>` or `repo:<repo-path>` for brief reference; GitHub repo is public.
- Default `new_paid_api=false`, `image_calls_max=0`, `auto_retry=false`, `max_parallel=1`; a 2-worker request needs `approval.parallel_approved=true`, and P1 still performs *no execution*. No fabricated cost/model/capabilities; unknown means unknown, not zero.
- P1 is **read-only advisory**: no model calls, file/PR writes, render, image generation, Cloudflare writes, social post, credential lookup or automatic fallbacks. No migration of existing historical output manifests in P1.
- Existing `router.plan(...)` signature, JSON keys, CLI output and all tests in `studio/production/tests/test_router.py` must remain unchanged and passing.
- Preserve existing GitHub `submitted-files` independent audit and `studio/work/recording` semantics. New P1 checks only supplement them and do **not** confer aesthetic/identity approval, rendered quality, or production readiness.
- The first PR includes only contract schemas, code, tests, docs and a path-filtered CI check. It does not change `studio.asyadaegitim.com`, Pages origins, editor records, pipelines, or brand assets.

## File structure: responsibilities and boundaries

| Path | Role |
|---|---|
| `studio/production/contracts/__init__.py` | Public contract validator exports; no execution side effects |
| `studio/production/contracts/schemas/task.schema.json` | TaskSpec v1 fields, spend/approval defaults, safe IDs |
| `studio/production/contracts/schemas/capability-report.schema.json` | Observed vs unknown executor capabilities with evidence |
| `studio/production/contracts/schemas/task-receipt.schema.json` | Immutable provenance / handoff metadata, nullable missing checks |
| `studio/production/contracts/schemas/output-manifest.schema.json` | Editable and raster evidence, canonical lockup hash and review status |
| `studio/production/contracts/requirements.txt` | `jsonschema==4.23.0` only (existing independent audit untouched) |
| `studio/production/contracts/validation.py` | Schema plus cross-record/path/brand safety validation |
| `studio/production/contracts/states.py` | Pure allowed status and role transitions; no storage |
| `studio/production/advisory.py` | Task+capability guard composed with legacy `router.plan` |
| `studio/production/contracts_cli.py` | On-demand `validate`, `route`, `transition` JSON CLI; errors redact payload |
| `studio/production/tests/fixtures/contracts/*.json` | Sanitized canonical fixtures; no private data |
| `studio/production/tests/test_contract_schemas.py` | JSON Schema fidelity and reject extra fields |
| `studio/production/tests/test_contract_validation.py` | Safe refs, brand/isolation, no secret or traversal |
| `studio/production/tests/test_contract_states.py` | Authorization/evidence and invalid transitions |
| `studio/production/tests/test_advisory.py` | Same brief on OpenCode/Work route, honest capability gaps, legacy parity |
| `studio/production/tests/test_contract_cli.py` | CLI return codes/outputs and no private payload echo |
| `.github/workflows/brandstudio-contracts.yml` | Path-filtered non-render P1 CI; `audit.yml` remains authoritative |
| `studio/production/contracts/README.md` | Canonical schema field meanings, P2 handoff usage and limitations |
| `studio/production/BOOTSTRAP.md` | Link to optional advisory P1 mode; v1 CLI remains the default |

Do not add duplicate provider-specific schema files under `.opencode/` or `.agents/`; those adapters load this common contract later in P2. Do not touch `studio/work/handoff-template.md` or `studio/production/recording/` yet; document optional mapping and preserve backward compatibility.

## Review Focus

Five boundary cases **must have executable tests in their owning task**, not just documentation:

1. **A public-looking brief ref contains a signed query token or arbitrary raw text.** Task 2 must reject it without echoing the input in errors.
2. **An executor claims capability by name but supplies no evidence, or a different executor is allowed.** Task 4 must mark it ineligible without starting any action.
3. **A valid SHA is paired with a sibling-brand output folder.** Task 2 must not substitute similar-looking brands; for TaskSpec, only its exact brand path or explicitly category-scoped `docs/` output is allowed, with no cross-brand source resolution.
4. **A successful GitHub CI check tries to become a human creative approval or “published” state.** Task 3 must reject the transition.
5. **Malformed JSON, arbitrary extra properties, large data, or UTF-8 secrets arrive via CLI.** Task 5 must exit nonzero with a short diagnostic that never prints the source payload.

---

### Task 1: Define four explicit v1 JSON Schema contracts

**Files:**
- Create: `studio/production/contracts/__init__.py`, `schemas/task.schema.json`, `schemas/capability-report.schema.json`, `schemas/task-receipt.schema.json`, `schemas/output-manifest.schema.json`, `requirements.txt`
- Create: `studio/production/tests/fixtures/contracts/task-valid.json`, `capability-opencode.json`, `capability-work.json`, `receipt-valid.json`, `manifest-prepared.json`
- Test: `studio/production/tests/test_contract_schemas.py`

**Interfaces:**
- Consumes: No P1 code; schema files remain portable JSON Schema Draft 2020-12.
- Produces: `SCHEMA_PATHS: dict[str, Path]` from `contracts/__init__.py` with kinds `task`, `capability-report`, `task-receipt`, `output-manifest`.
- All schemas require integer `schema_version: 1`, reject unknown keys, use `$defs` for SHA-40, SHA-256, safe slug, safe repo path, evidence enums. Use `if/then` in manifest for `prepared` and higher requiring nonempty editable/render evidence.
- `TaskSpec`: `task_id`, `brand_slug`, `category`, `brief_ref`, `base_sha` (40 lowercase hex), `output_ref`, `style_id` (slug or null), `required_capabilities` (unique nonempty list), `allowed_executors` (unique nonempty), `max_parallel` (1 or 2), `budget` (currency USD, `new_paid_api=false`, nonnegative `image_calls_max`, `auto_retry=false`), `approval` (`creative=pending`, `brand_identity=inherit-approved-assets`, `social_publish=false`, `parallel_approved` boolean).
- `CapabilityReport`: `executor`, `observed_at` (UTC ISO-8601), `host_kind` (`local`/`cloud`/`connector`), `model_id` nullable, `capabilities` map with only `observed` or `unknown` states and `evidence_source` nullable; no unverified label interpreted as observed.
- `TaskReceipt`: `task_id`, `executor`, `base_sha`, optional nullable `head_sha`, `branch`, `changed_paths`, `actual_tools`, `failure_codes`, `evidence_refs`; evidence may be empty but completed execution cannot be asserted from empty receipt.
- `OutputManifest`: `task_id`, `revision_id`, `status` (`draft`, `prepared`, `technical_verified`, `creative_review`, `accepted`, `delivered`), `editable_sources`, `renders` (each with width/height/SHA256), `lockup` (canonical ID / SHA256 or null while draft), `checks` (explicit observed booleans), `human_approval_ref` nullable. Require verified render before `technical_verified`; `accepted` needs nonnull human approval ref. Schema enforces structural constraints; semantic checker handles runtime evidence.

- [ ] **Step 1: Write schema tests and clean fixtures.** Tests: `test_all_schema_files_conform_to_draft_2020_12`, `test_all_fixture_documents_validate`, `test_extra_fields_wrong_version_and_missing_evidence_rejected`, `test_prepared_manifest_requires_render_and_editable_source`, `test_accepted_manifest_requires_human_reference`. Assert `Draft202012Validator.check_schema(...)` and `Draft202012Validator(...).validate(...)`.
- [ ] **Step 2: Run red test.** `python3 -m unittest studio.production.tests.test_contract_schemas -v` → FAIL for missing schemas/exports.
- [ ] **Step 3: Implement the listed JSON schemas, fixtures, `SCHEMA_PATHS` and pinned package.** Existing `router.py` and `routes.json` must not change.
- [ ] **Step 4: Install/test isolated dependency and verify green.** `python3 -m pip install -r studio/production/contracts/requirements.txt` in a temporary virtual environment, then `python3 -m unittest studio.production.tests.test_contract_schemas -v` → 0 failures.
- [ ] **Step 5: Commit.** `git add studio/production/contracts studio/production/tests/fixtures/contracts studio/production/tests/test_contract_schemas.py && git commit -m "feat: add portable Brandstudio v1 contract schemas"`.

### Task 2: Validate safely across JSON Schema and repository context

**Files:**
- Create: `studio/production/contracts/validation.py`
- Test: `studio/production/tests/test_contract_validation.py`

**Interfaces:**
- Consumes: Task 1 `SCHEMA_PATHS`, JSON files, `jsonschema.Draft202012Validator`.
- Produces: `validate_document(kind: str, document: dict, *, root: Path) -> None` (raises `ValueError` with **field name/reason only**, never serialized input).
- All repo references are normalized POSIX paths, relative, no `.`, `..`, backslash, empty/hidden components or `//`, no symlink escapes when a file exists, and restricted to approved source/output prefixes. Disallow URLs and unsafe `brief_ref`: exactly `private:<safe-id>` or `repo:<safe-repo-path>`.
- For registered brands require `brands/{brand_slug}/brand.json` except category `new-identity`; compare `category` with `routes.json`. Validate `output_ref` as a `docs/` path, reject path components containing a registered **different** brand slug (never infer sibling), and keep output manifest paths inside the exact declared output subtree when a TaskSpec is provided. Schema validation alone does not prove approved identity.
- `validate_document` validates one record only; `validate_bundle(task: dict, capability: dict | None, receipt: dict | None, manifest: dict | None, *, root: Path) -> None` additionally verifies same task IDs, selected executor and `output_ref` containment. No trust in caller-provided evidence of remote SHA/CI/visual inspection.
- Enforce `max_parallel==2` only with `approval.parallel_approved=true`; disallow budget increase as an implicit auto call and any creative/social approval fields set by an executor.
- Strict JSON decode (reject duplicate keys in CLI), redaction: throw `ValueError("Invalid field: ...")` rather than echo values or input snippets.

- [ ] **Step 1: Write tests** `test_valid_fixture_bundle`, `test_reject_private_brief_url_and_raw_secret_without_echo`, `test_reject_absolute_dotdot_symlink_and_foreign_brand_paths`, `test_reject_unregistered_existing_brand`, `test_reject_cross_record_task_mismatch`, `test_parallel_requires_explicit_approval`, `test_unknown_schema_version_rejected`.
- [ ] **Step 2: Run red test.** `python3 -m unittest studio.production.tests.test_contract_validation -v` → FAIL on absent import/implementation.
- [ ] **Step 3: Implement `validate_document` and `validate_bundle`**, using `Path.resolve` only under a controlled root and rejecting existing symlinks before resolved-path comparison. No file or network writes.
- [ ] **Step 4: Run green test.** Same command → 0 failures, including error-string tests (no secret echoes).
- [ ] **Step 5: Commit.** `git add studio/production/contracts/validation.py studio/production/tests/test_contract_validation.py && git commit -m "feat: validate v1 tasks and handoffs safely"`.

### Task 3: Pure, role-gated review workflow state machine

**Files:**
- Create: `studio/production/contracts/states.py`
- Test: `studio/production/tests/test_contract_states.py`

**Interfaces:**
- Consumes: State names from approved spec; do not use GitHub merge/CI signals as human approvals.
- Produces: `next_state(current: str, *, requested: str, actor_role: str, evidence_ref: str | None) -> str`, raises `ValueError` on invalid transition.
- Allowed linear states: `draft→ready→assigned→producing→prepared→technical_verified→creative_review→accepted→delivered`.
- Role map: `draft→ready` planner, `ready→assigned` planner, `assigned→producing` worker, `producing→prepared` worker, `prepared→technical_verified` reviewer, `technical_verified→creative_review` reviewer, `creative_review→accepted` human, `accepted→delivered` reviewer **only with actual delivery evidence**. Nontrivial transitions require safe evidence ref; for `human`, an explicitly observed human approval ref (never `ci:success`).
- `blocked` or `cancelled` permitted from active pre-delivery states with reason/ref, but not a shortcut to accepted. `creative_review→revision_requested` human only, terminal on that revision; continuing requires a **new immutable revision/task**, not mutating old record. `published` is **not** a TaskSpec state and can be recorded only by separate publication-tracker proof outside P1.

- [ ] **Step 1: Tests** `test_valid_planner_worker_reviewer_human_sequence`, `test_skip_and_wrong_actor_rejected`, `test_ci_does_not_approve_creative_or_publish`, `test_missing_evidence_rejected`, `test_revision_requires_new_task`, `test_blocked_and_cancelled_are_terminal`.
- [ ] **Step 2: Run red test.** `python3 -m unittest studio.production.tests.test_contract_states -v` → FAIL on missing function.
- [ ] **Step 3: Implement `next_state`** as a small immutable transition map; do not add persistent task storage in P1.
- [ ] **Step 4: Run green test.** Same command → 0 failures.
- [ ] **Step 5: Commit.** `git add studio/production/contracts/states.py studio/production/tests/test_contract_states.py && git commit -m "feat: enforce evidence-gated review states"`.

### Task 4: Add capability-evidenced advisory wrapper without breaking the existing router

**Files:**
- Create: `studio/production/advisory.py`
- Test: `studio/production/tests/test_advisory.py`
- Existing unchanged dependency: `studio/production/router.py` and `routes.json`.

**Interfaces:**
- Consumes: `validate_bundle` from Task 2, `router.plan(root, config, executor, brand, category, capabilities, ...)` current exact signature, TaskSpec and CapabilityReport contracts.
- Produces: `propose(*, task: dict, report: dict, root: Path, config: dict) -> dict`, side-effect-free.
- Response shape: `{"mode":"v3-advisory", "task_id":str, "eligible":bool, "blockers":list[str], "candidate":dict | null}`; `candidate` is the unchanged legacy router return, explicitly `candidate-not-benchmarked`, NOT a job launch record.
- An observed capability means `status=="observed"` AND nonblank `evidence_source`; omitted/unknown cannot be silently inferred. Executor must be in `allowed_executors`; `required_capabilities` must all be observed; `generic-limited-v1` cannot be eligible. If capability report cannot be substantiated, return `eligible:false` with reason, no costly/automatic fallback.
- The same TaskSpec with an `opencode` report and a `chatgpt-work` report produces legal, different **candidate** routes, with identical task_id, branded policy and human gates. If Work only has `github-read` and the task requires `browser-render`, it is blocked; do not claim it can render.
- `task_id`, `base_sha`, selected output and budget must not be rewritten by router. No executor can mark creative accepted.

- [ ] **Step 1: Write tests** `test_opencode_work_same_task_different_routes`, `test_missing_capability_and_no_evidence_blocks`, `test_executor_not_allowed_blocks`, `test_generic_limited_is_never_ready`, `test_no_hidden_model_spend_or_task_mutation`, `test_legacy_router_output_unchanged`.
- [ ] **Step 2: Run red test.** `python3 -m unittest studio.production.tests.test_advisory -v` → FAIL on missing `propose`.
- [ ] **Step 3: Implement `propose`** by calling existing `router.plan` and returning advisory annotations, never modifying `routes.json`.
- [ ] **Step 4: Run green and legacy tests.** `python3 -m unittest studio.production.tests.test_advisory studio.production.tests.test_router -v` → 0 failures. Confirm legacy CLI `python3 studio/production/router.py --executor codex --brand asyada-egitim --category instagram-carousel --capability filesystem --capability terminal` still prints `mode:read-only-dry-run`.
- [ ] **Step 5: Commit.** `git add studio/production/advisory.py studio/production/tests/test_advisory.py && git commit -m "feat: add honest multi-executor advisory readiness"`.

### Task 5: Offline CLI, targeted CI, documentation and complete acceptance

**Files:**
- Create: `studio/production/contracts_cli.py`
- Create: `studio/production/tests/test_contract_cli.py`
- Create: `studio/production/contracts/README.md`
- Create: `.github/workflows/brandstudio-contracts.yml`
- Modify: `studio/production/BOOTSTRAP.md` (small optional P1 section; leave existing steps intact).

**Interfaces:**
- Consumes: all Task 1–4 functions; file inputs only (no network or secrets).
- Produces CLI:
  - `python3 studio/production/contracts_cli.py validate --kind task --file /safe/path/task.json --root .`
  - `python3 studio/production/contracts_cli.py route --task /safe/path/task.json --report /safe/path/report.json --root .`
  - `python3 studio/production/contracts_cli.py transition --from creative_review --to accepted --actor human --evidence-ref review:approval-id`
- Output on success: strict JSON with mode/eligibility/state; on errors: nonzero exit, short safe error code/field (never source bytes, file contents, credential URLs). File read length limit **256 KiB** and JSON depth limit **32**, duplicate JSON keys rejected, UTF-8 only. Reject float NaN/Infinity and malformed ISO dates. JSON Schema `format` must use a format checker; the cross-record semantic checker is not a substitute for schema checks.
- `brandstudio-contracts.yml` only triggers when `studio/production/contracts/**`, `studio/production/advisory.py`, `studio/production/contracts_cli.py`, `studio/production/tests/**`, `studio/production/router.py`, `studio/production/routes.json`, `studio/production/BOOTSTRAP.md`, or that workflow changes. Use Python 3.12, install pinned public `jsonschema` package, run all `studio/production/tests` via `unittest`. No model/render/browser calls, no production/cloud credentials. Existing `audit.yml` stays as-is. **Do not mark new path-filtered workflow mandatory in branch protection** until missing-check behavior is assessed.
- Docs include 2 demonstrated executor report examples and a blocked-case, real vs claimed capability distinction, schema versioning rules, receipt vs recorder boundaries, a safe migration/rollback note and a link to the approved spec.

- [ ] **Step 1: Write CLI tests** `test_validate_valid_task_exit_zero`, `test_route_work_missing_capability_blocked`, `test_bad_json_duplicate_keys_oversized_and_deep_input_rejected`, `test_utf8_secret_is_not_echoed`, `test_transition_rejects_ci_creative_approval`; assert subprocess exit codes and stdout/stderr content.
- [ ] **Step 2: Run red tests.** `python3 -m unittest studio.production.tests.test_contract_cli -v` → FAIL on missing CLI.
- [ ] **Step 3: Implement CLI** with direct reused functions, size/depth/duplicate checks and strictly allowlisted error messages. Keep all user-facing output fields secret-free.
- [ ] **Step 4: Add workflow and docs**; test workflow syntax with a YAML parser in reviewer environment (do not misrepresent text-only inspection as YAML compilation). Document P1 advisory-only limitations; keep README and PUBLISHING rules untouched.
- [ ] **Step 5: Run full P1 and legacy tests** `python3 -m unittest discover -s studio/production/tests -v` → 0 failures; `python3 -m unittest discover -s studio/cloud/tests -v` → 0 failures; `python3 -m unittest discover -s studio/work/tests -v` → 0 failures. Independently run `python3 studio/cloud/audit.py --root .` → exit 0. Verify fixture probe from OpenCode and Work paths and CLI blocked-case output with no user data.
- [ ] **Step 6: Commit.** `git add studio/production/contracts_cli.py studio/production/tests/test_contract_cli.py studio/production/contracts/README.md studio/production/BOOTSTRAP.md .github/workflows/brandstudio-contracts.yml && git commit -m "feat: document and test advisory contracts via CLI and CI"`.

## Spec coverage and deferred work (explicit)

- **P1 implemented by this plan:** versioned TaskSpec/CapabilityReport/TaskReceipt/OutputManifest schemas, path/brand/budget/role checks, deterministic approval-state machine, documented on-demand CLI, legacy router compatibility, testable two-executor advisory route and extra CI evidence.
- **P2 only (NOT a P1 claim):** actually invoking OpenCode and Work/Codex in their respective environments; creating task branches; uploading outputs; real handoff/GitHub transaction leases; remote capability probing; capturing real token/cost/CI attestations.
- **P3 only:** reproducible browser rendering, pixel-diff QA, canonical SVG composite verification, cache.
- **P4 only:** panel task cards, auth/CORS/CSRF/Cloudflare route integration, durable workflow state.
- **P5 only:** content-addressed asset store, duplicate cleanup/migration, disk/RAM/runtime benchmarks.
- P1 does not remove any existing resource and requires no rollback of production services. If advisory experiments fail, delete only newly created P1 modules from its branch; `router.py` legacy path still works.

## Self-review for the implementer and PR reviewer

- Every named interface is produced by an earlier task: `SCHEMA_PATHS → validate_document/validate_bundle → next_state → propose → contracts_cli`.
- Five Review Focus inputs have tests in Tasks 2, 4, 2, 3, 5 respectively.
- `TaskSpec` vs router category mismatch checked in Task 2, evidence report vs route eligibility checked in Task 4, schema dependencies isolated to P1.
- Test setup uses a temporary Python environment; do not assume the existing user/CI host has `jsonschema`.
- P1 work must be reviewed on the exact checked PR HEAD, with `submitted-files` audit separate from the new contract check. No aesthetic green signal.
- A reviewer's concerns about adding a dependency should be resolved before implementation by comparing stdlib-limited schema-validation risks, not by silently downgrading JSON Schema conformance.

## Execution handoff

The architecture is approved; **this implementation plan awaits user review**. Recommend **native execution (single executor, test-by-test)** for P1: its modules form a sequential dependency chain, and multiple concurrent agents would add orchestration overhead without improving early correctness. Add fresh independent PR/CI review at final HEAD. If separate subagent contexts are truly available, a new reviewer per completed task is a stronger alternative, but do not claim subagent dispatch in an environment without it.

After approval, load `superpowers:executing-plans` (native) or `superpowers:subagent-driven-development` (per-task agent execution), implement on a new isolated branch, run fresh checks, and report actual results/remaining blockers. Do **not** merge a PR automatically while an explicit user design/implementation hold remains.
