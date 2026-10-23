# Brandstudio Visual Editor — optional post-production bridge

## Two distinct deployment surfaces

- **Prompt production remains primary.** OpenCode, Work, Codex or available ChatGPT tools create source HTML/CSS/SVG and real PNGs through the existing brand-specific workflow. This bridge never replaces the renderer or brand checks.
- **GitHub Pages is static.** The public \`docs/visual-editor/\` route provides a *per-product navigation entry* and a safe link to the locally installed companion. It cannot write files, create v2/v3 folders, run Python, access your computer or save to GitHub.
- **Local companion is opt-in.** Its UI/server is the independently tested \`brandstudio-product-visual-editor-workflow-mvp.zip\` package from the conversation. Install it yourself and start \`Brandstudio Başlat.command\` on your Mac. It serves *only* \`127.0.0.1:8765\` and stores private work locally in \`products/<category>/<product>/\`. This public repo intentionally does **not** commit the binary demo package, private drafts or local versions.
- **Repository adapter:** \`studio/visual-editor/bridge.py\` runs **after** verified prompt delivery, optionally registers that output into the companion via \`register-output\`, preserves the prompt output and its metadata, and refuses to re-register the same product. The adapter is explicit, not an automatic surprise side effect of making a carousel.

## Site flow

Site product tile → **Visual Editor** → \`docs/visual-editor/?product=<slug>&category=instagram-carousel\` → **Yerel editörde aç** → installed companion product route → edit → explicit save confirmation → \`versions/v2\`, \`v3\`…

If the companion is not installed/running, the site transparently explains how to start it. If a gallery item has not been registered locally, its local link returns "product not found"; use the registration step below. A public web link never silently provisions a product or writes files. The local service must NOT be exposed to a public port without authentication, CSRF and origin protections.

## Adapter example (from an isolated real production checkout)

\`\`\`sh
python3 studio/visual-editor/bridge.py \
  --repo . \
  --editor-home "$HOME/Brandstudio/brandstudio-workflow" \
  --output "/path/to/successfully-rendered-carousel" \
  --product neden-asyada-universite-okumali \
  --brand asyada-egitim --category instagram-carousel \
  --style editorial-campaign --logo-id P-01/light --dry-run
\`\`\`

When paths, source, PNG outputs, installed runtime and **exact, SHA-verified** canonical P-01 pass, omit \`--dry-run\` to register \`v1\`. The output must include \`source/01.html\`, \`source/style.css\`, \`slides/*.png\` and optionally \`assets/\`. Never use this adapter to regenerate approved files.

The current companion specifically supports P-01/light for complete-logo render. The adapter intentionally rejects other variants, rather than substituting or altering them.

## Persistence and publishing

- Public repo: instructions, adapters, stable studio URLs, *approved* sources and checked publication bundles when actually committed.
- Local, private: active editor changes, draft v2/v3 state, previews, and unapproved private prompts. Separate public PR/CI is required before anything is published to Pages.
- \`register-output\` is an optional step of a producer's *verified delivery*, not a new default route. Missing companion means the prompt-generated production remains complete without an editor button that falsely claims it's registered.
- GitHub Actions audits committed files; it does not execute, version or publish private UI changes.
- Visual/identity approval remains human. No site link implies visual approval or an approved style.

## Tests

\`\`\`sh
python3 -m unittest discover -s studio/visual-editor/tests -v
\`\`\`

These tests validate bridge controls only. They do not prove that a Mac companion is installed or that Pages can access localhost.
