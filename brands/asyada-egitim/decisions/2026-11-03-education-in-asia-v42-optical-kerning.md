# Education in Asia — V4.2 optical kerning

Date: 2026-11-03

User feedback: glyph family, Jost 550 and V-01 emblem now acceptable; the A–S, S–I and I–A visual gaps remain unequal, and all letters should sit closer.

The V4.1 uniform 20-unit glyph tracking was insufficient because contour shapes contribute extra uneven white space. Using actual approved Path2D outlines, sample alpha silhouettes across 125 scanlines (source y 40..164 on 260×220 canvas, path translated x40/y170). Pair minimum clearances were AS 36.500244, SI 20.635964, IA 22.399999 source units. Adjust the next glyph positions by AS -28, SI -12, IA -14 native units cumulatively. New minima: AS 8.500244, SI 8.635964, IA 8.399999; range 0.2359650000000002 source units. All are positive (no contact).

No glyph path d data changed. Font, 550 weight, the ASIA uniform scale and exact source V-01 seal are immutable. Recenter both IN and ASIA together by +53.587542 parent-space units. This maintains the IN–ASIA word gap rather than accidentally opening it; bottom line becomes ~90.49% of EDUCATION, centered. This prefers correct optically balanced kerning over exact full-width alignment and does not stretch glyphs.

Updated 6 SVG review candidates and all public mirrors. No generative image output; review only; canonical Turkish and bilingual lockups unchanged.
