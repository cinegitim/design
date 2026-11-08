#!/usr/bin/env python3
"""Independent pixel check: no copy may ride high inside a painted chip.

render.mjs already gates centring from SVG glyph outlines. This is the second,
independent opinion, and it reads the *finished PNG* rather than the vector
source. Chip rects come from text-layout.json (recorded from the DOM), so no
image segmentation is involved and photographic regions cannot produce false
positives.

The criterion is one-sided on purpose. A line is centred as a line box: space
reserved for descenders sits below the baseline, so the visible x-height band
naturally reads slightly low. Ink riding HIGH means the baseline was pushed
above its line box, which is the defect being guarded against.
"""
import json
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent.parent
# Ink colour is read per run from the recorded fill; chips may be light-on-dark.
TOL = 26
MIN_ROW_SHARE = 0.02  # row needs this share of chip width to count as ink
MAX_LIFT = 10.0       # px; ink riding higher than this inside the chip is a defect
MIN_TOP_GAP = 2       # px


def _near(px, rgb, tol=TOL):
    return all(abs(px[i] - rgb[i]) <= tol for i in range(3))


def _rgb(hex_colour):
    h = hex_colour.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _measure(im, chip, ink):
    """Ink extent inside a chip. Rows need a small share of the chip width so a
    cedilla cannot count, but low enough that a short trailing line registers."""
    x0, y0 = int(chip['x']) + 3, int(chip['y']) + 3
    x1, y1 = int(chip['x'] + chip['width']) - 3, int(chip['y'] + chip['height']) - 3
    px = im.load()
    need = max(3, int((x1 - x0) * MIN_ROW_SHARE))
    rows = [y for y in range(y0, y1 + 1)
            if sum(1 for x in range(x0, x1 + 1) if _near(px[x, y], ink)) >= need]
    if not rows:
        return None
    top_gap = rows[0] - int(chip['y'])
    bot_gap = int(chip['y'] + chip['height']) - rows[-1]
    return top_gap, bot_gap, bot_gap - top_gap, rows[0], rows[-1]


def main():
    layout = json.loads((HERE / 'text-layout.json').read_text())
    defects = worst = 0
    for slide in sorted(layout):
        im = Image.open(HERE / 'final' / f'{slide}.png').convert('RGB')
        chips = {}
        for item in layout[slide]['copy']:
            for run in item['runs']:
                if run.get('chipBox'):
                    key = json.dumps(run['chipBox'], sort_keys=True)
                    chips.setdefault(key, (item, run['chipBox'], run['color']))
        if not chips:
            continue
        print(f'\n== {slide}')
        for _, (item, chip, colour) in sorted(chips.items(), key=lambda kv: kv[1][1]['y']):
            got = _measure(im, chip, _rgb(colour))
            if got is None:
                print(f'  -- chip x{int(chip["x"])}-{int(chip["x"] + chip["width"])} '
                      f'no ink found')
                continue
            top_gap, bot_gap, lift, r0, r1 = got
            bad = top_gap < MIN_TOP_GAP or lift > MAX_LIFT
            defects += bool(bad)
            worst = max(worst, lift)
            print(f'  {"OFF" if bad else "OK "} #{item["index"]:<2} {item["role"]:<10} '
                  f'chip y{int(chip["y"])}-{int(chip["y"] + chip["height"])} '
                  f'ink y{r0}-{r1} top={top_gap:3d} bottom={bot_gap:3d} lift={lift:+5.1f}px')
    print(f'\nworst lift {worst:+.1f}px, {defects} defect(s)')
    return 1 if defects else 0


if __name__ == '__main__':
    sys.exit(main())
