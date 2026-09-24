# FREED roster portraits

Pixel-art bust portraits for the eight names in the roster (`docs/11-rules-act-1.md`,
section 7, plus NIOBE and LINK, already wired into `gmc/slides/base/base.tscn`
for Act II). Original designs, not photographic likenesses: a shared low-res
sprite style with a Matrix-green accent line, distinguished by outfit,
hairstyle and eyewear rather than by copying the films' character art.

- `<key>.png` — 384x384, nearest-neighbour upscaled from a 24x24 sprite, transparent
  background. Use this in slides/widgets (for example a `TextureRect` on
  `chapter_card.tscn` or next to each `Roster` entry in `base.tscn`).
- `native/<key>_24x24.png` — the raw 1:1 sprite, for a DMD-style crop or custom
  scaling.

Regenerate after editing the palette or drawing helpers in
`tools/make_pixel_portraits.py`:

```
python3 tools/make_pixel_portraits.py
```
