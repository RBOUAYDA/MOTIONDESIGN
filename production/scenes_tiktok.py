# -*- coding: utf-8 -*-
"""Version TikTok (section N du dossier) — remontée pour le fil : accroche visible dès la 1re image,
un plan toutes les 1,5 à 2,5 s, un chiffre toutes les 3 s au cœur, question finale au spectateur.
"""
from gfx import *
import charts as ch
from charts import fmt
import illus
from render import Shot

BG_TONE = BG


def build(TL):
    items = {it["key"]: it for it in TL["items"]}
    K = {k: v["start"] for k, v in items.items()}
    E = {k: v["end"] for k, v in items.items()}
    total = TL["total"]

    import json, os
    spoken = {m["key"]: m["spoken"] for m in json.load(open(os.path.join(os.path.dirname(__file__), "..", "assets", "voice", "tiktok", "manifest.json")))}

    def at(key, sub):
        """instant estimé où `sub` (texte prononcé) commence dans la phrase `key`."""
        it = items[key]; txt = spoken[key]
        i = txt.find(sub)
        assert i >= 0, (key, sub, txt)
        return it["start"] + it["dur"] * max(0, i) / max(1, len(txt))

    shots = []

    def add(t0, t1, fn, **kw):
        shots.append(Shot(t0, t1, fn, **kw))

    def hook_text(c, t, a=1.0):
        rrect(c, 70, 270, 940, 250, 10, "#000000", 0.55 * a)
        text(c, "LA RUE PEUT-ELLE", 100, 370, 80, "Bold", TXT, a, display=True)
        text(c, "FAIRE PLIER L'ÉTAT ?", 100, 470, 80, "Bold", ACC if False else "#8FA4FF", a, display=True)

    # 1 — accroche (visible dès l'image 0)
    def s_hook(c, t):
        illus.school_gate(c, t + 2, bins=True)
        badge(c)
        hook_text(c, t)
        chip(c, "LYCÉES BLOQUÉS · OCT. 2026", 90, 560, size=26, fill=ACC)
    add(0.0, K["t2"], s_hook, cam=("spi", 0.06, (540, 1200)))

    # 2 — Créteil
    def s_creteil(c, t):
        G = ch.geo(); fit = G.fit_france(540, 800, 900)
        z = ease(prog(t, K["t2"], 2.4))
        x, y = G.pt(2.4553, 48.7904, fit)
        s = 1 + 1.6 * (1 - z) * 0 + 0.6 * z
        c.save(); c.translate(x, y); c.scale(1 + 0.6 * z, 1 + 0.6 * z); c.translate(-x, -y)
        ch.france_map(c, t, 1.0, fit, hl={"Île-de-France": (ACC, 0.5)})
        ch.city_dot(c, x, y, 1, size=10, pulse_t=t)
        c.restore()
        rrect(c, 70, 270, 940, 190, 10, "#000000", 0.5)
        text(c, "CRÉTEIL", 100, 360, 84, "Bold", TXT, appear(t, K["t2"] - 0.2), display=True)
        text(c, "Mi-septembre · lycée Saint-Exupéry", 100, 420, 34, "SemiBold", NEU, appear(t, K["t2"]))
        source(c, "Rectorat de Créteil ; Éducation nationale", t, K["t2"])
    add(K["t2"], K["t3"], s_creteil)

    # 3 — trois mots-clés, un par plan
    kws = [("PROFS NON", "REMPLACÉS", K["t3"]), ("CLASSES", "SURCHARGÉES", at("t3", "des classes")), ("BÂTIMENTS", "DÉGRADÉS", at("t3", "des bâtiments"))]
    for i, (a1, a2, ts) in enumerate(kws):
        t_end = kws[i + 1][2] if i + 1 < len(kws) else K["t4"]
        def s_kw(c, t, a1=a1, a2=a2, ts=ts, i=i):
            illus.classroom(c, t + i * 3)
            c.drawRect(skia.Rect.MakeWH(W, H), paint(BG, 0.62))
            badge(c)
            k = ease(prog(t, ts, 0.35))
            text(c, a1, 90, 640 + 30 * (1 - k), 104, "Bold", TXT, k, display=True)
            text(c, a2, 90, 760 + 30 * (1 - k), 104, "Bold", "#8FA4FF", k, display=True)
            text(c, f"{i + 1}/3", 90, 470, 30, "SemiBold", NEU, 1, track=0.1)
        add(ts, t_end, s_kw, cam=("spi", 0.05))

    # 4 — toute la France
    def s_france(c, t):
        G = ch.geo(); fit = G.fit_france(540, 820, 900)
        regs = list(G.region_paths(fit).keys())
        hl = {r: (ACC, 0.55 * ease(prog(t, K["t4"] + 0.06 * i, 0.4))) for i, r in enumerate(regs)}
        ch.france_map(c, t, 1, fit, hl=hl)
        text(c, "PUIS TOUTE", 90, 360, 90, "Bold", TXT, appear(t, K["t4"] - 0.1), display=True)
        text(c, "LA FRANCE", 90, 460, 90, "Bold", TXT, appear(t, K["t4"]), display=True)
    add(K["t4"], K["t5"], s_france, cam=("zoomout", 0.08))

    # 5 — double comptage, en trois plans
    t5b = at("t5", "quatre cent quatre-vingt")
    def s_int(c, t):
        chip(c, "13 OCT.", 90, 330, size=30, fill=ACC)
        ch.big_number(c, t, K["t5"] + 0.6, 161500, ["manifestants", "selon l'Intérieur"], y=760, size=190)
        source(c, "Ministère de l'Intérieur — 13/10/2026", t, K["t5"])
    add(K["t5"], t5b - 0.1, s_int)

    def s_org(c, t):
        chip(c, "13 OCT.", 90, 330, size=30, fill=ACC)
        ch.big_number(c, t, t5b - 0.1, 480000, ["selon les", "organisateurs"], y=760, size=190, color=OCH)
        source(c, "Intersyndicale de la jeunesse — 13/10/2026", t, t5b)
    add(t5b - 0.1, E["t5"] - 1.2, s_org)

    def s_cmp(c, t):
        ch.double_bar(c, t, E["t5"] - 1.2, 161500, 480000, ["Intérieur"], ["Organisateurs"], 500000, y0=470, h=560, mid_t=E["t5"] - 0.6)
        text(c, "Méthodes de comptage différentes", 90, 400, 38, "SemiBold", TXT, appear(t, E["t5"] - 1.1))
    add(E["t5"] - 1.2, K["t6"], s_cmp)

    def s_214(c, t):
        ch.big_number(c, t, K["t6"], 214, ["lycées fermés"], y=780, size=260, count_frames=12)
        chip(c, "13 OCT.", 90, 360, size=30, fill=ACC)
        source(c, "Ministère de l'Éducation nationale (France 24)", t, K["t6"])
    add(K["t6"], K["t7"], s_214)

    t7b = at("t7", "quatre-vingt-six")
    def s_gav(c, t):
        ch.big_number(c, t, K["t7"], 6877, ["gardes à vue"], y=780, size=230, count_frames=12)
        chip(c, "AU 8 OCT.", 90, 360, size=30, fill=ACC)
        source(c, "Ministère de la Justice (franceinfo)", t, K["t7"])
    add(K["t7"], t7b - 0.1, s_gav)

    def s_86(c, t):
        text_tab(c, "86 %", 90, 800, 300, "Bold", "#8FA4FF", appear(t, t7b - 0.1, d_in=0.25))
        text(c, "de mineurs", 90, 900, 64, "SemiBold", TXT, appear(t, t7b + 0.1))
        source(c, "Ministère de la Justice — bilan au 08/10/2026", t, t7b)
    add(t7b - 0.1, K["t8"], s_86)

    def s_36(c, t):
        ch.big_number(c, t, K["t8"], 36, ["enquêtes confiées", "à l'IGPN"], y=760, size=260, count_frames=10)
        text(c, "Enquêtes en cours — pas des faits jugés", 90, 1000, 32, "SemiBold", OCH, appear(t, K["t8"] + 0.6))
        source(c, "ICI (ex-France Bleu) — 13-14/10/2026", t, K["t8"])
    add(K["t8"], K["t9"], s_36)

    def s_24(c, t):
        ch.big_number(c, t, K["t9"] + 0.2, 24, ["lycées incendiés", "ou saccagés"], y=760, size=260, count_frames=10, color=OCH)
        text(c, "selon le ministre de l'Éducation", 90, 1000, 32, "Medium", NEU, appear(t, K["t9"] + 1.0))
        source(c, "Édouard Geffray (CNEWS) — 07/10/2026", t, K["t9"])
    add(K["t9"], K["t10"], s_24)

    t10b = at("t10", "et promet")
    def s_3000(c, t):
        ch.big_number(c, t, K["t10"] + 0.3, 3000, ["remplaçants annoncés"], y=780, size=240, count_frames=12)
        source(c, "Édouard Geffray, TF1 — 08/10/2026 (franceinfo)", t, K["t10"])
    add(K["t10"], t10b, s_3000)

    def s_finoct(c, t):
        illus.facade(c, t)
        c.drawRect(skia.Rect.MakeWH(W, H), paint(BG, 0.55))
        badge(c)
        k = ease(prog(t, t10b, 0.3))
        rrect(c, 90, 520, 600, 150, 75, ACC, k)
        text(c, "FIN OCT.", 390, 625, 84, "Bold", TXT, k, align="center", display=True)
        text(c, "décisions promises par Matignon", 90, 760, 38, "SemiBold", TXT, appear(t, t10b + 0.3), shadow=True)
        source(c, "Allocution de Sébastien Lecornu — 07/10/2026", t, t10b)
    add(t10b, K["t11"], s_finoct, cam=("spi", 0.05))

    def s_why(c, t):
        k = ease(prog(t, K["t11"], 0.25))
        text(c, "POURQUOI", 540, 760, 140, "Bold", TXT, k, align="center", display=True)
        text(c, "PAS PLUS ?", 540, 900, 140, "Bold", "#8FA4FF", k, align="center", display=True)
    add(K["t11"], K["t12"], s_why, cam=("spi", 0.06))

    t12b = at("t12", "cinquante-sept"); t12c = at("t12", "mais cinquante-trois")
    def s_split(c, t):
        text(c, "L'OPINION", 90, 700, 120, "Bold", TXT, appear(t, K["t12"] - 0.05, d_in=0.25), display=True)
        text(c, "EST PARTAGÉE", 90, 830, 104, "Bold", OCH, appear(t, K["t12"] + 0.4, d_in=0.25), display=True)
    add(K["t12"], t12b - 0.1, s_split)

    def s_polls(c, t):
        for i, (v, lab, col, ts) in enumerate(((57, "soutiennent le mouvement", TXT, t12b - 0.1), (53, "veulent qu'il s'arrête", OCH, t12c))):
            a = appear(t, ts, d_in=0.25); k = ease(prog(t, ts, 0.6))
            y = 520 + i * 330
            c.drawRect(skia.Rect.MakeXYWH(90, y, 900, 130), paint(NEU, 0.35 * a, stroke=2))
            c.drawRect(skia.Rect.MakeXYWH(90, y, 900 * v / 100 * k, 130), paint(col, 0.9 * a))
            text_tab(c, f"{int(round(v * k))} %", 120, y + 98, 84, "Bold", BG, a)
            text(c, lab, 90, y + 190, 42, "SemiBold", TXT, a)
        source(c, "Cluster17 / L'Opinion — terrain 7-9/10/2026", t, t12b)
    add(t12b - 0.1, K["t13"], s_polls)

    def s_eco(c, t):
        icons = [ch.icon_refinery, ch.icon_port, ch.icon_rail]
        for i, fn in enumerate(icons):
            ts = K["t13"] + 0.2 + i * 0.35
            a = appear(t, ts, d_in=0.25)
            x = 210 + i * 330; y = 820
            fn(c, x, y, 170, NEU, a)
            ch.strike(c, x, y, 170, a, ease(prog(t, ts + 0.2, 0.3)))
        text(c, "UN LYCÉE BLOQUÉ", 90, 420, 84, "Bold", TXT, appear(t, K["t13"] - 0.05, d_in=0.25), display=True)
        text(c, "≠ économie paralysée", 90, 510, 56, "SemiBold", OCH, appear(t, K["t13"] + 0.6))
    add(K["t13"], K["t14"], s_eco)

    hist = [("2006", "CPE", "RETRAIT", GOOD, at("t14", "le cé pé")), ("2010", "Retraites", "ADOPTÉE", NEU, K["t15"]),
            ("2023", "Retraites", "ADOPTÉE", NEU, at("t15", "et deux mille vingt-trois"))]
    def s_hist(c, t):
        text(c, "L'HISTOIRE", 90, 380, 90, "Bold", TXT, appear(t, K["t14"] - 0.05, d_in=0.25), display=True)
        for i, (yr, n, res, col, ts) in enumerate(hist):
            a = appear(t, ts, d_in=0.25); k = ease(prog(t, ts, 0.3))
            y = 500 + i * 220 + 30 * (1 - k)
            rrect(c, 90, y, 900, 180, 10, "#1C2130", a)
            text(c, yr, 130, y + 115, 96, "Bold", TXT, a, display=True)
            text(c, n, 440, y + 105, 44, "SemiBold", TXT, a)
            bw = text_w(res, 30, "Bold", track=0.1) + 40
            rrect(c, 950 - bw, y + 60, bw, 60, 30, col, a)
            text(c, res, 950 - bw / 2, y + 101, 30, "Bold", BG, a, align="center", track=0.1)
        source(c, "vie-publique.fr ; Le Monde ; INA", t, K["t14"])
    add(K["t14"], K["t16"], s_hist)

    kw = [("LA DURÉE", at("t16", "la durée")), ("L'OPINION", at("t16", "l'opinion")),
          ("GRÈVES MULTI-SECTEURS", at("t16", "les grèves")), ("COÛT POLITIQUE", at("t16", "le coût"))]
    def s_kw4(c, t):
        text(c, "CE QUI FAIT BOUGER", 90, 380, 52, "Bold", NEU, 1, display=True, track=0.02)
        for i, (w, ts) in enumerate(kw):
            a = appear(t, ts - 0.1, d_in=0.25)
            on = (i == max([j for j, (_, tj) in enumerate(kw) if t >= tj - 0.1] or [0]))
            text(c, w, 90, 540 + i * 140, 84 if len(w) < 16 else 70, "Bold", "#8FA4FF" if on else TXT, a, display=True)
    add(K["t16"], K["t17"], s_kw4)

    def s_noviol(c, t):
        k = ease(prog(t, K["t17"] - 0.05, 0.2))
        text(c, "PAS LA", 540, 760, 150, "Bold", TXT, k, align="center", display=True)
        text(c, "VIOLENCE.", 540, 910, 150, "Bold", OCH, k, align="center", display=True)
        source(c, "Analyse historique ; Ifop/LCI 6-7/10/2026", t, K["t17"])
    add(K["t17"], K["t18"], s_noviol)

    def s_bastille(c, t):
        m = ch.paris_map(c, t, 0.9, cy=900, scale=6500, markers=[("B", *ch.BASTILLE)])
        bx, by = m["B"]
        ch.city_dot(c, bx, by, 1, "Paris · Bastille", pulse_t=t, lsize=30)
        chip(c, "SAM. 17 OCT.", 90, 330, size=40, fill=ACC)
        text(c, "NOUVEAU TEST", 90, 520, 96, "Bold", TXT, appear(t, at("t18", "nouveau"), d_in=0.25), display=True)
    add(K["t18"], K["t19"], s_bastille, cam=("spi", 0.06, (540, 900)))

    def s_q(c, t):
        a = appear(t, K["t19"] - 0.05, d_in=0.3)
        text(c, "POUR TOI,", 90, 520, 80, "Bold", NEU, a, display=True)
        para(c, "qu'est-ce qui ferait vraiment bouger les choses ?", 90, 640, 84, 880, "Bold", TXT, a, lh=1.12, display=True)
        a2 = appear(t, E["t19"] + 0.2)
        rrect(c, 90, 1060, 560, 80, 40, ACC, a2)
        text(c, "Réponds en commentaire", 370, 1112, 34, "SemiBold", TXT, a2, align="center")
        text(c, "Sources en commentaire épinglé", 90, 1200, 28, "Medium", NEU, a2)
    add(K["t19"], total, s_q, nosub=True)

    shots.sort(key=lambda s: s.t0)
    return shots
