# FREED roster character cards

Bigger, more detailed portraits for the same eight roster names as
`gmc/assets/portraits/`, styled after a reference the user supplied: chibi
(big-head/small-body) proportions, dithered coat shading, a Matrix code-rain
backdrop baked into the card, and green-rimmed sunglasses. Original designs,
not photographic likenesses.

- `<key>.png` — 448x608 (56x76 native, upscaled 8x, nearest-neighbour). The
  backdrop is part of the art, not transparent, so these suit a full-card
  reveal (a wizard-mode "crew freed" moment, an attract-mode slide) rather
  than a small in-line HUD icon — see `gmc/assets/portraits/` for that.

Regenerate after editing the palette or drawing helpers in
`tools/make_chibi_cards.py`:

```
python3 tools/make_chibi_cards.py
```
