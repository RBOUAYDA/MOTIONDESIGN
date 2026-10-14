# -*- coding: utf-8 -*-
"""Storyboard de la version longue (section F du dossier), recalé sur la voix réelle.

Les plans « ARCHIVE » du storyboard supposaient des images d'agence sous licence, indisponibles ici :
ils sont remplacés par des plans de data-design ou des illustrations au trait (bandeau ILLUSTRATION /
SCHÉMA permanent). Aucune image n'imite une archive réelle.
"""
import math
from gfx import *
import charts as ch
from charts import fmt
import illus
from render import Shot

BG_TONE = BG
CORTEGE = illus.Cortege()


def build(TL):
    K = {it["key"]: it["start"] for it in TL["items"]}
    E = {it["key"]: it["end"] for it in TL["items"]}
    SEC = {s["id"]: s for s in TL["sections"]}
    LEAD = {"ch1": 5.0, "ch2": 2.4, "ch3": 2.4, "ch4": 4.0, "ch5": 2.2, "ch6": 2.4, "d17": 2.0, "cond": 2.4, "concl": 2.2}
    card = {k: SEC[k]["vo_start"] - v for k, v in LEAD.items()}
    total = TL["total"]
    shots = []

    def add(t0, t1, fn, **kw):
        shots.append(Shot(t0, t1, fn, **kw))

    def tag(label):
        def f(c, t, a=1.0):
            chapter_tag(c, label, a)
        return f

    # ================================================================== INTRODUCTION (00:00-00:14, sans voix)
    def s_gate_dawn(c, t):
        illus.school_gate(c, t, bins=True, dawn=1.0)
        badge(c)
        chip(c, "13 OCT. 2026", 90, 230, t, 0.3, size=26, outline=TXT)
    add(0.0, 3.2, s_gate_dawn, cam=("spi", 0.03), tout="cut")

    def s_cortege(c, t):
        CORTEGE.draw(c, t + 5)
        badge(c, "SCHÉMA")
        slide_text(c, "Cortèges", 90, 330, 64, t, 3.4, weight="Bold", display=True)
        slide_text(c, "Mobilisation lycéenne et étudiante", 90, 385, 32, t, 3.6, color=NEU)
    add(3.2, 6.2, s_cortege, cam=("spi", 0.02))

    def s_ticker(c, t):
        text(c, "2 OCTOBRE", 90, 420, 30, "SemiBold", NEU, appear(t, 6.3), track=0.12)
        ch.big_number(c, t, 6.35, 1747, ["interpellations", "en une journée"], y=700, size=210)
        source(c, "Ministère de l'Intérieur — 02/10/2026", t, 6.4)
    add(6.2, 9.0, s_ticker)

    def s_cards(c, t):
        cards = [("13/10", "161 500", "manifestants selon l'Intérieur", "480 000 selon l'intersyndicale"),
                 ("13/10", "214", "lycées fermés", "ministère de l'Éducation"),
                 ("08/10", "6 877", "gardes à vue · 86 % de mineurs", "ministère de la Justice")]
        scroll = (t - 9.0) * 70
        for i, (d, v, l1, l2) in enumerate(cards):
            ts = 9.05 + i * 0.45
            a = appear(t, ts)
            if a <= 0: continue
            y = 330 + i * 300 - scroll + 30 * (1 - ease(prog(t, ts, IN)))
            rrect(c, 90, y, 850, 260, 10, "#E9E5DC", 0.96 * a)
            text(c, d, 124, y + 50, 24, "SemiBold", "#5A5E66", a, track=0.1)
            text(c, v, 124, y + 150, 92, "Bold", "#111317", a, display=True)
            text(c, l1, 124, y + 200, 30, "SemiBold", "#2A2D33", a)
            text(c, l2, 124, y + 236, 24, "Medium", "#5A5E66", a)
        source(c, "Intérieur ; intersyndicale ; Éducation nationale ; Justice", t, 9.2)
    add(9.0, 14.0, s_cards, tout="cut")

    def s_france_points(c, t):
        a = appear(t, 14.0)
        G = ch.geo(); fit = G.fit_france(540, 830, 860)
        ch.france_map(c, t, a, fit)
        rng = np.random.default_rng(5)
        names = list(CITIES.keys())
        for i, n in enumerate(names):
            ts = 14.3 + (i % 12) * 0.35 + rng.uniform(0, 0.3)
            x, y = G.pt(*CITIES[n], fit)
            ch.city_dot(c, x, y, appear(t, ts) * 0.9, size=10, pulse_t=t + i * 0.37)
        slide_text(c, "Blocages et manifestations", 90, 330, 46, t, 14.4, weight="SemiBold")
        slide_text(c, "dans toute la France", 90, 385, 46, t, 14.6, weight="SemiBold", color=NEU)
        badge(c, "SCHÉMA")
    add(14.0, K["i2"] - 0.2, s_france_points, tin="fade", cam=("spi", 0.04))

    def s_barriers(c, t):
        illus.street(c, t)
        illus.draw_barriers(c, 1230, 1.0)
        badge(c)
    add(K["i2"] - 0.2, K["i3"] - 0.1, s_barriers, cam=("spi", 0.03))

    def s_facade(c, t):
        illus.facade(c, t)
        badge(c)
        slide_text(c, "Hôtel de Matignon", 90, 300, 30, t, K["i3"], color=NEU, weight="SemiBold")
    add(K["i3"] - 0.1, SEC["title"]["start"], s_facade, cam=("spi", 0.05), tout="dip")

    def s_title(c, t):
        t0 = SEC["title"]["start"]
        mask_reveal(c, lambda: text(c, "FRANCE", 90, 760, 150, "Bold", TXT, 1, display=True, track=0.02), t, t0 + 0.2, 0.7, 80, 600, 960, 200)
        k = ease(prog(t, t0 + 0.9, 0.6))
        line(c, 90, 800, 90 + 210 * k, 800, ACC, 0.95, 6, cap="butt")
        mask_reveal(c, lambda: text(c, "LE RAPPORT", 90, 930, 118, "Bold", TXT, 1, display=True), t, t0 + 1.3, 0.8, 80, 800, 960, 160)
        mask_reveal(c, lambda: text(c, "DE FORCE", 90, 1060, 118, "Bold", TXT, 1, display=True), t, t0 + 1.5, 0.8, 80, 940, 960, 160)
        slide_text(c, "Blocages, manifestations :", 90, 1170, 40, t, t0 + 2.6, color=NEU)
        slide_text(c, "peuvent-ils faire bouger l'État ?", 90, 1222, 40, t, t0 + 2.8, color=NEU)
    add(SEC["title"]["start"], card["ch1"], s_title, tin="dip", tout="dip", cam=("spi", 0.02))

    # ================================================================== CHAPITRE 1
    T1 = "1 · COMMENT EN EST-ON ARRIVÉ LÀ ?"

    def s_card1(c, t):
        ch.chapter_card(c, t, card["ch1"] + 0.1, "1", "Comment en est-on arrivé là ?")
    add(card["ch1"], K["c1a"] + 0.2, s_card1, tin="dip")

    def s_creteil(c, t):
        G = ch.geo()
        # zoom sur le Val-de-Marne : carte départementale Île-de-France
        x, y = 2.4553, 48.7904
        k = G.k; sc = 1900
        fit = (540 - x * k * sc, 760 + y * sc, sc)
        a = appear(t, K["c1a"] + 0.2)
        dp = G.dep_paths(fit)
        for code in ("75", "77", "78", "91", "92", "93", "94", "95"):
            c.drawPath(dp[code], paint("#1A1E28", a))
            if code == "94":
                c.drawPath(dp[code], paint(ACC, 0.30 * appear(t, K["c1b"])))
            c.drawPath(dp[code], paint(TXT, 0.45 * a, stroke=2))
        X, Y = G.pt(x, y, fit)
        ch.city_dot(c, X, Y, appear(t, K["c1b"]), "Lycée Saint-Exupéry", sub="Créteil · Val-de-Marne (94)", pulse_t=t, lsize=36)
        px, py = G.pt(2.3522, 48.8566, fit)
        text(c, "Paris", px, py, 30, "SemiBold", NEU, a * 0.9, align="center")
        chip(c, "MI-SEPTEMBRE", 90, 300, t, K["c1c"], size=26, fill=ACC)
        slide_text(c, "Grève des professeurs : postes non pourvus", 90, 1150, 34, t, K["c1c"] + 0.8, weight="SemiBold")
        tag(T1)(c, t)
        source(c, "Synthèse Wikipédia ; Amnesty International France", t, K["c1c"] + 0.8)
    add(K["c1a"] + 0.2, K["c1d"], s_creteil, tin="fade", cam=("spi", 0.04, (540, 700)))

    def s_gate_block(c, t):
        illus.school_gate(c, t, bins=True)
        badge(c)
        a = appear(t, K["c1e"])
        if a > 0:
            line(c, 520, 1100, 520, 1460, TXT, 0.8 * a, 2)
            text(c, "Premiers blocus", 545, 1100, 34, "SemiBold", TXT, a, shadow=True)
            text(c, "dès le 18 septembre", 545, 1142, 28, "Medium", TXT, 0.8 * a, shadow=True)
    add(K["c1d"], K["c1f"], s_gate_block, cam=("spi", 0.04, (540, 1200)))

    def s_spread(c, t):
        G = ch.geo()
        z = 1 - ease(prog(t, K["c1f"] + 0.2, 2.2))
        fit_full = G.fit_france(540, 760, 900)
        # zoom arrière Créteil -> France
        cx, cy = G.pt(2.4553, 48.7904, fit_full)
        s = 1 + 3.0 * z
        c.save(); c.translate(540, 760); c.scale(s, s); c.translate(-(cx * z + 540 * (1 - z)), -(cy * z + 760 * (1 - z)))
        idf = appear(t, K["c1f"] + 0.3)
        allr = ease(prog(t, K["c1g"], 1.6))
        hl = {}
        regs = list(G.region_paths(fit_full).keys())
        for i, r in enumerate(regs):
            if r == "Île-de-France":
                hl[r] = (ACC, 0.65 * idf)
            else:
                kk = ease(prog(t, K["c1g"] + 0.12 * i, 0.5))
                hl[r] = (ACC, 0.32 * kk)
        ch.france_map(c, t, 1.0, fit_full, hl=hl)
        ch.city_dot(c, cx, cy, 1, size=10 / s * 1.5)
        c.restore()
        a1 = appear(t, K["c1f"] + 0.3)
        a2 = appear(t, K["c1g"])
        text(c, "≈\u00a010 lycées en Île-de-France", 90, 1150, 42, "SemiBold", TXT, a1 * (1 - a2))
        text(c, "23 septembre", 90, 1196, 28, "Medium", NEU, a1 * (1 - a2))
        text(c, "Des centaines · tout le pays", 90, 1170, 42, "SemiBold", TXT, a2)
        tag(T1)(c, t)
        source(c, "Rectorat de Créteil ; ministère de l'Éducation nationale", t, K["c1f"])
    add(K["c1f"], K["c1h"], s_spread, tin="fade")

    def s_timeline(c, t):
        items = [("17-18 SEPT.", "Grève des professeurs, premiers blocus à Créteil", K["c1h"]),
                 ("23 SEPT.", "Une dizaine de lycées franciliens", K["c1h"] + 0.4),
                 ("29 SEPT.", "Grève de la fonction publique : le mouvement change d'échelle", K["c1h"] + 0.9)]
        ch.timeline_v(c, t, items, y0=440, gap=230, active=lambda tt: 2 if tt > K["c1i"] else None)
        tag(T1)(c, t)
        source(c, "France 3 Occitanie — 29/09/2026 ; rectorat de Créteil", t, K["c1h"] + 0.9)
    add(K["c1h"], K["c1j"], s_timeline, tin="fade", cam=("spi", 0.02))

    def s_1747(c, t):
        ch.big_number(c, t, K["c1j"] + 0.6, 1747, ["interpellations", "en une seule journée"], y=760, size=230, date="2 OCT. 2026")
        tag(T1)(c, t)
        source(c, "Ministère de l'Intérieur, 02/10/2026 (franceinfo)", t, K["c1j"] + 0.6)
    add(K["c1j"], K["c1k"], s_1747)

    def s_double(c, t):
        ch.double_bar(c, t, K["c1l"], 256000, 450000, ["selon le ministère", "de l'Intérieur"], ["selon les", "organisateurs"],
                      480000, y0=440, h=640, mid_t=K["c1n"], date="6 OCT. · LE PIC",
                      notes=["comptage par segments", "extrapolation des relevés"], note_t=[K["c1n"] + 1.6, K["c1n"] + 3.3])
        a = appear(t, K["c1o"])
        if a > 0:
            text(c, "La vérité : probablement entre les deux", 90, 1215, 32, "SemiBold", ACC, a)
        tag(T1)(c, t)
        source(c, "Intérieur ; organisateurs (France 24) — 06/10/2026", t, K["c1l"], y=1258 if a <= 0 else 1262)
    add(K["c1k"], K["c1p"], s_double, tin="fade")

    def s_lines(c, t):
        series = [dict(name="Intérieur", color=TXT, pts=[(0, 256000), (0.5, 71500), (1, 161500)],
                       labels=["256 000", "71 500", "161 500"], ly=50),
                  dict(name="Organisateurs (CGT le 08/10)", color=OCH, dash=True, pts=[(0, 450000), (0.5, 130000), (1, 480000)],
                       labels=["450 000", "130 000", "480 000"])]
        ch.line_chart(c, t, K["c1p"], series, [0, 0.5, 1], ["6 oct.", "8 oct.", "13 oct."], 500000,
                      box=(170, 420, 720, 620), step_t=[K["c1p"] + 0.2, K["c1q"] + 0.5])
        tag(T1)(c, t)
        source(c, "Intérieur ; intersyndicale de la jeunesse ; CGT", t, K["c1p"])
    add(K["c1p"], K["c1r"], s_lines, tin="fade")

    def s_closed(c, t):
        items = [("6 oct.", 800, "≈ 800"), ("8 oct.", 224, "224"), ("13 oct.", 214, "214")]
        ch.bar_series(c, t, K["c1r"], items, 900, box=(150, 470, 780, 600), steps=[K["c1s"], K["c1r"] + 1.2, K["c1r"] + 0.3], hl=2)
        text(c, "Lycées fermés", 90, 380, 52, "Bold", TXT, appear(t, K["c1r"]), display=True)
        a1 = appear(t, K["c1t"]); a2 = appear(t, K["c1u"])
        text(c, "« en recul »", 150, 1180, 36, "SemiBold", TXT, a1)
        text(c, "— ministère", 150, 1220, 26, "Medium", NEU, a1)
        text(c, "« installé »", 560, 1180, 36, "SemiBold", OCH, a2)
        text(c, "— organisateurs", 560, 1220, 26, "Medium", NEU, a2)
        tag(T1)(c, t)
        source(c, "Ministère de l'Éducation nationale (France 24)", t, K["c1r"], y=1262)
    add(K["c1r"], card["ch2"], s_closed, tin="fade", tout="dip")

    # ================================================================== CHAPITRE 2
    T2 = "2 · POURQUOI ILS SE MOBILISENT"

    def s_card2(c, t):
        illus.classroom(c, t)
        c.drawRect(skia.Rect.MakeWH(W, H), paint(BG, 0.82))
        ch.chapter_card(c, t, card["ch2"] + 0.1, "2", "Pourquoi ils se mobilisent")
    add(card["ch2"], K["c2c"], s_card2, tin="dip")

    def column(c, t, title, items, color=TXT, a_mul=1.0, y=420):
        a = appear(t, items[0][1] - 0.3) * a_mul
        text(c, title, 90, y, 70, "Bold", color, a, display=True, track=0.01)
        line(c, 90, y + 30, 90 + 120 * ease(prog(t, items[0][1] - 0.3, 0.6)), y + 30, ACC, a, 5, cap="butt")
        ch.stack_list(c, t, items, y=y + 140, gap=96, size=46)

    def s_lyceens(c, t):
        illus.classroom(c, t)
        c.drawRect(skia.Rect.MakeWH(W, H), paint(BG, 0.72))
        badge(c)
        column(c, t, "LYCÉENS", [("Professeurs remplacés", K["c2c"] + 2.3), ("Classes moins chargées", K["c2c"] + 3.6),
                                  ("Bâtiments décents", K["c2c"] + 5.2), ("Emplois du temps", K["c2d"] + 1.0),
                                  ("Téléphone portable", K["c2d"] + 2.6)])
        tag(T2)(c, t)
        source(c, "Union syndicale lycéenne ; synthèse des revendications", t, K["c2c"])
    add(K["c2c"], K["c2e"], s_lyceens, cam=("spi", 0.03))

    def s_etudiants(c, t):
        illus.amphi(c, t)
        c.drawRect(skia.Rect.MakeWH(W, H), paint(BG, 0.7))
        badge(c)
        column(c, t, "ÉTUDIANTS", [("Budget des universités", K["c2e"] + 0.9), ("Parcoursup", K["c2e"] + 2.6), ("Repas à 1 €", K["c2e"] + 3.6)])
        tag(T2)(c, t)
        source(c, "Union étudiante ; Fage", t, K["c2e"])
    add(K["c2e"], K["c2f"], s_etudiants, tin="fade", cam=("par", 0.02))

    def s_syndicats(c, t):
        column(c, t, "SYNDICATS", [("Postes", K["c2f"] + 2.4), ("Salaires", K["c2f"] + 3.4), ("Budget 2027", K["c2f"] + 3.9)])
        a = appear(t, K["c2g"])
        x = 90
        for i, n in enumerate(["CFDT", "CGT", "FO", "UNSA", "FSU"]):
            x += chip(c, n, x, 940, t, K["c2g"] + 0.1 * i, size=28, outline=NEU) + 14
        chip(c, "5 NOV. · JOURNÉE INTERPROFESSIONNELLE", 90, 1040, t, K["c2g"] + 2.4, size=28, fill=ACC)
        tag(T2)(c, t)
        source(c, "CGT, CFDT, FO, UNSA, FSU ; Sortiraparis", t, K["c2f"])
    add(K["c2f"], K["c2h"], s_syndicats, tin="fade")

    def s_fuel(c, t):
        illus.fuel_station(c, t)
        c.drawRect(skia.Rect.MakeWH(W, 700), paint(BG, 0.55))
        badge(c)
        a = appear(t, K["c2h"])
        rrect(c, 90, 300, 640, 210, 8, NEU, 0.8 * a, stroke=2)
        p = paint(NEU, 0.8 * a, stroke=2); p.setPathEffect(skia.DashPathEffect.Make([10, 8], 0))
        text(c, "17 OCT. — APPELS DISTINCTS", 120, 360, 34, "Bold", TXT, a, track=0.03)
        text(c, "Réseaux sociaux, bannière « gilets jaunes »", 120, 408, 28, "Medium", NEU, a)
        text(c, "Prix des carburants, superprofits, RIC", 120, 448, 28, "Medium", NEU, a)
        a2 = appear(t, K["c2j"] + 0.6)
        if a2 > 0:
            line(c, 900, 840, 780, 760, TXT, 0.8 * a2, 2)
            rrect(c, 440, 640, 380, 140, 8, "#000000", 0.6 * a2)
            text(c, "GAZOLE", 466, 690, 26, "SemiBold", NEU, a2, track=0.12)
            text_tab(c, "2,352 €/L", 466, 760, 64, "Bold", TXT, a2)
            text(c, "prix moyen · 11/10", 466, 800 + 10, 22, "Medium", NEU, a2)
        a3 = appear(t, K["c2k"])
        if a3 > 0:
            rrect(c, 90, 1090, 900, 80, 6, BG, 0.75 * a3)
            text(c, "Pas le même mouvement", 120, 1145, 44, "Bold", OCH, a3, display=True)
        source(c, "prix-carburants.gouv.fr (via CNEWS), 11/10/2026 ; Aladom", t, K["c2j"] + 0.6)
    add(K["c2h"], K["c2m"], s_fuel, tin="fade", cam=("spi", 0.03, (900, 900)))

    def s_overview(c, t):
        cols = [("LYCÉENS", TXT, False), ("ÉTUDIANTS", TXT, False), ("SYNDICATS", TXT, False), ("17 OCT.", NEU, True)]
        for i, (n, col, dashed) in enumerate(cols):
            a = appear(t, K["c2m"] + 0.15 * i)
            x = 90 + i * 215
            if dashed:
                p = paint(NEU, 0.8 * a, stroke=2); p.setPathEffect(skia.DashPathEffect.Make([10, 8], 0))
                c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, 420, 195, 420), 8, 8), p)
            else:
                rrect(c, x, 420, 195, 420, 8, "#1C2130", a)
                rrect(c, x, 420, 195, 420, 8, TXT, 0.3 * a, stroke=1.5)
            text(c, n, x + 97, 470, 26, "Bold", col, a, align="center", track=0.06)
            dates = ["continu", "continu", "5 nov.", "17 oct."]
            text(c, dates[i], x + 97, 800, 26, "Medium", NEU, a, align="center")
        a1 = appear(t, K["c2n"]); a2 = appear(t, K["c2o"])
        text(c, "+ Force", 90, 960, 54, "Bold", TXT, a1, display=True)
        text(c, "la base s'élargit", 330, 960, 36, "Medium", NEU, a1)
        text(c, "– Faiblesse", 90, 1070, 54, "Bold", OCH, a2, display=True)
        text(c, "la négociation se complique", 410, 1070, 36, "Medium", NEU, a2)
        tag(T2)(c, t)
    add(K["c2m"], card["ch3"], s_overview, tin="fade", tout="dip")

    # ================================================================== CHAPITRE 3
    T3 = "3 · LES BLOCAGES"

    def s_card3(c, t):
        ch.chapter_card(c, t, card["ch3"] + 0.1, "3", "Les blocages")
    add(card["ch3"], K["c3a"] + 1.4, s_card3, tin="dip")

    def s_block(c, t):
        illus.school_gate(c, t, bins=True, barriers=False)
        badge(c)
        a = appear(t, K["c3b"])
        if a > 0:
            k = ease(prog(t, K["c3b"], 0.8))
            # étiquette trackée sur l'entrée
            line(c, 560, 1180, 560 + 0 * k, 1180 - 260 * k, ACC, a, 3)
            c.drawCircle(560, 1180, 9, paint(ACC, a))
            rrect(c, 560 - 150, 860, 300, 62, 31, "#000000", 0.55 * a)
            text(c, "entrée bloquée", 560, 902, 32, "SemiBold", TXT, a, align="center")
        a2 = appear(t, K["c3c"] + 0.8)
        text(c, "Objectif : être visible", 90, 330, 52, "Bold", TXT, a2, display=True, shadow=True)
        for i, w in enumerate(["élèves", "parents", "caméras"]):
            ts = K["c3e"] + i * 0.75
            chip(c, w, 90 + i * 230, 400, t, ts, size=30, fill="#000000", outline=TXT)
        tag(T3)(c, t)
    add(K["c3a"] + 1.4, K["c3f"], s_block, cam=("spi", 0.035, (560, 1100)))

    def s_split(c, t):
        a = appear(t, K["c3f"])
        mid = 820
        merge = ease(prog(t, K["c3k"] - 0.6, 0.8))
        if merge >= 1: return
        aa = a * (1 - merge)
        line(c, 90, mid, 990, mid, NEU, 0.5 * aa, 2)
        text(c, "IMPACT LOCAL", 90, 380, 44, "Bold", TXT, aa, track=0.06)
        ch.stack_list(c, t, [("Une journée de cours perdue", K["c3g"] + 1.6), ("Des familles inquiètes", K["c3g"] + 3.3),
                             ("Un proviseur sous pression", K["c3g"] + 4.6)], y=470, gap=80, size=40, t1=K["c3k"] - 0.3)
        text(c, "IMPACT NATIONAL", 90, mid + 90, 44, "Bold", TXT, appear(t, K["c3h"]) * (1 - merge), track=0.06)
        icons = [(ch.icon_refinery, "raffinerie"), (ch.icon_port, "port"), (ch.icon_rail, "trains")]
        for i, (fn, lab) in enumerate(icons):
            ts = K["c3j"] + 0.6 + i * 0.9
            ai = appear(t, ts) * (1 - merge)
            x = 200 + i * 300; y = mid + 260
            fn(c, x, y, 140, NEU, ai)
            ch.strike(c, x, y, 140, ai, ease(prog(t, ts + 0.3, 0.4)))
            text(c, lab, x, y + 130, 30, "Medium", NEU, ai, align="center")
        text(c, "non concernés", 540, mid + 460, 30, "SemiBold", NEU, appear(t, K["c3j"] + 3.2) * (1 - merge), align="center")
        ai = appear(t, K["c3i"]) * (1 - merge)
        text(c, "≈ 0 € de coût mesurable à l'économie", 90, mid + 160, 32, "SemiBold", OCH, ai * (1 - appear(t, K["c3j"] + 0.5)))
        tag(T3)(c, t)
    add(K["c3f"], K["c3k"] + 0.3, s_split, tin="fade")

    def s_words(c, t):
        words = [("RÉPÉTITION", K["c3k"] + 2.6), ("IMAGE", K["c3k"] + 3.4), ("RISQUE", K["c3k"] + 4.5)]
        for i, (w, ts) in enumerate(words):
            a = appear(t, ts)
            col = ACC if w == "RISQUE" and t > K["c3l"] else TXT
            text(c, w, 90, 470 + i * 130, 104, "Bold", col, a, display=True)
        ch.stack_list(c, t, [("Un mineur gravement blessé", K["c3l"] + 0.4), ("Des parents qui basculent", K["c3m"] + 0.4),
                             ("D'autres secteurs qui rejoignent", K["c3n"] + 0.6)], y=930, gap=84, size=40, color=TXT)
        tag(T3)(c, t)
    add(K["c3k"], card["ch4"], s_words, tin="fade", tout="dip")

    # ================================================================== CHAPITRE 4 (silence musical)
    T4 = "4 · LES VIOLENCES"

    def s_card4(c, t):
        ch.chapter_card(c, t, card["ch4"] + 0.2, "4", "Les violences")
    add(card["ch4"], K["c4c"], s_card4, tin="dip")

    def s_gav(c, t):
        ch.big_number(c, t, K["c4c"] + 2.0, 6877, ["personnes placées", "en garde à vue"], y=640, size=220, date="AU 8 OCT.")
        a = appear(t, K["c4d"])
        if a > 0:
            text_tab(c, "86 %", 90, 1010, 150, "Bold", ACC, a)
            text(c, "sont mineures", 470, 990, 46, "SemiBold", TXT, a)
        a2 = appear(t, K["c4e"])
        text(c, "Sans précédent récent pour un mouvement social", 90, 1110, 30, "Medium", NEU, a2)
        tag(T4)(c, t)
        source(c, "Ministère de la Justice, bilan arrêté au 08/10/2026 (franceinfo)", t, K["c4c"])
    add(K["c4c"], K["c4f"], s_gav, tin="fade")

    def s_blesses(c, t):
        vals = [(715, "policiers et", "gendarmes"), (215, "élèves", ""), (85, "personnels", "éducatifs")]
        trig = [K["c4f"] + 2.5, K["c4f"] + 4.4, K["c4f"] + 5.6]
        for i, (v, l1, l2) in enumerate(vals):
            x = 90 + i * 300
            a = appear(t, trig[i])
            k = ease(prog(t, trig[i], 18 / FPS))
            text_tab(c, fmt(v * k), x, 760, 130, "Bold", TXT, a)
            text(c, l1, x, 830, 34, "SemiBold", TXT, a); text(c, l2, x, 872, 34, "SemiBold", TXT, a)
        text(c, "Blessés", 90, 470, 70, "Bold", TXT, appear(t, K["c4f"]), display=True)
        chip(c, "BILAN OFFICIEL AU 6 OCT.", 90, 520, t, K["c4f"] + 0.3, size=24, outline=NEU)
        text(c, "Bilan gouvernemental, non contradictoire", 90, 1000, 28, "Medium", NEU, appear(t, K["c4f"] + 6.5))
        tag(T4)(c, t)
        source(c, "Matignon (Euronews) — 06/10/2026", t, K["c4f"])
    add(K["c4f"], K["c4g"], s_blesses, tin="fade")

    def s_cases(c, t):
        G = ch.geo()
        fit = G.fit_france(540, 760, 1080)
        c.save()
        ch.france_map(c, t, appear(t, K["c4g"]), fit, stroke_a=0.35)
        pts = [("Lens", "lycéen de 15 ans, main arrachée", K["c4h"] + 0.6, "right"),
               ("Saint-Ouen-l'Aumône", "près de Pontoise · 14 ans, mâchoire brisée", K["c4i"] + 0.6, "left"),
               ("Argenteuil", "blessure à l'œil", K["c4j"] + 1.5, "right"),
               ("Tours", "blessure à l'œil", K["c4j"] + 2.6, "right"),
               ("Marseille", "17 ans, blessé à la tête", K["c4j"] + 3.0, "right")]
        for (n, d, ts, side) in pts:
            x, y = G.pt(*CITIES[n], fit)
            a = appear(t, ts)
            lab = n if n != "Saint-Ouen-l'Aumône" else "St-Ouen-l'Aumône"
            ch.city_dot(c, x, y, a, lab, side=side, size=12, lsize=28, sub=d)
        c.restore()
        a = appear(t, K["c4k"])
        if a > 0:
            rrect(c, 90, 1050, 900, 150, 8, "#000000", 0.6 * a)
            text_tab(c, "36", 120, 1160, 96, "Bold", TXT, a)
            text(c, "enquêtes confiées à l'IGPN", 270, 1120, 36, "SemiBold", TXT, a)
            text(c, "enquêtes en cours — pas des faits jugés", 270, 1165, 28, "Medium", OCH, a)
        a2 = appear(t, K["c4l"])
        if a2 > 0:
            rrect(c, 90, 290, 900, 90, 8, "#000000", 0.6 * a2)
            text(c, "Enquête ouverte ≠ faute établie", 120, 352, 44, "Bold", TXT, a2, display=True)
        tag(T4)(c, t)
        source(c, "ICI (ex-France Bleu) ; franceinfo — 13-14/10/2026", t, K["c4h"])
    add(K["c4g"], K["c4n"], s_cases, tin="fade")

    def s_quotes(c, t):
        a1 = appear(t, K["c4n"]); a2 = appear(t, K["c4p"])
        rrect(c, 90, 330, 900, 360, 10, "#1A1E28", a1)
        c.drawRect(skia.Rect.MakeXYWH(90, 330, 8, 360), paint(TXT, a1))
        text(c, "LAURENT NUÑEZ · MINISTRE DE L'INTÉRIEUR", 130, 390, 24, "SemiBold", NEU, a1, track=0.08)
        text(c, "Rejette le terme", 130, 470, 46, "SemiBold", TXT, a1)
        text(c, "« disproportionné »", 130, 530, 46, "SemiBold", TXT, a1)
        text(c, "04/10 · France 24 / AFP", 130, 580, 24, "Medium", NEU, a1)
        a1b = appear(t, K["c4o"])
        text(c, "Suspend les grenades assourdissantes · 07/10", 130, 650, 30, "SemiBold", OCH, a1b)
        rrect(c, 90, 730, 900, 330, 10, "#1A1E28", a2)
        c.drawRect(skia.Rect.MakeXYWH(90, 730, 8, 330), paint(OCH, a2))
        text(c, "SYNDICAT DE LA MAGISTRATURE · LDH · AVOCATS", 130, 790, 24, "SemiBold", NEU, a2, track=0.08)
        text(c, "Dénoncent des", 130, 870, 46, "SemiBold", TXT, a2)
        text(c, "interpellations préventives", 130, 930, 46, "SemiBold", TXT, a2)
        text(c, "LDH : « arrestations préventives »", 130, 990, 26, "Medium", NEU, a2)
        tag(T4)(c, t)
        source(c, "France 24 / AFP ; CNEWS (RTL) ; LDH", t, K["c4n"])
    add(K["c4n"], K["c4q"], s_quotes, tin="fade", cam=("spi", 0.02))

    def s_lycees(c, t):
        ch.big_number(c, t, K["c4r"] + 2.0, 24, ["lycées incendiés ou saccagés"], y=640, size=220)
        a = appear(t, K["c4r"] + 4.6)
        if a > 0:
            k = ease(prog(t, K["c4r"] + 4.6, 18 / FPS))
            text_tab(c, "≈ " + fmt(30000 * k), 90, 960, 120, "Bold", OCH, a)
            text(c, "élèves privés de cours en présentiel", 90, 1020, 36, "SemiBold", TXT, a)
        chip(c, "SELON LE MINISTRE DE L'ÉDUCATION · 07/10", 90, 330, t, K["c4r"] + 0.4, size=24, outline=NEU)
        tag(T4)(c, t)
        source(c, "Édouard Geffray, ministre de l'Éducation (CNEWS) — 07/10/2026", t, K["c4r"])
    add(K["c4q"], K["c4s"], s_lycees, tin="fade")

    def s_two(c, t):
        a = appear(t, K["c4s"])
        line(c, 540, 400, 540, 400 + 700 * ease(prog(t, K["c4s"], 0.8)), NEU, 0.7 * a, 2)
        text(c, "Blessés,", 300, 640, 52, "Bold", TXT, a, align="center", display=True)
        text(c, "interpellations", 300, 700, 52, "Bold", TXT, a, align="center", display=True)
        text(c, "Dégradations", 780, 670, 52, "Bold", OCH, a, align="center", display=True)
        a2 = appear(t, K["c4t"])
        text(c, "Aucune n'efface l'autre.", 540, 1050, 48, "SemiBold", TXT, a2, align="center")
        tag(T4)(c, t)
    add(K["c4s"], card["ch5"], s_two, tin="fade", tout="dip")

    # ================================================================== CHAPITRE 5
    T5 = "5 · COMBIEN ÇA COÛTE ?"

    def s_card5(c, t):
        ch.chapter_card(c, t, card["ch5"] + 0.1, "5", "Combien ça coûte ?")
    add(card["ch5"], K["c5a"] + 0.8, s_card5, tin="dip")

    def s_costmap(c, t):
        G = ch.geo(); fit = G.fit_france(540, 720, 900)
        a1 = appear(t, K["c5a"] + 0.9); a2 = appear(t, K["c5b"] + 0.8)
        ch.france_map(c, t, appear(t, K["c5a"] + 0.8), fit, hl={"Île-de-France": (ACC, 0.7 * a1), "Auvergne-Rhône-Alpes": (OCH, 0.55 * a2)})
        x, y = G.pt(2.5, 48.75, fit)
        line(c, x, y, x + 120, 330, TXT, 0.8 * a1, 2)
        text(c, "8,5 M€", x + 130, 330, 64, "Bold", TXT, a1, display=True)
        text(c, "Île-de-France · région, 13/10", x + 130, 372, 26, "Medium", NEU, a1)
        x2, y2 = G.pt(4.8, 45.5, fit)
        line(c, x2, y2, 300, 1100, TXT, 0.8 * a2, 2)
        text(c, "25 à 30 M€", 90, 1160, 64, "Bold", OCH, a2, display=True)
        text(c, "Auvergne-Rhône-Alpes · président de région", 90, 1200, 26, "Medium", NEU, a2)
        tag(T5)(c, t)
        source(c, "Région Île-de-France ; président de la région AURA (Le Figaro)", t, K["c5a"] + 0.8, y=1245)
    add(K["c5a"] + 0.8, K["c5c"], s_costmap, tin="fade")

    def s_sum(c, t):
        a = appear(t, K["c5c"])
        base = 1100; sc = 16
        k = ease(prog(t, K["c5c"] + 0.3, 0.8))
        c.drawRect(skia.Rect.MakeXYWH(150, base - 30 * sc * k, 280, 30 * sc * k), paint(NEU, 0.7 * a))
        text(c, "30 M€ ?", 290, base - 30 * sc * k - 30, 60, "Bold", TXT, a, align="center", display=True)
        text(c, "chiffre national", 290, base + 50, 30, "SemiBold", TXT, a, align="center")
        text(c, "qui circule", 290, base + 88, 26, "Medium", NEU, a, align="center")
        a2 = appear(t, K["c5d"])
        k2 = ease(prog(t, K["c5d"] + 0.2, 1.0))
        h1 = 8.5 * sc * k2; h2 = 25 * sc * k2; h3 = 5 * sc * k2
        x = 600
        c.drawRect(skia.Rect.MakeXYWH(x, base - h1, 280, h1), paint(ACC, 0.8 * a2))
        c.drawRect(skia.Rect.MakeXYWH(x, base - h1 - h2, 280, h2), paint(OCH, 0.75 * a2))
        p = paint(OCH, 0.8 * a2, stroke=2); p.setPathEffect(skia.DashPathEffect.Make([8, 8], 0))
        c.drawRect(skia.Rect.MakeXYWH(x, base - h1 - h2 - h3, 280, h3), p)
        text(c, "IDF + AURA", x + 140, base + 50, 30, "SemiBold", TXT, a2, align="center")
        text(c, "33,5 à 38,5 M€", x + 140, base - h1 - h2 - h3 - 30, 50, "Bold", TXT, a2, align="center", display=True)
        sk = ease(prog(t, K["c5d"] + 2.0, 0.5))
        if sk > 0:
            line(c, 130, base - 30 * sc - 10, 130 + 320 * sk, base - 30 * sc + 60 * sk - 10, TXT, a, 6)
        line(c, 100, base, 980, base, NEU, 0.6 * a, 2)
        tag(T5)(c, t)
        source(c, "CNEWS — 10/10/2026 ; régions", t, K["c5c"])
    add(K["c5c"], K["c5e"] - 0.4, s_sum, tin="fade")

    def s_nocost(c, t):
        a = appear(t, K["c5e"] - 0.3)
        para(c, "Aucun coût total fiable n'est actuellement disponible.", 90, 760, 84, 900, "Bold", TXT, a, lh=1.12, display=True)
        tag(T5)(c, t)
    add(K["c5e"] - 0.4, K["c5f"], s_nocost, nosub=True, tin="cut")

    def s_3000(c, t):
        ch.big_number(c, t, K["c5f"] + 2.6, 3000, ["professeurs remplaçants"], y=700, size=220)
        a = appear(t, K["c5f"] + 5.0)
        text(c, "« plusieurs dizaines de millions d'euros »", 90, 900, 38, "SemiBold", OCH, a)
        text(c, "cette année", 90, 948, 32, "Medium", NEU, a)
        chip(c, "PREMIÈRE RÉPONSE DU GOUVERNEMENT · 08/10", 90, 380, t, K["c5f"] + 0.5, size=24, outline=NEU)
        tag(T5)(c, t)
        source(c, "Édouard Geffray, TF1 — 08/10/2026 (franceinfo)", t, K["c5f"] + 3.6)
    add(K["c5f"], card["ch6"], s_3000, tin="fade", tout="dip")

    # ================================================================== CHAPITRE 6
    T6 = "6 · EST-CE QUE L'ÉTAT BOUGE ?"

    def s_card6(c, t):
        ch.chapter_card(c, t, card["ch6"] + 0.1, "6", "Est-ce que l'État bouge ?")
    add(card["ch6"], K["c6a"] + 1.2, s_card6, tin="dip")

    def s_diagram(c, t):
        boxes = ["MOBILISATION", "VISIBILITÉ", "OPINION", "PRESSION SOCIALE", "PRESSION POLITIQUE", "NÉGOCIATION", "CONCESSION"]
        t0 = K["c6a"] + 1.3
        y0 = 300; gh = 126
        for i, b in enumerate(boxes):
            ts = t0 + i * 0.45
            a = appear(t, ts)
            y = y0 + i * gh
            dim = 1.0 if i < 5 else 0.75
            rrect(c, 90, y, 470, 84, 8, "#1C2130", a)
            rrect(c, 90, y, 470, 84, 8, TXT if i < 5 else NEU, 0.45 * a, stroke=2)
            text(c, b, 325, y + 54, 30, "Bold", TXT if i < 5 else NEU, a * dim, align="center", track=0.05)
            if i < len(boxes) - 1:
                aa = appear(t, ts + 0.3)
                if i == 4:
                    br = ease(prog(t, t0 + 4.2, 0.5))
                    p = paint(OCH, aa, stroke=3); p.setPathEffect(skia.DashPathEffect.Make([6, 8], 0))
                    c.drawLine(325, y + 88, 325 - 0 * br, y + gh - 4, p)
                    text(c, "pas automatique", 360, y + gh - 10, 24, "SemiBold", OCH, appear(t, t0 + 4.4))
                else:
                    line(c, 325, y + 88, 325, y + gh - 6, TXT, 0.6 * aa, 2)
        qs = [("Durée ?", K["c6c"]), ("Secteurs en grève ?", K["c6d"]), ("Coût économique ?", K["c6e"]), ("Opinion ?", K["c6f"] + 0.4)]
        for i, (q, ts) in enumerate(qs):
            a = appear(t, ts)
            col = ACC if i == 3 else TXT
            k = ease(prog(t, ts, IN))
            text(c, q, 620 + 20 * (1 - k), 420 + i * 150, 36, "SemiBold", col, a)
        tag(T6)(c, t)
    add(K["c6a"] + 1.2, K["c6g"], s_diagram, tin="fade")

    def s_polls(c, t):
        a = appear(t, K["c6g"])
        x0, x1 = 120, 960; y_s, y_a = 620, 960
        def X(v): return x0 + (x1 - x0) * (v - 45) / 15
        for v in (45, 50, 55, 60):
            line(c, X(v), 470, X(v), 1080, NEU, (0.6 if v == 50 else 0.2) * a, 2 if v == 50 else 1, dash=None if v == 50 else [6, 8])
            text(c, f"{v} %", X(v), 1120, 26, "Medium", NEU, a, align="center")
        text(c, "Sondages · 1er-12 oct.", 90, 380, 44, "Bold", TXT, a, display=True)
        a1 = appear(t, K["c6h"])
        text(c, "Soutiennent ou approuvent", 120, y_s - 70, 34, "SemiBold", TXT, a1)
        for (v, n, ts) in ((54, "Ipsos-BVA", K["c6h"] + 0.8), (57, "Cluster17", K["c6h"] + 1.4)):
            aa = appear(t, ts)
            c.drawCircle(X(v), y_s, 18, paint(TXT, aa))
            text(c, f"{v} %", X(v), y_s + 62, 34, "Bold", TXT, aa, align="center")
            text(c, n, X(v), y_s - 34, 22, "Medium", NEU, aa, align="center")
        if a1 > 0:
            line(c, X(54), y_s, X(57), y_s, TXT, 0.6 * a1, 6)
        a2 = appear(t, K["c6i"])
        text(c, "Veulent que ça s'arrête", 120, y_a - 70, 34, "SemiBold", OCH, a2)
        for (v, n, ts) in ((53, "Cluster17", K["c6i"] + 3.0), (55, "Elabe", K["c6i"] + 5.3)):
            aa = appear(t, ts)
            c.drawCircle(X(v), y_a, 18, paint(OCH, aa))
            text(c, f"{v} %", X(v), y_a + 62, 34, "Bold", OCH, aa, align="center")
            text(c, n, X(v), y_a - 34, 22, "Medium", NEU, aa, align="center")
        a3 = appear(t, K["c6j"])
        if a3 > 0:
            rrect(c, 90, 1150, 900, 80, 6, "#000000", 0.55 * a3)
            text(c, "Soutien aux causes · lassitude face aux blocages", 120, 1202, 32, "SemiBold", TXT, appear(t, K["c6k"]))
        tag(T6)(c, t)
        source(c, "Cluster17/L'Opinion 7-9/10 ; Ipsos-BVA/CESI ; Elabe/BFMTV 07/10", t, K["c6g"], y=1262)
    add(K["c6g"], K["c6l"], s_polls, tin="fade")

    hist = [("1968", "Mai 68", "PARTIEL", "grève générale", K["c6p"]),
            ("2006", "CPE", "RETRAIT", "front uni + opinion", K["c6m"]),
            ("2010", "Retraites", "ADOPTÉE", "loi maintenue", K["c6n"]),
            ("2018", "Gilets jaunes", "PARTIEL", "vitesse, opinion", K["c6o"]),
            ("2023", "Retraites", "ADOPTÉE", "49.3", K["c6n"] + 2.0),
            ("2025", "Retraites", "SUSPENDUE", "menace de censure", K["c6q"])]
    BADGE = {"RETRAIT": GOOD, "PARTIEL": OCH, "ADOPTÉE": NEU, "SUSPENDUE": OCH}

    def s_frieze(c, t):
        t0 = K["c6l"]
        # défilement vertical lent ; la carte évoquée s'éclaire
        order = sorted(range(len(hist)), key=lambda i: hist[i][4])
        cur = max([i for i in range(len(hist)) if t >= hist[i][4] - 0.2] or [None], key=lambda i: hist[i][4] if i is not None else -1) if any(t >= h[4] - 0.2 for h in hist) else None
        scroll = min(120, 6 * (t - t0))
        line(c, 150, 330 - scroll * 0.3, 150, 1240, NEU, 0.6, 2)
        for i, (yr, name, res, why, ts) in enumerate(hist):
            a = appear(t, t0 + 0.15 * i)
            y = 360 + i * 148 - scroll * 0.3
            on = (cur == i)
            c.drawCircle(150, y + 40, 12 if on else 9, paint(ACC if on else TXT, a))
            text(c, yr, 190, y + 54, 50, "Bold", ACC if on else TXT, a * (1 if on else 0.75), display=True)
            text(c, name, 345, y + 40, 32, "SemiBold", TXT, a * (1 if on else 0.6))
            text(c, why, 345, y + 78, 26, "Medium", NEU, a * (1 if on else 0.6))
            bw = text_w(res, 22, "Bold", track=0.1) + 28
            rrect(c, 950 - bw, y + 14, bw, 42, 21, BADGE[res], (0.9 if on else 0.45) * a)
            text(c, res, 950 - bw / 2, y + 43, 22, "Bold", BG, a, align="center", track=0.1)
        tag(T6)(c, t)
        source(c, "vie-publique.fr ; Le Monde ; INA", t, t0)
    add(K["c6l"], K["c6r"], s_frieze, tin="fade")

    def s_lesson(c, t):
        a = appear(t, K["c6r"])
        illus.hemicycle(c, t, 540, 1210, 0.35 * a)
        text(c, "Assemblée nationale (schéma)", 540, 1250, 22, "Medium", NEU, 0.8 * a, align="center")
        text(c, "Manifester ne garantit rien.", 90, 420, 52, "Bold", TXT, a, display=True)
        a2 = appear(t, K["c6s"])
        l1 = "Ce qui fait bouger : quand ne rien"; l2 = "faire coûte plus cher que céder."
        x = 90
        w = text_w("coûte plus cher que céder.", 52, "Bold", True)
        xo = 90 + text_w("faire ", 52, "Bold", True)
        highlight(c, xo, 640, w, 52, t, K["c6s"] + 2.2)
        text(c, l1, 90, 560, 52, "Bold", TXT, a2, display=True)
        text(c, l2, 90, 640, 52, "Bold", TXT, a2, display=True)
        tag(T6)(c, t)
    add(K["c6r"], card["d17"], s_lesson, tin="fade", cam=("spi", 0.03), tout="dip")

    # ================================================================== 17 OCTOBRE
    T7 = "LE 17 OCTOBRE"

    def s_card7(c, t):
        ch.chapter_card(c, t, card["d17"] + 0.1, "", "Le 17 octobre", sub="Confirmé · prévu · incertain")
    add(card["d17"], K["d7a"] + 0.3, s_card7, tin="dip")

    def s_paris(c, t):
        a = appear(t, K["d7a"] + 0.3)
        m = ch.paris_map(c, t, a, cy=860, scale=6200, markers=[("B", *ch.BASTILLE), ("R", *ch.REPUBLIQUE)])
        chip(c, "SAM. 17 OCT.", 90, 300, t, K["d7a"] + 0.3, size=34, fill=ACC)
        slide_text(c, "1er jour des vacances de la Toussaint", 90, 420, 34, t, K["d7b"], color=NEU)
        (bx, by), (rx, ry) = m["B"], m["R"]
        ab = appear(t, K["d7a"] + 1.2)
        ch.city_dot(c, bx, by, ab, "Bastille", pulse_t=t, lsize=28)
        ch.city_dot(c, rx, ry, ab, "République", side="left", pulse_t=t + 0.5, lsize=28)
        tag(T7)(c, t)
    add(K["d7a"] + 0.3, K["d7c"], s_paris, tin="fade", cam=("spi", 0.03))

    def s_three(c, t):
        cols = [("CONFIRMÉ", TXT, "fill", K["d7c"], ["CGT présente « partout où", "les conditions sont réunies »"]),
                ("PRÉVU", OCH, "outline", K["d7d"], ["Annoncé par les appelants :", "Paris, 14 h, Bastille", "ou République"]),
                ("INCERTAIN", NEU, "grey", K["d7e"], ["Aucune manifestation déclarée", "en préfecture (13/10 au soir)", "Pas d'appel lycéen formel",
                                                     "Grève des navigants suspendue"])]
        y = 330
        for i, (name, col, style, ts, lines) in enumerate(cols):
            a = appear(t, ts)
            if a <= 0:
                y += 70 + 50 * len(lines) + 60
                continue
            h = 70 + 46 * len(lines) + 20
            if style == "fill":
                rrect(c, 90, y, 900, h, 8, "#1F2633", a)
            elif style == "outline":
                rrect(c, 90, y, 900, h, 8, OCH, a, stroke=3)
            else:
                rrect(c, 90, y, 900, h, 8, "#202227", a)
            text(c, name, 120, y + 50, 30, "Bold", col, a, track=0.1)
            if name == "INCERTAIN":
                text(c, "estimation impossible", 960, y + 50, 22, "Medium", NEU, a, align="right")
            for j, l in enumerate(lines):
                tj = ts + (0 if name != "INCERTAIN" else [0, 0, K["d7f"] - ts, K["d7g"] - ts][j])
                text(c, l, 120, y + 100 + j * 46, 34, "SemiBold" if style != "grey" else "Medium", TXT if style != "grey" else "#C9CCD2", appear(t, tj))
            y += h + 30
        tag(T7)(c, t)
        source(c, "L'Humanité (13/10) ; Public Sénat ; Sud Radio ; Sortiraparis ; Aladom", t, K["d7c"], y=1262)
    add(K["d7c"], K["d7h"], s_three, tin="fade")

    def s_cal(c, t):
        items = [("17 OCT.", "Rassemblements annoncés — affluence imprévisible", K["d7h"] + 0.2),
                 ("FIN OCT.", "Décisions du gouvernement (Matignon)", K["d7i"] + 2.6),
                 ("5 NOV.", "Journée interprofessionnelle des syndicats", K["d7i"] + 5.2)]
        ch.timeline_v(c, t, items, y0=470, gap=250)
        tag(T7)(c, t)
        source(c, "Matignon (allocution du 07/10) ; intersyndicale", t, K["d7i"] + 2.6)
    add(K["d7h"], card["cond"], s_cal, tin="fade", tout="dip")

    # ================================================================== QUE FAUDRAIT-IL ?
    T8 = "QUE FAUDRAIT-IL ?"

    def s_card8(c, t):
        ch.chapter_card(c, t, card["cond"] + 0.1, "", "Que faudrait-il pour que l'État bouge ?")
    add(card["cond"], K["q1"] + 2.0, s_card8, tin="dip")

    def s_check(c, t):
        conds = [("Une mobilisation large, qui dure", "q2"), ("Des revendications précises, chiffrables", "q3"),
                 ("Le soutien de l'opinion", "q4"), ("Des grèves dans plusieurs secteurs", "q5"),
                 ("Des syndicats unis", "q6"), ("Des relais au Parlement", "q7")]
        text(c, "Ce que les mouvements gagnants cumulent", 90, 380, 38, "SemiBold", NEU, appear(t, K["q1"] + 2.0))
        for i, (s, k) in enumerate(conds):
            ts = K[k]
            a = appear(t, ts)
            y = 500 + i * 120
            rrect(c, 90, y - 40, 52, 52, 8, TXT, 0.7 * a, stroke=2.5)
            ck = ease(prog(t, ts + 0.2, 0.3))
            if ck > 0:
                p = skia.Path(); p.moveTo(102, y - 14); p.lineTo(114, y); p.lineTo(132 if ck > 0.5 else 114 + 36 * (ck - 0.5) * 2 * 0.5, y - 28 if ck > 0.5 else y - 28 * (ck - 0.5) * 2)
                c.drawPath(p, paint(ACC, a, stroke=5))
            text(c, s, 170, y, 42, "SemiBold", TXT, a)
        tag(T8)(c, t)
        source(c, "Analyse historique (section G du dossier)", t, K["q1"] + 2.0)
    add(K["q1"] + 2.0, K["q8"], s_check, tin="fade")

    def s_violence(c, t):
        a = appear(t, K["q8"])
        text(c, "VIOLENCE", 90, 520, 110, "Bold", TXT, a, display=True)
        text(c, "≠ EFFICACITÉ", 90, 640, 110, "Bold", OCH, appear(t, K["q8"] + 0.6), display=True)
        text(c, "POLITIQUE", 90, 760, 110, "Bold", OCH, appear(t, K["q8"] + 0.8), display=True)
        effs = [("Baisse du soutien du public", K["q9"] + 0.6), ("Revendications éclipsées", K["q9"] + 2.6),
                ("Ligne sécuritaire renforcée", K["q9"] + 4.6), ("Manifestants divisés", K["q9"] + 7.0)]
        ch.stack_list(c, t, effs, y=900, gap=76, size=38, bullet=OCH)
        tag(T8)(c, t)
    add(K["q8"], K["q10"], s_violence, tin="fade")

    def s_ifop(c, t):
        a = appear(t, K["q10"])
        text(c, "Responsables des débordements ?", 90, 390, 44, "Bold", TXT, a, display=True)
        for i, (lab, ts) in enumerate((("« certains lycéens »", K["q10"] + 1.4), ("le gouvernement", K["q11"] + 0.2))):
            aa = appear(t, ts)
            k = ease(prog(t, ts, 0.9))
            y = 560 + i * 280
            c.drawRect(skia.Rect.MakeXYWH(90, y, 900 * 0.78 * k, 110), paint(TXT if i == 0 else OCH, 0.85 * aa))
            c.drawRect(skia.Rect.MakeXYWH(90, y, 900, 110), paint(NEU, 0.4 * aa, stroke=1.5))
            text_tab(c, f"{int(round(78 * k))} %", 110, y + 80, 64, "Bold", BG, aa)
            text(c, lab, 90, y + 160, 36, "SemiBold", TXT, aa)
        text(c, "Les deux réponses n'étaient pas exclusives", 90, 1150, 28, "Medium", NEU, appear(t, K["q11"] + 1.0))
        tag(T8)(c, t)
        source(c, "Ifop pour LCI — terrain 6-7/10/2026", t, K["q10"])
    add(K["q10"], card["concl"], s_ifop, tin="fade", tout="dip")

    # ================================================================== CONCLUSION
    def s_trip(c, t):
        panels = [(illus.street, K["k1"]), (lambda cc, tt: illus.school_gate(cc, tt, bins=True), K["k2"]), (illus.platform, K["k3"])]
        for i, (fn, ts) in enumerate(panels):
            a = appear(t, ts - 0.2)
            if a <= 0: continue
            y0 = 300 + i * 320
            c.save()
            c.clipRect(skia.Rect.MakeXYWH(90, y0, 900, 290))
            c.saveLayerAlpha(None, int(255 * a))
            s = 1 + 0.04 * prog(t, ts, 10)
            c.translate(540, y0 + 145); c.scale(0.55 * s, 0.55 * s); c.translate(-540, -(760 if i != 1 else 1150))
            fn(c, t)
            c.restore(); c.restore()
            rrect(c, 90, y0, 900, 290, 4, TXT, 0.25 * a, stroke=1.5)
            lab = ["une rue", "une journée", "une économie"][i]
            verb = ["remplir", "perturber", "ralentir"][i]
            rrect(c, 110, y0 + 210, text_w(verb + " " + lab, 30, "SemiBold") + 30, 52, 4, "#000000", 0.6 * a)
            text(c, verb + " " + lab, 125, y0 + 247, 30, "SemiBold", TXT, a)
        badge(c)
        a4 = appear(t, K["k4"])
        text(c, "Aucun ne garantit, seul, une victoire politique.", 90, 1290 - 40, 30, "SemiBold", OCH, a4)
    add(card["concl"], K["k5"], s_trip, tin="dip")

    def s_keys(c, t):
        ws = [("DURER", K["k5"] + 2.5), ("GARDER L'OPINION", K["k5"] + 4.4), ("CRÉER UN COÛT POLITIQUE", K["k5"] + 6.8)]
        for i, (w, ts) in enumerate(ws):
            text(c, w, 90, 470 + i * 120, 72 if i < 2 else 64, "Bold", TXT, appear(t, ts), display=True)
        a = appear(t, K["k5"] + 9.6)
        text(c, "→ négocier plutôt qu'ignorer", 90, 900, 46, "SemiBold", ACC, a)
    add(K["k5"], K["k6"], s_keys, tin="fade")

    def s_bastille(c, t):
        a = appear(t, K["k6"])
        m = ch.paris_map(c, t, a * 0.8, cy=860, scale=6200, markers=[("B", *ch.BASTILLE)])
        bx, by = m["B"]
        ch.city_dot(c, bx, by, a, "Bastille · 17 oct.", pulse_t=t, lsize=28)
        aa = appear(t, K["k6"] + 3.6)
        text(c, "un test du", 90, 380, 44, "SemiBold", NEU, aa)
        text(c, "rapport de force", 90, 450, 64, "Bold", TXT, aa, display=True)
    add(K["k6"], K["k7"] - 0.5, s_bastille, tin="fade", cam=("spi", 0.04, (540, 820)))

    def s_final(c, t):
        a1 = appear(t, K["k7"], K["k8"] - 0.2, d_in=0.8, d_out=0.5)
        text(c, "Combien seront-ils ?", 540, 800, 60, "SemiBold", NEU, a1, align="center")
        a2 = appear(t, K["k8"], None, d_in=0.8)
        para(c, "Combien de temps le pouvoir pourra-t-il se permettre de ne pas répondre ?", 540, 720, 66, 880, "Bold", TXT, a2,
             lh=1.18, align="center", display=True)
    add(K["k7"] - 0.5, E["k8"] + 3.0, s_final, tin="fade", tout="black", nosub=True)

    def s_sources(c, t):
        t0 = E["k8"] + 3.0
        a = appear(t, t0 + 0.3)
        text(c, "SOURCES", 90, 330, 60, "Bold", TXT, a, display=True, track=0.06)
        text(c, "Pages consultées le 14 octobre 2026", 90, 380, 26, "Medium", NEU, a)
        src = ["Ministère de l'Intérieur — 06, 08, 13/10/2026", "Ministère de l'Éducation nationale — 13/10 (France 24)",
               "Ministère de la Justice — bilan au 08/10 (franceinfo)", "Matignon — allocution du 07/10 (24 heures / AFP)",
               "Région Île-de-France — 13/10 ; SNES-FSU — 27/01/2026", "France 24 · Europe 1 · Euronews · franceinfo",
               "ICI (ex-France Bleu) · CNEWS · Le JDD / Le Figaro", "France 3 Occitanie · Sud Radio · Sortiraparis",
               "L'Humanité (Titres Presse) · La Libre Belgique", "Public Sénat · Aladom · 17octobregiletjaune.net (appelants)",
               "Sondages : Cluster17/L'Opinion · Elabe/BFMTV", "Ifop/LCI · Ipsos-BVA/CESI · Odoxa/Le Figaro",
               "Amnesty International France · synthèse Wikipédia", "Historique : INA · vie-publique.fr · Le Monde", "",
               "Illustrations et schémas : réalisés pour ce film,", "signalés à l'écran — aucune image d'archive reconstituée.",
               "Voix de synthèse (Piper « tom ») · musique originale."]
        scroll = max(0, t - t0 - 4) * 14
        c.save(); c.clipRect(skia.Rect.MakeXYWH(0, 420, W, 1060))
        for i, s in enumerate(src):
            y = 480 + i * 52 - scroll
            text(c, s, 90, y, 28, "Medium", TXT if i < 14 else NEU, appear(t, t0 + 0.6 + i * 0.08))
        c.restore()
    add(E["k8"] + 3.0, total, s_sources, nosub=True, tin="fade")

    # recouvrements pour les fondus enchaînés
    shots.sort(key=lambda s: s.t0)
    for i in range(len(shots) - 1):
        if shots[i + 1].tin == "fade":
            shots[i].t1 = max(shots[i].t1, shots[i + 1].t0 + 0.5)
    return shots
