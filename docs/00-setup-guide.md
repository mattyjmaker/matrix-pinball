# MPF Machine Setup Guide (MPF 0.80 + GMC)

A practical order of operations for bringing up a new pinball machine on the
Mission Pinball Framework. It is distilled from the full docs review in the other
files in this folder, which have the detail, the YAML reference and the source
page paths. The docs were reviewed on 2026-09-19 from the `dev` branch of
`missionpinball/mpf-docs`.

> **Version baseline**
> - **MPF 0.80.0** (stable release, April 2026) uses the **Godot Media Controller (GMC)** for all display and sound.
> - The old Kivy-based MPF-MC (0.57) is legacy, so any doc page showing `slides:`, `widgets:`, `sounds:` or `keyboard:` YAML is out of date for 0.80.
> - 0.81 is currently in development on the `dev` branch. Some doc pages already describe 0.81/0.58 features, such as FAST `led_ports` and soft power. See file 03 §"Post-0.80 content".
> - Recommended set: Python 3.14 (3.10–3.14 supported), MPF 0.80.0, GMC 1.0.0, Godot 4.6.

---

## 0. How the system fits together

```
 ┌────────────────────────┐   BCP (TCP localhost:5050)  ┌─────────────────────────┐
 │ MPF (Python, game      │ ──────────────────────────▶ │ GMC (Godot 4 project    │
 │ engine, all rules,     │ ◀────────────────────────── │ + mpf-gmc addon)        │
 │ YAML config, shows,    │   events / player vars      │ slides, widgets, sound, │
 │ lights, hardware)      │                             │ video, DMD look, keys   │
 └──────────┬─────────────┘                             └─────────────────────────┘
            │ USB serial (platform driver)      ▲ MPF's own BCP server on :5051
            ▼                                    │ for MPF Monitor / service CLI
 ┌──────────────────────────────┐
 │ Pinball controller (FAST,    │  hardware rules run ON the controller:
 │ OPP, P-ROC, SPIKE, LISY ...) │  flippers, slings, pops need no PC round-trip
 └──────────────────────────────┘
```

- **Almost everything is YAML config**: the machine config, mode configs and show files. You write Python only for unusual logic (see file 07).
- **Modes** are stacked layers of config, each with a priority. Attract and game are built-in modes. Your game rules go in your own modes.
- **Events** are the glue. Every device posts events, and the config players (`variable_player`, `show_player`, `slide_player`, `sound_player`, `event_player` and so on) react to them.

## 1. Host computer and OS

- Use 64-bit Linux, e.g. Debian or Ubuntu, on a small x86 PC or a Raspberry Pi 5. Windows and macOS also work.
- The Linux, Raspberry Pi and Xubuntu install pages are **stale 0.57 guides** (the Pi page uses Python 3.9 and 0.56). There is no official 0.80 Pi guide, so treat those pages as hints only.
- Add your user to the `dialout` group so MPF can open the USB serial ports:
  ```bash
  sudo usermod -a -G dialout $USER     # then log out/in
  ```

## 2. Install MPF (Python)

```bash
python3 --version                 # need 3.10–3.14
python3 -m venv ~/mpfenv          # a venv is REQUIRED on Debian 12 / Ubuntu 23+
. ~/mpfenv/bin/activate
pip install mpf                   # docs still say "pip install mpf --pre"; 0.80.0 is now final
mpf --version
mpf diagnosis                     # shows versions, machine folder and detected serial ports
```

- To work on MPF itself, or track a branch, do an editable install instead: `git clone https://github.com/missionpinball/mpf && cd mpf && git checkout 0.80.x && pip install -e .`
- MPF Monitor, the playfield/switch visualiser, is a separate install. See file 01 §7.
- The MPF Language Server (`mpf-ls`) gives YAML auto-complete and validation in VS Code and other editors. It is worth installing.

## 3. Create the machine folder

The "machine folder" is the project root. You run `mpf` from here, and it should be a git repo.

```
my_machine/
├── config/config.yaml       # machine-wide config (starts with #config_version=6)
├── modes/<mode>/config/<mode>.yaml
├── modes/<mode>/slides/     # GMC slide scenes (only if Godot project is in the root)
├── shows/                   # light/show YAML (#show_version=6)
├── logs/
├── monitor/                 # MPF Monitor files
├── project.godot            # GMC Godot project (root by default)
├── addons/mpf-gmc/          # GMC plugin
└── gmc.cfg                  # GMC settings: keyboard map, sound buses, DMD filters, MPF launch
```

```bash
mkdir -p my_machine/config && cd my_machine
echo "#config_version=6" > config/config.yaml
```

> Keep the Godot project in the **machine root**, not a `gmc/` subfolder. Godot can't see
> files outside its own project folder, so a subfolder layout means `modes/*/slides` can't be used.

## 4. Install the Godot Media Controller

1. Download the **Godot 4.6** editor and keep it outside the project folder.
2. In Godot, create a new project **in the machine folder**. Use the *Mobile* renderer unless you need Forward+ 3D, or Compatibility for weak hardware.
3. Under Editor Settings > Text Editor > Behavior, **disable** "Convert Indent on Save", because GMC uses tabs.
4. From AssetLib, search "GMC" and install it. Alternatively, clone `github.com/missionpinball/mpf-gmc` and copy or symlink `addons/mpf-gmc`.
5. Under Project Settings > Plugins, enable **Godot MC**.
6. Under Project Settings > Globals > Autoload, use the folder icon to pick `addons/mpf-gmc/mpf_gmc.gd` and set the Node Name to **`MPF`** (exactly). Some pages misspell the file as `mpd_gmc.gd` or `mpf_gmc.md`; ignore them.
7. Reload the project. Errors on the first load are expected.
8. Press Play and choose `addons/mpf-gmc/slides/window.tscn` as the main scene. The window shows "Waiting for MPF...".
9. In a terminal, in the machine folder, run `mpf -xt`. The window should change to "Connected to MPF".

Details on slides, widgets, sounds, buses, the DMD look and multiple displays are in file 05.

## 5. Develop with virtual hardware first

```bash
mpf -X -t              # smart_virtual platform (simulates ball devices), no text UI
mpf both -X            # MPF + launch Godot project (needs godot on PATH or -G <path>)
mpf -b -x              # engine only, no media controller (otherwise MPF waits for the MC)
mpf game -t -v -V      # verbose debugging
```

- `-x`, `-X` and `--vpx` **silently override `hardware:`**. If real hardware does nothing, check for these flags first.
- Keyboard switch simulation for 0.80 goes in `gmc.cfg` under `[keyboard]`, not in the old `keyboard:` YAML.
- `virtual_platform_start_active_switches:` pre-fills the trough with balls in virtual mode.

## 6. Minimal machine config

These are the core devices every machine needs. Numbers depend on your platform (see §7). The example is condensed from files 03 and 04.

```yaml
#config_version=6
hardware:
  platform: fast          # or opp / p_roc / p3_roc / spike / lisy / pkone / virtual ...

switches:
  s_start:        {number: ..., tags: start}
  s_left_flipper: {number: ..., tags: left_flipper}
  s_right_flipper:{number: ..., tags: right_flipper}
  s_trough1:      {number: ..., type: NC}    # optos are NC
  # ... s_trough2..6
  s_trough_jam:   {number: ..., type: NC}
  s_plunger:      {number: ...}
  s_launch:       {number: ...}
  s_tilt:         {number: ..., tags: tilt_warning}
  # every other playfield switch: tags: playfield_active  (NOT the plunger lane)

coils:
  c_trough_eject:        {number: ..., default_pulse_ms: 20}
  c_plunger:             {number: ..., default_pulse_ms: 20}
  c_flipper_left_main:   {number: ..., default_pulse_ms: 30}
  c_flipper_left_hold:   {number: ..., allow_enable: true}

ball_devices:
  bd_trough:
    ball_switches: s_trough1, s_trough2, s_trough3, s_trough4, s_trough5, s_trough6, s_trough_jam
    eject_coil: c_trough_eject
    jam_switch: s_trough_jam
    eject_coil_jam_pulse: 15ms
    tags: trough, home, drain
    eject_targets: bd_plunger
    eject_timeouts: 3s          # default 10s is far too slow
  bd_plunger:
    ball_switches: s_plunger
    eject_coil: c_plunger
    mechanical_eject: true
    player_controlled_eject_event: s_launch_active
    eject_timeouts: 3s

playfields:
  playfield:
    default_source_device: bd_plunger
    tags: default
    enable_ball_search: true    # off by default!

flippers:
  left_flipper:
    main_coil: c_flipper_left_main
    hold_coil: c_flipper_left_hold
    activation_switch: s_left_flipper

autofire_coils:
  ac_sling_left: {coil: c_sling_left, switch: s_sling_left}

modes:                  # attract + game are automatic; these must be listed
  - base
  - tilt
  - bonus
  - high_score
  - credits             # only if coin-op
  - service
```

Traps to know about (all from the docs):

- Coils default to a 10 ms pulse and can't be held on without `allow_enable: true`.
- Flippers and autofires are only enabled **during a ball**. For bench testing, add `enable_events: machine_reset_phase_3`.
- Setting any `*_events` list replaces the defaults, and adding `enable_events` makes a device start disabled.
- Logic blocks such as counters and sequences complete **once** unless you set `reset_on_complete: true` and `disable_on_complete: false`.
- Bare numbers in time settings use that setting's default unit, which may be ms or seconds. Write `20ms` or `3s` explicitly.
- Many doc examples still use `#config_version=5` or `!!omap`. Don't copy those headers.

## 7. Real hardware bring-up

1. **Pick and wire the controller.** File 02 has a comparison table of FAST, OPP/CobraPin, P-ROC/P3-ROC, SPIKE, LISY/APC and PKONE, plus a numbering cheat-sheet for each.
   - **FAST Neuron on 0.80** uses the `fast: net: {controller: neuron, io_loop: ...}` and `fast: exp: boards:` layout. Numbers are `boardname-index`, e.g. `cabinet-0`. The `hardware/fast/*` tree describes the old Nano and MPF 0.56 only; use `config/fast*.md` instead.
   - **OPP/CobraPin:** a flipper's or autofire's switch and coil must be on the **same MCU**.
2. **Safety first.**
   - Use a **common ground** between logic and coil supplies. A missing common ground is the most common way to kill driver boards.
   - The coin-door "coil power off" switch must physically cut high voltage.
   - Fuse every supply.
3. **Scan the hardware:** run `mpf hardware scan` (with MPF not running), then `mpf hardware firmware_update` if needed.
4. **Test one device at a time.**
   - Switches: `mpf service` or MPF Monitor.
   - Coils: service mode coil test. Start with short pulses.
   - Flippers: bench-test with `enable_events: machine_reset_phase_3`.
5. **Tune.** Adjust pulse times and hold power, `eject_timeouts` and debounce. `mpf hardware benchmark` measures latency.
6. **Existing machine re-theme** (WPC, System 11, etc.): see file 02 §5. There are dangerous misconfigurations there, e.g. a P-ROC in a WPC game with `driverboards: pdb` fires every coil.

## 8. Build the game

- Write rules as modes with shots, shot groups, logic blocks, timers, `variable_player` scoring, ball saves, multiballs and locks. See file 04.
- Put lights and effects in shows. Shows still run in MPF, not GMC (file 05). Quote relative times like `time: "+1"`. `show_player` loops forever by default.
- Put displays and sound in GMC. Slides are Godot `.tscn` scenes with an `MPFSlide` root, triggered from MPF by `slide_player`. Sounds use `sound_player` with `bus:` in place of the old `track:` (file 05).
- For patterns and examples, see file 06. The official tutorial is written for 0.57 / the legacy MC, so translate its display steps to GMC.
- Automate tests with single-file `mpf test` tests or `MpfMachineTestCase` (files 01 and 07).

## 9. Production and the cabinet

- Build a bundle with `mpf build production_bundle -b` (always pass `-b` on 0.80). Rebuild it after every config, mode or show change and every MPF upgrade. The cabinet must run the **same MPF version** that built it.
- Run `mpf game -P -t` in a restart loop, because `-P` exits if startup fails.
- **Export** the Godot project to a binary, and re-export after every change.
- Auto-start on boot: the only documented recipe is an old Xubuntu LightDM auto-login plus an `~/.config/autostart` script (file 01 §4, file 06). A systemd service is a reasonable modern equivalent, but it isn't covered by the docs.
- Handle power-off safely: shut down via MPF or a shutdown controller, and consider a read-only root filesystem (file 06).
- Set up operator settings, audits, credits and service mode (files 04 and 06). Many finalization pages are empty stubs.

## 10. When stuck

1. Run with `-t -v` and read the newest file in `logs/`. Read chained errors **bottom-up**.
2. Look up the error code (CFE-/RE-/Log-) in file 01 §8.
3. Help channels: GitHub Discussions (`missionpinball`) and the MPF Google Group.
