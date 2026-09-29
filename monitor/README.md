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

## The playfield image: a placeholder, not this machine's real layout

`monitor/playfield.jpg` is a user-supplied stylised render of a generic
Matrix-themed playfield (two flippers, two slings, a handful of standups, two
ramps to a centre feature). **It is not a photo of this machine and does not
match its actual switch/device layout** in `config/config.yaml` and
`config/playfield_pending.yaml` — this machine has, among others, a trough,
five-bank and three-bank drop targets, three pop-up "agent" assemblies, four
ramps, an upper playfield with three standups, and a platform toy with a
magnet, none of which appear on this image. Per `docs/08-this-machine.md`,
the cabinet I/O board was still unwired as of 2026-09-20, so a real photo of
the built playfield likely doesn't exist yet either.

Treat device positions dragged onto this image as approximate placeholders
for exercising switch logic now. **Replace `monitor/playfield.jpg` with a
real photo once the playfield is built**, or sooner if a truer stand-in shows
up (the Dropbox design folder in `docs/10-dropbox-design-files.md` has
`Matrix v1 6/v1 7 Blueprint.png` and the draft playfield art PSD/PNG, but this
session has no Dropbox link or credentials to fetch them). Swapping the file
later won't invalidate `monitor/monitor.yaml`; positions are saved as
percentages, so they'll just want re-dragging onto the new image.

## Setup

1. Install Monitor (separate from MPF itself): `pip install mpf-monitor`.
2. `monitor/playfield.jpg` is already in place (see above).
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
