#!/usr/bin/env python3
"""Compare the film-clip manifest against what is actually on disk.

Clips are deliberately outside version control (see gmc/video/README.md), so a
fresh checkout has none of them. This says what is missing, what is present but
unlisted, and what is in a format Godot cannot open.

Exits 1 if any listed clip is missing, so it can gate a build.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
VIDEO_DIR = REPO / "gmc" / "video"
MANIFEST = VIDEO_DIR / "manifest.txt"
SAMPLE = REPO / "gmc" / "slides" / "attract" / "assets" / "matrixrain.ogv"

# Godot 4 exposes exactly one VideoStream subclass, VideoStreamTheora, so .ogv
# is the only format the engine can open. Anything else here is dead weight.
PLAYABLE = ".ogv"


def read_manifest() -> list[str]:
    if not MANIFEST.exists():
        sys.exit(f"No manifest at {MANIFEST}")
    names = []
    for line in MANIFEST.read_text().splitlines():
        line = line.split("#", 1)[0].strip()
        if line:
            names.append(line)
    return names


def main() -> int:
    if not VIDEO_DIR.is_dir():
        sys.exit(f"No clip folder at {VIDEO_DIR}")

    listed = read_manifest()
    on_disk = {p.stem: p for p in VIDEO_DIR.iterdir() if p.suffix == PLAYABLE}
    unplayable = [
        p for p in VIDEO_DIR.iterdir()
        if p.is_file() and p.suffix not in (PLAYABLE, ".md", ".txt")
    ]

    present = [n for n in listed if n in on_disk]
    missing = [n for n in listed if n not in on_disk]
    unlisted = sorted(set(on_disk) - set(listed))

    print(f"Clip folder: {VIDEO_DIR}")
    print(f"Listed: {len(listed)}   present: {len(present)}   missing: {len(missing)}")

    if present:
        print("\nPresent:")
        for name in present:
            size_mb = on_disk[name].stat().st_size / (1024 * 1024)
            print(f"  {name:<32} {size_mb:7.1f} MB")

    if missing:
        print("\nMissing (listed in the manifest, not on disk):")
        for name in missing:
            print(f"  {name}")
        if "matrixrain" in missing and SAMPLE.exists():
            rel = SAMPLE.relative_to(REPO)
            print(f"\n  The sample clip is in the repo. Copy it in with:")
            print(f"    cp {rel} gmc/video/")

    if unlisted:
        print("\nPresent but not in the manifest:")
        for name in unlisted:
            print(f"  {name}")
        print("  Add these to gmc/video/manifest.txt, or delete them.")

    if unplayable:
        print("\nGodot cannot open these. Re-encode to .ogv or remove them:")
        for path in unplayable:
            print(f"  {path.name}")

    if missing:
        print("\nFAIL: clips are missing.")
        return 1
    print("\nOK: every listed clip is present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
