# Brandstudio · One design language across all production agents

This is the live, **agent-neutral, opt-in** handoff for an existing brand style.
It does not install tools, invoke models, generate artwork, automatically submit a
GitHub PR, or claim approval. It supersedes no existing brand or publishing rule.

## Workflow

1. Open the Brandstudio Visual Editor, select an HTML carousel, and expand
   **Tasarım dili ve varyasyonlar**.
2. Choose a registered family, preset, approved logo variant and optional axes.
   Click **Stili düzenlemeye uygula**, then manually save the resulting editor
   revision to Cloudflare if you want this style choice retained.
3. **Ajan komutunu kopyala** gives a complete, consistent instruction plus the
   exact same JSON selection as **GitHub üretim fişi ↓**.
   Paste that prompt into OpenCode, Codex, Work, ChatGPT or another capable
   executor. It does NOT execute a task automatically. The original creative
   brief must be supplied separately and preserved verbatim.
4. In the agent checkout, save the JSON payload between
   `JSON_PAYLOAD_START` and `JSON_PAYLOAD_END` as a file (private working
   directory when containing unpublished details). Run:

       python3 studio/production/editor_handoff.py --brief PATH/production-brief.json

   Or pipe the exact JSON through stdin with `--brief -`.
   This stdlib-only operation checks the selection against the current local
   canonical style, exact Git blob, SHA-256 logo/seal, font and palette.
   **Fail closed on mismatch**; refresh the user-selected style rather than
   allowing an AI agent to silently substitute its preferred identity.
5. For an actual design production, read `AGENTS.md`,
   `studio/production/BOOTSTRAP.md`, `.agents/skills/production-router/SKILL.md`,
   and the exact style path. Resolve the executor's real tools separately.
   Use `studio/production/router.py` / `style_pack.py` when Python is available.
   Produce editable HTML/CSS/SVG, verify the canonical SVG, render with an
   actual browser, and obtain the required human creative approval.
6. Only after an approved design is finished, use the existing cloud
   finalization → GitHub review → immutable-source-version workflow.
   Never use a copied prompt as evidence of approval or publishing.

## Registered and unregistered scopes

- `asyada-egitim / instagram-carousel / editorial-campaign`: one actual
  source-verified style family, with four presets. It is **review-only**,
  not approved or locked as a creative style.
- Other category labels in `docs/visual-editor/browser/style-registry.json`
  are **not yet registered**. Don't fabricate family IDs or silently
  reuse an Instagram style as a social cover/print/web identity.
- The current selection is Turkish-language and uses the canonical
  Jost + paper/red/ink tokens with approved Turkish H-02/P-01 SVGs.
  English-only brand lockups are a distinct canonical family and are
  not implicitly inferred by a language guess.

## Integrity and resource behavior

- Source of truth: `brands/<brand>/styles/<category>/<style>/style.json`
  and verified brand/lockup manifests. Browser registry contains the Git blob
  SHA of the same source; UI selection includes the lockup and seal SHA-256.
- There is no polling, extra Cloudflare Worker call, model invocation,
  render, build, or GitHub write when copying the command.
- The new Python verifier reads only checkout files. It does not create any
  checkout artifacts or schedule work.
- This does not auto-configure a ChatGPT Project, OpenCode, Antigravity or
  any agent. The operator must give the selected prompt to the executor and
  confirm its actual tools and checkout.
- The `review-only` field and `github.status=not-submitted` remain
  accurate until independent human approval and actual GitHub delivery.
