#!/usr/bin/env bash
# Turn a 1080x1920 news story card into an 8-second Instagram Reel (MP4, H.264 + AAC).
# Usage: tools/make_reel.sh news/<date>/story.jpg news/<date>/reel.mp4
# Audio: uses a random track from audio/*.mp3 or audio/*.m4a if any exist (royalty-free only),
# otherwise a silent AAC track (Instagram requires an audio stream to be present for some players).
set -euo pipefail
IN="$1"; OUT="$2"; DUR=8; FPS=30
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TRACK=""
shopt -s nullglob
tracks=("$ROOT"/audio/*.mp3 "$ROOT"/audio/*.m4a)
if [ ${#tracks[@]} -gt 0 ]; then TRACK="${tracks[$RANDOM % ${#tracks[@]}]}"; fi

# Slow push-in: scale up 2x for smooth zoom, zoom from 1.00 to ~1.06 over the clip, centred.
VF="scale=2160:3840,zoompan=z='min(1+0.0075*on/${FPS},1.06)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=$((DUR*FPS)):s=1080x1920:fps=${FPS},format=yuv420p"

if [ -n "$TRACK" ]; then
  ffmpeg -y -loglevel error -loop 1 -i "$IN" -i "$TRACK" -vf "$VF" -t $DUR \
    -c:v libx264 -preset veryfast -profile:v high -crf 20 -r $FPS \
    -c:a aac -b:a 128k -ar 44100 -af "afade=t=in:d=0.5,afade=t=out:st=$((DUR-1)):d=1" \
    -shortest -movflags +faststart "$OUT"
else
  ffmpeg -y -loglevel error -loop 1 -i "$IN" -f lavfi -i anullsrc=channel_layout=stereo:sample_rate=44100 \
    -vf "$VF" -t $DUR -c:v libx264 -preset veryfast -profile:v high -crf 20 -r $FPS \
    -c:a aac -b:a 128k -shortest -movflags +faststart "$OUT"
fi
echo "reel written: $OUT${TRACK:+ (audio: $(basename "$TRACK"))}"
