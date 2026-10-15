#!/bin/bash
# Chaîne de production complète : voix -> timeline -> mixage -> rendu -> export + contrôle qualité.
# Usage : production/run_production.sh   (journal : build/production.log)
set -e
cd "$(dirname "$0")/.."
export LD_LIBRARY_PATH=/opt/egl GRAIN=${GRAIN:-0.035}
mkdir -p build
LOG=build/production.log
step() { echo "=== $1 — $(date)" >> $LOG; }
: > $LOG
step "VOIX";            python3 production/voice.py long >> $LOG 2>&1; python3 production/voice.py tiktok >> $LOG 2>&1
step "TIMELINE";        python3 production/timeline.py long >> $LOG 2>&1; python3 production/timeline.py tiktok >> $LOG 2>&1
step "MIXAGE";          python3 production/mix.py long >> $LOG 2>&1; python3 production/mix.py tiktok >> $LOG 2>&1
step "RENDU TIKTOK";    python3 production/render.py tiktok --video --scale 1 --jobs 4 --crf 16M --preset slow >> $LOG 2>&1
step "EXPORT TIKTOK";   python3 production/finalize.py tiktok >> $LOG 2>&1
step "RENDU MASTER 4K"; python3 production/render.py long --video --scale 2 --jobs 4 --crf 18 --preset fast >> $LOG 2>&1
step "EXPORT MASTER";   python3 production/finalize.py long >> $LOG 2>&1
step "APERÇU";          mkdir -p exports/preview && ffmpeg -y -loglevel error -i exports/tiktok/france_rapport_de_force_TIKTOK.mp4 \
                          -vf scale=720:1280 -c:v libx264 -preset slow -b:v 2200k -maxrate 2600k -bufsize 5M -c:a aac -b:a 128k \
                          -movflags +faststart exports/preview/TIKTOK_apercu_720p.mp4 >> $LOG 2>&1
step "TERMINÉ"
