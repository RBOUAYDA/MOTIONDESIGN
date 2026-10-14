# -*- coding: utf-8 -*-
"""Moteur graphique (Skia) — grammaire visuelle du dossier (section G).

Espace de conception : 1080 x 1920 (zones sûres TikTok), rendu à l'échelle S (2 = 4K).
Couleurs : fond #0E0F11, texte #F2F0EB, accent #4C6EF5 (80 %), ocre #C8A15A, neutre #8A8F98.
Courbes : entrées 12-16 images ease-out cubic-bezier(0.2, 0.8, 0.2, 1), sorties 8 images.
"""
import math, os, json
import numpy as np
import skia

FPS = 30
W, H = 1080, 1920
FONT_DIR = "/usr/share/fonts/opentype/inter"
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def rgb(h, a=1.0):
    h = h.lstrip("#")
    return skia.Color4f(int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255, a)


BG = "#0E0F11"; TXT = "#F2F0EB"; ACC = "#4C6EF5"; OCH = "#C8A15A"; NEU = "#8A8F98"; DIM = "#3A3D44"
GOOD = "#7FA88B"  # vert sourd (CONFIRMÉ)


# ------------------------------------------------------------------ polices
_TF = {}


def tf(weight="Medium", display=False):
    key = (weight, display)
    if key not in _TF:
        fam = "InterDisplay" if display else "Inter"
        _TF[key] = skia.Typeface.MakeFromFile(f"{FONT_DIR}/{fam}-{weight}.otf")
    return _TF[key]


_FONTS = {}


def font(size, weight="Medium", display=False):
    key = (round(size, 2), weight, display)
    if key not in _FONTS:
        f = skia.Font(tf(weight, display), size)
        f.setSubpixel(True); f.setEdging(skia.Font.Edging.kAntiAlias)
        f.setHinting(skia.FontHinting.kNone)
        _FONTS[key] = f
    return _FONTS[key]


# ------------------------------------------------------------------ courbes
def _bez(p1, p2, x):
    # cubic-bezier(0,0,p1x,p1y,p2x,p2y,1,1) : résout t pour x puis renvoie y
    (x1, y1), (x2, y2) = p1, p2
    t = x
    for _ in range(8):
        cx = 3 * x1 * t * (1 - t) ** 2 + 3 * x2 * t ** 2 * (1 - t) + t ** 3 - x
        dx = 3 * x1 * (1 - t) ** 2 + 6 * (x2 - x1) * t * (1 - t) + 3 * (1 - x2) * t ** 2
        if abs(dx) < 1e-6: break
        t -= cx / dx
        t = min(1, max(0, t))
    return 3 * y1 * t * (1 - t) ** 2 + 3 * y2 * t ** 2 * (1 - t) + t ** 3


def ease(x):
    """ease-out du dossier : cubic-bezier(0.2, 0.8, 0.2, 1)."""
    x = min(1.0, max(0.0, x))
    return _bez((0.2, 0.8), (0.2, 1.0), x)


def ease_io(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def prog(t, start, dur):
    """progression 0..1 de l'animation qui démarre à start (s) et dure dur (s)."""
    if dur <= 0: return 1.0 if t >= start else 0.0
    return min(1.0, max(0.0, (t - start) / dur))


IN = 14 / FPS    # entrée : 14 images
OUT = 8 / FPS    # sortie : 8 images


def appear(t, t0, t1=None, d_in=IN, d_out=OUT):
    """opacité 0..1 : entre à t0, sort à t1."""
    a = ease(prog(t, t0, d_in))
    if t1 is not None:
        a *= 1 - ease_io(prog(t, t1 - d_out, d_out))
    return a


# ------------------------------------------------------------------ dessin de base
def paint(color=TXT, a=1.0, stroke=None, cap="round", blur=None):
    p = skia.Paint(AntiAlias=True)
    c = rgb(color, a) if isinstance(color, str) else color
    p.setColor4f(c)
    if stroke is not None:
        p.setStyle(skia.Paint.kStroke_Style); p.setStrokeWidth(stroke)
        p.setStrokeCap({"round": skia.Paint.kRound_Cap, "butt": skia.Paint.kButt_Cap, "square": skia.Paint.kSquare_Cap}[cap])
        p.setStrokeJoin(skia.Paint.kRound_Join)
    if blur:
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    return p


def text_w(s, size, weight="Medium", display=False, track=0.0):
    f = font(size, weight, display)
    if track == 0:
        return f.measureText(s)
    return sum(f.measureText(ch) for ch in s) + track * size * (len(s) - 1)


def text(c, s, x, y, size, weight="Medium", color=TXT, a=1.0, align="left", display=False, track=0.0, shadow=False):
    """Texte (ligne de base y). track = interlettrage en em (ex. 0.08 pour les capitales)."""
    if a <= 0.003 or not s: return 0
    f = font(size, weight, display)
    w = text_w(s, size, weight, display, track)
    if align == "center": x -= w / 2
    elif align == "right": x -= w
    if shadow:
        sp = paint("#000000", 0.6 * a, blur=4)
        _draw_str(c, s, x, y + 2, f, sp, track, size)
    _draw_str(c, s, x, y, f, paint(color, a), track, size)
    return w


def _draw_str(c, s, x, y, f, p, track, size):
    if track == 0:
        c.drawString(s, x, y, f, p)
    else:
        for ch in s:
            c.drawString(ch, x, y, f, p)
            x += f.measureText(ch) + track * size


def text_tab(c, s, x, y, size, weight="SemiBold", color=TXT, a=1.0, align="left", display=True):
    """Chiffres tabulaires (cellule fixe) : aucun tremblement pendant les compteurs."""
    f = font(size, weight, display)
    dw = max(f.measureText(d) for d in "0123456789")
    widths = [dw if ch.isdigit() else f.measureText(ch) for ch in s]
    tw = sum(widths)
    if align == "center": x -= tw / 2
    elif align == "right": x -= tw
    p = paint(color, a)
    for ch, w in zip(s, widths):
        off = (w - f.measureText(ch)) / 2
        c.drawString(ch, x + off, y, f, p)
        x += w
    return tw


def wrap_lines(s, size, maxw, weight="Medium", display=False):
    words = s.split(" "); lines = []; cur = ""
    for w in words:
        trial = (cur + " " + w).strip()
        if cur and text_w(trial, size, weight, display) > maxw:
            lines.append(cur); cur = w
        else:
            cur = trial
    if cur: lines.append(cur)
    return lines


def para(c, s, x, y, size, maxw, weight="Medium", color=TXT, a=1.0, lh=1.25, align="left", display=False):
    lines = wrap_lines(s, size, maxw, weight, display)
    for i, l in enumerate(lines):
        text(c, l, x, y + i * size * lh, size, weight, color, a, align, display)
    return len(lines) * size * lh


def slide_text(c, s, x, y, size, t, t0, t1=None, dy=20, **kw):
    """Entrée : glissement de 20 px + fondu (14 images)."""
    a = appear(t, t0, t1)
    if a <= 0: return
    k = ease(prog(t, t0, IN))
    text(c, s, x, y + dy * (1 - k), size, a=a * kw.pop("a", 1.0), **kw)


def mask_reveal(c, draw, t, t0, d, x0, y0, w, h, direction="lr"):
    """Révélation par masque horizontal."""
    k = ease(prog(t, t0, d))
    if k <= 0: return
    c.save()
    if direction == "lr":
        c.clipRect(skia.Rect.MakeXYWH(x0, y0, w * k, h))
    else:
        c.clipRect(skia.Rect.MakeXYWH(x0, y0 + h * (1 - k), w, h * k))
    draw()
    c.restore()


def highlight(c, x, y_base, w, size, t, t0, color=ACC, a=0.35):
    """Surlignage : bande accent à 35 % qui se dessine de gauche à droite (10 images)."""
    k = ease(prog(t, t0, 10 / FPS))
    if k <= 0: return
    c.drawRect(skia.Rect.MakeXYWH(x - 6, y_base - size * 0.78, (w + 12) * k, size * 1.0), paint(color, a))


def rrect(c, x, y, w, h, r, color, a=1.0, stroke=None):
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), r, r), paint(color, a, stroke))


def line(c, x0, y0, x1, y1, color=TXT, a=1.0, w=2, dash=None, cap="round"):
    p = paint(color, a, stroke=w, cap=cap)
    if dash: p.setPathEffect(skia.DashPathEffect.Make(dash, 0))
    c.drawLine(x0, y0, x1, y1, p)


def chip(c, s, x, y, t=1.0, t0=-1, size=26, color=TXT, fill=None, a=1.0, outline=None, track=0.06, weight="SemiBold"):
    """Puce (date, étiquette)."""
    aa = appear(t, t0) * a if t0 >= 0 else a
    if aa <= 0: return 0
    w = text_w(s, size, weight, track=track) + size * 1.1
    h = size * 1.75
    if fill: rrect(c, x, y, w, h, h / 2, fill, aa)
    if outline: rrect(c, x, y, w, h, h / 2, outline, aa, stroke=2)
    text(c, s, x + size * 0.55, y + h * 0.66, size, weight, color, aa, track=track)
    return w


def source(c, s, t, t0, t1=None, y=1258):
    """Puce source : Inter 26 px, 70 % d'opacité, au-dessus de la zone sous-titres."""
    a = appear(t, t0 + 6 / FPS, t1)
    if a <= 0: return
    text(c, "SOURCE", 90, y, 20, "SemiBold", NEU, 0.85 * a, track=0.12)
    text(c, s, 90 + text_w("SOURCE", 20, "SemiBold", track=0.12) + 14, y, 24, "Medium", TXT, 0.7 * a)


def badge(c, s="ILLUSTRATION", t=1.0, a=1.0):
    """Bandeau permanent pour toute image non factuelle."""
    w = text_w(s, 20, "SemiBold", track=0.14) + 30
    rrect(c, 90, 168, w, 36, 4, "#000000", 0.45 * a)
    rrect(c, 90, 168, w, 36, 4, TXT, 0.35 * a, stroke=1.5)
    text(c, s, 105, 192, 20, "SemiBold", TXT, 0.9 * a, track=0.14)


def chapter_tag(c, s, a=1.0):
    text(c, s, 90, 236, 22, "SemiBold", NEU, 0.9 * a, track=0.12)


# ------------------------------------------------------------------ fond & texture
class Textures:
    def __init__(self, S):
        rng = np.random.default_rng(7)
        self.S = S
        # grain 35 mm (tuiles)
        self.grain = []
        for i in range(6):
            g = rng.normal(0, 1, (512, 512))
            g = (np.clip(g * 40 + 128, 0, 255)).astype(np.uint8)
            img = np.stack([g, g, g, np.full_like(g, 255)], -1)
            self.grain.append(skia.Image.fromarray(img))
        # papier sombre (fibres très légères) à la résolution de sortie / 2
        h, w = 960, 540
        base = rng.normal(0, 1, (h, w))
        from scipy.ndimage import gaussian_filter
        fib = gaussian_filter(rng.normal(0, 1, (h, w)), (0.6, 6)) * 3 + gaussian_filter(base, 1.2) * 1.5
        fib = gaussian_filter(fib, 0.5)
        v = np.clip(128 + fib * 9, 0, 255).astype(np.uint8)
        self.paper = skia.Image.fromarray(np.stack([v, v, v, np.full_like(v, 255)], -1))

        self._bg = {}; self._vig = {}
        # grain « signé » : blanc ou noir avec alpha variable, composé en SrcOver (rapide)
        self.grain2 = []
        for i in range(6):
            g = rng.normal(0, 1, (512, 512))
            al = np.clip(np.abs(g) * 70, 0, 255).astype(np.uint8)
            col = np.where(g > 0, 255, 0).astype(np.uint8)
            # prémultiplié
            pm = (col.astype(np.uint16) * al // 255).astype(np.uint8)
            img = np.stack([pm, pm, pm, al], -1)
            self.grain2.append(skia.Image.fromarray(img, colorType=skia.kRGBA_8888_ColorType, alphaType=skia.kPremul_AlphaType))

    def _raster(self, draw):
        Wp, Hp = int(W * self.S), int(H * self.S)
        info = skia.ImageInfo.Make(Wp, Hp, skia.kRGBA_8888_ColorType, skia.kPremul_AlphaType)
        surf = skia.Surface.MakeRaster(info)
        cc = surf.getCanvas(); cc.clear(skia.Color4f(0, 0, 0, 0)); cc.scale(self.S, self.S)
        draw(cc)
        return surf.makeImageSnapshot()

    def draw_bg(self, c, t, tone=BG, paper_a=0.05, glow=None):
        key = (tone, paper_a, glow)
        if key not in self._bg:
            def d(cc):
                cc.clear(rgb(tone))
                p = skia.Paint(); p.setAlphaf(paper_a); p.setBlendMode(skia.BlendMode.kOverlay)
                cc.drawImageRect(self.paper, skia.Rect.MakeXYWH(-20, -20, W + 40, H + 40), skia.SamplingOptions(skia.FilterMode.kLinear), p)
                g = glow or (540, 760, "#1C2233")
                sh = skia.GradientShader.MakeRadial(skia.Point(g[0], g[1]), 900, [rgb(g[2], 0.9), rgb(g[2], 0.0)])
                p2 = skia.Paint(); p2.setShader(sh)
                cc.drawRect(skia.Rect.MakeWH(W, H), p2)
            self._bg[key] = self._raster(d)
        p = skia.Paint(); p.setBlendMode(skia.BlendMode.kSrc)
        c.save(); c.resetMatrix(); c.drawImage(self._bg[key], 0, 0, skia.SamplingOptions(), p); c.restore()

    def _grain_big(self):
        if not hasattr(self, "_gb"):
            rng = np.random.default_rng(11)
            Wp, Hp = int(W * self.S) + 400, int(H * self.S) + 400
            self._gb = []
            for i in range(3):
                # grain 35 mm : grains de ~2 px (à l'échelle 4K), faible amplitude
                from scipy.ndimage import gaussian_filter, zoom
                g = rng.normal(0, 1, (Hp // 2 + 1, Wp // 2 + 1)).astype(np.float32)
                g = zoom(g, 2, order=1)[:Hp, :Wp]
                g = gaussian_filter(g, 0.6 * self.S / 2); g /= g.std() + 1e-6
                al = np.clip(np.abs(g) * 70 * self._gamt, 0, 255).astype(np.uint8)
                pm = np.where(g > 0, al, 0).astype(np.uint8)
                img = np.stack([pm, pm, pm, al], -1)
                self._gb.append(skia.Image.fromarray(img, colorType=skia.kRGBA_8888_ColorType, alphaType=skia.kPremul_AlphaType))
        return self._gb

    def draw_grain(self, c, frame, amount=0.09):
        self._gamt = min(1.0, amount * 1.6)
        imgs = self._grain_big()
        rng = np.random.default_rng(frame)
        ox, oy = rng.integers(0, 400, 2)
        c.save(); c.resetMatrix()
        c.drawImage(imgs[frame % 3], -float(ox), -float(oy))
        c.restore()

    def draw_vignette(self, c, a=0.55):
        if a not in self._vig:
            def d(cc):
                sh = skia.GradientShader.MakeRadial(skia.Point(W / 2, H * 0.45), H * 0.75,
                                                    [rgb("#000000", 0.0), rgb("#000000", 0.0), rgb("#000000", a)], [0.0, 0.55, 1.0])
                p = skia.Paint(); p.setShader(sh)
                cc.drawRect(skia.Rect.MakeWH(W, H), p)
            self._vig[a] = self._raster(d)
        c.save(); c.resetMatrix(); c.drawImage(self._vig[a], 0, 0); c.restore()


# ------------------------------------------------------------------ sous-titres
def draw_subtitle(c, sub, t, fade=4 / FPS, cx=515, base=1420, size=54):
    if not (sub["start"] <= t < sub["end"]): return
    a = min(1.0, (t - sub["start"]) / fade, (sub["end"] - t) / fade)
    lines = sub["lines"]; lh = size * 1.22
    hl = sub.get("hl")
    for i, l in enumerate(lines):
        y = base - (len(lines) - 1 - i) * lh
        f = font(size, "SemiBold")
        w = f.measureText(l)
        x = cx - w / 2
        # ombre portée 0 2 8 noir 60 %, pas de boîte pleine
        sp = paint("#000000", 0.6 * a, blur=4)
        c.drawString(l, x, y + 2, f, sp)
        c.drawString(l, x + 0.5, y + 2.5, f, paint("#000000", 0.35 * a, blur=2))
        if hl and hl in l.split(" "):
            pre = l.split(" ")
            xx = x
            for wd in pre:
                col = ACC if wd == hl else TXT
                if wd == hl:
                    # accent éclairci pour la lisibilité sur fond sombre
                    c.drawString(wd, xx, y, f, paint("#8FA4FF", a))
                else:
                    c.drawString(wd, xx, y, f, paint(TXT, a))
                xx += f.measureText(wd + " ")
            hl = None
        else:
            c.drawString(l, x, y, f, paint(TXT, a))


# ------------------------------------------------------------------ géographie
class Geo:
    """Projection simple (équirectangulaire corrigée à 46,5° N) de la France métropolitaine."""
    LAT0 = 46.5

    def __init__(self):
        d = os.path.join(ROOT, "assets", "data")
        self.regions = json.load(open(os.path.join(d, "regions.geojson")))["features"]
        self.deps = json.load(open(os.path.join(d, "departements.geojson")))["features"]
        self.k = math.cos(math.radians(self.LAT0))
        self._cache = {}

    def proj(self, lon, lat):
        return lon * self.k, -lat

    def path(self, geom, fit):
        """fit = (ox, oy, scale) en coordonnées design ; renvoie skia.Path."""
        ox, oy, s = fit
        p = skia.Path()
        polys = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
        for poly in polys:
            for ring in poly:
                for i, (lon, lat) in enumerate(ring):
                    x, y = self.proj(lon, lat)
                    X, Y = ox + x * s, oy + y * s
                    (p.moveTo if i == 0 else p.lineTo)(X, Y)
                p.close()
        return p

    def fit_france(self, cx=540, cy=700, width=900):
        # bornes métropole (hors Corse pour le cadrage) lon -5.2..8.3 / lat 42.3..51.1
        x0, _ = self.proj(-5.2, 0); x1, _ = self.proj(9.6, 0)
        _, y0 = self.proj(0, 51.1); _, y1 = self.proj(0, 41.3)
        s = width / (x1 - x0)
        ox = cx - (x0 + x1) / 2 * s; oy = cy - (y0 + y1) / 2 * s
        return (ox, oy, s)

    def pt(self, lon, lat, fit):
        ox, oy, s = fit
        x, y = self.proj(lon, lat)
        return ox + x * s, oy + y * s

    def region_paths(self, fit):
        key = ("r", fit)
        if key not in self._cache:
            self._cache[key] = {f["properties"]["nom"]: self.path(f["geometry"], fit) for f in self.regions}
        return self._cache[key]

    def dep_paths(self, fit):
        key = ("d", fit)
        if key not in self._cache:
            self._cache[key] = {f["properties"]["code"]: self.path(f["geometry"], fit) for f in self.deps}
        return self._cache[key]


CITIES = {
    "Paris": (2.3522, 48.8566), "Créteil": (2.4553, 48.7904), "Lens": (2.8319, 50.4329),
    "Saint-Ouen-l'Aumône": (2.1110, 49.0443), "Argenteuil": (2.2475, 48.9472), "Tours": (0.6848, 47.3941),
    "Marseille": (5.3698, 43.2965), "Lyon": (4.8357, 45.7640), "Toulouse": (1.4442, 43.6047),
    "Nantes": (-1.5536, 47.2184), "Rennes": (-1.6778, 48.1173), "Bordeaux": (-0.5792, 44.8378),
    "Lille": (3.0573, 50.6292), "Strasbourg": (7.7521, 48.5734), "Grenoble": (5.7245, 45.1885),
    "Montpellier": (3.8767, 43.6108), "Rouen": (1.0993, 49.4432), "Dijon": (5.0415, 47.3220),
    "Clermont-Ferrand": (3.0863, 45.7772), "Nice": (7.2620, 43.7102), "Brest": (-4.4861, 48.3904),
    "Limoges": (1.2611, 45.8336), "Caen": (-0.3707, 49.1829), "Dunkerque": (2.3768, 51.0344),
    "Nancy": (6.1844, 48.6921), "Poitiers": (0.3404, 46.5802), "Orléans": (1.9093, 47.9030),
    "Amiens": (2.2957, 49.8941), "Besançon": (6.0241, 47.2378), "Perpignan": (2.8948, 42.6887),
}
