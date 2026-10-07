# Image Production — Hybrid Raster/Vector Policy

Verified backends (do not re-derive; use as stated):

- **Default raster backend:** Pollinations `gen_edit_image_free` (project-local adapter `.opencode/plugins/pollinations/`). No key, no login; quota is dynamic per-IP — always read it live, never assume a fixed daily limit, never expose IP or quota metadata beyond remaining/max.
- **Secondary backend:** local ChatGPT adapter (`image_generate` / `image_edit`). Its backend has repeatedly returned temporary overload errors. NEVER fall back to it automatically. Use only on explicit user request or explicit workflow authorization.

## Hybrid split (quality + quota rule)

Build directly in HTML/CSS/SVG — never spend raster quota on these:

- logo construction and exploration, wordmarks where feasible, typography specimens, color systems, grids, layout systems, naturally vector/geometric patterns, icon systems, clear-space diagrams, brand-system documentation.

Use Pollinations primarily for:

- art-direction imagery, photography direction, illustration direction, visual-world exploration, texture/material studies, campaign imagery, hero imagery, atmospheric compositions, mockup imagery where raster adds real value.

## Per-direction budget (`/brand` exploration)

For each of the 3 directions:

1. Concept + visual grammar first, then the vector/layout portion of the board in HTML/CSS/SVG.
2. Only if raster materially improves understanding: AT MOST ONE initial Pollinations visual per direction.
3. `read` the generated file back as ACTUAL multimodal image input and critique what is visible — never infer success from the prompt.
4. Check: prompt compliance, hierarchy, composition, distinctiveness, aesthetic coherence, cliché level, brand suitability, direction consistency.
5. Regenerate only for a concrete, high-impact visual defect. Maximum ONE corrective regeneration per direction before presenting.

Budget: 0–3 raster generations normally; absolute maximum 6 if every direction needs one correction. Fewer or zero when SVG/HTML communicates better. Never consume quota to test whether something "might look better". Never auto-retry a failure.

## Board composition

Each direction board combines: SVG logo/mark exploration · HTML/CSS wordmark and type specimens · HTML/CSS palette · HTML/CSS layout/grid · SVG/CSS devices and patterns · actual generated raster where appropriate · one application example in whichever medium demonstrates the concept best.

Never render typography as AI-generated raster text when HTML/SVG can set it accurately. Never generate the final wordmark with an image model.

## Quota behaviour

Read quota before `/brand` raster work. If sufficient, proceed economically. If insufficient, continue in HTML/SVG, briefly state which raster explorations were skipped, and never ask the user to buy credits. Never expose IP or unnecessary quota metadata.

## Multimodal critique rule

Critique of a generated local image requires the actual file as multimodal image input (`read` the image file). Never critique from prompt, filename, source code, or generation metadata. If image input fails, mark visual inspection as unavailable — do not pretend to have seen the render.

## GPT-6.1 Sol

Unchanged: explicit `/brand-review` only. Never invoke automatically after generation or critique.

## Source of truth (fidelity transfer)

A selected direction's generated image is the VISUAL SOURCE OF TRUTH until production proves aesthetic parity. Reconstruct toward it (finer variance, gradient/glow where vector-native, dark-field authority, type rhythm) rather than regularizing it away. Full pipeline: `identity-development.md`; comparison protocol: `visual-quality.md`.

## Locked logos — never regenerate

Once a human approves a logo, it stops being a design task and becomes a locked asset. Check `brands/<slug>/brand.json` for `canonicalLogo.locked` **before any raster work**.

If a canonical logo exists, these rules are absolute:

- **Never** prompt an image model to draw, recreate, imitate, approximate, trace or typeset the logo — not in a mockup, not in a scene, not "just for texture", not as a background element, not at low priority in a longer prompt.
- **Always** composite the exact canonical SVG file from disk.
- Image models generate the **visual / background / composition only**. The logo is never part of the generated pixels.
- The only permitted changes are **placement parameters**: position, size, clearspace, and an approved colour variant. The underlying geometry never changes — no restyling, no re-colouring outside the approved variants, no re-fitting, no re-simplifying.
- If a brand needs the logo **inside a flat design**, reserve a clean logo-safe area during generation (empty, uncluttered, correct contrast) and composite the canonical SVG into it afterward.
- If a brand needs the logo on a **perspective or physical surface** (billboard, packaging wrap, signage in-scene, garment), do **not** attempt it by regeneration. Flag it for the separate perspective/mockup workflow, which warps the same canonical asset deterministically.
- Every final branded output records `canonical_logo_sha256` in its manifest. Verify the asset is intact first:

```sh
studio/tools/verify-canonical-logo.sh
```

A locked logo is finished. Requests to "improve", "clean up" or "refine" it are declined; only an explicit new human decision plus a new lock record can change a canonical asset.
