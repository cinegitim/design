# Brandstudio Style Library · Category → Family → Preset → Axes

One **category** describes the deliverable (Instagram carousel, single social post,
print, web, identity application). Multiple independent **style families** can
coexist inside each category. A family has its own composition grammar and
multiple **presets** (subvariations) and optional **variation axes**.

A style is *not* an individual design, template, color swap, agent profile,
creative approval or publication status. Existing user design products and their
GitHub/Cloudflare versions remain separate from style-family definitions.

## Registered Asya'da Eğitim candidates

| Category | Style family | Distinction | Presets | Status |
| --- | --- | --- | --- | --- |
| Instagram carousel | Editorial Campaign | Image + type editorial cadence | Institutional Paper / Campaign Dynamic / Photo Editorial / Ink Accent | review-only |
| Instagram carousel | Data Atlas | Facts, metrics, timelines, comparison structures | Metrics Overview / Timeline Path / Comparison Led | review-only |
| Instagram carousel | Conceptual Breakout | Object metaphor, dramatic typography, storytelling collage | Object Metaphor / Typographic Shock / Editorial Collage | review-only |

These are **registered candidate visual grammars**, not rendered sample
artworks or human-approved creative directions. The small diagrams on the
interface are schematic markers for navigation, **not visual quality evidence**.
Other categories currently have no registered families; they are ready to hold
multiple families when actual source definitions are authored.

## Source of truth and adding another family

A new style belongs at:

`brands/<brand>/styles/<category>/<style-id>/style.json`

with a companion README. Preserve the existing style schema but make the
`layout_grammar`, `soft_constants`, `variation_axes`, presets and expected
visual outcomes materially distinct. Keep `status: review-only` and
`approval.human_style_approval: false` until the human approves the style.
Do **not** copy an existing family and simply rename its presets/colors.

The canonical logo SVGs, their SHA-256 records, V-01 seal, Jost and approved
paper/red/ink tokens remain locked; the actual asset bytes are never rewritten
for a new style. Do not invent artwork or media merely to fill a catalog card.

Both `docs/visual-editor/browser/style-registry.json` and
`docs/system/catalog.json` are **derived, cacheable snapshots**. To update them
from style manifests in a real checkout, explicitly run:

```sh
python3 studio/production/style_registry_sync.py --write
python3 studio/production/style_registry_sync.py --check
```

Neither command performs API calls, visual generation, rendering, GitHub
writes, scheduling, or Cloudflare work. `--check` is run as part of existing
GitHub Cloudflare-stage CI when styles or editor files change.

## How the UI behaves

- **System Hub**: category selector → independently clickable style family
  cards → chosen style details and presets; selection also updates the
  production brief.
- **Visual Editor**: category bound to actual product format → family cards
  and a keyboard-accessible select → presets and axes → explicit **apply**.
  Selecting a card alone does not restyle or autosave existing artwork.
- **Agent handoff**: the selection and exact Git blob SHA are carried into
  the agent brief, checked against canonical style and SVG sources. Agents
  cannot silently replace a chosen family or claim approval.
- **GitHub versions**: a selected style is an input to a new approved design
  candidate, not a replacement of any existing product source revision.

## Future category design

Social post, print/catalog, web design and identity application each maintain
their own family lists and compositional constraints. Register independent
families *only when real valid style manifests exist*. Never imply all product
types use Instagram carousel 1080×1350 geometry or its composition rules.
