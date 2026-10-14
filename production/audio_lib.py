# -*- coding: utf-8 -*-
"""Synthèse audio originale : partition (ré mineur, 72 BPM) et bibliothèque SFX / ambiances.

Tout est généré ici (aucune banque sous licence n'était accessible depuis l'environnement) :
- piano feutré (synthèse additive, partiels légèrement inharmoniques, marteau feutré)
- nappes de cordes graves (dents de scie désaccordées filtrées, attaque lente)
- pulsation électronique douce (kick filtré)
- ambiances (foule = murmure obtenu en superposant des voix de synthèse rendues inintelligibles,
  ville, vent, métro), sirène lointaine, radio, ticks feutrés, impacts sourds, papier.
"""
import os, json, glob
import numpy as np
from scipy import signal

SR = 48000
RNG = np.random.default_rng(1717)


# ---------------------------------------------------------------- utilitaires
def t_axis(d):
    return np.arange(int(d * SR)) / SR


def lp(x, f, order=2):
    return signal.sosfilt(signal.butter(order, f, "lp", fs=SR, output="sos"), x, axis=0)


def hp(x, f, order=2):
    return signal.sosfilt(signal.butter(order, f, "hp", fs=SR, output="sos"), x, axis=0)


def bp(x, f1, f2, order=2):
    return signal.sosfilt(signal.butter(order, [f1, f2], "bp", fs=SR, output="sos"), x, axis=0)


def stereo(x, pan=0.0, width=0.0):
    """mono -> stéréo (pan -1..1), width ajoute une décorrélation légère."""
    l = x * np.sqrt((1 - pan) / 2) * np.sqrt(2)
    r = x * np.sqrt((1 + pan) / 2) * np.sqrt(2)
    if width > 0:
        d = int(0.011 * SR)
        r = (1 - width) * r + width * np.concatenate([np.zeros(d), r[:-d]])
    return np.stack([l, r], 1)


def reverb_ir(dur=2.4, decay=2.2, bright=6000, seed=3):
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    t = np.arange(n) / SR
    env = np.exp(-t * (6.9 / decay))
    ir = rng.standard_normal((n, 2)) * env[:, None]
    ir = lp(ir, bright)
    ir[: int(0.012 * SR)] *= np.linspace(0, 1, int(0.012 * SR))[:, None]
    return ir / np.sqrt((ir ** 2).sum(0)).max()


_IRS = {}


def reverb(x, mix=0.25, dur=2.4, decay=2.2, bright=6000):
    key = (dur, decay, bright)
    if key not in _IRS:
        _IRS[key] = reverb_ir(dur, decay, bright)
    ir = _IRS[key]
    if x.ndim == 1:
        x = stereo(x)
    wet = np.stack([signal.fftconvolve(x[:, c], ir[:, c])[: len(x)] for c in range(2)], 1)
    return (1 - mix) * x + mix * wet


def fade(x, fi=0.01, fo=0.01):
    n = len(x)
    a = min(int(fi * SR), n); b = min(int(fo * SR), n)
    w = np.ones(n)
    if a: w[:a] = np.linspace(0, 1, a)
    if b: w[n - b:] *= np.linspace(1, 0, b)
    return x * (w[:, None] if x.ndim == 2 else w)


def norm(x, peak=0.9):
    m = np.abs(x).max()
    return x * (peak / m) if m > 0 else x


def pink(n, rng=RNG):
    w = rng.standard_normal(n)
    f = np.fft.rfft(w); k = np.arange(len(f)); k[0] = 1
    return np.fft.irfft(f / np.sqrt(k), n)


def brown(n, rng=RNG):
    w = np.cumsum(rng.standard_normal(n)); w = hp(w, 20)
    return w / (np.abs(w).max() + 1e-9)


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


# ---------------------------------------------------------------- instruments
def felt_piano(note, dur, vel=0.6):
    f0 = midi(note)
    L = dur + 2.5
    t = t_axis(L)
    y = np.zeros_like(t)
    B = 0.00018
    for k in range(1, 14):
        fk = f0 * k * np.sqrt(1 + B * k * k)
        if fk > 9000: break
        amp = (1 / k ** 1.3) * (0.6 + 0.4 * vel)
        dec = 2.8 / (1 + 0.35 * k) * (1.4 - 0.6 * (note - 40) / 50)
        y += amp * np.exp(-t / max(dec, 0.08)) * np.sin(2 * np.pi * fk * t + RNG.uniform(0, 6.28))
    # marteau feutré
    ham = lp(RNG.standard_normal(len(t)) * np.exp(-t / 0.012), 1800) * 0.25
    y = y + ham
    att = int(0.006 * SR); y[:att] *= np.linspace(0, 1, att)
    # relâchement (étouffoir)
    rel = int(dur * SR)
    if rel < len(y):
        y[rel:] *= np.exp(-(t[rel:] - t[rel]) / 0.35)
    y = lp(y, 1200 + 2400 * vel)  # feutre : sonorité étouffée
    return y * vel


def string_pad(notes, dur, att=2.5, rel=2.5, bright=900):
    L = dur + rel
    t = t_axis(L)
    out = np.zeros((len(t), 2))
    for n in notes:
        for d, pan in ((-0.07, -0.6), (0.0, 0.0), (0.06, 0.6)):
            f = midi(n) * 2 ** (d / 12)
            vib = 1 + 0.0025 * np.sin(2 * np.pi * (4.6 + RNG.uniform(-.4, .4)) * t + RNG.uniform(0, 6))
            ph = 2 * np.pi * np.cumsum(f * vib) / SR + RNG.uniform(0, 6)
            saw = np.zeros_like(t)
            for k in range(1, 18):
                if f * k > 6000: break
                saw += np.sin(k * ph) / k
            out += stereo(saw, pan)
    env = np.ones(len(t))
    a = int(att * SR); env[:a] = np.linspace(0, 1, a) ** 1.5
    r0 = int(dur * SR); env[r0:] = np.linspace(1, 0, len(t) - r0) ** 2
    out = lp(out, bright, 2) * env[:, None]
    return out / (len(notes) * 3)


def soft_kick():
    t = t_axis(0.6)
    f = 46 + 50 * np.exp(-t / 0.03)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.22)
    y += 0.08 * lp(RNG.standard_normal(len(t)), 300) * np.exp(-t / 0.02)
    return lp(y, 220)


# ---------------------------------------------------------------- partition
BPM = 72
BEAT = 60 / BPM
BAR = 4 * BEAT
# i - VI - III - VII  (Rém - Sib - Fa - Do), deux mesures chacun
PROG = [
    ([38, 50, 53, 57], [62, 65, 69]),   # Dm
    ([34, 46, 50, 53], [62, 65, 70]),   # Bb
    ([41, 48, 53, 57], [60, 65, 69]),   # F
    ([36, 48, 52, 55], [60, 64, 67]),   # C
]
MOTIF = [74, 74, 77, 76]  # quatre notes : ré ré fa mi (thème)


def render_music_part(kind, dur, seed=0, offset_bars=0):
    """kind : 'nappe', 'pulse', 'theme', 'theme_full'. Retourne un stéréo de durée dur."""
    rng = np.random.default_rng(seed)
    n = int(dur * SR) + SR * 6
    out = np.zeros((n, 2))
    nbars = int(np.ceil(dur / BAR)) + 1
    for b in range(nbars):
        ch = PROG[((b + offset_bars) // 2) % 4]
        t0 = int(b * BAR * SR)
        if b % 2 == 0:
            pad = string_pad(ch[0][1:] if kind != "nappe" else ch[0][1:3] + [ch[0][0] + 12], 2 * BAR, att=2.2, rel=2.0,
                             bright=700 if kind == "nappe" else 950)
            gain = 0.55 if kind == "nappe" else 0.42
            seg = pad[: n - t0] * gain
            out[t0:t0 + len(seg)] += seg
            # basse tenue
            bass = string_pad([ch[0][0]], 2 * BAR, att=1.5, rel=1.5, bright=300) * 0.6
            seg = bass[: n - t0]; out[t0:t0 + len(seg)] += seg
        if kind in ("pulse", "theme_full"):
            k = soft_kick()
            for beat in range(4):
                if beat in (0, 2) or kind == "theme_full":
                    p = t0 + int(beat * BEAT * SR)
                    seg = k[: max(0, n - p)] * (0.55 if beat == 0 else 0.35)
                    out[p:p + len(seg)] += stereo(seg)[: len(seg)]
            # ostinato piano feutré grave (croches)
            notes = [ch[0][1], ch[0][2], ch[0][3], ch[0][2]] * 2
            for i, nn in enumerate(notes):
                p = t0 + int(i * BEAT / 2 * SR)
                y = felt_piano(nn, BEAT / 2, vel=0.28 + 0.06 * (i % 4 == 0))
                seg = y[: max(0, n - p)]
                out[p:p + len(seg)] += stereo(seg, -0.2)[: len(seg)] * 0.5
        if kind in ("theme", "theme_full") and b % 2 == 0:
            for i, nn in enumerate(MOTIF):
                p = t0 + int(i * BEAT * SR)
                y = felt_piano(nn - (0 if (b // 2) % 2 == 0 else 2) if i == 3 else nn, BEAT * 0.9, vel=0.55)
                seg = y[: max(0, n - p)]
                out[p:p + len(seg)] += stereo(seg, 0.15)[: len(seg)] * 0.6
            # réponse grave
            p = t0 + int(BAR * SR)
            y = felt_piano(ch[0][1], BAR, vel=0.4); seg = y[: max(0, n - p)]
            out[p:p + len(seg)] += stereo(seg, -0.1)[: len(seg)] * 0.45
    out = reverb(out, mix=0.32, dur=3.2, decay=2.8, bright=5000)
    return out[: int(dur * SR)]


# ---------------------------------------------------------------- SFX
def sfx_tick():
    t = t_axis(0.08)
    y = bp(RNG.standard_normal(len(t)), 1200, 3500) * np.exp(-t / 0.004)
    y += 0.5 * np.sin(2 * np.pi * 420 * t) * np.exp(-t / 0.012)
    return norm(lp(y, 5000), 0.5)


def sfx_click():
    t = t_axis(0.05)
    y = bp(RNG.standard_normal(len(t)), 2000, 6000) * np.exp(-t / 0.002)
    return norm(y, 0.4)


def sfx_impact():
    """Impact sourd grave (sub 40-60 Hz), sans whoosh."""
    t = t_axis(3.0)
    f = 44 + 18 * np.exp(-t / 0.08)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.9)
    y += 0.25 * lp(RNG.standard_normal(len(t)), 160) * np.exp(-t / 0.15)
    y = lp(y, 180)
    return reverb(norm(y, 0.9), 0.2, 3.0, 2.5, 1500)


def sfx_paper():
    t = t_axis(0.9)
    env = np.exp(-((t - 0.35) / 0.18) ** 2) + 0.4 * np.exp(-((t - 0.6) / 0.1) ** 2)
    crack = (RNG.random(len(t)) < 0.004) * RNG.standard_normal(len(t))
    y = hp(RNG.standard_normal(len(t)) * env * 0.4 + lp(crack, 6000) * env * 2, 900)
    return stereo(norm(y, 0.5), 0.1, 0.3)


def sfx_page():
    t = t_axis(0.7)
    env = np.sin(np.pi * np.clip(t / 0.55, 0, 1)) ** 2
    y = bp(RNG.standard_normal(len(t)), 600, 7000) * env
    y *= 1 + 0.6 * np.sin(2 * np.pi * 9 * t)
    return stereo(norm(y, 0.45), -0.1, 0.3)


def sfx_pump_beep():
    t = t_axis(0.5)
    y = np.zeros_like(t)
    for s in (0.0, 0.22):
        m = (t >= s) & (t < s + 0.12)
        y[m] = np.sin(2 * np.pi * 1850 * t[m]) * 0.4
    y = lp(y, 4000)
    return reverb(stereo(fade(y, 0.002, 0.01), 0.2), 0.25, 0.8, 0.6, 4000)


def sfx_siren_far(dur=6.0):
    """Deux-tons lointain (la 435 Hz / si 488 Hz), filtré et réverbéré, une seule fois."""
    t = t_axis(dur)
    sq = (np.floor(t / 0.6) % 2)
    f = np.where(sq == 0, 435.0, 488.0)
    ph = 2 * np.pi * np.cumsum(f) / SR
    y = np.sign(np.sin(ph)) * 0.3 + np.sin(ph) * 0.5 + 0.2 * np.sin(2 * ph)
    y = lp(bp(y, 300, 2500), 1600)
    env = np.minimum(1, t / 1.5) * np.minimum(1, (dur - t) / 2.0)
    y = y * env * (1 + 0.15 * np.sin(2 * np.pi * 0.3 * t))
    return reverb(stereo(norm(y, 0.5), 0.5, 0.5), 0.6, 3.5, 3.0, 2500)


def sfx_whistle_far():
    t = t_axis(1.4)
    f = 2900 + 120 * np.sin(2 * np.pi * 38 * t)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR)
    env = np.zeros_like(t)
    for s, d in ((0.0, 0.25), (0.35, 0.6)):
        m = (t >= s) & (t < s + d); env[m] = np.sin(np.pi * (t[m] - s) / d) ** 0.3
    y = lp(y * env, 3500)
    return reverb(stereo(norm(y, 0.25), -0.4), 0.7, 3.0, 2.6, 3000)


def sfx_radio(dur=3.0):
    """Radio de service générique : squelch + babillage bande étroite inintelligible (synthétique)."""
    t = t_axis(dur)
    sq = bp(RNG.standard_normal(int(0.12 * SR)), 1500, 4000) * 0.5
    voice = np.zeros_like(t)
    # syllabes synthétiques (formants) inintelligibles
    p = 0.2
    while p < dur - 0.4:
        d = RNG.uniform(0.07, 0.16)
        m = (t >= p) & (t < p + d)
        f0 = RNG.uniform(110, 150)
        ph = 2 * np.pi * f0 * t[m]
        src = signal.sawtooth(ph)
        voice[m] = src * np.sin(np.pi * (t[m] - p) / d)
        p += d + RNG.uniform(0.0, 0.08) + (0.3 if RNG.random() < 0.12 else 0)
    for f1 in (650, 1200, 2400):
        voice = voice + 0.0
    voice = bp(voice, 400, 2600, 3)
    y = voice * 0.6 + bp(RNG.standard_normal(len(t)), 300, 3000) * 0.04
    y[: len(sq)] += sq; y[-len(sq):] += sq
    y = np.tanh(y * 2.5) * 0.35
    return reverb(stereo(y, 0.3), 0.18, 1.0, 0.8, 3500)


def crowd_bed(dur, babble, density=1.0, distance=0.5, seed=0):
    """Foule multicouche : murmure obtenu en superposant des voix rendues inintelligibles."""
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    out = np.zeros((n, 2))
    nvoices = int(26 * density)
    for i in range(nvoices):
        src = babble[rng.integers(len(babble))]
        # variation de hauteur par rééchantillonnage
        rate = rng.uniform(0.85, 1.2)
        src = signal.resample(src, int(len(src) / rate))
        src = src[::-1] if rng.random() < 0.5 else src  # inintelligible
        start = rng.integers(-len(src), n)
        a = max(0, start); b = min(n, start + len(src))
        if b <= a: continue
        seg = src[a - start:b - start] * rng.uniform(0.3, 1.0)
        out[a:b] += stereo(seg, rng.uniform(-0.9, 0.9))
        # boucle pour couvrir la durée
    # second passage pour remplir
    out = lp(out, 2600 - 1400 * distance)
    out = hp(out, 140)
    out += stereo(lp(pink(n, rng), 900) * 0.04, 0, 0.5)
    out = reverb(out, 0.35 + 0.3 * distance, 2.0, 1.8, 3000)
    lfo = 1 + 0.15 * np.sin(2 * np.pi * 0.07 * np.arange(n) / SR + rng.uniform(0, 6))
    return norm(out * lfo[:, None], 0.5)


def chant_far(dur, babble, seed=1):
    """Slogan scandé lointain, rythmé mais sans paroles intelligibles."""
    rng = np.random.default_rng(seed)
    n = int(dur * SR); out = np.zeros((n, 2))
    period = 1.25
    p = 0.3
    while p < dur - 1:
        for j in range(4):
            src = babble[rng.integers(len(babble))]
            o = rng.integers(0, max(1, len(src) - int(0.25 * SR)))
            syl = src[o:o + int(0.22 * SR)] * np.hanning(int(0.22 * SR))[: len(src[o:o + int(0.22 * SR)])]
            for v in range(10):
                q = int((p + j * period / 4 + rng.normal(0, 0.02)) * SR)
                if q + len(syl) < n:
                    out[q:q + len(syl)] += stereo(syl * rng.uniform(0.5, 1), rng.uniform(-0.8, 0.8))
        p += period * rng.choice([1, 1, 1.5])
    out = lp(hp(out, 200), 1300)
    return norm(reverb(out, 0.7, 3.0, 2.5, 2000), 0.4)


def wind_bed(dur, seed=4):
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    x = np.stack([pink(n, rng), pink(n, rng)], 1)
    t = np.arange(n) / SR
    lfo = 0.6 + 0.4 * np.sin(2 * np.pi * 0.09 * t + 1) * np.sin(2 * np.pi * 0.031 * t)
    y = bp(x, 180, 1400) * lfo[:, None]
    return norm(y, 0.35)


def city_bed(dur, seed=5):
    rng = np.random.default_rng(seed)
    n = int(dur * SR); t = np.arange(n) / SR
    base = lp(np.stack([brown(n, rng), brown(n, rng)], 1), 250) * 0.6
    base += lp(np.stack([pink(n, rng), pink(n, rng)], 1), 1200) * 0.15
    # passages de véhicules
    p = rng.uniform(0, 3)
    while p < dur:
        d = rng.uniform(3, 6)
        m = (t >= p) & (t < p + d)
        env = np.sin(np.pi * (t[m] - p) / d) ** 3
        car = lp(pink(m.sum(), rng), rng.uniform(500, 900)) * env * rng.uniform(0.3, 0.6)
        pan = np.linspace(rng.choice([-1, 1]) * 0.8, 0, m.sum())
        out = np.stack([car * (1 - pan) / 2, car * (1 + pan) / 2], 1)
        base[m] += out
        p += rng.uniform(2, 7)
    return norm(hp(base, 30), 0.4)


def metro_bed(dur, seed=6):
    rng = np.random.default_rng(seed)
    n = int(dur * SR); t = np.arange(n) / SR
    rumble = lp(np.stack([brown(n, rng), brown(n, rng)], 1), 180)
    env = np.clip(np.minimum(t / 3, (dur - t) / 3), 0, 1)
    clacks = np.zeros(n)
    p = 0.5
    while p < dur - 0.3:
        for off in (0, 0.11):
            q = int((p + off) * SR)
            k = lp(rng.standard_normal(int(0.04 * SR)), 900) * np.exp(-np.arange(int(0.04 * SR)) / SR / 0.01)
            clacks[q:q + len(k)] += k * 0.8
        p += 0.95
    y = rumble * 0.8 + stereo(clacks, 0, 0.4) * 0.5
    y += stereo(bp(rng.standard_normal(n), 2500, 5000) * 0.02)
    return norm(y * env[:, None], 0.45)


def room_tone(dur, seed=7):
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    y = lp(np.stack([pink(n, rng), pink(n, rng)], 1), 500) * 0.4
    y += np.stack([np.sin(2 * np.pi * 50 * np.arange(n) / SR)] * 2, 1) * 0.01
    return norm(y, 0.12)


def bins_sfx():
    """Conteneurs déplacés : roulement plastique + chocs creux."""
    t = t_axis(2.2)
    roll = lp(RNG.standard_normal(len(t)), 600) * (0.3 + 0.2 * np.sin(2 * np.pi * 13 * t)) * np.clip(np.minimum(t / 0.2, (1.4 - t) / 0.3), 0, 1)
    y = roll * 0.6
    for s in (1.45, 1.8):
        q = int(s * SR); L = int(0.35 * SR)
        tt = np.arange(L) / SR
        hit = (np.sin(2 * np.pi * 140 * tt) + 0.6 * np.sin(2 * np.pi * 310 * tt) + 0.3 * np.sin(2 * np.pi * 720 * tt)) * np.exp(-tt / 0.07)
        hit += lp(RNG.standard_normal(L), 2000) * np.exp(-tt / 0.02)
        y[q:q + L] += hit[: len(y) - q] * 0.7
    return reverb(stereo(norm(y, 0.6), -0.2, 0.3), 0.3, 1.5, 1.2, 4000)


def steps(dur, rate=1.9, seed=8):
    rng = np.random.default_rng(seed)
    n = int(dur * SR); y = np.zeros(n)
    p = 0.1
    while p < dur - 0.2:
        q = int(p * SR); L = int(0.09 * SR)
        k = lp(rng.standard_normal(L), rng.uniform(700, 1100)) * np.exp(-np.arange(L) / SR / 0.018)
        y[q:q + L] += k * rng.uniform(0.6, 1)
        p += 1 / rate + rng.normal(0, 0.02)
    return reverb(stereo(norm(y, 0.4), 0.1, 0.3), 0.3, 1.2, 1.0, 3000)


def glass_tinkle():
    t = t_axis(1.5); y = np.zeros_like(t)
    for i in range(7):
        s = RNG.uniform(0, 0.6); q = int(s * SR); L = len(t) - q
        tt = np.arange(L) / SR
        f = RNG.uniform(3000, 6500)
        y[q:] += np.sin(2 * np.pi * f * tt) * np.exp(-tt / RNG.uniform(0.05, 0.15)) * RNG.uniform(0.1, 0.3)
    return reverb(stereo(y, 0.3), 0.4, 1.5, 1.2, 8000) * 0.5


def chair_creak():
    t = t_axis(0.9)
    f = 380 + 120 * np.sin(2 * np.pi * 1.1 * t)
    y = signal.sawtooth(2 * np.pi * np.cumsum(f) / SR) * (RNG.random(len(t)) < 0.5)
    y = bp(y, 600, 2500) * np.sin(np.pi * t / 0.9) ** 2
    return reverb(stereo(norm(y, 0.2), -0.3), 0.4, 1.4, 1.0, 4000)


def amphi_echo(dur, babble):
    b = crowd_bed(dur, babble, density=0.35, distance=0.3, seed=11)
    return norm(reverb(b, 0.6, 3.5, 3.0, 3500), 0.35)


def riser(dur=3.0):
    t = t_axis(dur)
    f = 40 + 30 * (t / dur) ** 2
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * (t / dur) ** 2
    y += lp(pink(len(t)), 900) * 0.2 * (t / dur) ** 3
    return stereo(norm(lp(y, 1500), 0.5), 0, 0.4)


def load_babble(dirs):
    files = []
    for d in dirs:
        files += sorted(glob.glob(os.path.join(d, "*.wav")))
    import soundfile as sf
    out = []
    for f in files:
        y, sr = sf.read(f)
        if y.ndim > 1: y = y.mean(1)
        if sr != SR: y = signal.resample_poly(y, SR, sr)
        out.append(y.astype(np.float32))
    return out
