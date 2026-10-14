# -*- coding: utf-8 -*-
"""Construit la timeline réelle à partir des voix générées :
- position de chaque phrase (respect des fenêtres du storyboard + pauses du script)
- piste voix complète
- sous-titres recalés sur la voix (pages de 1 à 2 lignes, coupures aux pauses détectées)
- export SRT final

Usage : python3 timeline.py long|tiktok
"""
import json, os, re, sys
import numpy as np
import soundfile as sf

sys.path.insert(0, os.path.dirname(__file__))
from script_data import LONG, TIKTOK

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SR = 48000
NBSP = " "

# Délais avant la voix pour chaque section (cartons de chapitre, respirations)
LEAD_LONG = {"intro": None, "ch1": 5.0, "ch2": 2.4, "ch3": 2.4, "ch4": 4.0, "ch5": 2.2,
             "ch6": 2.4, "d17": 2.0, "cond": 2.4, "concl": 2.2}


def typo(text):
    """Typographie française : espaces insécables avant : ; ? ! % » et après «, et dans les nombres."""
    t = text
    t = re.sub(r"(\d) (\d{3})\b", lambda m: m.group(1) + NBSP + m.group(2), t)
    t = re.sub(r"\s+([:;?!%»])", NBSP + r"\1", t)
    t = re.sub(r"«\s+", "«" + NBSP, t)
    t = re.sub(r"(\d+) (euros|millions|milliards|ans|heures|octobre|novembre|septembre|lycées|enquêtes|policiers|élèves|personnes|manifestants|professeurs|gardes|remplaçants)",
               lambda m: m.group(1) + NBSP + m.group(2), t)
    t = t.replace("Le 8,", "Le" + NBSP + "8,")
    return t


def find_gaps(y, min_gap=0.11, thr_db=-38):
    """Silences internes (début, fin) en secondes."""
    win = int(0.01 * SR)
    env = np.sqrt(np.convolve(y.astype(np.float64) ** 2, np.ones(win) / win, mode="same"))
    thr = 10 ** (thr_db / 20) * env.max()
    quiet = env < thr
    gaps = []
    i = 0; n = len(quiet)
    while i < n:
        if quiet[i]:
            j = i
            while j < n and quiet[j]: j += 1
            if (j - i) / SR >= min_gap and i > 0 and j < n:
                gaps.append((i / SR, j / SR))
            i = j
        else:
            i += 1
    return gaps


def build(version):
    script = LONG if version == "long" else TIKTOK
    man = {m["key"]: m for m in json.load(open(os.path.join(ROOT, "assets/voice", version, "manifest.json")))}
    items = []
    t = 0.0
    sections = []
    for sec in script:
        if version == "long":
            if sec["id"] == "intro":
                t = sec["start"]
            else:
                t = t + LEAD_LONG[sec["id"]]
        else:
            t = sec["start"]
        sstart = t
        for (k, text, pause, style) in sec["items"]:
            m = man[k]
            items.append(dict(key=k, section=sec["id"], text=typo(text), start=round(t, 3), end=round(t + m["dur"], 3),
                              dur=m["dur"], file=m["file"], style=style, pause=pause))
            t = t + m["dur"] + pause
        sections.append(dict(id=sec["id"], start=sstart, vo_start=sstart, end=t))
        if version == "long" and sec["id"] == "intro":
            # titre « FRANCE — LE RAPPORT DE FORCE » (00:36-00:45)
            sections.append(dict(id="title", start=t + 0.9, vo_start=t + 0.9, end=t + 0.9 + 8.4))
            t = t + 0.9 + 8.4
    total_vo_end = items[-1]["end"]
    return items, sections, total_vo_end


def voice_track(items, length):
    y = np.zeros(int(length * SR) + SR, dtype=np.float32)
    for it in items:
        a, sr = sf.read(os.path.join(ROOT, it["file"]), dtype="float32")
        p = int(it["start"] * SR)
        y[p:p + len(a)] += a
    return y[: int(length * SR)]


# ------------------------------------------------------------ pages de sous-titres
def tokens(text):
    # les citations courtes (« en recul ») ne sont jamais coupées
    text = re.sub(r"«\u00a0([^»]{1,22})\u00a0»", lambda m: "«\u00a0" + m.group(1).replace(" ", "\u00a0") + "\u00a0»", text)
    return [w for w in text.split(" ") if w]


def measure_factory():
    os.environ.setdefault("LD_LIBRARY_PATH", "/opt/egl")
    import skia
    tf = skia.Typeface.MakeFromFile("/usr/share/fonts/opentype/inter/Inter-SemiBold.otf")
    font = skia.Font(tf, 54)
    return lambda s: font.measureText(s)


def wrap(words, measure, maxw):
    lines = []; cur = []
    for w in words:
        trial = " ".join(cur + [w])
        if cur and measure(trial) > maxw:
            lines.append(cur); cur = [w]
        else:
            cur.append(w)
    if cur: lines.append(cur)
    return lines


FUNC = set("de des du la le les un une à et en d'un au aux ou par pour sur ni se ne que qui qu'il s'y y son sa ses leur leurs ce cette dans avec contre l'interdiction".split())


def bad_end(w):
    wl = w.lower()
    return wl in FUNC or wl.endswith("'")


def balance2(words, measure, maxw):
    """1 ligne si possible, sinon 2 lignes équilibrées (coupure de préférence après ponctuation)."""
    if measure(" ".join(words)) <= maxw:
        return [" ".join(words)]
    best = None
    for i in range(1, len(words)):
        a = " ".join(words[:i]); b = " ".join(words[i:])
        wa, wb = measure(a), measure(b)
        if wa > maxw or wb > maxw: continue
        cost = abs(wa - wb) * 0.6
        if wb > wa: cost *= 0.7   # pyramide inversée légère acceptée
        if words[i - 1][-1] in ",:;": cost -= 220
        if bad_end(words[i - 1]): cost += 400
        if best is None or cost < best[0]:
            best = (cost, [a, b])
    return best[1] if best else None


def pages_for(text, measure, maxw=850):
    """Découpage optimal (programmation dynamique) d'une phrase en pages de 1-2 lignes."""
    words = tokens(text)
    n = len(words)
    INF = 1e18
    best = [INF] * (n + 1); prev = [-1] * (n + 1); best[0] = 0
    for j in range(1, n + 1):
        for i in range(max(0, j - 16), j):
            seg = words[i:j]
            if not balance2(seg, measure, maxw):
                continue
            chars = len(" ".join(seg))
            c = 1000  # coût fixe par page : minimise le nombre de pages
            if chars < 19 and n > 3: c += 1600
            if j < n:
                if seg[-1][-1] in ",:;…": c -= 500
                elif seg[-1][-1] not in ".?!": c += 650
                if bad_end(seg[-1]): c += 1500
            c += abs(chars - 44) * 6
            if best[i] + c < best[j]:
                best[j] = best[i] + c; prev[j] = i
    pages = []; j = n
    while j > 0:
        i = prev[j]; pages.append(words[i:j]); j = i
    return pages[::-1]


def highlight_word(lines):
    for li, l in enumerate(lines):
        for wi, w in enumerate(l.split(" ")):
            if re.search(r"\d", w):
                return w
    return None


def subtitles(items, measure):
    subs = []
    for it in items:
        y, _ = sf.read(os.path.join(ROOT, it["file"]), dtype="float32")
        gaps = find_gaps(y)
        pages = pages_for(it["text"], measure)
        from voice import normalize
        plen = [len(normalize(" ".join(p).replace("\u00a0", " "))) for p in pages]
        total_chars = sum(plen)
        bounds = [0.0]
        acc = 0
        for pi, p in enumerate(pages[:-1]):
            acc += plen[pi]
            # estimation sur le reste de la phrase, à partir de la dernière coupure retenue
            rest = sum(plen[pi:])
            est = bounds[-1] + (it["dur"] - bounds[-1]) * plen[pi] / max(1, rest)
            # cale la coupure sur le silence le plus proche
            best = None
            for (g0, g1) in gaps:
                c = (g0 + g1) / 2
                if abs(c - est) < 0.9 and (best is None or abs(c - est) < abs(best - est)):
                    best = c
            b = best if best is not None else est
            if b <= bounds[-1] + 0.6:   # deux coupures sur la même pause : on garde l'estimation
                b = max(est, bounds[-1] + 0.8)
            bounds.append(min(b, it["dur"] - 0.5))
        bounds.append(it["dur"])
        for i, p in enumerate(pages):
            a = it["start"] + bounds[i]; b = it["start"] + bounds[i + 1]
            lines = balance2(p, measure, 850) or wrap(p, measure, 850)
            if isinstance(lines[0], list): lines = [" ".join(x) for x in lines]
            subs.append(dict(start=a, end=b, lines=lines, key=it["key"], hl=highlight_word(lines)))
    # règles : 80 ms d'écart, durée mini 0,8 s, prolongation pendant les pauses courtes
    for i, s in enumerate(subs):
        nxt = subs[i + 1]["start"] if i + 1 < len(subs) else s["end"] + 1.5
        s["end"] = min(max(s["end"] + 0.25, s["start"] + 0.8), nxt - 0.08)
        s["start"] = round(s["start"], 3); s["end"] = round(s["end"], 3)
    return subs


def srt_time(x):
    h = int(x // 3600); m = int(x % 3600 // 60); s = x % 60
    return f"{h:02d}:{m:02d}:{int(s):02d},{int(round((s - int(s)) * 1000)) % 1000:03d}"


def write_srt(subs, path):
    with open(path, "w", encoding="utf-8") as f:
        for i, s in enumerate(subs, 1):
            f.write(f"{i}\n{srt_time(s['start'])} --> {srt_time(s['end'])}\n" + "\n".join(s["lines"]) + "\n\n")


def main(version):
    items, sections, vo_end = build(version)
    measure = measure_factory()
    subs = subtitles(items, measure)
    if version == "long":
        total = vo_end + 3.0 + 20.0   # fondu au noir + carton SOURCES
    else:
        total = vo_end + 3.2          # question finale tenue
    out = os.path.join(ROOT, "assets", "data", f"timeline_{version}.json")
    json.dump(dict(items=items, sections=sections, subs=subs, total=total, vo_end=vo_end), open(out, "w"), ensure_ascii=False, indent=1)
    vt = voice_track(items, total)
    sf.write(os.path.join(ROOT, "assets", "voice", f"vo_{version}.wav"), vt, SR, subtype="PCM_24")
    os.makedirs(os.path.join(ROOT, "exports", "master" if version == "long" else "tiktok"), exist_ok=True)
    srt = os.path.join(ROOT, "exports", "master" if version == "long" else "tiktok",
                       "france_rapport_de_force_MASTER.srt" if version == "long" else "france_rapport_de_force_TIKTOK.srt")
    write_srt(subs, srt)
    print(version, "durée totale", round(total, 2), "s;", len(items), "phrases;", len(subs), "sous-titres")
    for s in sections: print(f"  {s['id']:6s} {s['start']:7.2f} -> {s['end']:7.2f}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "long")
