# -*- coding: utf-8 -*-
"""Composants de data-journalisme animés (section G du dossier)."""
import math
import numpy as np
import skia
from gfx import *

GEO = None


def geo():
    global GEO
    if GEO is None:
        GEO = Geo()
    return GEO


def fmt(n, dec=0):
    if dec:
        s = f"{n:,.{dec}f}".replace(",", " ").replace(".", ",")
    else:
        s = f"{int(round(n)):,}".replace(",", " ")
    return s.replace(" ", " ")


# ------------------------------------------------------------------ carton de chapitre
def chapter_card(c, t, t0, num, title, t1=None, sub=None):
    a = appear(t, t0, t1)
    if a <= 0: return
    y = 760
    if num:
        k = ease(prog(t, t0, 16 / FPS))
        text(c, num, 90, y - 40 + 20 * (1 - k), 150, "Bold", ACC, a, display=True)
    lines = wrap_lines(title, 92, 880, "Bold", True)
    for i, l in enumerate(lines):
        yy = y + 110 + i * 104
        mask_reveal(c, lambda l=l, yy=yy: text(c, l, 90, yy, 92, "Bold", TXT, a, display=True), t, t0 + 0.15 + i * 0.12, 0.7, 80, yy - 100, 960, 130)
    k2 = ease(prog(t, t0 + 0.3, 0.8))
    line(c, 90, y + 150 + len(lines) * 104 - 60, 90 + 300 * k2, y + 150 + len(lines) * 104 - 60, ACC, 0.9 * a, 4, cap="butt")
    if sub:
        slide_text(c, sub, 90, y + 160 + len(lines) * 104, 34, t, t0 + 0.6, t1, color=NEU, weight="Medium")


# ------------------------------------------------------------------ chiffre plein écran
def big_number(c, t, t0, value, label, y=760, size=200, dec=0, suffix="", prefix="", t1=None, color=TXT,
               date=None, sub=None, x=90, align="left", count_frames=18):
    a = appear(t, t0, t1)
    if a <= 0: return
    k = ease(prog(t, t0, count_frames / FPS))
    v = value * k
    s = prefix + (fmt(v, dec) if dec else fmt(v)) + suffix
    text_tab(c, s, x, y, size, "Bold", color, a, align=align)
    la = appear(t, t0 + 6 / FPS + count_frames / FPS * 0.6, t1)
    if label:
        for i, l in enumerate(label if isinstance(label, list) else [label]):
            text(c, l, x if align == "left" else x, y + 80 + i * 60, 50, "SemiBold", TXT, la, align=align)
    if date:
        chip(c, date, x if align == "left" else x - 100, y - size - 40, t, t0 + 0.3, size=24, color=TXT, outline=NEU)
    if sub:
        nl = len(label) if isinstance(label, list) else 1
        text(c, sub, x, y + 80 + nl * 60 + 10, 34, "Medium", NEU, la, align=align)


# ------------------------------------------------------------------ double comptage
def double_bar(c, t, t0, va, vb, la, lb, maxv, t1=None, y0=430, h=720, note_t=None, notes=None, mid_t=None,
               date=None, ca=TXT, cb=OCH, labels_top=None):
    a = appear(t, t0, t1)
    if a <= 0: return
    base = y0 + h
    line(c, 90, base, 940, base, NEU, 0.6 * a, 2)
    cols = [(220, va, la, ca, 0.0), (600, vb, lb, cb, 0.35)]
    for (x, v, l, col, dl) in cols:
        k = ease(prog(t, t0 + dl, 0.9))
        bh = h * v / maxv * k
        c.drawRect(skia.Rect.MakeXYWH(x, base - bh, 240, bh), paint(col, (0.9 if col == TXT else 0.85) * a))
        na = appear(t, t0 + dl + 0.3, t1)
        text_tab(c, fmt(v * k), x + 120, base - bh - 26, 74, "Bold", TXT, na, align="center")
        for i, ll in enumerate(l):
            text(c, ll, x + 120, base + 52 + i * 38, 30, "Medium", TXT if i == 0 else NEU, na, align="center")
    if mid_t is not None:
        # zone grisée « écart de méthode »
        ma = appear(t, mid_t, t1)
        top = base - h * vb / maxv; bot = base - h * va / maxv
        p = paint(NEU, 0.22 * ma)
        c.drawRect(skia.Rect.MakeLTRB(460, top, 600, bot), p)
        line(c, 460, top, 600, top, NEU, 0.6 * ma, 2, dash=[8, 8]); line(c, 460, bot, 600, bot, NEU, 0.6 * ma, 2, dash=[8, 8])
        text(c, "écart", 530, (top + bot) / 2 - 6, 26, "SemiBold", TXT, ma, align="center")
        text(c, "de méthode", 530, (top + bot) / 2 + 26, 26, "SemiBold", TXT, ma, align="center")
    if notes and note_t is not None:
        for i, (nt, s) in enumerate(zip(note_t, notes)):
            na = appear(t, nt, t1)
            x = 340 if i == 0 else 720
            text(c, s, x, base + 150, 26, "Medium", NEU, na, align="center")
    if date:
        chip(c, date, 90, 300, t, t0, size=24, outline=NEU)
    if labels_top:
        slide_text(c, labels_top, 90, 390, 40, t, t0, t1, weight="SemiBold")


# ------------------------------------------------------------------ courbes
def line_chart(c, t, t0, series, xs, xlabels, maxv, t1=None, box=(130, 420, 800, 640), step_t=None, date=None, title=None):
    a = appear(t, t0, t1)
    if a <= 0: return
    x0, y0, w, h = box
    for gv in (0, maxv / 2, maxv):
        yy = y0 + h - h * gv / maxv
        line(c, x0, yy, x0 + w, yy, NEU, 0.25 * a, 1.5)
        text(c, fmt(gv), x0 - 12, yy + 8, 22, "Medium", NEU, a * 0.8, align="right")
    for i, (xx, xl) in enumerate(zip(xs, xlabels)):
        X = x0 + w * xx
        text(c, xl, X, y0 + h + 44, 28, "SemiBold", TXT, a, align="center")
    if title:
        text(c, title, 90, y0 - 60, 40, "SemiBold", TXT, a)
    for si, s in enumerate(series):
        pts = [(x0 + w * xx, y0 + h - h * v / maxv) for (xx, v) in s["pts"]]
        st = t0 + 0.3 + si * 0.5 if step_t is None else step_t[si]
        k = ease(prog(t, st, 1.2))
        if k <= 0: continue
        n = len(pts)
        path = skia.Path(); path.moveTo(*pts[0])
        upto = k * (n - 1)
        for j in range(1, n):
            if j <= upto:
                path.lineTo(*pts[j])
            else:
                f = upto - (j - 1)
                if f > 0:
                    px = pts[j - 1][0] + (pts[j][0] - pts[j - 1][0]) * f
                    py = pts[j - 1][1] + (pts[j][1] - pts[j - 1][1]) * f
                    path.lineTo(px, py)
                break
        p = paint(s["color"], a, stroke=5)
        if s.get("dash"): p.setPathEffect(skia.DashPathEffect.Make([14, 10], 0))
        c.drawPath(path, p)
        for j, (X, Y) in enumerate(pts):
            if j <= upto + 1e-6:
                c.drawCircle(X, Y, 10, paint(s["color"], a))
                c.drawCircle(X, Y, 10, paint(BG, a, stroke=3))
                lab = s.get("labels", [None] * n)[j]
                if lab:
                    text(c, lab, X + s.get("lx", 0), Y + s.get("ly", -26), 30, "SemiBold", TXT, a, align="center")
        # légende
        ly = y0 - 10 + si * 0
        lx = 90 + si * 430
        c.drawRect(skia.Rect.MakeXYWH(lx, y0 + h + 90, 34, 6), paint(s["color"], a))
        text(c, s["name"], lx + 46, y0 + h + 100, 26, "Medium", TXT, a)
    if date:
        chip(c, date, 90, 300, t, t0, size=24, outline=NEU)


# ------------------------------------------------------------------ barres verticales en série
def bar_series(c, t, t0, items, maxv, t1=None, box=(150, 470, 780, 640), steps=None, color=TXT, hl=None):
    a = appear(t, t0, t1)
    if a <= 0: return
    x0, y0, w, h = box
    n = len(items); bw = w / n * 0.56; gap = w / n
    line(c, x0 - 20, y0 + h, x0 + w, y0 + h, NEU, 0.6 * a, 2)
    for i, (lab, v, vlab) in enumerate(items):
        st = t0 + 0.2 + i * 0.35 if steps is None else steps[i]
        k = ease(prog(t, st, 0.8))
        if k <= 0: continue
        X = x0 + i * gap + (gap - bw) / 2
        bh = h * v / maxv * k
        col = ACC if (hl is not None and i == hl) else color
        c.drawRect(skia.Rect.MakeXYWH(X, y0 + h - bh, bw, bh), paint(col, 0.85 * a))
        ba = appear(t, st + 0.2, t1)
        text(c, vlab, X + bw / 2, y0 + h - bh - 22, 56, "Bold", TXT, ba, align="center", display=True)
        text(c, lab, X + bw / 2, y0 + h + 48, 30, "SemiBold", NEU, ba, align="center")


# ------------------------------------------------------------------ liste qui s'empile
def stack_list(c, t, items, x=90, y=520, gap=92, size=50, t1=None, color=TXT, bullet=ACC, weight="SemiBold", maxw=840):
    for i, (s, ts) in enumerate(items):
        a = appear(t, ts, t1)
        if a <= 0: continue
        k = ease(prog(t, ts, IN))
        yy = y + i * gap + 20 * (1 - k)
        c.drawRect(skia.Rect.MakeXYWH(x, yy - size * 0.62, 6, size * 0.8), paint(bullet, a))
        text(c, s, x + 30, yy, size, weight, color, a)


# ------------------------------------------------------------------ timeline verticale
def timeline_v(c, t, items, x=150, y0=420, gap=170, t1=None, active=None):
    """items : (date, texte, t_apparition). Ligne 2 px à gauche, jalons ronds ; la date arrive en premier."""
    if not items: return
    first = items[0][2]
    a0 = appear(t, first, t1)
    last_y = y0 + (len(items) - 1) * gap
    k = ease(prog(t, first, 0.6 + 0.2 * len(items)))
    line(c, x, y0 - 40, x, y0 - 40 + (last_y - y0 + 80) * k, NEU, 0.7 * a0, 2)
    for i, (d, s, ts) in enumerate(items):
        a = appear(t, ts, t1)
        if a <= 0: continue
        y = y0 + i * gap
        on = active is not None and active(t) == i
        c.drawCircle(x, y, 13, paint(ACC if on else TXT, a))
        c.drawCircle(x, y, 13, paint(BG, a, stroke=3))
        kd = ease(prog(t, ts, 8 / FPS))
        text(c, d, x + 44, y + 12 - 20 * (1 - kd), 44, "Bold", ACC if on else TXT, a, display=True)
        kt = ease(prog(t, ts + 8 / FPS, IN))
        if kt > 0:
            for j, l in enumerate(wrap_lines(s, 32, 700)):
                text(c, l, x + 44 + 20 * (1 - kt), y + 58 + j * 40, 32, "Medium", NEU if not on else TXT, a * kt)


# ------------------------------------------------------------------ carte de France
def france_map(c, t, a=1.0, fit=None, hl=None, hl_alpha=None, deps=False, dep_hl=None, stroke_a=0.5, fill="#1A1E28"):
    """hl : dict nom_region -> (couleur, opacité)."""
    if a <= 0: return
    G = geo(); fit = fit or G.fit_france()
    if deps:
        for code, p in G.dep_paths(fit).items():
            if dep_hl and code in dep_hl:
                col, al = dep_hl[code]
                c.drawPath(p, paint(col, al * a))
            c.drawPath(p, paint(TXT, 0.2 * a, stroke=1.2))
    for name, p in G.region_paths(fit).items():
        if not deps:
            c.drawPath(p, paint(fill, a))
        if hl and name in hl:
            col, al = hl[name]
            if al > 0: c.drawPath(p, paint(col, al * a))
        c.drawPath(p, paint(TXT, stroke_a * a, stroke=1.6))


def city_dot(c, x, y, a, label=None, side="right", size=14, color=TXT, pulse_t=None, lsize=30, sub=None):
    if a <= 0: return
    if pulse_t is not None:
        ph = (pulse_t % 1.6) / 1.6
        c.drawCircle(x, y, size * (1 + 2.2 * ph), paint(color, 0.3 * (1 - ph) * a, stroke=2))
    c.drawCircle(x, y, size * 1.6, paint(color, 0.3 * a))
    c.drawCircle(x, y, size / 2, paint(color, a))
    if label:
        if side == "right":
            text(c, label, x + 24, y + 10, lsize, "SemiBold", TXT, a, shadow=True)
            if sub: text(c, sub, x + 24, y + 10 + lsize * 1.15, lsize * 0.8, "Medium", NEU, a, shadow=True)
        else:
            text(c, label, x - 24, y + 10, lsize, "SemiBold", TXT, a, align="right", shadow=True)
            if sub: text(c, sub, x - 24, y + 10 + lsize * 1.15, lsize * 0.8, "Medium", NEU, a, align="right", shadow=True)


# ------------------------------------------------------------------ icônes infrastructures
def icon_refinery(c, x, y, s, col, a):
    p = paint(col, a, stroke=4)
    c.drawRect(skia.Rect.MakeXYWH(x - s * 0.45, y - s * 0.1, s * 0.9, s * 0.5), p)
    for k in (-0.25, 0.05, 0.3):
        c.drawRect(skia.Rect.MakeXYWH(x + k * s - s * 0.06, y - s * 0.55, s * 0.12, s * 0.45), p)
    c.drawCircle(x - s * 0.22, y + s * 0.15, s * 0.1, p)


def icon_port(c, x, y, s, col, a):
    p = paint(col, a, stroke=4)
    c.drawLine(x - s * 0.45, y + s * 0.35, x + s * 0.45, y + s * 0.35, p)
    path = skia.Path(); path.moveTo(x - s * 0.4, y); path.lineTo(x + s * 0.4, y); path.lineTo(x + s * 0.28, y + s * 0.25); path.lineTo(x - s * 0.3, y + s * 0.25); path.close()
    c.drawPath(path, p)
    for k in range(3):
        c.drawRect(skia.Rect.MakeXYWH(x - s * 0.3 + k * s * 0.2, y - s * 0.22, s * 0.16, s * 0.2), p)
    c.drawLine(x + s * 0.35, y, x + s * 0.35, y - s * 0.5, p); c.drawLine(x + s * 0.35, y - s * 0.5, x + s * 0.05, y - s * 0.4, p)


def icon_rail(c, x, y, s, col, a):
    p = paint(col, a, stroke=4)
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x - s * 0.3, y - s * 0.45, s * 0.6, s * 0.7), 12, 12), p)
    c.drawRect(skia.Rect.MakeXYWH(x - s * 0.2, y - s * 0.35, s * 0.4, s * 0.22), p)
    c.drawCircle(x - s * 0.15, y + s * 0.12, s * 0.05, p); c.drawCircle(x + s * 0.15, y + s * 0.12, s * 0.05, p)
    c.drawLine(x - s * 0.25, y + s * 0.4, x - s * 0.35, y + s * 0.5, p); c.drawLine(x + s * 0.25, y + s * 0.4, x + s * 0.35, y + s * 0.5, p)


def icon_school(c, x, y, s, col, a):
    p = paint(col, a, stroke=4)
    c.drawRect(skia.Rect.MakeXYWH(x - s * 0.42, y - s * 0.1, s * 0.84, s * 0.5), p)
    path = skia.Path(); path.moveTo(x - s * 0.5, y - s * 0.1); path.lineTo(x, y - s * 0.45); path.lineTo(x + s * 0.5, y - s * 0.1)
    c.drawPath(path, p)
    c.drawRect(skia.Rect.MakeXYWH(x - s * 0.1, y + s * 0.1, s * 0.2, s * 0.3), p)


def strike(c, x, y, s, a, k):
    if k <= 0: return
    line(c, x - s * 0.55, y + s * 0.55, x - s * 0.55 + s * 1.1 * k, y + s * 0.55 - s * 1.1 * k, TXT, a, 5)


# ------------------------------------------------------------------ carte de Paris (schéma)
SEINE = [(2.224, 48.853), (2.250, 48.846), (2.268, 48.840), (2.280, 48.846), (2.292, 48.856), (2.300, 48.862),
         (2.312, 48.864), (2.326, 48.861), (2.338, 48.857), (2.350, 48.853), (2.362, 48.849), (2.372, 48.842),
         (2.383, 48.834), (2.396, 48.826), (2.412, 48.820)]
CANAL = [(2.369, 48.853), (2.367, 48.862), (2.366, 48.870), (2.370, 48.879), (2.375, 48.888)]


def paris_map(c, t, a=1.0, cx=540, cy=760, scale=9000.0, markers=None):
    G = geo()
    k = G.k
    ox = cx - 2.3488 * k * scale; oy = cy + 48.8566 * scale
    fit = (ox, oy, scale)
    paths = G.dep_paths(fit)
    for code in ("92", "93", "94"):
        c.drawPath(paths[code], paint(TXT, 0.10 * a, stroke=2))
    c.drawPath(paths["75"], paint("#1A1E28", a))
    c.drawPath(paths["75"], paint(TXT, 0.55 * a, stroke=3))
    pth = skia.Path()
    for i, (lon, lat) in enumerate(SEINE):
        X, Y = G.pt(lon, lat, fit); (pth.moveTo if i == 0 else pth.lineTo)(X, Y)
    c.drawPath(pth, paint("#3B4F7A", 0.9 * a, stroke=16))
    pth = skia.Path()
    for i, (lon, lat) in enumerate(CANAL):
        X, Y = G.pt(lon, lat, fit); (pth.moveTo if i == 0 else pth.lineTo)(X, Y)
    c.drawPath(pth, paint("#3B4F7A", 0.6 * a, stroke=5))
    text(c, "Seine", *G.pt(2.27, 48.835, fit), 24, "Medium", "#7D90BD", 0.8 * a)
    out = {}
    for (name, lon, lat) in (markers or []):
        out[name] = G.pt(lon, lat, fit)
    return out


BASTILLE = (2.3692, 48.8532)
REPUBLIQUE = (2.3636, 48.8674)
