# -*- coding: utf-8 -*-
"""Bande son complète : ambiances, SFX, musique originale, ducking, mixage, loudness -14 LUFS / TP -1 dBTP.

Hiérarchie : VOIX OFF > sons réels (ambiances) > SFX > musique.
Usage : python3 mix.py long|tiktok
"""
import json, os, sys, subprocess, math
import numpy as np
import soundfile as sf
import pyloudnorm as pyln
from scipy import signal

sys.path.insert(0, os.path.dirname(__file__))
import audio_lib as A
from audio_lib import SR

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SFX_DIR = os.path.join(ROOT, "assets", "sfx")
MUS_DIR = os.path.join(ROOT, "assets", "music")


def db(x): return 10 ** (x / 20)


# ------------------------------------------------------------------ murmures pour la foule
BABBLE_TXT = [
    "On ne lâchera rien, on sera encore là demain matin devant le lycée.", "Il faut des profs, pas des promesses, tout le monde le sait.",
    "Tu viens avec nous au rassemblement cet après-midi ou pas ?", "Regarde, il y a encore du monde qui arrive par la rue.",
    "Ils disent que les cours reprendront lundi, mais personne n'y croit.", "Attends, on se retrouve devant la grille dans dix minutes.",
    "Ça fait trois semaines que ça dure et rien ne bouge vraiment.", "Ma mère m'a dit de faire attention, elle s'inquiète beaucoup.",
    "On avance doucement, restez groupés, on suit le cortège.", "Il y a beaucoup trop d'élèves par classe cette année.",
    "Le proviseur a parlé aux délégués ce matin dans la cour.", "Ils ont annoncé une réunion avec le ministre, on verra bien.",
    "Moi je pense qu'il faut continuer, sinon on n'obtiendra rien.", "Les profs étaient en grève hier aussi, c'est pour ça.",
]


def make_babble():
    out = os.path.join(SFX_DIR, "babble"); os.makedirs(out, exist_ok=True)
    if len(os.listdir(out)) >= 40: return out
    import sherpa_onnx
    voices = [("fr_FR-siwis-medium", 0), ("fr_FR-upmc-medium", 0), ("fr_FR-upmc-medium", 1), ("fr_FR-tom-medium", 0)]
    i = 0
    for name, sid in voices:
        d = f"/tmp/tts/vits-piper-{name}"
        cfg = sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(vits=sherpa_onnx.OfflineTtsVitsModelConfig(
            model=f"{d}/{name}.onnx", tokens=f"{d}/tokens.txt", data_dir=f"{d}/espeak-ng-data"), num_threads=4))
        tts = sherpa_onnx.OfflineTts(cfg)
        for j, s in enumerate(BABBLE_TXT):
            a = tts.generate(s, sid=sid, speed=float(np.random.default_rng(i).uniform(0.9, 1.25)))
            y = signal.resample_poly(np.array(a.samples), SR, a.sample_rate)
            sf.write(os.path.join(out, f"b{i:03d}.wav"), y.astype(np.float32), SR); i += 1
    return out


class Bus:
    def __init__(self, dur):
        self.n = int(dur * SR) + SR
        self.x = np.zeros((self.n, 2), np.float32)

    def add(self, t, sig, gain_db=0.0, fi=0.0, fo=0.0, dur=None):
        if sig.ndim == 1: sig = A.stereo(sig)
        if dur is not None: sig = sig[: int(dur * SR)]
        sig = A.fade(sig, fi, fo) * db(gain_db)
        p = int(t * SR)
        if p < 0: sig = sig[-p:]; p = 0
        m = min(len(sig), self.n - p)
        if m > 0: self.x[p:p + m] += sig[:m].astype(np.float32)


def loud(x):
    meter = pyln.Meter(SR)
    return meter.integrated_loudness(x.astype(np.float64))


def norm_lufs(x, target):
    L = loud(x)
    if not np.isfinite(L): return x
    return x * db(target - L)


def music_track(plan, total, cache_key):
    """plan : liste (t0, t1, kind, gain_db). Rendu calé sur la grille de mesures (continuité harmonique)."""
    bus = Bus(total)
    for i, (t0, t1, kind, g) in enumerate(plan):
        if kind is None or t1 <= t0: continue
        bar0 = math.floor(t0 / A.BAR)
        start = bar0 * A.BAR
        fn = os.path.join(MUS_DIR, f"{cache_key}_{i:02d}_{kind}_{bar0}_{int((t1 - start) * 10)}.wav")
        if os.path.exists(fn):
            y, _ = sf.read(fn, dtype="float32")
        else:
            y = A.render_music_part(kind, t1 - start + 3.0, seed=i, offset_bars=bar0)
            sf.write(fn, y.astype(np.float32), SR)
        off = t0 - start
        seg = y[int(off * SR): int((t1 - start + 2.5) * SR)]
        fo_len = 2.5
        bus.add(t0, seg, g, fi=0.8 if i else 0.05, fo=fo_len)
    return bus.x


def duck_env(voice, depth_db=-9.0, att=0.05, rel=0.45):
    env = np.abs(voice.mean(1) if voice.ndim == 2 else voice)
    win = int(0.03 * SR)
    env = np.sqrt(np.convolve(env ** 2, np.ones(win) / win, mode="same"))
    act = (env > db(-40) * env.max()).astype(np.float64)
    # attaque / relâchement
    out = np.zeros_like(act)
    a_c = math.exp(-1 / (att * SR)); r_c = math.exp(-1 / (rel * SR))
    y = 0.0
    sig = act
    # lissage récursif (implémentation rapide via lfilter sur deux régimes)
    up = signal.lfilter([1 - a_c], [1, -a_c], sig)
    down = signal.lfilter([1 - r_c], [1, -r_c], sig)
    out = np.maximum(up, down)
    out = np.clip(out * 1.4, 0, 1)
    return db(depth_db * out)


# ------------------------------------------------------------------ plans sonores
def plan_long(TL):
    K = {it["key"]: it["start"] for it in TL["items"]}
    E = {it["key"]: it["end"] for it in TL["items"]}
    SEC = {s["id"]: s for s in TL["sections"]}
    LEAD = {"ch1": 5.0, "ch2": 2.4, "ch3": 2.4, "ch4": 4.0, "ch5": 2.2, "ch6": 2.4, "d17": 2.0, "cond": 2.4, "concl": 2.2}
    card = {k: SEC[k]["vo_start"] - v for k, v in LEAD.items()}
    T = SEC["title"]["start"]; total = TL["total"]
    music = [
        (3.2, 9.0, "nappe", -6), (6.2, 14.0, "pulse", -9), (14.0, K["i3"] - 1.0, "nappe", -6),
        (T, card["ch1"] + 3.0, "theme", 0),
        (card["ch1"] + 3.0, K["c1f"], "nappe", -3), (K["c1f"], K["c1j"], "pulse", -2), (K["c1j"], K["c1k"], "nappe", -12),
        (K["c1k"], K["c1r"], "nappe", -6), (K["c1r"], card["ch2"], "pulse", -1),
        (card["ch2"], K["c2c"] + 2, "theme", -2), (K["c2c"] + 2, K["c2h"], "nappe", -3), (K["c2h"], E["c2o"], "nappe", -10),
        (card["ch3"], K["c3f"], "pulse", -4), (K["c3f"], K["c3k"], "nappe", -4), (K["c3k"], card["ch4"], "pulse", -12),
        # chapitre 4 : silence musical, puis nappe très basse
        (K["c4g"], K["c4n"], "nappe", -14), (K["c4n"], E["c4t"] + 0.5, "nappe", -9),
        (card["ch5"], K["c5c"], "pulse", -4), (K["c5c"], K["c5e"] - 0.5, "nappe", -12),
        (K["c5f"], card["ch6"] + 1.0, "theme", -3),
        (card["ch6"], K["c6g"], "pulse", -3), (K["c6g"], K["c6l"], "nappe", -12), (K["c6l"], K["c6r"], "nappe", -4),
        (K["c6r"], card["d17"] + 0.5, "theme", -2),
        (card["d17"], K["d7c"], "pulse", -3), (K["d7c"], K["d7h"], "nappe", -10), (K["d7h"], card["cond"], "nappe", -5),
        (card["cond"], K["q8"], "nappe", -4), (K["q8"], K["q10"], "nappe", -14),
        (card["concl"], K["k6"], "theme_full", -2), (K["k6"], K["k7"] - 0.4, "nappe", -6),
        (K["k7"] - 0.4, E["k8"] + 4.0, "theme", -6),
    ]
    amb, sfx = [], []
    # ouverture
    amb += [("city", 0.0, 3.4, -20, 0.05, 0.4), ("crowd_near", 3.1, 3.3, -14, 0.1, 0.4), ("chant", 3.1, 3.3, -20, 0.2, 0.4),
            ("crowd_far", 14.0, K["i2"] - 14.0, -24, 1.0, 2.0), ("wind", K["i2"] - 0.5, K["i3"] - K["i2"], -22, 1.0, 1.0)]
    sfx += [("bins", 0.4, -10), ("whistle", 1.6, -14), ("radio", 6.4, -16), ("radio", 7.9, -20),
            ("paper", 9.05, -12), ("paper", 9.5, -14), ("paper", 9.95, -14), ("riser", T - 2.6, -18), ("impact", T + 0.2, -4)]
    # ch1
    sfx += [("click", card["ch1"] + 0.1, -16)]
    amb += [("city", K["c1a"], K["c1d"] - K["c1a"], -26, 1.0, 1.0), ("crowd_far", K["c1h"], K["c1j"] - K["c1h"], -26, 0.8, 0.6)]
    sfx += [("tick", K["c1f"] + 0.3, -18), ("tick", K["c1g"], -18), ("tick", K["c1g"] + 0.6, -20), ("tick", K["c1g"] + 1.2, -20),
            ("click", K["c1j"] + 0.6, -14), ("tick", K["c1l"], -20), ("tick", K["c1l"] + 0.35, -20), ("tick", K["c1r"] + 0.3, -20)]
    # ch2
    sfx += [("click", card["ch2"] + 0.1, -16), ("chair", K["c2c"] + 0.6, -18), ("pump", K["c2j"] + 0.6, -16)]
    amb += [("amphi", K["c2e"], K["c2f"] - K["c2e"], -26, 0.6, 0.6), ("city", K["c2h"], K["c2m"] - K["c2h"], -27, 0.8, 0.8)]
    sfx += [("tick", K["c2c"] + 2.3 + d, -22) for d in (0, 1.3, 2.9)]
    # ch3
    sfx += [("click", card["ch3"] + 0.1, -16), ("bins", K["c3a"] + 1.6, -14)]
    sfx += [("tick", K["c3e"] + i * 0.75, -20) for i in range(3)]
    sfx += [("tick", K["c3k"] + d, -18) for d in (2.6, 3.4, 4.5)]
    sfx += [("tick", K["c3j"] + 0.9 + i * 0.9, -22) for i in range(3)]
    amb += [("city", K["c3a"] + 1.4, K["c3f"] - K["c3a"] - 1.4, -27, 0.5, 0.8)]
    # ch4 : ambiance de pièce seule
    amb += [("room", card["ch4"], E["c4t"] - card["ch4"] + 1.0, -30, 1.0, 1.5),
            ("wind", K["c4q"], K["c4s"] - K["c4q"], -26, 1.0, 1.0)]
    sfx += [("glass", K["c4r"] + 0.5, -24), ("click", K["c4c"] + 2.0, -18)]
    # ch5
    sfx += [("click", card["ch5"] + 0.1, -16), ("tick", K["c5a"] + 0.9, -18), ("tick", K["c5b"] + 0.8, -18),
            ("tick", K["c5d"] + 0.2, -20), ("click", K["c5f"] + 2.6, -18)]
    # ch6
    sfx += [("click", card["ch6"] + 0.1, -16)]
    sfx += [("tick", K["c6a"] + 1.3 + i * 0.45, -22) for i in range(7)]
    sfx += [("tick", K[k], -20) for k in ("c6c", "c6d", "c6e", "c6f")]
    sfx += [("page", K[k] - 0.15, -16) for k in ("c6m", "c6n", "c6o", "c6p", "c6q")]
    # 17 oct
    sfx += [("click", card["d17"] + 0.1, -16)]
    amb += [("city", K["d7a"], K["d7c"] - K["d7a"] + 1.0, -22, 1.0, 1.5)]
    sfx += [("tick", K[k], -20) for k in ("d7c", "d7d", "d7e")]
    # conditions
    sfx += [("click", card["cond"] + 0.1, -16)] + [("tick", K[k] + 0.2, -20) for k in ("q2", "q3", "q4", "q5", "q6", "q7")]
    # conclusion : les ambiances s'éteignent une à une
    amb += [("city", K["k1"] - 0.2, K["k4"] - K["k1"] + 2, -24, 0.5, 4.0), ("crowd_far", K["k2"] - 0.2, K["k4"] - K["k2"] + 3, -28, 0.5, 4.0),
            ("metro", K["k3"] - 0.2, K["k4"] - K["k3"] + 4, -24, 0.5, 4.0), ("wind", K["k6"], K["k7"] - K["k6"], -26, 1.0, 2.0)]
    return music, amb, sfx, total


def plan_tiktok(TL):
    K = {it["key"]: it["start"] for it in TL["items"]}
    E = {it["key"]: it["end"] for it in TL["items"]}
    total = TL["total"]
    music = [(0.0, K["t7"], "pulse", -4), (K["t9"], K["t11"], "nappe", -6), (K["t11"] + 0.4, K["t16"], "pulse", -4),
             (K["t16"], K["t18"], "theme_full", -4), (K["t18"], total, "theme", -4)]
    amb = [("crowd_near", 0.0, 3.5, -16, 0.02, 0.8), ("chant", 0.0, 3.5, -22, 0.1, 0.8),
           ("room", K["t7"], K["t10"] - K["t7"], -30, 0.4, 0.6), ("city", K["t18"], total - K["t18"], -24, 0.5, 2.0)]
    sfx = [("impact", 0.02, -6), ("bins", 0.5, -16)]
    for k in ("t2", "t4", "t5", "t6", "t7", "t8", "t9", "t10", "t12", "t13", "t14", "t15", "t16", "t17"):
        sfx.append(("tick", K[k] + 0.05, -20))
    sfx += [("tick", K["t3"] + d, -22) for d in (0.0, 1.4, 2.7)]
    sfx += [("riser", K["t11"] - 1.8, -20), ("impact", K["t11"], -12), ("page", K["t14"] - 0.1, -16), ("page", K["t15"] - 0.1, -16)]
    return music, amb, sfx, total


def build(version):
    TL = json.load(open(os.path.join(ROOT, "assets", "data", f"timeline_{version}.json")))
    os.makedirs(SFX_DIR, exist_ok=True); os.makedirs(MUS_DIR, exist_ok=True)
    babble = A.load_babble([make_babble()])
    music_plan, amb_plan, sfx_plan, total = (plan_long if version == "long" else plan_tiktok)(TL)
    vo, _ = sf.read(os.path.join(ROOT, "assets", "voice", f"vo_{version}.wav"), dtype="float32")
    n = int(total * SR) + SR
    vo = np.pad(vo, (0, max(0, n - len(vo))))[:n]
    voice = A.stereo(vo.astype(np.float64)).astype(np.float32)

    # --- bibliothèque SFX (rendue une fois, exportée dans assets/sfx)
    lib = {}
    def get(name, dur=None):
        key = (name, round(dur or 0, 1))
        if key in lib: return lib[key]
        d = dur or 4
        if name == "city": y = A.city_bed(d + 2, seed=int(d * 10) % 97)
        elif name == "crowd_near": y = A.crowd_bed(d + 2, babble, 1.2, 0.2, seed=int(d * 10) % 97)
        elif name == "crowd_far": y = A.crowd_bed(d + 2, babble, 0.9, 0.85, seed=int(d * 7) % 97)
        elif name == "chant": y = A.chant_far(d + 2, babble)
        elif name == "wind": y = A.wind_bed(d + 2)
        elif name == "room": y = A.room_tone(d + 2)
        elif name == "metro": y = A.metro_bed(d + 2)
        elif name == "amphi": y = A.amphi_echo(d + 2, babble)
        elif name == "tick": y = A.stereo(A.sfx_tick())
        elif name == "click": y = A.stereo(A.sfx_click())
        elif name == "impact": y = A.sfx_impact()
        elif name == "paper": y = A.sfx_paper()
        elif name == "page": y = A.sfx_page()
        elif name == "pump": y = A.sfx_pump_beep()
        elif name == "radio": y = A.sfx_radio(2.4)
        elif name == "whistle": y = A.sfx_whistle_far()
        elif name == "bins": y = A.bins_sfx()
        elif name == "glass": y = A.glass_tinkle()
        elif name == "chair": y = A.chair_creak()
        elif name == "riser": y = A.riser(2.6)
        elif name == "siren": y = A.sfx_siren_far()
        else: raise KeyError(name)
        y = np.asarray(y, np.float32)
        if y.ndim == 1: y = A.stereo(y)
        # niveau de référence : crête -6 dBFS pour les SFX, RMS cohérente pour les ambiances
        y = y / (np.abs(y).max() + 1e-9) * 0.5
        lib[key] = y
        sf.write(os.path.join(SFX_DIR, f"{name}.wav"), y, SR)
        return y

    amb = Bus(total); sfx = Bus(total)
    for (name, t0, d, g, fi, fo) in amb_plan:
        if d <= 0: continue
        amb.add(t0, get(name, d), g, fi, fo, dur=d)
    for (name, t0, g) in sfx_plan:
        sfx.add(t0, get(name), g, 0.002, 0.05)
    mus = music_track(music_plan, total, version)

    # --- ducking : musique et ambiances baissent sous la voix
    dk = duck_env(voice, -10.0)[:, None]
    dk_amb = duck_env(voice, -6.0)[:, None]
    n = min(len(voice), len(mus), len(amb.x))
    voice, mus, ambx, sfxx, dk, dk_amb = voice[:n], mus[:n], amb.x[:n], sfx.x[:n], dk[:n], dk_amb[:n]
    # niveaux : voix -16 LUFS, musique ~-27 LUFS hors voix (=> ~-37 sous la voix)
    vL = loud(voice)
    voice = voice * db(-16 - vL)
    mL = loud(mus[np.abs(mus).sum(1) > 1e-4]) if np.any(np.abs(mus) > 1e-4) else -70
    mus = mus * db(-27 - mL)
    ambx = ambx * db(10.0)
    mix = voice + mus * dk + ambx * dk_amb + sfxx
    # bus : compression douce + limiteur à -1 dBTP après normalisation
    stems = os.path.join(ROOT, "build", version); os.makedirs(stems, exist_ok=True)
    sf.write(os.path.join(stems, "mix_pre.wav"), mix.astype(np.float32), SR, subtype="FLOAT")
    for nm, s in (("stem_voice", voice), ("stem_music", mus * dk), ("stem_amb", ambx * dk_amb), ("stem_sfx", sfxx)):
        sf.write(os.path.join(stems, nm + ".wav"), s.astype(np.float32), SR, subtype="FLOAT")
    # loudnorm deux passes (EBU R128) -> -14 LUFS, TP -1
    src = os.path.join(stems, "mix_pre.wav"); dst = os.path.join(stems, "mix_final.wav")
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", src, "-af", "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True)
    js = r.stderr[r.stderr.rfind("{"): r.stderr.rfind("}") + 1]
    m = json.loads(js)
    af = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:"
          f"measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true,aresample=48000")
    subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-af", af, "-ar", "48000", "-c:a", "pcm_s24le", dst])
    print("mix", version, "->", dst, "mesure entrée", m["input_i"], "LUFS")


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else "long")
