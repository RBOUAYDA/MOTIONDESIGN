# -*- coding: utf-8 -*-
"""Rendu image par image (Skia) -> FFmpeg (H.264).

Usage :
  python3 render.py long|tiktok --stills 12,45.5,...   (aperçus PNG)
  python3 render.py long|tiktok --video [--scale 2] [--jobs 4]
"""
import argparse, json, math, os, subprocess, sys, time
import numpy as np
import skia

sys.path.insert(0, os.path.dirname(__file__))
from gfx import *

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
GRAIN = float(os.environ.get('GRAIN', '0.05'))
DIP = 6 / FPS      # fondu court au noir : 6 images
XF = 0.5           # fondu enchaîné


class Shot:
    def __init__(self, t0, t1, fn, tin="cut", tout="cut", cam=None, nosub=False, bg="tex", name=""):
        self.t0, self.t1, self.fn = t0, t1, fn
        self.tin, self.tout, self.cam, self.nosub, self.bg, self.name = tin, tout, cam, nosub, bg, name

    def alpha(self, t):
        a = 1.0
        if self.tin == "fade":
            a *= ease_io(prog(t, self.t0, XF))
        return a

    def black(self, t):
        b = 0.0
        if self.tin == "dip":
            b = max(b, 1 - prog(t, self.t0, DIP))
        if self.tout == "dip":
            b = max(b, prog(t, self.t1 - DIP, DIP))
        if self.tout == "black":  # fondu au noir progressif (fin)
            b = max(b, ease_io(prog(t, self.t1 - 2.0, 2.0)))
        return b


def camera(c, shot, t):
    if not shot.cam: return
    k = (t - shot.t0) / max(0.001, shot.t1 - shot.t0)
    kind = shot.cam[0]; amt = shot.cam[1] if len(shot.cam) > 1 else 0.03
    if kind == "spi":
        s = 1 + amt * ease_io(k)
        cx, cy = (shot.cam[2] if len(shot.cam) > 2 else (540, 760))
        c.translate(cx, cy); c.scale(s, s); c.translate(-cx, -cy)
    elif kind == "par":
        c.translate(-W * amt * (k - 0.5), 0)
    elif kind == "zoomout":
        s = 1 + amt * (1 - ease(k))
        c.translate(540, 760); c.scale(s, s); c.translate(-540, -760)
    elif kind == "tilt":
        c.translate(0, -amt * H * (k - 0.5))


class Renderer:
    def __init__(self, version, scale):
        self.version = version
        self.S = scale
        self.TL = json.load(open(os.path.join(ROOT, "assets", "data", f"timeline_{version}.json")))
        self.tex = Textures(scale)
        if version == "long":
            import scenes_long as sc
        else:
            import scenes_tiktok as sc
        self.shots = sc.build(self.TL)
        self.sc = sc
        self.total = self.TL["total"]
        self.subs = self.TL["subs"]
        self.Wp, self.Hp = int(W * scale), int(H * scale)
        self.info = skia.ImageInfo.Make(self.Wp, self.Hp, skia.kRGBA_8888_ColorType, skia.kPremul_AlphaType)
        self.surf = skia.Surface.MakeRaster(self.info)
        self.buf = np.empty((self.Hp, self.Wp, 4), np.uint8)

    def frame(self, fi):
        t = fi / FPS
        c = self.surf.getCanvas()
        c.save(); c.scale(self.S, self.S)
        active = [s for s in self.shots if s.t0 <= t < s.t1]
        bg_tone = getattr(self.sc, "BG_TONE", BG)
        self.tex.draw_bg(c, t, bg_tone)
        black = 0.0
        nosub = False
        for s in active:
            a = s.alpha(t)
            if a <= 0: continue
            c.save()
            if a < 0.999: c.saveLayerAlpha(None, int(255 * a))
            camera(c, s, t)
            s.fn(c, t)
            if a < 0.999: c.restore()
            c.restore()
            black = max(black, s.black(t))
            nosub = nosub or s.nosub
        if black > 0:
            c.drawRect(skia.Rect.MakeWH(W, H), paint("#000000", min(1.0, black)))
        self.tex.draw_vignette(c, 0.5)
        if not nosub:
            sh = skia.GradientShader.MakeLinear([skia.Point(0, 1270), skia.Point(0, 1480)], [rgb("#000000", 0.0), rgb("#000000", 0.45)])
            pp = skia.Paint(); pp.setShader(sh); c.drawRect(skia.Rect.MakeLTRB(0, 1270, W, 1560), pp)
            sh2 = skia.GradientShader.MakeLinear([skia.Point(0, 1480), skia.Point(0, 1560)], [rgb("#000000", 0.45), rgb("#000000", 0.0)])
            pp2 = skia.Paint(); pp2.setShader(sh2); c.drawRect(skia.Rect.MakeLTRB(0, 1480, W, 1560), pp2)
            for sub in self.subs:
                if sub["start"] <= t < sub["end"]:
                    draw_subtitle(c, sub, t)
        self.tex.draw_grain(c, fi // 2, GRAIN)
        c.restore()
        self.surf.readPixels(self.info, self.buf)
        return self.buf


def ffmpeg_cmd(out, S, crf, preset):
    w, h = int(W * S), int(H * S)
    rc = ["-crf", str(crf)]
    if isinstance(crf, str) and crf.endswith("M"):
        rc = ["-b:v", crf, "-maxrate", "20M", "-bufsize", "32M", "-level", "4.2"]
    return ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{w}x{h}", "-r", str(FPS),
            "-i", "-", "-c:v", "libx264", "-preset", preset] + rc + ["-profile:v", "high",
            "-pix_fmt", "yuv420p", "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
            "-color_range", "tv", "-x264-params", "keyint=60:min-keyint=30", "-threads", "2", out]


def render_chunk(version, scale, f0, f1, out, crf, preset):
    R = Renderer(version, scale)
    p = subprocess.Popen(ffmpeg_cmd(out, scale, crf, preset), stdin=subprocess.PIPE)
    t0 = time.time()
    for fi in range(f0, f1):
        p.stdin.write(R.frame(fi).tobytes())
        if (fi - f0) % 300 == 0:
            el = time.time() - t0
            print(f"[{out}] {fi - f0}/{f1 - f0} {el:.0f}s", flush=True)
    p.stdin.close(); p.wait()
    return p.returncode


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("version"); ap.add_argument("--stills"); ap.add_argument("--video", action="store_true")
    ap.add_argument("--scale", type=float, default=2); ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--chunk", type=str); ap.add_argument("--out", type=str)
    ap.add_argument("--crf", type=str, default="17"); ap.add_argument("--preset", default="medium")
    ap.add_argument("--range", type=str)
    a = ap.parse_args()
    if a.stills:
        from PIL import Image
        R = Renderer(a.version, a.scale)
        od = a.out or os.path.join(ROOT, "build", "stills"); os.makedirs(od, exist_ok=True)
        for ts in a.stills.split(","):
            fi = int(round(float(ts) * FPS))
            Image.fromarray(R.frame(fi)[..., :3].copy()).save(os.path.join(od, f"{a.version}_{float(ts):07.2f}.png"))
        return
    if a.chunk:
        f0, f1 = map(int, a.chunk.split(":"))
        sys.exit(render_chunk(a.version, a.scale, f0, f1, a.out, a.crf, a.preset))
    if a.video:
        TL = json.load(open(os.path.join(ROOT, "assets", "data", f"timeline_{a.version}.json")))
        nf = int(math.ceil(TL["total"] * FPS))
        r0, r1 = (0, nf)
        if a.range:
            r0, r1 = [int(float(x) * FPS) for x in a.range.split(":")]
        bd = os.path.join(ROOT, "build", a.version); os.makedirs(bd, exist_ok=True)
        n = a.jobs
        bounds = [r0 + (r1 - r0) * i // n for i in range(n + 1)]
        procs = []
        for i in range(n):
            out = os.path.join(bd, f"part{i:02d}.mp4")
            procs.append(subprocess.Popen([sys.executable, __file__, a.version, "--chunk", f"{bounds[i]}:{bounds[i+1]}",
                                           "--out", out, "--scale", str(a.scale), "--crf", str(a.crf), "--preset", a.preset]))
        rc = [p.wait() for p in procs]
        print("chunks", rc)
        with open(os.path.join(bd, "parts.txt"), "w") as f:
            for i in range(n): f.write(f"file 'part{i:02d}.mp4'\n")
        subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", os.path.join(bd, "parts.txt"),
                               "-c", "copy", os.path.join(bd, "video.mp4")])
        print("ok", os.path.join(bd, "video.mp4"))


if __name__ == "__main__":
    main()
