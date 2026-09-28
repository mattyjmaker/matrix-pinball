# MPF Monitor

MPF Monitor is a separate PyQt6 tool that connects to a running MPF over BCP
(`localhost:5051`) and shows switches, lights, modes and variables. You can
drag each switch and light onto a photo of the playfield, then:

- **left-click** a switch to tap it
- **right-click** a switch to toggle/hold it
- watch lights show their live colour

It is not a physics simulator, and it does not replace the `[keyboard]`
mappings in `gmc.cfg` (those still work at the same time). Its advantage here
is coverage: `gmc.cfg [keyboard]` only maps the switches someone bothered to
assign a key to, so switches such as the five-bank, the three standups on the
upper playfield, the platform targets, the slings and the pop bumper area
currently have **no** keyboard mapping at all. Monitor reaches every switch,
by clicking its position on the playfield image, with nothing to memorise.
See `docs/01-install-running-tools.md` section 7 for the full reference this
was drawn from.

## What's needed: a playfield photo

Monitor requires `monitor/playfield.jpg` to exist before device positions
mean anything (it drags devices onto that image and saves their positions as
percentages in `monitor/monitor.yaml`). **This folder does not have one yet**,
and none could be sourced automatically:

- No playfield photo exists anywhere in this repository.
- The Dropbox design folder (`docs/10-dropbox-design-files.md`) has candidate
  art (`Drawings/Playfield/Playfield v79.dxf`, `Matrix v1 6/v1 7
  Blueprint.png`, the draft playfield art PSD/PNG) but this session has no
  Dropbox link or credentials to fetch them.
- Per `docs/08-this-machine.md`, the cabinet I/O board was still unwired as
  of 2026-09-20, so a photo of the actual physical playfield as currently
  built may not exist yet either.
- `*.jpg`/`*.png` are Git LFS-tracked (`.gitattributes`), and `git-lfs` is not
  installed in this container, so even a placeholder image couldn't be
  committed correctly from here.

**To finish setup:** add a JPG or PNG of the playfield (a phone photo of the
bare playfield is fine — it doesn't need to be finished or wired) as
`monitor/playfield.jpg`, or run `mpf monitor -i your_image.jpg` to point at a
differently named file. A blueprint or the draft playfield art from Dropbox
works too as a stand-in until a real photo exists.

## Setup

1. Install Monitor (separate from MPF itself): `pip install mpf-monitor`.
2. Add `monitor/playfield.jpg` (see above).
3. Run `mpf monitor` from the repo root (the machine folder).
4. Start MPF in another terminal, e.g. `mpf -Xt` (smart_virtual platform,
   recommended with Monitor since it simulates ball devices; matches the
   `virtual_platform_start_active_switches` trough seeding already in
   `config/config.yaml`).
5. In Monitor's Inspector window, use the "Monitor" tab to show the Device
   window, then drag each switch/light onto its position on the photo.

Device positions save to `monitor/monitor.yaml` — commit that once it's
populated, it's useful project state. Window layout saves to
`monitor/settings.ini`; per the MPF docs, don't commit that one (already
ignored, see `.gitignore`).
