# Projects

One folder per brand: `projects/<brand-slug>/`.

## Layout

```text
projects/<slug>/
  brand-brief.md        # agent-filled inferred brief
  brand-system.md       # CANONICAL system — source of truth
  boards/
    direction-a.html
    direction-b.html
    direction-c.html
    logo-board.html
  assets/
    logo-primary.svg
    logo-secondary.svg
    icon.svg
    logo-mono.svg
    favicon.svg
  applications/         # /brand-apply outputs (HTML/SVG)
```

## Rules

- `brand-system.md` is canonical. Update it before changing any derived artifact.
- Boards and applications are self-contained HTML + inline SVG; validate in a capability-aware way (use an actually available browser/preview/screenshot tool when present; otherwise `read` back and validate source/structure without claiming a visual preview).
- Never invent orphan colors/fonts/devices in applications — trace every choice to the system.
- No actual brands exist yet. `/brand` creates the first one.
