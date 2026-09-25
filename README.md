# matrix-pinball

Matrix Pinball game code for the Mission Pinball Framework (MPF) with the
Godot Media Controller (GMC) and FAST Pinball Neuron hardware.

## Versions this repo targets

| Component | Version | Notes |
| --- | --- | --- |
| MPF | 0.80.x | Requires Python 3.10 to 3.14 |
| GMC addon | 1.0.0 | Vendored in `gmc/addons/mpf-gmc`. Latest release; verified running on Godot 4.7.2 |
| Godot | 4.7.2 (latest stable) | Download from godotengine.org, not the distro package. The project is tagged `4.7`. |
| FAST hardware | Neuron, FP-EXP-2000, FP-CAB-0001, FP-I/O-1616, FP-I/O-3208 | Supported by mainline MPF. No FAST fork needed. FAST's own MPF docs and starter configs are at https://fastpinball.com/mpf/ |

## Layout

- `config/` and `modes/` are the MPF machine folder (repo root is the machine path).
  `config/playfield_pending.yaml` holds the playfield features that are not
  built or wired yet (see "Game rules" below).
- `tests/` runs the rules against the real config with MPF's test framework.
- `gmc/` is the Godot project. Slides live in `gmc/slides/<name>/<name>.tscn`.
- `docs/` holds the MPF documentation summaries, this machine's hardware notes and the parts inventory. Start at `docs/README.md`.

## Machine PC: Ubuntu 24.04 LTS

Ubuntu 24.04 ships Python 3.12, which MPF 0.80 supports, so no extra Python
PPA is needed.

    sudo apt update && sudo apt full-upgrade
    sudo apt install python3-venv git git-lfs
    sudo usermod -a -G dialout $USER

Reboot after the group change. The `dialout` group is required for MPF to
open the FAST serial ports.

## Python environment and MPF

    mkdir -p ~/.mpfenv
    python3 -m venv ~/.mpfenv/matrix
    source ~/.mpfenv/matrix/bin/activate
    pip install --upgrade pip
    pip install "mpf==0.80.*"

Pin the minor version. MPF and GMC must match, and this repo's vendored GMC is
1.0.0, which pairs with MPF 0.80.x. Update later with
`pip install --upgrade "mpf==0.80.*"`. Do not use `--pre`, which pulls 0.81 dev
builds.

Clone with Git LFS so fonts, images and video assets are fetched:

    git lfs install
    git clone <repo url>

## Godot and GMC

1. Install Godot 4.7.2 from https://godotengine.org. The project is tagged `4.7`, so an older
   editor will warn that the project was made with a newer version.
2. Open `gmc/project.godot`. The first open in a newer Godot rewrites the import cache
   and UID files. Let it finish, then commit any changed `.import` or `.uid` files.
3. The GMC addon is already vendored and enabled. To upgrade it, replace the whole
   `gmc/addons/mpf-gmc` folder with the matching release from
   https://github.com/missionpinball/mpf-gmc. Do not edit files inside the addon.

## Running MPF with Godot

Manual (development):

    source ~/.mpfenv/matrix/bin/activate
    cd <repo root>
    mpf               # real FAST hardware
    mpf -X            # smart_virtual, no hardware
    mpf -b -X         # smart_virtual, no hardware, no Godot

Then press Play in the Godot editor with `gmc/project.godot` open. Godot will show
"Connected to MPF" once the BCP link is up.

`mpf` runs the `game` command whenever the first argument is not a subcommand
name, so `mpf` and `mpf game` are the same thing.

The platform comes from `hardware: platform:` in `config/config.yaml`, which is
`fast`. The command line only overrides it:

| Flag | Effect |
| --- | --- |
| `-X` | Force the `smart_virtual` platform. Ball movement through devices is simulated. Use this one for development |
| `-x` | Force the plain `virtual` platform. Devices respond, ball movement is not simulated |
| `-b` | Do not attempt a BCP connection, so MPF runs without Godot |
| `-t` | Turn **off** the ASCII text UI. It has nothing to do with hardware selection |
| `-v` / `-V` | Verbose logging to the log file / to the console |
| `-f` | Load all assets at startup, which surfaces broken asset paths early |
| `-a` | Ignore the config cache and reload from the config files |

### Starting both at once

    mpf both -X

Add `-G <path>` if the Godot binary is not on your PATH as `godot`.

Beware that two different files are called `gmc.cfg`, read by different
programs:

| File | Read by | Holds |
| --- | --- | --- |
| `gmc/gmc.cfg` | Godot, as `res://gmc.cfg` | `[keyboard]`, `[sound_system]`, `[mpf]` |
| `gmc.cfg` (repo root) | the `mpf both` CLI | `[cli]` only |

`mpf both` defaults the Godot project path to the machine path, which is the
repo root, while `project.godot` lives in `gmc/`. The root `gmc.cfg` sets
`gmc_project_path = "gmc"` to correct that. Delete it and `mpf both` aborts with
`FileNotFoundError: Unable to find GMC project.godot file` unless you pass
`-g gmc` by hand.

Note that the Godot editor's MPF tab rewrites `gmc/gmc.cfg` in full when it
saves, and `ConfigFile.save()` does not preserve comments, so the comments in
that file are lost on the first editor save. The root `gmc.cfg` is not touched
by Godot.

Godot can also spawn MPF itself. Configure this in the Godot editor's MPF tab,
which writes `spawn_mpf` and `executable_path` into the `[mpf]` section of
`gmc/gmc.cfg`. See the MPF docs page "Launching the MPF game with Godot".

On the virtual platforms the trough is seeded via
`virtual_platform_start_active_switches:` in `config/config.yaml`, so the start
button works as soon as the machine reaches attract. One listed switch is one
ball. MPF raises `CFE-Smart_Virtual_Platform-1` on any switch name it cannot
find, so the list must only name switches that are currently defined.

## Game rules

The cabinet runs two games on the one playfield. A game select before the
first ball chooses one for every player: flippers step, start confirms, and
after 15 s with no choice the Matrix starts.

- **The Matrix, Act I** (the first film): four chapter modes in film order,
  the VPX Trinity and Sentinel multiballs, the FREED roster and The One
  wizard. The rules, every timer and score, and the mode map are in
  `docs/11-rules-act-1.md`.
- **Terminator 2**: four chapter modes in film order, the Future War and
  T-1000 multiballs, the SAVED roster and the Judgment Day wizard, on the same
  hardware under its own names. The rules and the game select are in
  `docs/12-rules-terminator-2.md`.

### Running the tests

With the MPF venv active, from the repo root:

    python -m unittest discover -s tests -t .

The tests run the real config on the smart_virtual platform, with no hardware
or Godot, and play through every chapter, multiball and wizard stage.

### Unwired features run on the virtual platform

`hardware: platform: fast, virtual` loads both platforms. Everything in
`config/playfield_pending.yaml` is `platform: virtual`, so the full rules load
on the real machine: those switches never close and those coils do nothing
until the feature is wired. To bring one online, move its entries into
`config/config.yaml`, give them FAST numbers and delete `platform: virtual`.
Keep each switch's `events_when_activated:` line: the modes listen to those
events, never to switch names.

### Hardware names are generic

Every switch, coil, device and event names what the hardware is
(`left_lock_ramp`, `platform_gate`, `popup_1`, `right_outlane_lock`), never
what a game calls it, because the same playfield will run more than one game
(`docs/12-rules-terminator-2.md`). The Matrix modes keep the film's names in
their display text and comments; the mapping is in `docs/11-rules-act-1.md`,
section 11, and each renamed entry in the config carries a `# was ...`
comment. `tests/test_shots.py` fails if a Matrix word gets into a hardware
name.

### Keyboard

On `mpf both -X` the `[keyboard]` section of `gmc/gmc.cfg` drives the switches.
Keys marked toggle stay closed until pressed again, which is how a ball sits in
a device or a drop target stays down.

| Key | Switch (Matrix name) | | Key | Switch (Matrix name) |
| --- | --- | --- | --- | --- |
| `1` | Start | | `u` | Middle loop VUK (Deja Vu VUK, toggle) |
| `a` / `d` | Left / right flipper | | `i` | Platform VUK (Sentinel VUK, toggle) |
| `q` | Mode drop (Mission Drop, toggle) | | `o` | Pop-up scoop (Agents Coming, toggle) |
| `w` | Mode scoop (Mission scoop, toggle) | | `f` `g` `h` | Left lock 1 to 3 (Trinity lock, toggle) |
| `e` | Left lock ramp (Trinity Ramp) | | `j` | Right outlane lock (Ammo Lock, toggle) |
| `r` | Middle loop ramp (Deja Vu Ramp) | | `l` | Right outlane lock target (Ammo target) |
| `t` | Right loop ramp (Real World Ramp) | | `s` / `5` | Platform gate left / right (Sentinel entrance targets) |
| `y` | Backboard ramp (Sentinel Ramp) | | `6` | Platform magnet (Sentinel magnet) |
| `2` `3` `4` | Pop-ups 1 to 3 (Agents, toggle) | | `0` `9` `8` `7` | Outlanes and inlanes |

The trough keys are `x c v b n m k`. The five-bank and three-bank drops, upper
playfield standups, platform targets and pop area standups have no key; use
MPF Monitor (`pinball-monitor`) for those. The Godot editor's MPF tab rewrites
`gmc/gmc.cfg` in full, so check this section survives an editor save.

## Slides and the Matrix look

Slides live in `gmc/slides/<name>/<name>.tscn` and are put on screen by
`slide_player:` in the MPF config.

| Slide | Shown on | Contents |
| --- | --- | --- |
| `attract` | `mode_attract_started` | Digital rain, MATRIX title, pulsing PRESS START |
| `base` | `mode_base_started` while the Matrix is the chosen game | Matrix gameplay HUD: player, ball, score, per-player scores |
| `base_t2` | `mode_base_started` while Terminator 2 is the chosen game | Terminator 2 gameplay HUD in the T-800's red view, same layout (`slides/base_t2/`) |
| `welcome` | `init_done` | Loading placeholder |
| `plunge_ready` | `mode_plunge_ready_started` | "wake up player 1..." terminal line |

Both Matrix screens share two shaders in `gmc/assets/shaders/`:

- `matrix_rain.gdshader` draws the digital rain procedurally, as pseudo-glyphs
  on a 5x7 dot matrix. Procedural rather than a video loop so it stays sharp at
  any display size, costs no video decode during gameplay and needs no new LFS
  assets. Every parameter is exposed, so `attract` runs it bright and fast while
  `base` runs the same shader dimmed and slowed so it does not fight the HUD.
- `phosphor.gdshader` adds CRT scanlines and a vignette as a dark overlay.

`slides/attract/assets/matrixrain.ogv` is still in the repo but no longer used
by the attract slide. Swap it back in by replacing the `Rain` ColorRect with a
`VideoStreamPlayer` if you prefer the video.

### The gameplay HUD

`base.tscn` keeps its centre deliberately empty. That space is the stage a mode
takes over with `widget_player:`; nothing permanent is drawn there, so the score
reads when nothing is happening and a mode owns the screen when it is. The
persistent HUD sits around it: player and ball top left, act top centre, player
scores top right, the FREED roster down the left, power station locks bottom
right, and the objective line above the score.

While the stage is idle it runs ambient effects, which `slides/base/stage.gd`
fades out as soon as a widget appears and back in when it goes. It finds the
widget container by name (`_<slide>_widgets`, created lazily by MPFSlide), so if
the addon ever renames it the effects simply stay visible.

#### Player variables the HUD reads

The HUD is already wired to these. Set them from the mode code and the display
follows; until then each element shows its authored placeholder.

| Variable | Type | Drives |
| --- | --- | --- |
| `score`, `player`, `ball` | int | Score, player and ball readouts |
| `game` | str | `matrix` or `t2`, the game this player is in |
| `act` | str | The `ACT ...` marker, e.g. `I`, `II`, `III` (Matrix) |
| `chapter` | str | The marker for Terminator 2: `CHAPTER 1`, `JUDGMENT DAY`, `COMPLETE` |
| `objective` | str | The objective line above the score |
| `balls_locked` | int | How many lock cells are lit (both games) |
| `freed_trinity`, `freed_tank`, … | bool | Lights that name in the FREED roster |
| `saved_john`, `saved_sarah`, … | bool | Lights that name in the SAVED roster |

The Act I modes set all of these (docs/11-rules-act-1.md, section 9); the
Terminator 2 modes set theirs (docs/12-rules-terminator-2.md, section 11).

#### Stage widgets

The modes draw on the centre stage with five widgets in `gmc/widgets/`:
`countdown` (a hurry-up clock that churns and locks like the trace readout),
`chapter_card`, `mode_banner`, `pill_choice` and `act_select`. Terminator 2
has the same layouts in its own palette: `t2_countdown`, `t2_card`,
`t2_banner`, `dyson_choice`, plus `game_select`, which plays before the game
is chosen. The zones they use, and the rules for adding more, are in
docs/11-rules-act-1.md, section 9; the T2 look is docs/12-rules-terminator-2.md,
section 11.
In short: a mode's widgets are cleared when it stops, so a mode's ending is
shown by a mode that keeps running, and a clock on screen is changed with
`action: update`.

#### The trace readout

`slides/base/trace_readout.gd` is the number-lock from the films: every position
churns through digits until it locks, one at a time, left to right, locked
positions bright and unlocked ones dim. Separators in the target string are
treated as structure and lock immediately rather than churning.

It is self-driving, so it loops on the idle stage with no rules behind it. Once
modes exist, call `set_target("...")` to make a trace spell something meaningful
and connect `trace_locked` to fire an award when the last position lands. Set
`loop` false for a one-shot trace that stays locked.

The signal is `trace_locked` rather than `finished` because `RichTextLabel`
already defines a `finished` signal, and redefining it is a parse error.

#### Effect shaders

- `signal_trace.gdshader` is the idle stage: a sonar-style sweep with range
  rings and contacts that light as the arm passes. Morpheus tracing Neo, rather
  than a generic decoration. Set `aspect` to the node's width / height or the
  dish turns into an ellipse.
- `matrix_rain.gdshader` gained a `radial_falloff`, so the same shader is both
  the full-screen backdrop (`0.0`, the default) and the brighter, coarser "code
  well" inside the trace dish.
- `glitch.gdshader` tears the whole slide for about 220 ms every 9 seconds:
  bands shift sideways and the colour channels pull apart. It reads the back
  buffer, so it must stay the last child, and it samples straight through
  between tears. That back-buffer copy runs every frame, which is free on the
  cabinet's GPU but is the first thing to remove if a weaker machine struggles.

### Display scaling

`project.godot` sets `window/stretch/mode="canvas_items"` with
`window/stretch/aspect="expand"`. Slides are laid out against the 2560x1440
design size and the whole canvas is scaled to whatever the window or panel
actually is, so font sizes scale with it. Without this the layouts reflowed on
their anchors but text stayed a fixed pixel size, which made the 190px score
swamp a 720p window.

`expand` fills the screen and reveals a little more area on a panel that is not
exactly 16:9, rather than letterboxing. Switch `aspect` to `keep` if you would
rather have black bars and a guaranteed-identical composition. On a 16:9 panel
the two are the same.

### Font notes

- `Miltown1.ttf` is the display face, used for the MATRIX title. Its glyphs have
  long horizontal arms that overlap their neighbours by design, so it needs a
  `FontVariation` with `spacing_glyph` (the title uses 70). Widening the spacing
  further does not stop the arms crossing; that is how the face is drawn.
- **Miltown1's digits render as plain horizontal bars**, so it cannot be used for
  scores or any number.
- `Miltown2.ttf` is an overlay companion to Miltown1, not a standalone face. On
  its own the letters sit on top of each other.
- `JackInput.ttf`, via the `ui-code.tres` theme, is the monospace used for all
  HUD text and every numeric value.

## Film clips

### Format: Ogg Theora only

Godot 4.7.2 exposes exactly one `VideoStream` subclass, `VideoStreamTheora`, so
`.ogv` is the only video the engine can open. There is no h264, mp4 or WebM
support to fall back on. Encoding and naming are covered in
`gmc/video/README.md`.

Audio is separate: Godot's file-backed streams are `AudioStreamWAV`,
`AudioStreamOggVorbis` and `AudioStreamMP3`, and GMC catalogues `.wav`, `.ogg`,
`.mp3` and `.tres` from the sounds folder.

| Use | Format | Why |
| --- | --- | --- |
| Callouts and short effects | WAV, 16-bit 44.1 kHz | No decode latency, so it fires on the frame |
| Music and long ambience | Ogg Vorbis | Good compression, clean looping |
| Anything | Not MP3 | Supported, but no advantage over Vorbis and worse for gapless loops |

Prefer stripping audio from clips and driving sound through GMC's sound system,
which gives you buses and ducking. Keep it embedded only where lip-sync matters.

### One widget, not one scene per clip

`gmc/widgets/video_clip.tscn` plays any clip. `widget_player` passes the name as
a token and the widget loads `res://video/<name>.ogv` at play time:

    widget_player:
      agent_battle_started:
        video_clip:
          tokens:
            clip: agent_smith_intro

Adding a clip is one line of YAML and one file, rather than a new scene each
time. The widget registers itself as an updater on its parent, which is what
makes plain tokens arrive without needing `action: method` in the config. A name
with no file behind it logs an error and carries on rather than crashing, and
falls back to `fallback_clip` if one is set.

`MPFVideoPlayer` supplies the rest: `end_behavior` to tear the widget down when
the clip finishes, `events_when_stopped` to post an event back to MPF so a mode
can chain off it, and a `bus` so the audio ducks.

Three rules worth holding to:

1. **One video at a time.** Theora decodes on the CPU; two clips during
   multiball is how frames get dropped.
2. **Preload the widget** with `get_widget_instance(name, preload_only)`. A clip
   that stutters on start is worse than no clip.
3. **Short and inset during play.** The player is watching the playfield.
   Full-screen belongs to mode intros, ball end and attract.

The idle stage cooperates already: `stage.gd` fades the trace and rain out as
soon as a widget appears, so a clip gets a clean background for free.

### The clips are not in version control

`.gitignore` excludes everything in `gmc/video/` except its README and manifest,
because a clip library runs to gigabytes and committing film footage publishes
it. Keep the library in Dropbox with the design files and sync it onto the
machine.

`gmc/video/manifest.txt` lists what the machine expects. Check a checkout with:

    python3 tools/check_video.py

It reports missing clips, clips present but unlisted, and any file in a format
Godot cannot open, and exits non-zero if something listed is missing.

For a production export, add `video/*` to the export preset's include filter.
`VideoStreamTheora` has no scriptable file path, so clips have to be `res://`
resources and will otherwise be left out of the pack.

## Hardware test state

Several switches and devices are not yet installed or do not have confirmed
FAST numbers. They are commented out in `config/config.yaml` and marked
`TODO(hardware)`. Until restored:

- The trough runs on seven switches (trough 1 opto and jam opto are not fitted).
- **The machine is set to seven balls** for the Act I multiballs:
  `machine: balls_installed: 7`, and the virtual trough is seeded with seven.
  Load seven balls, or attract mode ball-searches constantly. The trough is the
  8-ball PBL-100-0016-00; raise both to 8 once the trough 1 opto is fitted.
- Playfield features not yet built or wired are on the virtual platform in
  `config/playfield_pending.yaml` (see "Game rules").
- The plunger lane has no switch, so the trough ejects directly to the playfield
  as described in the MPF docs for plunger lanes without a switch.

### Cabinet I/O board (FP-CAB-0001)

`s_left_flipper`, `s_right_flipper`, `s_start` and the `flippers:` section are
now configured against the `cab` board, so the side flipper buttons and the
start button work once the board is wired. The board is internally an
`FP-I/O-0024`: 24 switch inputs (`cab-0` to `cab-23`) and 8 drivers
(`cab-0` to `cab-7`). The numbers in the config follow FAST's recommended
cabinet recipe and are **not yet confirmed on this machine**:

| Device | Number | Header |
| --- | --- | --- |
| `s_left_flipper` | `cab-8` | left-side cabinet header (`cab-8` to `cab-15`) |
| `s_start` | `cab-10` | left-side cabinet header |
| `s_right_flipper` | `cab-16` | right-side cabinet header (`cab-16` to `cab-23`) |

MPF only range-checks these against the 24 inputs the board reports, so a
wrong-but-in-range number will not raise an error. Confirm each one in the
service-mode switch test after wiring and correct the config if it differs.

Two things must be right before any `cab-…` number resolves at all:

1. The Cabinet I/O board's NET cable has to be in the I/O loop.
2. `io_loop:` in `config/config.yaml` must list every board with `order:`
   values matching the real daisy-chain out of the Neuron. It currently
   declares three boards but four are installed (the second `FP-I/O-1616` is
   missing). Run `mpf hardware scan` to get the true order.

## Serial terminal access

The `dialout` group above also covers terminal emulators such as CoolTerm.
Some guides add the `tty` group as well; it is not required for MPF.
