#!/bin/bash
# Prépare l'environnement de production à chaque session Claude Code (cloud) :
# bibliothèques Python, libEGL (Skia), FFmpeg, police Inter, voix Piper FR et Whisper (QC).
# Idempotent : ne réinstalle/retélécharge que ce qui manque.
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

cd "${CLAUDE_PROJECT_DIR:-$(dirname "$0")/../..}"
log() { echo "[session-start] $*" >&2; }

# --- paquets système
APT=()
dpkg -s libegl1 >/dev/null 2>&1 || APT+=(libegl1)
command -v ffmpeg >/dev/null || APT+=(ffmpeg)
[ -d /usr/share/fonts/opentype/inter ] || APT+=(fonts-inter)
if [ ${#APT[@]} -gt 0 ]; then
  log "apt : ${APT[*]}"
  apt-get install -y -q "${APT[@]}" >/dev/null 2>&1 || { apt-get update -q >/dev/null 2>&1; apt-get install -y -q "${APT[@]}" >/dev/null; }
fi

# --- bibliothèques Python
if ! python3 -c "import numpy, scipy, PIL, skia, soundfile, pyloudnorm, sherpa_onnx, num2words" 2>/dev/null; then
  log "pip : requirements.txt"
  pip install --break-system-packages -q -r requirements.txt 2>&1 | grep -v "Running pip as the 'root'" >&2 || true
  pip install --break-system-packages -q --no-deps num2words 2>&1 | grep -v "Running pip as the 'root'" >&2 || true
fi

# --- modèles (voix off, foule, contrôle qualité Whisper)
TTS=/tmp/tts
REL=https://github.com/k2-fsa/sherpa-onnx/releases/download
mkdir -p "$TTS"
for v in fr_FR-tom-medium fr_FR-siwis-medium fr_FR-upmc-medium; do
  if [ ! -f "$TTS/vits-piper-$v/$v.onnx" ]; then
    log "modèle voix $v"
    curl -sSfL --retry 4 "$REL/tts-models/vits-piper-$v.tar.bz2" | tar xj -C "$TTS"
  fi
done
if [ ! -f "$TTS/sherpa-onnx-whisper-turbo/turbo-encoder.int8.onnx" ]; then
  log "modèle Whisper turbo"
  curl -sSfL --retry 4 "$REL/asr-models/sherpa-onnx-whisper-turbo.tar.bz2" | tar xj -C "$TTS"
  rm -rf "$TTS/sherpa-onnx-whisper-turbo/test_wavs"
fi

python3 -c "import numpy, scipy, PIL, skia, soundfile, pyloudnorm, sherpa_onnx, num2words"
log "environnement prêt"
