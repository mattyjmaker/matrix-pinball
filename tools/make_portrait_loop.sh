#!/usr/bin/env bash
# Turn an AI-generated "living portrait" clip into a looping Theora file for
# the video_clip widget: centre-crop to a fixed portrait frame, apply one
# shared green grade so all eight crew read as a set, play forward then
# backward so the end meets the start, and encode to Ogg Theora (the only
# video format Godot 4 plays).
#
#   tools/make_portrait_loop.sh [options] <input-video> <name>
#
# Writes gmc/video/portrait_<name>.ogv. That folder is outside version control
# (see gmc/video/README.md), so the output stays local.
#
# Options:
#   --size WxH       output size (default 480x640)
#   --crop W:H:X:Y   explicit ffmpeg crop instead of the centre crop
#   --fps N          output frame rate (default 30)
#   --quality N      Theora quality, 0 to 10 (default 8)
#   --no-grade       skip the green grade
#   --no-pingpong    keep the clip as-is (use when the AI tool already made
#                    the last frame match the first)
#   --out DIR        output folder (default gmc/video)

set -euo pipefail

usage() { sed -n '2,23p' "$0" | sed 's/^# \{0,1\}//'; exit "${1:-0}"; }

REPO="$(cd "$(dirname "$0")/.." && pwd)"
SIZE="480x640"
CROP=""
FPS=30
QUALITY=8
GRADE=1
PINGPONG=1
OUT_DIR="$REPO/gmc/video"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --size) SIZE="$2"; shift 2 ;;
    --crop) CROP="$2"; shift 2 ;;
    --fps) FPS="$2"; shift 2 ;;
    --quality) QUALITY="$2"; shift 2 ;;
    --no-grade) GRADE=0; shift ;;
    --no-pingpong) PINGPONG=0; shift ;;
    --out) OUT_DIR="$2"; shift 2 ;;
    -h|--help) usage 0 ;;
    -*) echo "Unknown option: $1" >&2; usage 1 ;;
    *) break ;;
  esac
done

[[ $# -eq 2 ]] || usage 1
INPUT="$1"
NAME="$2"

[[ -f "$INPUT" ]] || { echo "No such file: $INPUT" >&2; exit 1; }
[[ "$NAME" =~ ^[a-z0-9_]+$ ]] || { echo "Name must be lower case letters, digits and underscores: $NAME" >&2; exit 1; }
[[ "$SIZE" =~ ^([0-9]+)x([0-9]+)$ ]] || { echo "--size must be WxH, e.g. 480x640" >&2; exit 1; }
W="${BASH_REMATCH[1]}"
H="${BASH_REMATCH[2]}"
command -v ffmpeg >/dev/null && command -v ffprobe >/dev/null || { echo "ffmpeg and ffprobe are required" >&2; exit 1; }

if [[ -n "$CROP" ]]; then
  CROP_FILTER="crop=$CROP"
else
  CROP_FILTER="crop='min(iw,ih*$W/$H)':'min(ih,iw*$H/$W)'"
fi

FILTERS="$CROP_FILTER,scale=$W:$H:flags=lanczos,setsar=1,fps=$FPS"
if [[ "$GRADE" -eq 1 ]]; then
  FILTERS="$FILTERS,eq=saturation=0.6:contrast=1.08,colorchannelmixer=rr=0.82:gg=1.04:bb=0.74"
fi

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
STAGE="$TMP/stage.mkv"

# Pass 1: crop, scale, grade and resample to a lossless intermediate, so the
# frame count used for the ping-pong trim below is exact.
ffmpeg -hide_banner -loglevel error -y -i "$INPUT" -vf "$FILTERS" -an -c:v ffv1 "$STAGE"

FRAMES="$(ffprobe -v error -select_streams v:0 -count_frames \
  -show_entries stream=nb_read_frames -of csv=p=0 "$STAGE")"

mkdir -p "$OUT_DIR"
OUTPUT="$OUT_DIR/portrait_$NAME.ogv"

if [[ "$PINGPONG" -eq 1 && "$FRAMES" -ge 3 ]]; then
  # The reversed half drops its first and last frames: they duplicate the
  # forward half's last frame and the loop's first frame, and a held frame
  # at either turn reads as a stutter.
  LAST=$((FRAMES - 1))
  ffmpeg -hide_banner -loglevel error -y -i "$STAGE" -filter_complex \
    "[0:v]split[f][b];[b]reverse,trim=start_frame=1:end_frame=$LAST,setpts=PTS-STARTPTS[r];[f][r]concat=n=2:v=1:a=0[v]" \
    -map "[v]" -c:v libtheora -q:v "$QUALITY" "$OUTPUT"
  OUT_FRAMES=$((FRAMES * 2 - 2))
else
  ffmpeg -hide_banner -loglevel error -y -i "$STAGE" -c:v libtheora -q:v "$QUALITY" "$OUTPUT"
  OUT_FRAMES="$FRAMES"
fi

# Counted from the lossless stage: ffprobe undercounts frames in Ogg files.
echo "Wrote $OUTPUT (${W}x${H}, $OUT_FRAMES frames at $FPS fps)"
echo "Add 'portrait_$NAME' to gmc/video/manifest.txt if it is not listed."
