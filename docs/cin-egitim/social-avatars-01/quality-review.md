# Visual QA — social avatars 01

Inspected actual exported profile PNGs in the local gallery, plus a PNG contact sheet built from all three circle exports and all three favicon exports. Read circle-red.png directly as image input. No image/model calls.

- Hierarchy 9/10: one symbol per avatar, no small wordmark; background and mark are immediately distinguishable.
- Consistency 9/10: exact original path/transform geometry; existing light/dark/white colour variants; Source Serif 4 + Manrope in the gallery.
- Aesthetics 9/10: clear margin between brush silhouette and circular edge; ivory matches selected P-01; red negative has strong separation; dark variant retains red ring and white pagoda.
- Usability 9/10: inspected 250/64/40/24 px previews and mobile 375 px screenshot. Document width equals viewport at 375/768/1440 px. Actual PNG images loaded. Download links have at least 32 px target height.

Fix: small plain download links enlarged to 32 px minimum targets. No Critical/High issue remains. Self-review is not human creative approval.

Alpha validation: sharp raw RGBA read of every export: all profile and favicon pixels have alpha 255; circle pixels at least two px inside disk have alpha 255; circle corner alpha is zero. Exact 1080×1080 and 64×64 dimensions verified. Independent stdlib audit checks canonical geometry, colours, crop placement, actual PNG dimensions/hashes and ZIP bytes; it does not independently render or judge aesthetics.

Production uses installed macOS librsvg 2.63.0. Pinned Linux Python/Node/Chromium recipe was not executed. Old locked artwork and old deliveries unchanged.
