#!/usr/bin/env python3
"""Trace the current user-supplied Cin Eğitim symbol into vector paths.

This deliberately does not use any of the older Concept 03 references.
"""
from collections import defaultdict
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "brands/cin-egitim/explorations/enso"
SOURCE = RUN / "source-user-upload.png"
OUTPUT = RUN / "user-upload-trace.svg"
MONO = RUN / "user-upload-trace-mono.svg"


def rdp(points, epsilon):
    """Iterative Ramer-Douglas-Peucker for an open point sequence."""
    if len(points) <= 2:
        return points
    keep = {0, len(points) - 1}
    stack = [(0, len(points) - 1)]
    while stack:
        first, last = stack.pop()
        ax, ay = points[first]
        bx, by = points[last]
        dx, dy = bx - ax, by - ay
        length = (dx * dx + dy * dy) ** 0.5
        best_distance, best_index = -1.0, None
        for i in range(first + 1, last):
            px, py = points[i]
            if length:
                distance = abs(dy * (px - ax) - dx * (py - ay)) / length
            else:
                distance = ((px - ax) ** 2 + (py - ay) ** 2) ** 0.5
            if distance > best_distance:
                best_distance, best_index = distance, i
        if best_index is not None and best_distance > epsilon:
            keep.add(best_index)
            stack.extend(((first, best_index), (best_index, last)))
    return [points[i] for i in sorted(keep)]


def simplify_loop(loop, epsilon=0.8):
    if len(loop) < 5:
        return loop
    # Split a closed contour at approximately opposite vertices, simplify both
    # halves, then join them. This avoids a degenerate closed RDP baseline.
    a = max(range(1, len(loop)), key=lambda i: (loop[i][0] - loop[0][0]) ** 2 + (loop[i][1] - loop[0][1]) ** 2)
    b = max((i for i in range(1, len(loop)) if i != a),
            key=lambda i: (loop[i][0] - loop[a][0]) ** 2 + (loop[i][1] - loop[a][1]) ** 2)
    if a > b:
        a, b = b, a
    chain1 = loop[a:b + 1]
    chain2 = loop[b:] + loop[:a + 1]
    result = rdp(chain1, epsilon)[:-1] + rdp(chain2, epsilon)[:-1]
    return result if len(result) >= 3 else loop


def mask_contours(mask, width, height):
    """Return pixel-edge contours, preserving enclosed negative-space holes."""
    edges = []
    for y in range(height):
        row = mask[y]
        for x, active in enumerate(row):
            if not active:
                continue
            if y == 0 or not mask[y - 1][x]:
                edges.append(((x, y), (x + 1, y)))
            if x + 1 == width or not row[x + 1]:
                edges.append(((x + 1, y), (x + 1, y + 1)))
            if y + 1 == height or not mask[y + 1][x]:
                edges.append(((x + 1, y + 1), (x, y + 1)))
            if x == 0 or not row[x - 1]:
                edges.append(((x, y + 1), (x, y)))

    outgoing = defaultdict(list)
    for i, (start, end) in enumerate(edges):
        outgoing[start].append(i)
    used = bytearray(len(edges))
    direction = {(1, 0): 0, (0, 1): 1, (-1, 0): 2, (0, -1): 3}
    contours = []
    for first in range(len(edges)):
        if used[first]:
            continue
        start, end = edges[first]
        contour = [start]
        current_edge = first
        while not used[current_edge]:
            used[current_edge] = 1
            a, b = edges[current_edge]
            contour.append(b)
            if b == start:
                break
            incoming = direction[(b[0] - a[0], b[1] - a[1])]
            candidates = [i for i in outgoing.get(b, ()) if not used[i]]
            if not candidates:
                break
            # At a diagonal touch, take the tight right turn so separate
            # foreground regions do not become a self-crossing contour.
            rank = {1: 0, 0: 1, 3: 2, 2: 3}
            current_edge = min(
                candidates,
                key=lambda i: rank[(direction[(edges[i][1][0] - b[0], edges[i][1][1] - b[1])] - incoming) % 4],
            )
        if len(contour) > 4 and contour[-1] == contour[0]:
            contours.append(contour[:-1])
    return contours


def path_for(mask, width, height, offset_x, offset_y):
    paths = []
    for contour in mask_contours(mask, width, height):
        points = simplify_loop(contour)
        if len(points) < 3:
            continue
        coords = [(x + offset_x, y + offset_y) for x, y in points]
        d = f"M{coords[0][0]} {coords[0][1]}"
        d += "".join(f"L{x} {y}" for x, y in coords[1:]) + "Z"
        paths.append(d)
    return "".join(paths)


def main():
    image = Image.open(SOURCE).convert("RGB")
    width, height = image.size
    pixels = image.load()
    red_mask = [[False] * width for _ in range(height)]
    ink_mask = [[False] * width for _ in range(height)]
    red_points, ink_points = [], []
    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            is_red = r - g > 70 and r - b > 35 and r > 100
            is_ink = max(r, g, b) < 100
            red_mask[y][x] = is_red
            ink_mask[y][x] = is_ink
            if is_red:
                red_points.append((x, y))
            if is_ink:
                ink_points.append((x, y))

    all_points = red_points + ink_points
    min_x = min(x for x, _ in all_points) - 14
    min_y = min(y for _, y in all_points) - 14
    max_x = max(x for x, _ in all_points) + 15
    max_y = max(y for _, y in all_points) + 15
    view_box = f"{min_x} {min_y} {max_x - min_x} {max_y - min_y}"
    red_d = path_for(red_mask, width, height, 0, 0)
    ink_d = path_for(ink_mask, width, height, 0, 0)

    color_svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{view_box}" role="img" '
        'aria-labelledby="title desc"><title id="title">Çin Eğitim — kullanıcı referansından izleme</title>'
        '<desc id="desc">Kullanıcının son gönderdiği görselden vektörleştirilmiş kırmızı ve siyah sembol. '
        'Onay bekleyen çalışma adayıdır.</desc>'
        f'<path fill="#B62B34" fill-rule="evenodd" d="{red_d}"/>'
        f'<path fill="#1F1F1F" fill-rule="evenodd" d="{ink_d}"/></svg>'
    )
    mono_svg = color_svg.replace('fill="#B62B34"', 'fill="#1F1F1F"')
    OUTPUT.write_text(color_svg, encoding="utf-8")
    MONO.write_text(mono_svg, encoding="utf-8")
    print(f"source={image.size}; viewBox={view_box}")
    print(f"red_pixels={len(red_points)}; ink_pixels={len(ink_points)}")
    print(f"svg_bytes={len(color_svg.encode())}; contours_red={red_d.count('M')}; contours_ink={ink_d.count('M')}")
    print(f"wrote={OUTPUT.relative_to(ROOT)} and {MONO.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
