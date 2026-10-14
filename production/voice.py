# -*- coding: utf-8 -*-
"""Génère la voix off (Piper « tom », voix neuronale FR) phrase par phrase.

Usage : python3 voice.py long|tiktok
Sortie : assets/voice/<version>/<clé>.wav (48 kHz mono, traitée) + manifest.json
"""
import json, os, re, sys
import numpy as np
import soundfile as sf
from num2words import num2words
from scipy import signal

sys.path.insert(0, os.path.dirname(__file__))
from script_data import LONG, TIKTOK

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MODEL_DIR = os.environ.get("PIPER_DIR", "/tmp/tts/vits-piper-fr_FR-tom-medium")
SR = 48000

SPEED = {"n": 0.94, "g": 0.86, "a": 0.99, "s": 0.82}

ABBR = [
    (r"\bIpsos-BVA\b", "Ipsos bé vé a"),
    (r"\bCluster17\b", "Kleusteur dix-sept"),
    (r"\bIGPN\b", "i gé pé ène"),
    (r"\bCGT\b", "cé gé té"),
    (r"\bCPE\b", "cé pé euh"),
    (r"Île-de-France", "Île de France"),
    (r"À Lens", "À Lance"),
    (r"Aucun coût total fiable", "Aucun coût total, fiable,"),
    (r"Parcoursup", "Parcours sup"),
    (r"lycéen s'y", "lycéen, s'y"),
    (r"il y a le 17 octobre", "il y a le dix sept octobre"),
    (r"\bElabe\b", "Élabe"),
    (r"\bIfop\b", "Ifop"),
    (r"\bprofs\b", "profs"),
    (r"\bmai 68\b", "mai soixante-huit"),
    (r"\bLe 8,", "Le huit,"),
]


def n2w(n):
    return num2words(n, lang="fr")


def normalize(text):
    t = text
    for a, b in ABBR:
        t = re.sub(a, b, t)
    t = t.replace("«", "").replace("»", "").replace("…", ",")
    # prix : 2,35 euros -> deux euros trente-cinq
    t = re.sub(r"(\d+),(\d{2}) euros", lambda m: f"{n2w(int(m.group(1)))} euros {n2w(int(m.group(2)))}", t)
    # décimaux : 8,5 -> huit virgule cinq
    t = re.sub(r"(\d+),(\d+)", lambda m: f"{n2w(int(m.group(1)))} virgule {n2w(int(m.group(2)))}", t)
    # milliers séparés par espace (ou insécable)
    t = re.sub(r"(\d{1,3})[   ](\d{3})\b", lambda m: m.group(1) + m.group(2), t)
    t = re.sub(r"(\d+)\s*%", lambda m: f"{n2w(int(m.group(1)))} pour cent", t)
    t = re.sub(r"\d+", lambda m: n2w(int(m.group(0))), t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


_tts = None


def get_tts():
    global _tts
    if _tts is None:
        import sherpa_onnx
        name = os.path.basename(MODEL_DIR).replace("vits-piper-", "")
        cfg = sherpa_onnx.OfflineTtsConfig(
            model=sherpa_onnx.OfflineTtsModelConfig(
                vits=sherpa_onnx.OfflineTtsVitsModelConfig(
                    model=f"{MODEL_DIR}/{name}.onnx", tokens=f"{MODEL_DIR}/tokens.txt",
                    data_dir=f"{MODEL_DIR}/espeak-ng-data", noise_scale=0.6, noise_scale_w=0.75),
                num_threads=4))
        _tts = sherpa_onnx.OfflineTts(cfg)
    return _tts


def trim(y, sr, thr_db=-55, pad=0.03, tail=0.16):
    env = np.abs(y)
    win = int(sr * 0.01)
    env = np.convolve(env, np.ones(win) / win, mode="same")
    thr = 10 ** (thr_db / 20) * max(env.max(), 1e-9)
    idx = np.where(env > thr)[0]
    if len(idx) == 0:
        return y
    a = max(0, idx[0] - int(pad * sr)); b = min(len(y), idx[-1] + int(tail * sr))
    return y[a:b]


def process(y, sr):
    """Chaîne voix « broadcast » : rééchantillonnage 48 k, passe-haut, chaleur, présence, compression douce."""
    y = signal.resample_poly(y, SR, sr) if sr != SR else y
    sos = signal.butter(2, 75, "hp", fs=SR, output="sos"); y = signal.sosfilt(sos, y)
    # léger bas-médium (chaleur) et présence
    def peq(x, f0, g_db, q):
        A = 10 ** (g_db / 40); w = 2 * np.pi * f0 / SR; al = np.sin(w) / (2 * q)
        b = [1 + al * A, -2 * np.cos(w), 1 - al * A]; a = [1 + al / A, -2 * np.cos(w), 1 - al / A]
        return signal.lfilter(b, a, x)
    y = peq(y, 160, 2.0, 0.8)
    y = peq(y, 3200, 1.5, 1.0)
    y = peq(y, 7500, -2.0, 1.5)  # dé-essage statique
    # compression RMS douce 3:1
    env = np.sqrt(np.convolve(y ** 2, np.ones(480) / 480, mode="same") + 1e-12)
    lvl = 20 * np.log10(env + 1e-9); thr = -22
    gain_db = np.where(lvl > thr, (thr - lvl) * (1 - 1 / 3), 0)
    gain_db = signal.lfilter([0.02], [1, -0.98], gain_db)
    y = y * 10 ** (gain_db / 20)
    y = y / (np.abs(y).max() + 1e-9) * 0.7
    # fondus anti-clic
    f = int(0.008 * SR); y[:f] *= np.linspace(0, 1, f); g = int(0.06 * SR); y[-g:] *= np.linspace(1, 0, g) ** 2
    return y.astype(np.float32)


def main(version):
    script = LONG if version == "long" else TIKTOK
    out = os.path.join(ROOT, "assets", "voice", version); os.makedirs(out, exist_ok=True)
    tts = get_tts()
    manifest = []
    for sec in script:
        for (k, text, pause, style) in sec["items"]:
            spoken = normalize(text)
            sp = SPEED[style] * (1.04 if version == "tiktok" else 1.0)
            a = tts.generate(spoken, sid=0, speed=sp)
            y = trim(np.array(a.samples, dtype=np.float32), a.sample_rate)
            y = process(y, a.sample_rate)
            fn = os.path.join(out, f"{k}.wav"); sf.write(fn, y, SR, subtype="PCM_24")
            manifest.append(dict(key=k, section=sec["id"], text=text, spoken=spoken, pause=pause,
                                 style=style, dur=len(y) / SR, file=os.path.relpath(fn, ROOT)))
            print(f"{k:5s} {len(y)/SR:6.2f}s  {spoken}")
    json.dump(manifest, open(os.path.join(out, "manifest.json"), "w"), ensure_ascii=False, indent=1)
    print("total voix", sum(m["dur"] for m in manifest), "pauses", sum(m["pause"] for m in manifest))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "long")
