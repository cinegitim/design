# Visual Quality — Self-Critique Loop

Critique every board, logo, and application before presenting. If visually weak, iterate.

## Procedure

1. Validate in a capability-aware way: use an actually available browser/preview/screenshot tool when present; otherwise `read` the file back and validate source/structure (and shell-based checks where reasonable). Never deliver sight-unseen and never claim a visual preview occurred when it did not.
2. Multimodal rule for generated raster: `read` the actual image file as image input and judge only what is visible (prompt compliance, hierarchy, composition, distinctiveness, coherence, cliché, suitability). Never critique from prompt, filename, source, or metadata. If image input fails, mark visual inspection as unavailable.
3. Score 4 categories 1–10 (caps: any open Critical caps its category at 4 and overall at 6; any open High caps its category at 7):

| Category | Weight | Checks |
|---|---|---|
| Hierarchy | 25% | One focal point; clear 1-2-3 reading order; most important = largest + strongest color + most whitespace |
| Consistency | 25% | ≤2 typefaces; 5–8 distinct sizes; 4/8px spacing scale; one color system; on-system vs `brand-system.md` |
| Aesthetics | 25% | Palette harmony, whitespace, polish, fit to concept (cite one concrete observation, never "looks premium") |
| Usability | 25% | Contrast AA, min sizes hold, responsive (375/768/1440), no overflow, touch targets ≥24px, `prefers-reduced-motion` |

3. Log severity-ranked fixes, apply, re-validate (capability-aware; generated raster re-inspected as image input). State the top fix in one line to the user.

## Severity

- **Critical** — blocks the task or fails AA on core content (illegible type, invisible CTA, broken layout, logo unreadable at size).
- **High** — works but undermines the goal (competing focal points, off-system colors/fonts, weak hierarchy).
- **Medium** — polish most users feel (off-grid spacing, inconsistent radii, 10+ font sizes).
- **Low** — designer-level refinement (widows, letter-spacing drift, minor alignment).

Order fixes by severity, then impact ÷ effort.

## Craft checklist (brand-specific)

- [ ] Typography: display/text pairing deliberate; headline ≥3× body; `text-wrap: balance` on headlines; body 45–75ch, 1.5–1.75 line-height.
- [ ] Palette: 60/30/10 discipline; every text/bg pair contrast-checked; max 1–2 brand + neutrals + 1 accent.
- [ ] Composition: rule-of-thirds or grid-intentional focal point; related items proximal; consistent page margins.
- [ ] Logo: one distinctive feature; holds 16px→billboard; light/dark/photo variants; clear space respected.
- [ ] Imagery: matches photo/illustration language in the system; one treatment; forbidden subjects absent.
- [ ] Boards: generous whitespace, specimen blocks (`display:grid; place-items:center; min-height:200px`), swatch grid (`auto-fit, minmax(160px,1fr)`), restrained motion only.
- [ ] Text: every word spelled correctly; no garbled lettering in SVG marks; no clipped/overlapping text on mobile widths.

## Fix format (internal)

`[Severity] Issue — Evidence (region/measure) — Fix (specific token/CSS) — Impact`

## Fidelity review (source vs reconstruction)

For every production reconstruction of a generated direction: render source and implementation side by side and judge "does this still feel like the same brand?" — not "did we implement the rules?" Score fidelity loss explicitly: sophistication, tension, typographic character, regularization excess, genericization, cheapness-vs-source, unencoded source qualities. If the source looks materially better, production is unfinished — improve the reconstruction (type, spacing, proportions, silhouette, negative space, texture, controlled irregularity), never dilute the direction. A written system never overrides visible source evidence.
