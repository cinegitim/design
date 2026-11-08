# Generation notes

**Pipeline (deterministic, reproducible):**
1. `build.py --css` — legacy CSS prototypes (kept for provenance; the commit does not ship them).
2. `svgmaster.py` — converts the measured CSS geometry (`qa/geometry-report.json`) into six
   `source/NN.svg` vector masters: pre-cropped photos with object-fit semantics, text at measured
   baselines with real Jost metrics, decorative devices, and the canonical lockups linked as
   `<image>` (never redrawn). Writes `source/NN.html` wrappers that inline the same SVG.
3. `build.py` — renders `export/NN.png` (1080×1350) with headless Chromium and runs the in-page
   QA harness (copy, bounds, safe area, clipping, overlaps, per-line metrics).
4. `deliver.py` — manifest, render-validation, comparison sheets, ZIP, gallery copy.

**Why original/ equals export/:** this pipeline has no post-render raster editing; the delivered PNG
is the deterministic render of `source/NN.svg`. `original/` records that first (and only) render.

**Single source of truth for colour:** `svgmaster.py`. The campaign accent is Korean blue `#003478`;
brand red `#BD2120` survives only inside the linked canonical lockup SVGs under `assets/lockups/`,
which are locked assets and were never edited. Slide 01's accent line additionally carries the
`QS_SHADOW` drop shadow for legibility over photography — see `quality-review.md`.

**Note on generated docs:** `quality-review.md` and `generation-notes.md` (this file) are themselves
emitted by `deliver.py`. Edit the templates inside `deliver.py`, never these files — a hand edit
here is silently overwritten on the next run.

**Image generation:** none. Zero AI raster calls; all photography is real Wikimedia Commons imagery
(`photo-credits.md`). No paid image or API usage.

**Fonts:** Jost variable font (SIL OFL 1.1) bundled at `assets/Jost-VF.ttf`.

**Reproduce:** `python3 build.py --css && python3 svgmaster.py && python3 build.py && python3 deliver.py`
(requires Google Chrome and Python 3 + Pillow; no network needed at render time).
