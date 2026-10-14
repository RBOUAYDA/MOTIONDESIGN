# -*- coding: utf-8 -*-
"""Assemblage final (vidéo + mix) et contrôle qualité automatique.

Usage : python3 finalize.py long|tiktok   -> exporte puis écrit build/<v>/qc.json + planches contact
"""
import json, os, subprocess, sys, re
import numpy as np
import soundfile as sf

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = {"long": os.path.join(ROOT, "exports", "master", "france_rapport_de_force_MASTER_4K.mp4"),
       "tiktok": os.path.join(ROOT, "exports", "tiktok", "france_rapport_de_force_TIKTOK.mp4")}


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def mux(version):
    bd = os.path.join(ROOT, "build", version)
    out = OUT[version]; os.makedirs(os.path.dirname(out), exist_ok=True)
    br = "320k"
    subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-i", os.path.join(bd, "video.mp4"), "-i", os.path.join(bd, "mix_final.wav"),
                           "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac", "-b:a", br, "-ar", "48000", "-ac", "2",
                           "-shortest", "-movflags", "+faststart", "-metadata", "title=France — Le rapport de force",
                           "-metadata:s:a:0", "language=fra", out])
    return out


def qc(version, path):
    bd = os.path.join(ROOT, "build", version)
    rep = {"file": path}
    pr = json.loads(run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", path]).stdout)
    v = [s for s in pr["streams"] if s["codec_type"] == "video"][0]
    a = [s for s in pr["streams"] if s["codec_type"] == "audio"][0]
    rep.update(width=v["width"], height=v["height"], vcodec=v["codec_name"], profile=v.get("profile"), pix_fmt=v["pix_fmt"],
               fps=v["r_frame_rate"], color=v.get("color_primaries"), nb_frames=v.get("nb_frames"),
               acodec=a["codec_name"], sample_rate=a["sample_rate"], channels=a["channels"],
               duration=float(pr["format"]["duration"]), size_mb=round(int(pr["format"]["size"]) / 1e6, 1),
               bitrate_mbps=round(int(pr["format"]["bit_rate"]) / 1e6, 1))
    rep["ratio_9_16"] = abs(v["width"] / v["height"] - 9 / 16) < 1e-3
    # décodage intégral (frames corrompues) + détection d'images noires
    r = run(["ffmpeg", "-v", "error", "-i", path, "-vf", "scale=270:480,blackdetect=d=0.4:pix_th=0.06", "-af", "ebur128=peak=true",
             "-f", "null", "-"])
    err = r.stderr
    r2 = run(["ffmpeg", "-hide_banner", "-i", path, "-vf", "scale=270:480,blackdetect=d=0.4:pix_th=0.06", "-af", "ebur128=peak=true",
              "-f", "null", "-"])
    log = r2.stderr
    rep["decode_errors"] = [l for l in err.splitlines() if l.strip()][:10]
    rep["black_segments"] = [(float(m.group(1)), float(m.group(2))) for m in re.finditer(r"black_start:([\d.]+) black_end:([\d.]+)", log)]
    m = re.search(r"Integrated loudness:\s+I:\s+([-\d.]+) LUFS", log); rep["lufs"] = float(m.group(1)) if m else None
    m = re.search(r"True peak:\s+Peak:\s+([-\d.]+) dBFS", log); rep["true_peak"] = float(m.group(1)) if m else None
    # sous-titres : synchronisation avec l'énergie de la voix réelle
    TL = json.load(open(os.path.join(ROOT, "assets", "data", f"timeline_{version}.json")))
    vo, sr = sf.read(os.path.join(ROOT, "assets", "voice", f"vo_{version}.wav"), dtype="float32")
    win = int(0.02 * sr)
    env = np.sqrt(np.convolve(vo ** 2, np.ones(win) / win, mode="same"))
    act = env > 10 ** (-40 / 20) * env.max()
    bad = []
    for i, s in enumerate(TL["subs"]):
        seg = act[int(s["start"] * sr): int(s["end"] * sr)]
        cover = float(seg.mean()) if len(seg) else 0
        if cover < 0.35: bad.append((i, s["start"], round(cover, 2), " / ".join(s["lines"])))
        if s["end"] - s["start"] < 0.6: bad.append((i, s["start"], "court", " / ".join(s["lines"])))
        if len(s["lines"]) > 2: bad.append((i, s["start"], "3 lignes", ""))
    # voix non sous-titrée
    covered = np.zeros_like(act)
    for s in TL["subs"]: covered[int(s["start"] * sr): int(s["end"] * sr)] = True
    unsub = act & ~covered
    rep["voice_without_subtitle_s"] = round(float(unsub.sum()) / sr, 2)
    rep["subtitle_issues"] = bad
    rep["subtitles"] = len(TL["subs"])
    # largeur des sous-titres (zone sûre x 90-940)
    os.environ.setdefault("LD_LIBRARY_PATH", "/opt/egl")
    sys.path.insert(0, os.path.dirname(__file__))
    from gfx import font
    f = font(54, "SemiBold")
    widest = max(f.measureText(l) for s in TL["subs"] for l in s["lines"])
    rep["subtitle_max_width_px"] = round(widest, 1)
    rep["subtitle_in_safe_zone"] = widest <= 850
    # planches contact (1 image / N s)
    step = 4 if version == "long" else 1.5
    cs = os.path.join(bd, "contact"); os.makedirs(cs, exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", path, "-vf", f"fps=1/{step},scale=216:384,tile=12x4",
                    os.path.join(cs, "sheet_%02d.png")])
    json.dump(rep, open(os.path.join(bd, "qc.json"), "w"), ensure_ascii=False, indent=1)
    return rep


if __name__ == "__main__":
    v = sys.argv[1]
    p = OUT[v] if "--qc-only" in sys.argv else mux(v)
    rep = qc(v, p)
    print(json.dumps({k: rep[k] for k in rep if k not in ("subtitle_issues",)}, ensure_ascii=False, indent=1))
    print("subtitle issues:", len(rep["subtitle_issues"]))
    for b in rep["subtitle_issues"][:30]: print("  ", b)
