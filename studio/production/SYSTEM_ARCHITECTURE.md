# Brandstudio System Hub — Repository Architecture

This phase makes the repository's existing categories, styles, agent routes and LLM-family guidance navigable from the site. No historical design source, edition history, publication proof, login or worker is migrated.

## Authority hierarchy

1. **Canonical brand identity:** \`brands/<brand>/brand.json\`, approved lockup manifest and byte-exact SVG assets. These rules are immutable to agents.
2. **Design languages:** \`brands/<brand>/styles/<category>/<style-id>/style.json\`. A review-only style must not be portrayed as approved.
3. **Executor routes:** \`studio/production/routes.json\` + \`router.py\`. Real tools/capabilities are observed at runtime; repo records alone do not establish access.
4. **LLM-family overlays:** \`studio/production/model-families.json\`. These are editorial production hints, not verified individual model capabilities or an instruction to switch models. Codes and images need different treatment; canonical SVGs are always composited as files.
5. **Public read-only system hub:** \`studio/production/public_catalog.py\` verifies sources and generates \`docs/system/catalog.json\`; UI in \`docs/system/\` reads that snapshot. Validate with \`python3 studio/production/public_catalog.py --check\`.
6. **Editing:** Existing Visual Editor saves cloud drafts and version history; selected design-style metadata can be exported as a production brief but does not create a GitHub PR.
7. **Production/publishing:** A true GitHub version requires a branch, file commit, tests, and PR. Social publishing needs independently verified platform evidence; family-level proof is not proof of an exact revision.

## Navigation

The brand-select home and Asya'da Eğitim workspace link to the central **Tasarım Sistemi** hub. It has three anchored areas: **Tasarım Kütüphanesi** (categories, current style and presets), **Üretim Merkezi** (executor route + LLM-family advisory selectors, editable brief copying), **Teslim Akışı** (cloud drafts → PR → proof). Existing artwork gallery, editor and archive remain separate destinations.

The UI must not label unconfigured categories as available design languages, infer that GPT/Gemini/Claude/GLM/Qwen have specific enabled capabilities, or promise background work. Copying a brief is not a model invocation. The static site and repository are public even if \`studio.asyadaegitim.com\` is behind Access; do not place secrets in this catalog.

## Later work

- Add and approve actual category-specific style families; keep label counts derived from sources.
- Build separately versioned executor/model runtime adapters that explicitly verify tool availability. Then bind style selection and runtime profile to the new GitHub task/PR recorder.
- Support a privileged, auditable **Visual Editor revision → GitHub PR** action through a server-side credential, with explicit authorization, no browser token exposure and conflict checks.
- Improve exact-version social publication matching, preserving existing family-level proof and the user-triggered refresh workflow.

Current hub is deliberately read-only; it does not implement those later privileged actions.
