# -*- coding: utf-8 -*-
"""Illustrations au trait (plans non factuels), toujours accompagnées du bandeau ILLUSTRATION / SCHÉMA.
Aucune personne, aucun uniforme, aucun logo, aucun texte parasite : uniquement des décors.
"""
import math
import numpy as np
import skia
from gfx import *

INK = TXT


def grad_rect(c, x, y, w, h, stops, vertical=True):
    pts = [skia.Point(x, y), skia.Point(x, y + h)] if vertical else [skia.Point(x, y), skia.Point(x + w, y)]
    cols = [rgb(s[1], s[2]) for s in stops]; pos = [s[0] for s in stops]
    sh = skia.GradientShader.MakeLinear(pts, cols, pos)
    p = skia.Paint(AntiAlias=True); p.setShader(sh)
    c.drawRect(skia.Rect.MakeXYWH(x, y, w, h), p)


def glow(c, x, y, r, color, a):
    sh = skia.GradientShader.MakeRadial(skia.Point(x, y), r, [rgb(color, a), rgb(color, 0)])
    p = skia.Paint(AntiAlias=True); p.setShader(sh)
    c.drawCircle(x, y, r, p)


def poly(c, pts, color, a=1.0, stroke=None, close=True):
    p = skia.Path(); p.moveTo(*pts[0])
    for q in pts[1:]: p.lineTo(*q)
    if close: p.close()
    c.drawPath(p, paint(color, a, stroke))


# ------------------------------------------------------------------ grille de lycée à l'aube
def school_gate(c, t, bins=True, barriers=False, dawn=1.0, night=False):
    sky_top = "#0B1020" if not night else "#07090F"
    grad_rect(c, 0, 0, W, 1300, [(0, sky_top, 1), (0.6, "#18203A", 1), (1.0, "#3A3446" if dawn else "#151A28", 1)])
    glow(c, 760, 980, 700, "#C8A15A", 0.10 * dawn)
    # bâtiment du lycée
    c.drawRect(skia.Rect.MakeXYWH(60, 560, 960, 640), paint("#14171F"))
    line(c, 60, 560, 1020, 560, INK, 0.35, 2)
    for r in range(3):
        for k in range(8):
            x = 100 + k * 115; y = 610 + r * 150
            lit = (r * 8 + k) in (5, 11, 18)
            c.drawRect(skia.Rect.MakeXYWH(x, y, 70, 100), paint("#C8A15A" if lit else "#0F1218", 0.22 if lit else 1))
            c.drawRect(skia.Rect.MakeXYWH(x, y, 70, 100), paint(INK, 0.22, stroke=1.5))
            line(c, x + 35, y, x + 35, y + 100, INK, 0.12, 1)
    # mur d'enceinte + piliers
    c.drawRect(skia.Rect.MakeXYWH(0, 1150, W, 220), paint("#1A1D25"))
    for x in (120, 920):
        c.drawRect(skia.Rect.MakeXYWH(x, 860, 60, 510), paint("#22262F"))
        c.drawRect(skia.Rect.MakeXYWH(x, 860, 60, 510), paint(INK, 0.45, stroke=2))
        c.drawRect(skia.Rect.MakeXYWH(x - 8, 845, 76, 22), paint(INK, 0.5, stroke=2))
    # grille (barreaux à pointes)
    for i in range(30):
        x = 195 + i * 24.5
        line(c, x, 930, x, 1370, INK, 0.55, 3)
        poly(c, [(x - 6, 935), (x, 912), (x + 6, 935)], INK, 0.55)
    for y in (960, 1180, 1340):
        line(c, 180, y, 920, y, INK, 0.5, 4)
    # sol, trottoir humide
    grad_rect(c, 0, 1370, W, 550, [(0, "#16181E", 1), (1, "#0B0C0F", 1)])
    line(c, 0, 1372, W, 1372, INK, 0.4, 2)
    for i in range(9):
        y = 1420 + i * i * 7
        line(c, 0, y, W, y, INK, 0.05, 1.2)
    # reflets
    glow(c, 760, 1500, 260, "#C8A15A", 0.07 * dawn)
    # lampadaire
    line(c, 1000, 600, 1000, 1372, INK, 0.5, 5)
    line(c, 1000, 600, 940, 620, INK, 0.5, 4)
    glow(c, 935, 632, 160 + 6 * math.sin(t * 3), "#E9D9B0", 0.25)
    c.drawCircle(935, 630, 9, paint("#F4E7C6", 0.9))
    if bins:
        draw_bins(c, t)
    if barriers:
        draw_barriers(c, 1395, 0.9)


def draw_bins(c, t):
    specs = [(250, 1210, -4, "#2A3140"), (420, 1235, 3, "#2B2F37"), (600, 1200, -2, "#262C36"), (760, 1240, 6, "#2E333C")]
    for (x, y, ang, col) in specs:
        c.save(); c.translate(x, y); c.rotate(ang)
        w, h = 130, 190
        poly(c, [(-w / 2, 0), (w / 2, 0), (w / 2 - 12, h), (-w / 2 + 12, h)], col, 1)
        poly(c, [(-w / 2, 0), (w / 2, 0), (w / 2 - 12, h), (-w / 2 + 12, h)], INK, 0.55, stroke=2.5)
        rrect(c, -w / 2 - 8, -22, w + 16, 24, 5, col, 1)
        rrect(c, -w / 2 - 8, -22, w + 16, 24, 5, INK, 0.6, stroke=2.5)
        for k in (-1, 1):
            c.drawCircle(k * (w / 2 - 22), h + 8, 13, paint("#0E0F11"))
            c.drawCircle(k * (w / 2 - 22), h + 8, 13, paint(INK, 0.5, stroke=2))
        line(c, -w / 2 + 20, 40, w / 2 - 20, 40, INK, 0.18, 2)
        c.restore()


def draw_barriers(c, y, a=1.0):
    for k in range(3):
        x0 = 120 + k * 290
        line(c, x0, y - 170, x0 + 270, y - 170, INK, 0.6 * a, 4)
        line(c, x0, y - 10, x0 + 270, y - 10, INK, 0.6 * a, 4)
        for i in range(13):
            xx = x0 + 10 + i * 20
            line(c, xx, y - 170, xx, y - 10, INK, 0.45 * a, 2.2)
        for xx in (x0 + 15, x0 + 255):
            line(c, xx, y - 10, xx - 18, y + 25, INK, 0.6 * a, 4)
            line(c, xx, y - 10, xx + 18, y + 25, INK, 0.6 * a, 4)


# ------------------------------------------------------------------ façade institutionnelle générique
def facade(c, t, label=None):
    grad_rect(c, 0, 0, W, H, [(0, "#0C0F18", 1), (0.55, "#141A28", 1), (1, "#0B0C0F", 1)])
    glow(c, 540, 700, 800, "#2A3550", 0.35)
    # corps de bâtiment
    x0, x1, top, base = 70, 1010, 520, 1330
    c.drawRect(skia.Rect.MakeLTRB(x0, top, x1, base), paint("#171B24"))
    c.drawRect(skia.Rect.MakeLTRB(x0, top, x1, base), paint(INK, 0.4, stroke=2))
    # corniche et toit mansardé
    poly(c, [(x0 - 20, top), (x1 + 20, top), (x1 - 30, top - 150), (x0 + 30, top - 150)], "#12151D", 1)
    poly(c, [(x0 - 20, top), (x1 + 20, top), (x1 - 30, top - 150), (x0 + 30, top - 150)], INK, 0.45, stroke=2)
    for k in range(5):
        x = 170 + k * 185
        rrect(c, x, top - 115, 70, 85, 30, "#0F1218", 1); rrect(c, x, top - 115, 70, 85, 30, INK, 0.35, stroke=1.5)
    line(c, x0 - 25, top + 10, x1 + 25, top + 10, INK, 0.5, 4)
    # fenêtres hautes
    for r in range(2):
        for k in range(7):
            if k == 3: continue
            x = 110 + k * 132; y = 600 + r * 300
            c.drawRect(skia.Rect.MakeXYWH(x, y, 72, 200), paint("#0D1016"))
            c.drawRect(skia.Rect.MakeXYWH(x, y, 72, 200), paint(INK, 0.35, stroke=1.6))
            line(c, x + 36, y, x + 36, y + 200, INK, 0.15, 1); line(c, x, y + 70, x + 72, y + 70, INK, 0.15, 1)
            line(c, x - 10, y - 14, x + 82, y - 14, INK, 0.35, 2.5)
            if (r, k) in ((0, 1), (1, 5)):
                c.drawRect(skia.Rect.MakeXYWH(x + 4, y + 4, 64, 192), paint("#C8A15A", 0.12))
    # portail central avec colonnes
    poly(c, [(420, 720), (660, 720), (540, 640)], INK, 0.45, stroke=2.5)
    for x in (430, 470, 610, 650):
        line(c, x, 735, x, 1330, INK, 0.5, 6)
    rrect(c, 495, 860, 90, 470, 45, "#0B0D12", 1)
    rrect(c, 495, 860, 90, 470, 45, INK, 0.4, stroke=2)
    # mât sans drapeau
    line(c, 540, 640, 540, 470, INK, 0.5, 3)
    # sol / cour
    grad_rect(c, 0, 1330, W, 590, [(0, "#121419", 1), (1, "#0A0B0D", 1)])
    for i in range(1, 12):
        x = 540 + (i - 6) * 140
        line(c, 540 + (i - 6) * 30, 1335, x * 1.0 + (x - 540) * 1.8, 1920, INK, 0.05, 1.5)
    line(c, 0, 1332, W, 1332, INK, 0.4, 2)


# ------------------------------------------------------------------ salle de classe vide
def classroom(c, t):
    grad_rect(c, 0, 0, W, H, [(0, "#121620", 1), (1, "#0B0C0F", 1)])
    vx, vy = 540, 760  # point de fuite
    # murs
    poly(c, [(0, 0), (260, 470), (260, 1050), (0, 1920)], "#151A24", 1)
    poly(c, [(W, 0), (820, 470), (820, 1050), (W, 1920)], "#121620", 1)
    c.drawRect(skia.Rect.MakeLTRB(260, 470, 820, 1050), paint("#181D28"))
    for (a, b) in (((0, 0), (260, 470)), ((W, 0), (820, 470)), ((0, 1920), (260, 1050)), ((W, 1920), (820, 1050))):
        line(c, *a, *b, INK, 0.3, 2)
    c.drawRect(skia.Rect.MakeLTRB(260, 470, 820, 1050), paint(INK, 0.3, stroke=2))
    # tableau effacé
    rrect(c, 330, 560, 420, 220, 4, "#1F2B27", 1); rrect(c, 330, 560, 420, 220, 4, INK, 0.4, stroke=2)
    for k in range(3):
        line(c, 360 + k * 90, 610 + k * 30, 520 + k * 70, 600 + k * 40, INK, 0.05, 18)
    # fenêtres à gauche + rayons
    for k in range(3):
        y0 = 380 + k * 330; y1 = y0 + 230
        xa = 40 + k * 60
        poly(c, [(xa, y0 - 40 + k * 30), (xa + 120 - k * 20, y0 + 40 + k * 10), (xa + 120 - k * 20, y1 - 20), (xa, y1 + 40)], "#2B3550", 0.6)
        poly(c, [(xa, y0 - 40 + k * 30), (xa + 120 - k * 20, y0 + 40 + k * 10), (xa + 120 - k * 20, y1 - 20), (xa, y1 + 40)], INK, 0.35, stroke=1.5)
        poly(c, [(xa + 120, y0 + 40), (xa + 120, y1 - 20), (700, 1500 + k * 100), (520, 1300 + k * 80)], "#C8D4F0", 0.035)
    # ventilateur sur le bureau du professeur
    rrect(c, 560, 900, 220, 70, 3, "#1B2029", 1); rrect(c, 560, 900, 220, 70, 3, INK, 0.4, stroke=2)
    c.drawCircle(735, 868, 26, paint(INK, 0.45, stroke=2)); line(c, 735, 894, 735, 900, INK, 0.45, 3)
    # rangées de tables en perspective
    for r in range(5):
        z = 1 + r * 0.55
        y = 1040 + r * r * 32 + r * 120
        for k in (-1, 1):
            cx = vx + k * (150 * z)
            w = 230 * z * 0.75; h = 40 * z
            poly(c, [(cx - w / 2, y), (cx + w / 2, y), (cx + w / 2 + 10 * z * k, y + h), (cx - w / 2 + 10 * z * k, y + h)], "#2A2620", 1)
            poly(c, [(cx - w / 2, y), (cx + w / 2, y), (cx + w / 2 + 10 * z * k, y + h), (cx - w / 2 + 10 * z * k, y + h)], INK, 0.45, stroke=2)
            for s in (-0.42, 0.42):
                line(c, cx + s * w, y + h, cx + s * w, y + h + 70 * z, INK, 0.35, 2.5)
            # chaise
            rrect(c, cx - 40 * z, y + h + 40 * z, 80 * z, 18 * z, 3, INK, 0.25, stroke=1.6)
    # poussière dans la lumière
    rng = np.random.default_rng(3)
    pts = rng.uniform([150, 500], [700, 1500], (60, 2))
    for i, (x, y) in enumerate(pts):
        yy = y + 20 * math.sin(t * 0.4 + i)
        c.drawCircle(x + 8 * math.sin(t * 0.3 + i * 2), yy, 1.6, paint("#F2F0EB", 0.18 + 0.1 * math.sin(t + i)))


# ------------------------------------------------------------------ amphithéâtre
def amphi(c, t):
    grad_rect(c, 0, 0, W, H, [(0, "#10131B", 1), (1, "#0A0B0E", 1)])
    glow(c, 540, 1350, 600, "#2A3550", 0.4)
    for r in range(11):
        rad = 300 + r * 95
        rect = skia.Rect.MakeXYWH(540 - rad * 1.25, 1450 - rad * 0.55 - r * 70, rad * 2.5, rad * 1.1)
        p = paint(INK, 0.32 - r * 0.018, stroke=3)
        c.drawArc(rect, 200, 140, False, p)
        p2 = paint(INK, 0.14, stroke=14, cap="butt")
        p2.setPathEffect(skia.DashPathEffect.Make([8, 22], r * 5))
        c.drawArc(skia.Rect.MakeXYWH(rect.x() + 14, rect.y() + 12, rect.width() - 28, rect.height() - 12), 205, 130, False, p2)
    rrect(c, 360, 1330, 360, 80, 3, "#1B2029", 1); rrect(c, 360, 1330, 360, 80, 3, INK, 0.4, stroke=2)
    c.drawRect(skia.Rect.MakeXYWH(300, 1100, 480, 170), paint(INK, 0.25, stroke=2))


# ------------------------------------------------------------------ station-service (totem vierge)
def fuel_station(c, t):
    grad_rect(c, 0, 0, W, H, [(0, "#0E1220", 1), (0.6, "#1A1E2C", 1), (1, "#0A0B0D", 1)])
    # auvent
    poly(c, [(80, 520), (1000, 520), (1000, 600), (80, 600)], "#1E232E", 1)
    poly(c, [(80, 520), (1000, 520), (1000, 600), (80, 600)], INK, 0.45, stroke=2)
    for k in range(6):
        x = 150 + k * 150
        glow(c, x, 610, 120, "#E9E2CC", 0.18)
        c.drawRect(skia.Rect.MakeXYWH(x - 30, 598, 60, 6), paint("#F4EEDC", 0.8))
    for x in (230, 850):
        c.drawRect(skia.Rect.MakeXYWH(x - 14, 600, 28, 760), paint("#191D26"))
        c.drawRect(skia.Rect.MakeXYWH(x - 14, 600, 28, 760), paint(INK, 0.35, stroke=1.5))
    # pompes
    for x in (380, 640):
        rrect(c, x, 1060, 110, 300, 8, "#1C212B", 1); rrect(c, x, 1060, 110, 300, 8, INK, 0.45, stroke=2)
        c.drawRect(skia.Rect.MakeXYWH(x + 20, 1090, 70, 50), paint("#2C3A55", 0.8))
        line(c, x + 110, 1150, x + 140, 1250, INK, 0.4, 3)
    # totem de prix (affichage vierge)
    c.drawRect(skia.Rect.MakeXYWH(905, 760, 120, 620), paint("#171B23"))
    c.drawRect(skia.Rect.MakeXYWH(905, 760, 120, 620), paint(INK, 0.5, stroke=2))
    for k in range(4):
        c.drawRect(skia.Rect.MakeXYWH(920, 800 + k * 110, 90, 80), paint("#0A0C10"))
        c.drawRect(skia.Rect.MakeXYWH(920, 800 + k * 110, 90, 80), paint(INK, 0.3, stroke=1.5))
    # sol mouillé et reflets
    grad_rect(c, 0, 1360, W, 560, [(0, "#14161B", 1), (1, "#09090B", 1)])
    line(c, 0, 1362, W, 1362, INK, 0.35, 2)
    for k in range(6):
        x = 150 + k * 150
        c.drawRect(skia.Rect.MakeXYWH(x - 25, 1380, 50, 200 + 30 * math.sin(t + k)), paint("#E9E2CC", 0.04))


# ------------------------------------------------------------------ hémicycle (schéma)
def hemicycle(c, t, cx=540, cy=980, a=1.0, prog_k=1.0):
    n_rows = 12
    seats = 0
    for r in range(n_rows):
        rad = 170 + r * 30
        n = int(math.pi * rad / 24)
        for i in range(n):
            ang = math.pi + math.pi * (i + 0.5) / n
            k = (seats % 577) / 577
            seats += 1
            if k > prog_k: continue
            x = cx + rad * math.cos(ang); y = cy + rad * math.sin(ang)
            c.drawCircle(x, y, 7, paint(NEU, 0.55 * a))
    rrect(c, cx - 70, cy - 30, 140, 50, 6, INK, 0.5 * a, stroke=2)


# ------------------------------------------------------------------ quai de gare
def platform(c, t):
    grad_rect(c, 0, 0, W, H, [(0, "#0D1019", 1), (1, "#09090B", 1)])
    vx, vy = 620, 820
    for k in range(-4, 6):
        line(c, vx, vy, vx + k * 400, 1920, INK, 0.08, 1.5)
    poly(c, [(0, 1920), (0, 1050), (vx - 40, vy), (vx - 10, vy), (380, 1920)], "#1A1D24", 1)
    line(c, vx - 10, vy, 380, 1920, "#C8A15A", 0.55, 6)
    for (o, w) in ((60, 4), (260, 5)):
        line(c, vx + o * 0.05, vy, vx + o * 3.2, 1920, INK, 0.5, w)
        line(c, vx + o * 0.05 + 15, vy, vx + o * 3.2 + 260, 1920, INK, 0.5, w)
    for k in range(9):
        y = vy + (k ** 1.8) * 22
        line(c, vx + 5 + (y - vy) * 0.05, y, vx + 20 + (y - vy) * 1.0, y, INK, 0.2, 3)
    # marquise
    for k in range(8):
        x = 40 + k * 70; y = 360 + k * 50
        line(c, x, 0, x + 40, y, INK, 0.25, 2)
        glow(c, x + 40, y + 10, 70, "#E9E2CC", 0.12)


# ------------------------------------------------------------------ rue vide
def street(c, t):
    grad_rect(c, 0, 0, W, H, [(0, "#0C0F17", 1), (0.5, "#151926", 1), (1, "#09090B", 1)])
    vx, vy = 540, 900
    for side in (-1, 1):
        for k in range(7):
            x0 = vx + side * (60 + k * k * 22); y0 = vy - 380 - k * 120
            c.drawRect(skia.Rect.MakeLTRB(min(x0, x0 + side * 160), y0, max(x0, x0 + side * 160), vy + 40 + k * 60),
                       paint("#161A23" if k % 2 else "#13161E"))
            for w in range(4):
                c.drawRect(skia.Rect.MakeXYWH(min(x0, x0 + side * 160) + 30, y0 + 40 + w * 90, 100, 50), paint(INK, 0.12, stroke=1.2))
    poly(c, [(vx - 30, vy), (vx + 30, vy), (W + 400, H), (-400, H)], "#121419", 1)
    line(c, vx, vy, vx, H, INK, 0.25, 4)
    p = paint(INK, 0.35, stroke=6, cap="butt"); p.setPathEffect(skia.DashPathEffect.Make([60, 50], -t * 40))
    c.drawLine(vx, vy + 10, vx, H, p)
    glow(c, vx, vy - 40, 300, "#3A4560", 0.4)


# ------------------------------------------------------------------ cortège vu du dessus (schéma de flux)
class Cortege:
    def __init__(self, n=2600, seed=9):
        rng = np.random.default_rng(seed)
        self.u = rng.uniform(0, 1, n)          # position le long du boulevard
        self.v = rng.normal(0, 0.28, n).clip(-0.48, 0.48)  # position transversale
        self.sp = rng.uniform(0.006, 0.011, n)
        self.size = rng.uniform(2.0, 3.6, n)

    def draw(self, c, t, a=1.0):
        # boulevard en courbe douce
        def P(u):
            x = -100 + u * 1300; y = 1550 - u * 1200 + 140 * math.sin(u * 3.0)
            return x, y
        # bords
        for side in (-1, 1):
            pth = skia.Path()
            for i in range(60):
                u = i / 59; x, y = P(u)
                dx, dy = 1300, -1200 + 140 * 3 * math.cos(u * 3)
                L = math.hypot(dx, dy); nx, ny = -dy / L, dx / L
                X, Y = x + nx * 150 * side, y + ny * 150 * side
                (pth.moveTo if i == 0 else pth.lineTo)(X, Y)
            c.drawPath(pth, paint(INK, 0.25 * a, stroke=2))
        # immeubles schématiques
        rng = np.random.default_rng(4)
        for i in range(40):
            u = (i + 0.5) / 40; x, y = P(u)
            for side in (-1, 1):
                dx, dy = 1300, -1200 + 420 * math.cos(u * 3); L = math.hypot(dx, dy)
                nx, ny = -dy / L, dx / L
                X, Y = x + nx * 240 * side, y + ny * 240 * side
                s = rng.uniform(40, 80)
                c.drawRect(skia.Rect.MakeXYWH(X - s / 2, Y - s / 2, s, s), paint(INK, 0.08 * a, stroke=1.2))
        uu = (self.u + self.sp * t) % 1.0
        pts = []
        for u, v in zip(uu, self.v):
            x, y = P(u)
            dx, dy = 1300, -1200 + 420 * math.cos(u * 3); L = math.hypot(dx, dy)
            nx, ny = -dy / L, dx / L
            pts.append(skia.Point(x + nx * v * 280, y + ny * v * 280))
        p = paint(TXT, 0.55 * a, stroke=4.2); p.setStrokeCap(skia.Paint.kRound_Cap)
        c.drawPoints(skia.Canvas.kPoints_PointMode, pts, p)
