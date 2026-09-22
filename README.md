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

## Slides and the Matrix look

Slides live in `gmc/slides/<name>/<name>.tscn` and are put on screen by
`slide_player:` in the MPF config.

| Slide | Shown on | Contents |
| --- | --- | --- |
| `attract` | `mode_attract_started` | Digital rain, MATRIX title, pulsing PRESS START |
| `base` | `mode_base_started` | Gameplay HUD: player, ball, score, per-player scores |
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

## Hardware test state

Several switches and devices are not yet installed or do not have confirmed
FAST numbers. They are commented out in `config/config.yaml` and marked
`TODO(hardware)`. Until restored:

- The trough runs on seven switches (trough 1 opto and jam opto are not fitted).
- **The machine is set to a single ball while the rules are built out.**
  `machine: balls_installed: 1` and the virtual trough is seeded with one ball.
  Raise both together when multiball work starts. The trough is the 8-ball
  PBL-100-0016-00, so 8 is the ceiling, 7 until the trough 1 opto is fitted.
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
