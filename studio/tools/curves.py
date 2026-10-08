#!/usr/bin/env python
"""Corner-aware cubic Bézier reconstruction of the Asya'da Eğitim wordmark.

The WU wordmark is a polygonal reconstruction: 592 vertices, 552 straight
segments, zero curves, traced with approxPolyDP(epsilon=0.9). At 800 % that
reads as flat facets and small bumps. This module rebuilds each contour as
cubic Béziers WITHOUT smoothing indiscriminately.

Method
------
1. Trace dense contours (CHAIN_APPROX_NONE) from the same reference mask, so
   the input carries no approximation error of its own.
2. Detect true corners by multi-scale turning: a vertex is a corner when the
   angle between its incoming and outgoing chords stays sharp across several
   window sizes. Raster stair-steps are 1-2 px and wash out at larger windows;
   a genuine apex in an A or the terminal of an S stays sharp at every scale.
   That separation is what lets the S bowl be smoothed while the A apex and
   the E arm terminals stay sharp.
3. Split each contour at corners into smooth spans.
4. Fit a chain of cubic Béziers to each span. Endpoints are fixed at the
   original vertices, and end tangents at a CORNER are pinned to the corner
   bisector so the fit meets the corner exactly. Interior joins are G1.
5. Subdivide adaptively: keep splitting the worst-fitting span until every
   span is under the error tolerance, so curvature is represented only where
   the letterform actually has it.

Fitting is least-squares (Schneider's method) with tangents estimated by
one-sided weighted least squares, re-estimated after each split. Corner error
and max radial deviation are both reported, and every fit is checked against
a raster re-render before it is accepted.
"""
import math

import cv2
import numpy as np

INK, PAPER = "#1D2027", "#F7F3E9"


# --------------------------------------------------------------------------
# corner detection
# --------------------------------------------------------------------------
def _turn_angle(pts, i, window):
    """Angle (radians) between the chords entering and leaving vertex i."""
    n = len(pts)
    a = pts[(i - window) % n]
    b = pts[i]
    c = pts[(i + window) % n]
    v1 = np.array([a[0] - b[0], a[1] - b[1]], float)
    v2 = np.array([c[0] - b[0], c[1] - b[1]], float)
    n1, n2 = np.linalg.norm(v1), np.linalg.norm(v2)
    if n1 < 1e-9 or n2 < 1e-9:
        return 0.0
    cs = float(np.clip(np.dot(v1, v2) / (n1 * n2), -1.0, 1.0))
    return math.acos(cs)


def _fit_line(seg):
    """Total-least-squares line; returns (angle_in_[0,pi), max_residual).

    The angle is folded into [0, pi) so a line's direction is ORIENTATION
    INDEPENDENT. atan2 alone returns a principal direction, and two lines that
    are the same line traversed in opposite directions come out 180 deg apart —
    which made a straight edge read as a hard corner and a circle read as
    hundreds of them.
    """
    p = np.asarray(seg, float)
    c = p.mean(axis=0)
    q = p - c
    u, s, vt = np.linalg.svd(q, full_matrices=False)
    d = vt[0]                       # principal axis = the line's DIRECTION
    normal = vt[1]                  # vt[1] is perpendicular to it
    resid = np.abs(q @ normal)       # PERPENDICULAR deviation from the line
    ang = math.atan2(d[1], d[0]) % math.pi
    return ang, float(resid.max() if len(resid) else 0.0)


def find_corners(pts, half=6, sharp_deg=34.0, max_resid=0.55, cluster_n=6.0):
    """Vertices where two genuinely STRAIGHT edges meet.

    Windowed turn angles alone cannot separate a corner from dense sampling: on
    a circle the chord angle grows in proportion to the window, so it passes
    any absolute threshold by w=32 and the whole curve reads as 60+ "corners".

    So each vertex is tested structurally instead: fit a line to the half-window
    before it and another to the half-window after it. A real corner has two
    low-residual straight fits meeting at a large angle. A point on a curve has
    two good fits too, but they meet at a small angle. Stair-step noise fails
    the residual test.
    """
    n = len(pts)
    if n < 4 * half + 4:
        return []
    thresh = math.radians(sharp_deg)
    # A half-window must be long enough that a line fitted through it hugs the
    # true edge. At half=6 on a 0.7 px resample the window spans ~4 px, so the
    # fitted line still carries ~1.7 px of residual and a genuine 90 deg corner
    # fails the flatness test. Scale the window to the contour's own step so
    # the test is resolution-independent.
    seg = np.linalg.norm(np.diff(np.vstack([np.asarray(pts, float),
                                              np.asarray(pts, float)[:1]]), axis=0), axis=1)
    step = float(np.median(seg)) if len(seg) else 1.0
    if step <= 1e-9:
        return []
    half = max(3, half)
    if n < 4 * half + 4:
        return []
    # Flatness limit relative to this contour's own step. A fitted line through
    # half a window of samples deviates by roughly the window's sagitta, so a
    # real straight edge leaves a residual on the order of one step. Two steps
    # keeps that test meaningful without rejecting genuine corners on a
    # 0.7 px resample (where a 3-sample window still leaves ~0.7 px).
    resid_limit = max(max_resid, step * 2.0)
    cands = []
    for i in range(n):
        pre = [pts[(i - k) % n] for k in range(1, half + 1)]
        post = [pts[(i + k) % n] for k in range(1, half + 1)]
        a1, r1 = _fit_line(pre)
        a2, r2 = _fit_line(post)
        if max(r1, r2) > resid_limit:
            continue
        da = abs(a2 - a1)
        if da > math.pi / 2:
            da = math.pi - da          # lines are undirected: [0, pi/2]
        if da >= thresh:
            cands.append((da, i))
    # A single geometric corner registers on SEVERAL adjacent samples, because
    # the two straight edges stay flat for a sample or two either side. Cluster
    # candidates by spatial proximity (not index distance, which depends on the
    # resample step) and keep the sharpest of each cluster.
    if not cands:
        return []
    cands.sort(key=lambda t: -t[0])
    # Cluster along the CONTOUR. A single geometric corner shows up as a run of
    # adjacent candidates — the two straight edges stay flat for a window or two
    # either side of the true vertex (a square corner registers over ~7 samples).
    # The run length is set by the ANALYSIS WINDOW, not by a fixed distance: a
    # smaller radius than ~2x half leaves the run split into several corners.
    keep = []
    window = max(6, half * 2)
    for da, i in sorted(cands, key=lambda t: t[1]):   # traverse in order
        if keep:
            last = keep[-1][1]
            # wrap-aware: index 0 and index n-1 are neighbours on a closed ring
            gap = min(abs(i - last), n - abs(i - last))
            if gap < window:
                if da > keep[-1][0]:
                    keep[-1] = (da, i)
                continue
        keep.append((da, i))
    if len(keep) > 1:
        a, b = keep[0][1], keep[-1][1]
        if n - (b - a) < window:
            # same corner straddling the ring's start point
            if keep[0][0] >= keep[-1][0]:
                keep.pop()
            else:
                keep.pop(0)
    return sorted(i for _, i in keep)


def split_spans(pts, corners):
    """Contour points split into spans between consecutive corners."""
    n = len(pts)
    if not corners:
        return [list(range(n))]
    spans = []
    for k in range(len(corners)):
        a = corners[k]
        b = corners[(k + 1) % len(corners)]
        if b > a:
            spans.append(list(range(a, b + 1)))
        else:                                  # wraps through index 0
            spans.append(list(range(a, n)) + list(range(0, b + 1)))
    return [s for s in spans if len(s) >= 4]


# --------------------------------------------------------------------------
# cubic Bézier fitting (Schneider)
# --------------------------------------------------------------------------
def _bezier(t, p0, p1, p2, p3):
    t = t[:, None]
    mt = 1 - t
    return (mt ** 3) * p0 + 3 * (mt ** 2) * t * p1 + 3 * mt * (t ** 2) * p2 + (t ** 3) * p3


def _chord_parameterize(pts):
    """Normalised cumulative chord length, one value per point."""
    pts = np.asarray(pts, float)
    if len(pts) < 2:
        return np.zeros(len(pts))
    d = np.linalg.norm(np.diff(pts, axis=0), axis=1)
    u = np.concatenate([[0.0], np.cumsum(d)])
    if u[-1] <= 0:
        return np.linspace(0, 1, len(pts))
    return u / u[-1]


def _bernstein(t):
    mt = 1 - t
    return (mt ** 3, 3 * mt ** 2 * t, 3 * mt * t ** 2, t ** 3)


def _generate_bezier(pts, t1, t2, t):
    """Least-squares cubic with fixed endpoints and fixed end tangent DIRECTIONS.

    Solves the 2x2 normal equations for the two tangent magnitudes alpha1, alpha2
    (Schneider's method). Tangents are unit direction vectors here; only their
    magnitudes are fitted, so the direction is never corrupted.

    `t` is the chord-length parameterisation of `pts`.
    """
    t = np.asarray(t, float)
    if t.shape[0] != pts.shape[0]:
        t = np.linspace(0.0, 1.0, pts.shape[0])
    p0, p3 = pts[0], pts[-1]
    t1 = np.asarray(t1, float)
    t2 = np.asarray(t2, float)
    n = min(t1[0], t1[1]) if t1[0] != 0 or t1[1] != 0 else 1.0
    if np.hypot(*t1) < 1e-12:
        t1 = np.array([1.0, 0.0])
    if np.hypot(*t2) < 1e-12:
        t2 = np.array([1.0, 0.0])

    b0, b1, b2, b3 = _bernstein(t)
    # C(t) = (b0+b1)p0 + (b2+b3)p3 + b1*a1*t1 - b2*a2*t2
    # because p2 = p3 - a2*t2. The MINUS on the second column is what makes the
    # 2x2 solve come out positive; leaving it out yields a negative alpha2, which
    # the clamp silently zeroes and every curve collapses (p2 == p3).
    w1 = b1[:, None] * t1[None, :]              # (n,2)
    w2 = -(b2[:, None] * t2[None, :])
    rhs = pts - (b0 + b1)[:, None] * p0 - (b2 + b3)[:, None] * p3
    A = np.array([[np.sum(w1 * w1), np.sum(w1 * w2)],
                  [np.sum(w1 * w2), np.sum(w2 * w2)]])
    b = np.array([np.sum(w1 * rhs), np.sum(w2 * rhs)])
    try:
        alpha = np.linalg.solve(A + np.eye(2) * 1e-12, b)
    except np.linalg.LinAlgError:
        alpha = np.array([len(t) / 3.0, len(t) / 3.0])
    chord = float(np.linalg.norm(p3 - p0))
    if chord < 1e-9:
        # endpoints coincide (closing sample of a tiny contour): nothing to fit
        return pts[0].copy(), pts[0].copy()
    # A cubic through points that actually CURVE cannot have a zero tangent
    # magnitude: that would make it a straight line, and the least-squares
    # solve returns ~0 whenever a span is short and the normal equations are
    # ill-conditioned. Chained, those straight segments are exactly the
    # stair-stepped facets that made the polygonal build look bad at 800 %.
    #
    # The floor is applied unconditionally, not only to "curved" spans. On a
    # genuine straight edge the two end tangents both lie along the chord, so a
    # small magnitude keeps the control polygon collinear and renders the
    # identical straight line — the floor costs nothing there and buys tangent
    # continuity everywhere else.
    cap = chord * 2.5
    floor = chord * 0.05
    a1 = float(np.clip(alpha[0], floor, cap))
    a2 = float(np.clip(alpha[1], floor, cap))
    return p0 + t1 * a1, p3 - t2 * a2


def _reparameterize(pts, bez):
    p0, p1, p2, p3 = bez
    dense = np.linspace(0, 1, 200)
    approx = _bezier(dense, p0, p1, p2, p3)
    d = np.linalg.norm(approx[:, None, :] - pts[None, :, :], axis=2)
    j = np.argmin(d, axis=0)
    err = d[j, np.arange(len(pts))]
    return err, j


def _chord_tangent(pts, first, last):
    """One-sided tangent at a span endpoint, pointing ALONG the span.

    Both endpoints return the FORWARD travel direction; `_generate_bezier`
    already subtracts the second control point from the endpoint
    (`p3 - a2*t2`), so the span-end tangent must not be negated here. Negating
    it yields a negative least-squares magnitude, which the clamp then zeroes,
    collapsing every curve.
    """
    p = np.asarray(pts, float)
    n = len(p)
    if n < 3:
        return np.array([1.0, 0.0])
    # Central difference over the first/last three points. The naive
    # (a-b)+(c-b) estimator nearly CANCELS at a span end on a curve — the
    # backward step and the forward step are equal and opposite along the
    # tangent — so the result collapses toward the curve normal, and every
    # fitted segment comes back degenerate with p1 == p0.
    if first:
        v = p[2] - p[0]
        forward = p[1] - p[0]
    else:
        v = p[-1] - p[-3]
        forward = p[-1] - p[-2]
    if np.hypot(*v) < 1e-9:
        v = forward.copy()
    nrm = np.hypot(*v)
    if nrm < 1e-9:
        return np.array([1.0, 0.0])
    t = v / nrm
    fw = forward / (np.hypot(*forward) or 1.0)
    if float(np.dot(t, fw)) < 0:
        t = -t
    return t


def resample(pts, step=0.7):
    """Resample a closed contour to ~`step` px spacing.

    OpenCV contour output is unevenly spaced and can be very sparse on flat
    edges. Multi-scale corner detection needs several points per edge to tell
    an edge junction from sampling density, so the contour is resampled first.
    Corners survive: resampling walks the polyline, so a corner vertex falls on
    or very near a sample.
    """
    pts = np.asarray(pts, float)
    n = pts.shape[0]
    if n < 2:
        return pts
    # cum has n+1 entries when the ring is closed, n when open
    closed = np.allclose(pts[0], pts[-1])
    seg = np.linalg.norm(np.diff(pts, axis=0), axis=1)
    cum = np.concatenate([[0.0], np.cumsum(seg)])
    total = cum[-1]
    if total <= 0:
        return pts
    n_out = max(8, int(round(total / step)))
    targets = np.linspace(0.0, total, n_out, endpoint=closed)
    out = np.empty((targets.shape[0], 2), float)
    for d in (0, 1):
        out[:, d] = np.interp(targets, cum, pts[:, d])
    return out


def _polyline_fallback(pts):
    """Too-short span: follow the polyline instead of collapsing to a line.

    Emitting a zero-magnitude cubic here renders as a straight cut across the
    span, which is one of the visible facets.
    """
    pts = np.asarray(pts, float)
    segs = [(pts[k], pts[k], pts[k + 1], pts[k + 1]) for k in range(len(pts) - 1)]
    return segs or [(pts[0], pts[0], pts[-1], pts[-1])]


def fit_cubic_chain(pts, tol=0.16, max_split=9, corner_ends=None):
    """Fit cubics to a smooth span; subdivide until max deviation < tol."""
    pts = np.asarray(pts, float)
    if len(pts) < 8:
        # Too few points for a central-difference tangent to mean anything: on a
        # 4-point square it returns the DIAGONAL of the shape, and the fitted
        # cubic then bows far outside the outline. Such a span is a run of
        # straight edges between nearby corners, so the polyline through the
        # points IS the outline.
        return _polyline_fallback(pts), 0.0
    if corner_ends:
        a = corner_ends[0] if corner_ends[0] is not None else _chord_tangent(pts, True, False)
        b = corner_ends[1] if corner_ends[1] is not None else _chord_tangent(pts, False, True)
    else:
        a = _chord_tangent(pts, True, False)
        b = _chord_tangent(pts, False, True)
    return _fit_recursive(pts, a, b, tol, 0, max_split)


def _fit_recursive(pts, t1, t2, tol, depth, max_split, corner_ends=None):
    pts = np.asarray(pts, float)
    n = len(pts)
    if n < 4:
        return _polyline_fallback(pts), 0.0
    t = _chord_parameterize(pts)
    p1, p2 = _generate_bezier(pts, t1, t2, t)
    bez = (pts[0], p1, p2, pts[-1])
    err, _ = _reparameterize(pts, bez)
    if depth >= max_split or err.max() <= tol or n < 8:
        # Do not split below 8 points. A sub-span that short is only a few
        # pixels long, the normal equations go singular, and the fit falls back
        # to a polyline — chaining those is what produced the visible facets.
        # Fitting one cubic across the whole short span is both smoother and
        # more accurate than subdividing it.
        return [bez], float(err.max())
    i = int(np.argmax(err))
    # Both halves keep enough points to fit a well-conditioned cubic.
    i = min(max(i, 4), n - 4)
    # Forward tangent AT the split point index i. It must be taken from the
    # points surrounding i, not from the start of the left sub-span — reading
    # it from pts[:i+1] as a START tangent returns the direction near index 0,
    # which sends both sub-spans off with a wrong end tangent and every fitted
    # segment comes back degenerate.
    mid_fwd = _chord_tangent(pts[i - 2:i + 1], False, True)
    l, wl = _fit_recursive(pts[:i + 1], t1, mid_fwd, tol, depth + 1, max_split)
    r, wr = _fit_recursive(pts[i:], mid_fwd, t2, tol, depth + 1, max_split)
    return l + r, max(wl, wr)


# --------------------------------------------------------------------------
# SVG emission
# --------------------------------------------------------------------------
def fmt(v):
    s = "%.2f" % v
    return s.rstrip("0").rstrip(".") if "." in s else s


def _corner_tangents(pts, span, corners):
    """Tangents pinned so a span meets each corner exactly on its bisector.

    Without this the fit rounds off sharp terminals: the curve arrives at the
    apex with whatever tangent the least-squares wanted, which is what turns a
    pointed A into a blunt one.
    """
    a_idx, b_idx = span[0], span[-1]
    t1 = t2 = None
    if a_idx in corners:
        i = a_idx % len(pts)
        prev_pt = np.array(pts[(i - 1) % len(pts)], float)
        here = np.array(pts[i], float)
        nxt = np.array(pts[(i + 1) % len(pts)], float)
        v1 = prev_pt - here
        v2 = nxt - here
        n1, n2 = np.linalg.norm(v1), np.linalg.norm(v2)
        if n1 > 1e-9 and n2 > 1e-9:
            t1 = (v1 / n1 + v2 / n2)
            t1 = -t1 / (np.linalg.norm(t1) or 1.0)   # point INTO the span
    if b_idx in corners:
        j = b_idx % len(pts)
        prev_pt = np.array(pts[(j - 1) % len(pts)], float)
        here = np.array(pts[j], float)
        nxt = np.array(pts[(j + 1) % len(pts)], float)
        v1 = prev_pt - here
        v2 = nxt - here
        n1, n2 = np.linalg.norm(v1), np.linalg.norm(v2)
        if n1 > 1e-9 and n2 > 1e-9:
            t2 = (v1 / n1 + v2 / n2)
            t2 = t2 / (np.linalg.norm(t2) or 1.0)    # point OUT of the span
    return t1, t2


def shift_path(d, dx, dy):
    """Translate every coordinate in an SVG path string by (dx, dy).

    Walks the command stream rather than pattern-matching a letter followed by
    a pair. The letter-based regex silently skips any coordinate pair that does
    not directly follow a command letter — and `fmt` strips trailing zeros, so
    most coordinates come out as bare integers ("C100 100 100 100 99 4"). Only
    the first pair of each command was being shifted, which scattered control
    points and rendered the letterforms as hair-thin spikes.
    """
    import re
    toks = re.findall(r"[MLCZmlcz]|[-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?", d)
    out = []
    i = 0
    ncoord = {"M": 2, "L": 2, "C": 6, "m": 2, "l": 2, "c": 6}
    while i < len(toks):
        t = toks[i]
        if t in ncoord:
            k = ncoord[t]
            # coordinates alternate x, y, x, y ... — dx on the even positions,
            # dy on the odd ones
            vals = []
            for j in range(k):
                v = float(toks[i + 1 + j])
                vals.append(fmt(v + (dx if j % 2 == 0 else dy)))
            out.append(t + " " + " ".join(vals))
            i += 1 + k
        else:
            out.append(t)
            i += 1
    return " ".join(out)


def flatten_path(d, per_seg=16):
    """Flatten an SVG path (M/L/C/Z) to a dense polygon, for verification.

    Returns a list of (n,2) arrays, one per subpath.
    """
    import re
    toks = re.findall(r"[MLCZ]|[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", d)
    i, cur, out, subs = 0, (0.0, 0.0), [], []
    while i < len(toks):
        t = toks[i]
        if t == "M":
            if len(out) > 1:
                subs.append(np.array(out, float))
            out = []
            cur = (float(toks[i + 1]), float(toks[i + 2])); i += 3
            out.append(cur)
        elif t == "L":
            cur = (float(toks[i + 1]), float(toks[i + 2])); i += 3
            out.append(cur)
        elif t == "C":
            x1, y1, x2, y2, x3, y3 = (float(v) for v in toks[i + 1:i + 7])
            p0 = cur
            for k in range(1, per_seg + 1):
                u = k / per_seg
                mu = 1 - u
                out.append((mu ** 3 * p0[0] + 3 * mu ** 2 * u * x1 + 3 * mu * u ** 2 * x2 + u ** 3 * x3,
                            mu ** 3 * p0[1] + 3 * mu ** 2 * u * y1 + 3 * mu * u ** 2 * y2 + u ** 3 * y3))
            cur = (x3, y3); i += 7
        elif t == "Z":
            if len(out) > 1:
                subs.append(np.array(out, float))
            out = []
            i += 1
        else:
            i += 1
    if len(out) > 1:
        subs.append(np.array(out, float))
    return subs if subs else [np.array(out, float).reshape(-1, 2)]


def path_deviation(path_d, pts, per_seg=24):
    """Max distance from each source point to the nearest flattened subpath."""
    pts = np.asarray(pts, float)
    if pts.ndim != 2 or pts.shape[1] != 2 or pts.shape[0] < 1:
        raise ValueError("pts must be an (n,2) array, got %r" % (pts.shape,))
    best = None
    for poly in flatten_path(path_d, per_seg=per_seg):
        if len(poly) < 2:
            continue
        # reduce over the FLATTENED points, leaving one value per source point
        dd = np.linalg.norm(poly[:, None, :] - pts[None, :, :], axis=2).min(0)
        best = dd if best is None else np.minimum(best, dd)
    if best is None or best.shape[0] != pts.shape[0]:
        return np.full(pts.shape[0], np.inf)
    return best


def _as_points(pts):
    """Coerce a ring to an (n,2) float array.

    Accepts tuples, numpy rows, or arrays; unwraps a leading singleton list so
    a stored ring ([outer, hole...], each a list of points) can be passed whole.
    """
    a = np.asarray(pts, dtype=object)
    # stored form is [[outer, hole, ...]] — one ring per group element, each a
    # list of points — so a leading singleton axis means "one ring here"
    if a.ndim == 3 and a.shape[0] == 1:
        a = a[0]
    if a.ndim == 3:
        a = np.reshape(a, (-1, 2))
    if a.ndim == 1 and a.shape[0] and isinstance(a[0], (list, np.ndarray)) \
            and np.asarray(a[0]).ndim >= 2:
        a = np.asarray(a[0], dtype=object)
    if a.ndim != 2:
        a = np.reshape(a, (-1, 2))
    out = np.empty((a.shape[0], 2), float)
    for i, p in enumerate(a):
        row = np.asarray(p, dtype=object).ravel()
        out[i, 0] = float(row[0])
        out[i, 1] = float(row[1])
    return out


def smooth_span(pts, passes=3, keep_ends=3):
    """Endpoint-pinned binomial smoothing along one span.

    A contour traced from a raster carries the source image's own quantisation:
    its outline steps in whole pixels, so a dense 0.7 px resample turns those
    1 px steps into small ripples that the Bézier fit then faithfully
    reproduces. The polygonal build never showed them because `approxPolyDP`
    averaged over the steps on its way through.

    Repeated [1 2 1]/4 convolution is the same low-pass, applied only along the
    span, with the first and last `keep_ends` samples held fixed so corner
    vertices and span endpoints stay exactly on the outline. Corners are
    therefore never rounded: they are the boundaries of the spans being
    smoothed, not part of any one span's interior.
    """
    p = np.asarray(pts, float)
    n = len(p)
    if n < 2 * keep_ends + 3 or passes <= 0:
        return p
    out = p.copy()
    for _ in range(passes):
        q = out.copy()
        mid = slice(keep_ends, n - keep_ends)
        q[mid] = (out[keep_ends - 1:n - keep_ends - 1]
                  + 2.0 * out[keep_ends:n - keep_ends]
                  + out[keep_ends + 1:n - keep_ends + 1]) / 4.0
        out = q
    return out


def bezier_path(rings, tol=0.16, smooth_passes=3):
    """Emit one SVG path string for a ring-group ([outer, holes...]).

    Corners are handled by SPLITTING, not by bending: each span between corners
    is fitted on its own and its endpoints are pinned to the corner vertices, so
    the outline passes exactly through every sharp point. The tangent at a span
    end is simply taken from the neighbouring points, which at a corner follows
    the incoming edge (and at the next span, the outgoing one) — leaving a real
    direction change there, which is what a corner IS.

    Pinning the end tangents to the corner BISECTOR instead (so the curve would
    arrive and leave along the same direction) produces hair-thin spikes: the
    fit is forced to reconcile two different edge directions with one tangent,
    and the least-squares magnitudes blow up.
    """
    parts = []
    for pts in rings:
        pts = _as_points(pts)
        corners = find_corners(pts)
        spans = split_spans(pts, corners)
        if not spans:
            continue
        first = True
        for span in spans:
            sub = np.array([pts[j] for j in span], float)
            fit_src = smooth_span(sub, passes=smooth_passes)
            segs, _ = fit_cubic_chain(fit_src, tol=tol)
            for p0, p1, p2, p3 in segs:
                if first:
                    parts.append("M%s %s" % (fmt(p0[0]), fmt(p0[1])))
                    first = False
                parts.append("C%s %s %s %s %s %s" % (
                    fmt(p1[0]), fmt(p1[1]), fmt(p2[0]), fmt(p2[1]),
                    fmt(p3[0]), fmt(p3[1])))
    return "".join(parts) + "Z"


def _fit_with_ends(pts, t1, t2, tol, max_split=9):
    """Fit a span whose end tangents are pinned (used at corners)."""
    pts = np.asarray(pts, float)
    if len(pts) < 4:
        return _polyline_fallback(pts), 0.0
    a = t1 if t1 is not None else _chord_tangent(pts, True, False)
    b = t2 if t2 is not None else _chord_tangent(pts, False, True)
    return _fit_recursive(pts, a, b, tol, 0, max_split)