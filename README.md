# Motion design — « France : rapport de force »

Chaîne de production Python/Skia/FFmpeg qui génère deux vidéos à partir de `assets/data/` :
un master 4K (`exports/master/`) et une version TikTok 1080×1920 (`exports/tiktok/`).

## Environnement (automatique)

Dans une session Claude Code cloud, `.claude/hooks/session-start.sh` s'exécute au démarrage
de chaque conversation (déclaré dans `.claude/settings.json`) et installe ce qui manque :

| Élément | Rôle |
|---|---|
| numpy, scipy, pillow | calcul, audio, images |
| skia-python + libEGL | dessin du motion design |
| soundfile, pyloudnorm | lecture/écriture WAV, loudness -14 LUFS |
| num2words | nombres → texte prononcé |
| sherpa-onnx | voix off Piper et transcription Whisper |
| FFmpeg, police Inter | encodage vidéo, typographie |
| `/tmp/tts/vits-piper-fr_FR-{tom,siwis,upmc}-medium` | voix FR (narration + foule) |
| `/tmp/tts/sherpa-onnx-whisper-turbo` | contrôle qualité de la voix |

En local : `CLAUDE_CODE_REMOTE=true .claude/hooks/session-start.sh`.

## Lancer

```bash
production/run_production.sh          # tout : voix → timeline → mixage → rendus → exports → aperçu
tail -f build/production.log          # suivre l'avancement
```

Étape par étape (`long` ou `tiktok`) :

```bash
python3 production/voice.py tiktok     # voix off -> assets/voice/tiktok/
python3 production/timeline.py tiktok  # timeline + sous-titres
python3 production/mix.py tiktok       # bande son -> build/tiktok/mix_final.wav
python3 production/render.py tiktok --stills 5,30,60 --scale 0.5   # images de contrôle -> build/stills/
python3 production/render.py tiktok --video --scale 1 --jobs 4      # vidéo
python3 production/finalize.py tiktok  # mux audio/vidéo + QC
```
