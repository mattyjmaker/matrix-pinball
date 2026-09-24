"""Generates the FREED roster's chibi-style character cards.

Original character designs (not photographic likenesses): big-head/
small-body proportions, dithered coat shading and a Matrix code-rain
backdrop baked into each card, styled after a reference the user supplied
(dark trenchcoats, green-rimmed sunglasses, code rain). Regenerate after
editing PALETTE or the drawing helpers below:

    python3 tools/make_chibi_cards.py

Requires Pillow (``pip install pillow``).
"""

import argparse
import os
import random

from PIL import Image

W, H = 56, 76
SCALE = 8


def ellipse(cx, cy, rx, ry, x, y):
    return ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1.0


def mix(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


def set_px(canvas, x, y, color):
    if 0 <= x < W and 0 <= y < H:
        canvas[y][x] = tuple(color) if len(color) == 4 else (*color, 255)


def get_px(canvas, x, y):
    if 0 <= x < W and 0 <= y < H:
        return canvas[y][x]
    return (0, 0, 0, 0)


# ---------------------------------------------------------------- backdrop

def draw_rain(canvas, seed, base=(2, 8, 4), glow=(70, 230, 120), bright=(190, 255, 200)):
    rng = random.Random(seed)
    for x in range(W):
        col_shift = rng.uniform(-4, 4)
        streaks = []
        cursor = rng.randint(-H, 0)
        while cursor < H:
            length = rng.randint(4, 14)
            streaks.append((cursor, length))
            cursor += length + rng.randint(2, 10)
        for y in range(H):
            v = y / H
            bg = mix((base[0] + col_shift, base[1] + col_shift * 1.5, base[2] + col_shift), (0, 0, 0), v * 0.5)
            px = tuple(max(0, min(255, int(c))) for c in bg)
            in_streak = False
            for start, length in streaks:
                if start <= y < start + length:
                    t = (y - start) / length
                    px = bright if t < 0.15 else mix(glow, base, min(1.0, (t - 0.15) / 0.85))
                    in_streak = True
                    break
            if not in_streak and rng.random() < 0.02:
                px = mix(glow, base, 0.4)
            set_px(canvas, x, y, px)


def vignette(canvas, strength=0.35):
    cx, cy = W / 2, H * 0.42
    maxd = ((W / 2) ** 2 + (H * 0.6) ** 2) ** 0.5
    for y in range(H):
        for x in range(W):
            d = (((x - cx) ** 2 + (y - cy) ** 2) ** 0.5) / maxd
            if d > 0.55:
                t = min(1.0, (d - 0.55) / 0.45) * strength
                r, g, b, _a = get_px(canvas, x, y)
                set_px(canvas, x, y, mix((r, g, b), (0, 0, 0), t))


# ------------------------------------------------------------------ figure

def draw_coat(canvas, cx, outfit, outfit_dark, shoulder_y, hip_y, shoulder_w, flare_w):
    for y in range(shoulder_y, hip_y):
        t = (y - shoulder_y) / max(1, (hip_y - shoulder_y))
        half = shoulder_w + (flare_w - shoulder_w) * (t ** 1.6)
        left, right = int(cx - half), int(cx + half)
        for x in range(left, right + 1):
            edge = (x - (cx - half)) / max(1, (right - left))
            shade = outfit_dark if edge < 0.22 or edge > 0.93 else outfit
            if 0.40 < edge < 0.46:
                shade = mix(outfit, (0, 0, 0), 0.35)  # centre seam
            set_px(canvas, x, y, shade)
    # jagged flared hem for a "coat caught mid-stride" edge
    hem_rng = random.Random(int(cx * 97) + hip_y)
    for x in range(int(cx - flare_w), int(cx + flare_w) + 1):
        jag = hem_rng.randint(0, 2)
        for y in range(hip_y - jag, hip_y):
            set_px(canvas, x, y, (0, 0, 0, 0))


def draw_arms(canvas, cx, outfit_dark, skin, shoulder_y, sleeve_len, shoulder_w):
    for side in (-1, 1):
        ax = cx + side * (shoulder_w + 2)
        for y in range(shoulder_y + 2, shoulder_y + sleeve_len):
            for dx in range(-3, 4):
                set_px(canvas, int(ax + dx * 0.6), y, outfit_dark)
        for y in range(shoulder_y + sleeve_len, shoulder_y + sleeve_len + 3):
            for dx in range(-2, 3):
                set_px(canvas, int(ax + dx * 0.6), y, skin)


def draw_head(canvas, cx, cy, skin, skin_shadow, r=11):
    # smooth per-row silhouette: a circular crown tapering to a rounded
    # chibi chin, so there is no post-hoc clipping to leave hard notches
    top, bottom = cy - r, cy + r * 1.05
    for y in range(int(top), int(bottom) + 1):
        if y <= cy:
            dy = (cy - y) / r
            half = r * (1 - dy * dy) ** 0.5 if dy <= 1 else 0
        else:
            f = (y - cy) / (bottom - cy)
            half = r * (1 - 0.4 * f)
        for x in range(int(cx - half), int(cx + half) + 1):
            shade = skin_shadow if (x - cx) < -half * 0.35 else skin
            set_px(canvas, x, y, shade)


def draw_hair(canvas, style, cx, cy, r, hair, hair_dark):
    top = int(cy - r)
    if style == "bald":
        for x in range(int(cx - r * 0.5), int(cx + r * 0.5)):
            set_px(canvas, x, top + 2, mix(hair, (255, 255, 255), 0.35))
        return
    # cap: a crown slightly larger than the head, covering down to the
    # brow line, using the same smooth-silhouette shape as draw_head
    cap_r = r * 1.08
    cap_bottom = cy - r * 0.15
    for y in range(top - 1, int(cap_bottom) + 1):
        dy = (cy - y) / cap_r
        if dy > 1:
            continue
        half = cap_r * (1 - dy * dy) ** 0.5
        for x in range(int(cx - half), int(cx + half) + 1):
            shade = hair_dark if x < cx - half * 0.3 else hair
            set_px(canvas, x, y, shade)
    if style == "spiky":
        rng = random.Random(7)
        for i, x in enumerate(range(int(cx - r), int(cx + r), 3)):
            peak = top - rng.randint(2, 5)
            for y in range(peak, top + 2):
                set_px(canvas, x, y, hair if i % 2 == 0 else hair_dark)
    elif style == "dread":
        for side in (-1, 1):
            xs = range(int(cx - r * 1.05), int(cx - r * 0.5)) if side < 0 else range(int(cx + r * 0.5), int(cx + r * 1.05))
            for i, x in enumerate(xs):
                length = 20 - (i % 3) * 3
                for y in range(int(cy - r * 0.1), int(cy - r * 0.1) + length):
                    if y % 6 < 4:
                        set_px(canvas, x, y, hair if i % 2 else hair_dark)
    elif style == "bandana":
        for x in range(int(cx - r * 1.05), int(cx + r * 1.05) + 1):
            for y in range(top + 1, top + 5):
                set_px(canvas, x, y, hair)
        for y in range(top + 2, top + 9):
            set_px(canvas, int(cx + r * 1.0), y, hair)
            set_px(canvas, int(cx + r * 1.0) + 1, y + 1, hair_dark)


def draw_sunglasses(canvas, cx, cy, r, lens=(8, 9, 11), rim=(35, 220, 120), glint=(120, 255, 190)):
    y0 = int(cy - r * 0.05)
    for y in range(y0, y0 + 3):
        for x in range(int(cx - r * 0.7), int(cx + r * 0.7) + 1):
            set_px(canvas, x, y, lens)
    for x in range(int(cx - r * 0.75), int(cx + r * 0.75) + 1):
        set_px(canvas, x, y0 - 1, rim)
    set_px(canvas, int(cx - 1), y0, rim)
    set_px(canvas, int(cx), y0, rim)
    set_px(canvas, int(cx - r * 0.45), y0, glint)
    set_px(canvas, int(cx + r * 0.35), y0, glint)


def draw_round_glasses(canvas, cx, cy, r, skin, rim=(50, 45, 42)):
    y0 = cy - r * 0.05
    for ex in (cx - r * 0.4, cx + r * 0.4):
        for y in range(int(y0 - 3), int(y0 + 4)):
            for x in range(int(ex - 3), int(ex + 4)):
                if ellipse(ex, y0, 3, 3, x, y):
                    shade = skin if ellipse(ex, y0, 2, 2, x, y) else rim
                    set_px(canvas, x, y, shade)
        set_px(canvas, int(ex), int(y0), (30, 26, 24))
    set_px(canvas, int(cx), int(y0), rim)


def draw_eyes(canvas, cx, cy, r, pupil=(20, 16, 16)):
    for ex in (cx - r * 0.4, cx + r * 0.4):
        set_px(canvas, int(ex), int(cy), pupil)
        set_px(canvas, int(ex) + 1, int(cy), pupil)


def draw_mouth(canvas, cx, cy, r, shadow):
    for x in range(int(cx - r * 0.25), int(cx + r * 0.25) + 1):
        set_px(canvas, x, int(cy + r * 0.45), shadow)


def draw_mustache(canvas, cx, cy, r, color):
    for x in range(int(cx - r * 0.55), int(cx + r * 0.55) + 1):
        set_px(canvas, x, int(cy + r * 0.32), color)


def draw_collar(canvas, cx, neck_y, color, half_w=6):
    for x in range(int(cx - half_w), int(cx + half_w) + 1):
        set_px(canvas, x, neck_y, color)
        set_px(canvas, x, neck_y + 1, mix(color, (0, 0, 0), 0.25))


# One entry per FREED roster name (docs/11-rules-act-1.md, section 7, plus
# NIOBE and LINK, already wired into gmc/slides/base/base.tscn for Act II).
PALETTE = {
    "TRINITY": dict(
        skin=(235, 200, 172), skin_shadow=(205, 168, 142),
        hair="slick_part", hair_color=(18, 16, 20), hair_shadow=(10, 9, 12),
        outfit=(24, 24, 28), outfit_dark=(11, 11, 14),
        collar=(35, 210, 110), eyewear="sunglasses",
        rain_seed=1,
    ),
    "TANK": dict(
        skin=(100, 66, 50), skin_shadow=(72, 47, 36),
        hair="bald", hair_color=(20, 16, 14), hair_shadow=(12, 10, 9),
        outfit=(104, 120, 66), outfit_dark=(66, 78, 40),
        collar=(150, 160, 110), eyewear=None,
        rain_seed=2,
    ),
    "DOZER": dict(
        skin=(180, 130, 94), skin_shadow=(142, 100, 70),
        hair="short", hair_color=(26, 21, 19), hair_shadow=(15, 12, 11),
        outfit=(146, 60, 47), outfit_dark=(100, 38, 30),
        collar=(200, 150, 120), eyewear=None, mustache=(26, 21, 19),
        rain_seed=3,
    ),
    "SWITCH": dict(
        skin=(236, 208, 186), skin_shadow=(206, 176, 156),
        hair="spiky", hair_color=(230, 230, 238), hair_shadow=(188, 188, 200),
        outfit=(18, 18, 22), outfit_dark=(8, 8, 11),
        collar=(190, 190, 205), eyewear="sunglasses",
        rain_seed=4,
    ),
    "APOC": dict(
        skin=(114, 78, 60), skin_shadow=(84, 55, 41),
        hair="dread", hair_color=(30, 24, 22), hair_shadow=(17, 13, 12),
        outfit=(20, 20, 24), outfit_dark=(9, 9, 12),
        collar=(35, 210, 110), eyewear="sunglasses",
        rain_seed=5,
    ),
    "MOUSE": dict(
        skin=(232, 190, 158), skin_shadow=(200, 160, 130),
        hair="short", hair_color=(98, 63, 41), hair_shadow=(67, 43, 27),
        outfit=(150, 140, 96), outfit_dark=(106, 98, 64),
        collar=(190, 182, 140), eyewear="round",
        rain_seed=6,
    ),
    "NIOBE": dict(
        skin=(120, 82, 63), skin_shadow=(87, 57, 43),
        hair="slick_part", hair_color=(20, 17, 19), hair_shadow=(11, 9, 11),
        outfit=(18, 16, 20), outfit_dark=(8, 7, 10),
        collar=(35, 210, 110), eyewear="sunglasses",
        rain_seed=7,
    ),
    "LINK": dict(
        skin=(106, 73, 57), skin_shadow=(77, 51, 39),
        hair="bandana", hair_color=(212, 98, 33), hair_shadow=(24, 20, 18),
        outfit=(98, 102, 108), outfit_dark=(64, 68, 74),
        collar=(212, 98, 33), eyewear=None,
        rain_seed=8,
    ),
}


def render(spec):
    canvas = [[(0, 0, 0, 0) for _ in range(W)] for _ in range(H)]
    draw_rain(canvas, spec["rain_seed"])

    cx = W / 2
    head_cy = H * 0.27
    r = 11
    shoulder_y = int(head_cy + r * 1.15)
    hip_y = H - 2

    draw_coat(canvas, cx, spec["outfit"], spec["outfit_dark"], shoulder_y, hip_y,
              shoulder_w=r * 1.15, flare_w=r * 1.9)
    draw_arms(canvas, cx, spec["outfit_dark"], spec["skin"], shoulder_y, sleeve_len=14, shoulder_w=int(r * 1.15))
    draw_collar(canvas, cx, shoulder_y - 1, spec["collar"])
    draw_head(canvas, cx, head_cy, spec["skin"], spec["skin_shadow"], r=r)
    draw_hair(canvas, spec["hair"], cx, head_cy, r, spec["hair_color"], spec["hair_shadow"])

    if spec["eyewear"] == "sunglasses":
        draw_sunglasses(canvas, cx, head_cy, r)
    elif spec["eyewear"] == "round":
        draw_round_glasses(canvas, cx, head_cy, r, spec["skin"])
    else:
        draw_eyes(canvas, cx, head_cy, r)
    if "mustache" in spec:
        draw_mustache(canvas, cx, head_cy, r, spec["mustache"])
    draw_mouth(canvas, cx, head_cy, r, spec["skin_shadow"])

    vignette(canvas)
    return canvas


def to_image(canvas):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for y in range(H):
        for x in range(W):
            img.putpixel((x, y), canvas[y][x])
    return img


def main():
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    default_out = os.path.join(repo_root, "gmc", "assets", "cards")

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default=default_out, help="output directory (default: gmc/assets/cards)")
    args = parser.parse_args()

    os.makedirs(args.out, exist_ok=True)
    for key, spec in PALETTE.items():
        img = to_image(render(spec))
        img.resize((W * SCALE, H * SCALE), Image.NEAREST).save(os.path.join(args.out, f"{key.lower()}.png"))
        print(f"wrote {key.lower()}.png")


if __name__ == "__main__":
    main()
