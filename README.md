# matrix-pinball

Matrix Pinball game code for the Mission Pinball Framework (MPF) with the
Godot Media Controller (GMC) and FAST Pinball Neuron hardware.

## Versions this repo targets

| Component | Version | Notes |
| --- | --- | --- |
| MPF | 0.80.x | Requires Python 3.10 to 3.14 |
| GMC addon | 1.0.0 | Vendored in `gmc/addons/mpf-gmc`. Requires Godot 4.5 or newer |
| Godot | 4.6 or newer (4.7.x is current stable) | Download from godotengine.org, not the distro package |
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
    pip install mpf

Update later with `pip install --upgrade mpf`.

Clone with Git LFS so fonts, images and video assets are fetched:

    git lfs install
    git clone <repo url>

## Godot and GMC

1. Install Godot 4.6 or newer from https://godotengine.org. The project is currently tagged for 4.6.
2. Open `gmc/project.godot`. The first open in a newer Godot rewrites the import cache
   and UID files. Let it finish, then commit any changed `.import` or `.uid` files.
3. The GMC addon is already vendored and enabled. To upgrade it, replace the whole
   `gmc/addons/mpf-gmc` folder with the matching release from
   https://github.com/missionpinball/mpf-gmc. Do not edit files inside the addon.

## Running MPF with Godot

Manual (development):

    source ~/.mpfenv/matrix/bin/activate
    cd <repo root>
    mpf -t            # real hardware
    mpf -xt           # virtual platform, no hardware

Then press Play in the Godot editor with `gmc/project.godot` open. Godot will show
"Connected to MPF" once the BCP link is up.

Godot can also spawn MPF itself. Configure this in the Godot editor's MPF tab
(it writes an `[mpf]` section to `gmc/gmc.cfg`). See the MPF docs page
"Launching the MPF game with Godot".

## Hardware test state

Several switches and devices are not yet installed or do not have confirmed
FAST numbers. They are commented out in `config/config.yaml` and marked
`TODO(hardware)`. Until restored:

- No flipper or start buttons are configured, so the `flippers:` section is off.
- The trough runs on seven switches (trough 1 opto and jam opto are not fitted).
- The plunger lane has no switch, so the trough ejects directly to the playfield
  as described in the MPF docs for plunger lanes without a switch.

## Serial terminal access

The `dialout` group above also covers terminal emulators such as CoolTerm.
Some guides add the `tty` group as well; it is not required for MPF.
