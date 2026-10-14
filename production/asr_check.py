"""Contrôle qualité de la voix : transcription Whisper (hors-ligne) de chaque phrase et comparaison au texte."""
import json, sys, os, difflib, re, numpy as np, soundfile as sf, sherpa_onnx
from scipy import signal
D = "/tmp/tts/sherpa-onnx-whisper-turbo"
rec = sherpa_onnx.OfflineRecognizer.from_whisper(encoder=f"{D}/turbo-encoder.int8.onnx", decoder=f"{D}/turbo-decoder.int8.onnx",
        tokens=f"{D}/turbo-tokens.txt", language="fr", task="transcribe", num_threads=4)
man = json.load(open(sys.argv[1])); root = sys.argv[2]
def norm(s): return re.sub(r"[^a-zàâçéèêëîïôûùüÿœ0-9 ]", " ", s.lower()).split()
res = []
for m in man:
    y, sr = sf.read(os.path.join(root, m["file"])); y = np.concatenate([np.zeros(8000), signal.resample_poly(y, 16000, sr), np.zeros(16000)]).astype(np.float32)
    s = rec.create_stream(); s.accept_waveform(16000, y); rec.decode_stream(s); hyp = s.result.text.strip()
    r = difflib.SequenceMatcher(None, norm(m["spoken"]), norm(hyp)).ratio()
    res.append(dict(key=m["key"], ratio=r, hyp=hyp, ref=m["text"])); print(f"{m['key']:5s} {r:.2f} | {hyp}", flush=True)
json.dump(res, open(sys.argv[3], "w"), ensure_ascii=False, indent=1)
