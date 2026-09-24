"""Generates the FREED roster's pixel-art bust portraits.

Original character designs (not photographic likenesses) in a shared
low-resolution sprite style, for use on the game's HUD (roster, chapter
card). Regenerate after editing PALETTE or the drawing helpers below:

    python3 tools/make_pixel_portraits.py

Requires Pillow (``pip install pillow``).
"""

import argparse
import os

from PIL import Image

W, H = 24, 24
SCALE = 16
TRANSPARENT = (0, 0, 0, 0)


def ellipse(cx, cy, rx, ry, x, y):
    return ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1.0


def make_canvas():
    return [[TRANSPARENT for _ in range(W)] for _ in range(H)]


def set_px(canvas, x, y, color):
    if 0 <= x < W and 0 <= y < H:
        canvas[y][x] = color


def draw_face(canvas, skin, skin_shadow, cx=11.5, cy=10.5, rx=5.0, ry=5.5):
    for y in range(H):
        for x in range(W):
            if ellipse(cx, cy, rx, ry, x, y):
                col = skin_shadow if (x - cx) < -rx * 0.35 else skin
                set_px(canvas, x, y, col)


def draw_neck_and_shoulders(canvas, skin, outfit, outfit_shadow, collar=None):
    for y in range(15, 18):
        for x in range(9, 15):
            set_px(canvas, x, y, skin)
    if collar:
        for x in range(8, 16):
            set_px(canvas, x, 17, collar)
    top_y, bottom_y = 18, 23
    for y in range(top_y, bottom_y + 1):
        t = (y - top_y) / (bottom_y - top_y)
        half_w = 4 + t * 8
        left = int(round(11.5 - half_w))
        right = int(round(11.5 + half_w))
        for x in range(max(0, left), min(W, right + 1)):
            col = outfit_shadow if x < 11.5 - half_w * 0.55 else outfit
            set_px(canvas, x, y, col)


def draw_hair(canvas, style, hair, hair_shadow):
    if style == "bald":
        return
    if style in ("short", "natural", "slicked"):
        for y in range(3, 9):
            for x in range(W):
                if ellipse(11.5, 8.0, 5.6, 5.2, x, y) and y <= 8:
                    if not ellipse(11.5, 10.5, 4.4, 4.8, x, y) or y < 6:
                        col = hair_shadow if x < 8 else hair
                        set_px(canvas, x, y, col)
    elif style == "spiky":
        draw_hair(canvas, "short", hair, hair_shadow)
        for i, x in enumerate([7, 9, 11, 13, 15, 17]):
            peak = 2 if i % 2 == 0 else 1
            for y in range(peak, 5):
                set_px(canvas, x, y, hair if i % 2 == 0 else hair_shadow)
    elif style == "dread":
        draw_hair(canvas, "short", hair, hair_shadow)
        strand_cols = [4, 6, 18, 20]
        for x in strand_cols:
            length = 15 if x in (6, 18) else 12
            for y in range(6, length):
                if y % 5 != 4:
                    set_px(canvas, x, y, hair if x < 12 else hair_shadow)
    elif style == "bandana":
        for y in range(4, 7):
            for x in range(W):
                if ellipse(11.5, 8.0, 5.6, 5.2, x, y) and y <= 6:
                    set_px(canvas, x, y, hair)  # `hair` doubles as bandana colour here
        for x, y in [(6, 8), (7, 9), (16, 8), (17, 9)]:
            set_px(canvas, x, y, hair_shadow)


def draw_sunglasses(canvas, lens=(10, 10, 12), rim=(30, 200, 110)):
    for y in (9, 10):
        for x in range(7, 17):
            set_px(canvas, x, y, lens)
    for x in range(7, 17):
        set_px(canvas, x, 8, rim)
    set_px(canvas, 11, 9, rim)
    set_px(canvas, 12, 9, rim)
    set_px(canvas, 9, 9, (60, 230, 140))
    set_px(canvas, 15, 9, (60, 230, 140))


def draw_round_glasses(canvas, rim=(60, 55, 50), skin=(225, 185, 150)):
    for cx in (9.5, 14.5):
        for y in range(8, 12):
            for x in range(W):
                if ellipse(cx, 9.5, 2.1, 2.1, x, y):
                    if ellipse(cx, 9.5, 1.5, 1.5, x, y):
                        set_px(canvas, x, y, skin)
                    else:
                        set_px(canvas, x, y, rim)
        set_px(canvas, int(cx), 9, (35, 30, 30))
    set_px(canvas, 12, 9, rim)


def draw_eyes(canvas, pupil=(25, 20, 20)):
    set_px(canvas, 9, 10, pupil)
    set_px(canvas, 10, 10, pupil)
    set_px(canvas, 14, 10, pupil)
    set_px(canvas, 15, 10, pupil)


def draw_mouth(canvas, shadow):
    for x in range(10, 14):
        set_px(canvas, x, 13, shadow)


def draw_mustache(canvas, color):
    for x in range(8, 16):
        set_px(canvas, x, 12, color)


# One entry per FREED roster name (docs/11-rules-act-1.md, section 7, plus
# NIOBE and LINK, already wired into gmc/slides/base/base.tscn for Act II).
PALETTE = {
    "TRINITY": dict(
        skin=(235, 200, 172), skin_shadow=(205, 168, 142),
        hair="short", hair_color=(18, 16, 20), hair_shadow=(10, 9, 12),
        outfit=(20, 20, 24), outfit_shadow=(10, 10, 13),
        collar=(35, 210, 110),
        eyewear="sunglasses",
    ),
    "TANK": dict(
        skin=(96, 64, 48), skin_shadow=(70, 46, 34),
        hair="bald", hair_color=None, hair_shadow=None,
        outfit=(100, 116, 64), outfit_shadow=(70, 84, 42),
        collar=(150, 160, 110),
        eyewear=None,
    ),
    "DOZER": dict(
        skin=(176, 128, 92), skin_shadow=(140, 98, 68),
        hair="short", hair_color=(24, 20, 18), hair_shadow=(14, 12, 10),
        outfit=(140, 58, 46), outfit_shadow=(104, 40, 32),
        collar=(200, 150, 120),
        eyewear=None, mustache=(24, 20, 18),
    ),
    "SWITCH": dict(
        skin=(236, 208, 186), skin_shadow=(206, 176, 156),
        hair="spiky", hair_color=(228, 228, 236), hair_shadow=(190, 190, 202),
        outfit=(16, 16, 20), outfit_shadow=(8, 8, 11),
        collar=(180, 180, 195),
        eyewear="sunglasses",
    ),
    "APOC": dict(
        skin=(112, 76, 58), skin_shadow=(82, 54, 40),
        hair="dread", hair_color=(30, 24, 22), hair_shadow=(18, 14, 13),
        outfit=(18, 18, 22), outfit_shadow=(9, 9, 12),
        collar=(35, 210, 110),
        eyewear="sunglasses",
    ),
    "MOUSE": dict(
        skin=(232, 190, 158), skin_shadow=(200, 160, 130),
        hair="natural", hair_color=(96, 62, 40), hair_shadow=(66, 42, 26),
        outfit=(150, 140, 96), outfit_shadow=(112, 104, 70),
        collar=(190, 182, 140),
        eyewear="round",
    ),
    "NIOBE": dict(
        skin=(118, 80, 62), skin_shadow=(86, 56, 42),
        hair="slicked", hair_color=(20, 17, 19), hair_shadow=(11, 9, 11),
        outfit=(18, 16, 20), outfit_shadow=(9, 8, 11),
        collar=(35, 210, 110),
        eyewear="sunglasses",
    ),
    "LINK": dict(
        skin=(104, 72, 56), skin_shadow=(76, 50, 38),
        hair="bandana", hair_color=(210, 96, 32), hair_shadow=(24, 20, 18),
        outfit=(96, 100, 106), outfit_shadow=(66, 70, 76),
        collar=(210, 96, 32),
        eyewear=None,
    ),
}


def render(spec):
    canvas = make_canvas()
    draw_neck_and_shoulders(canvas, spec["skin"], spec["outfit"], spec["outfit_shadow"], spec["collar"])
    draw_face(canvas, spec["skin"], spec["skin_shadow"])
    if spec["hair"] != "bald":
        draw_hair(canvas, spec["hair"], spec["hair_color"], spec["hair_shadow"])
    if spec["eyewear"] == "sunglasses":
        draw_sunglasses(canvas)
    elif spec["eyewear"] == "round":
        draw_round_glasses(canvas, skin=spec["skin"])
    else:
        draw_eyes(canvas)
    if "mustache" in spec:
        draw_mustache(canvas, spec["mustache"])
    draw_mouth(canvas, spec["skin_shadow"])
    return canvas


def to_image(canvas):
    img = Image.new("RGBA", (W, H), TRANSPARENT)
    for y in range(H):
        for x in range(W):
            img.putpixel((x, y), canvas[y][x])
    return img


def main():
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    default_out = os.path.join(repo_root, "gmc", "assets", "portraits")

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default=default_out, help="output directory (default: gmc/assets/portraits)")
    args = parser.parse_args()

    native_dir = os.path.join(args.out, "native")
    os.makedirs(native_dir, exist_ok=True)

    for key, spec in PALETTE.items():
        img = to_image(render(spec))
        img.save(os.path.join(native_dir, f"{key.lower()}_24x24.png"))
        img.resize((W * SCALE, H * SCALE), Image.NEAREST).save(os.path.join(args.out, f"{key.lower()}.png"))
        print(f"wrote {key.lower()}.png")


if __name__ == "__main__":
    main()
