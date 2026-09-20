# MPF 0.80: Installing, Running, Tools and Troubleshooting

This is a condensed reference drawn from the MPF documentation source (the `dev` branch, which covers MPF 0.80). Everything here comes from those docs. Where a page is out of date, or two pages disagree, it is marked **[DOC CONFLICT]** or **[STALE]**. Where something only applies to the old Kivy-based media controller, it is marked **[0.57/LEGACY]**.

- **Current release:** MPF **0.80.0**, released April 25, 2026. It uses the Godot Media Controller (GMC).
- **Long-term-support (LTS) release:** MPF **0.57.5**, released the same day. It uses the legacy Kivy-based MPF-MC.

---

## 1. What MPF is

- MPF (Mission Pinball Framework) is free, open-source (MIT) Python software. It runs on a computer inside a real pinball machine and controls everything in it: lights, solenoids/coils, switches, motors, DMD/LCD/segment displays, sound, and game rules (modes, multiball, ball save, scoring, and so on).
- It runs on Windows, Mac, Linux and Raspberry Pi. The computer connects to a pinball control system over USB. Supported systems include FAST (Modern/Neuron and Retro), OPP, CobraPin, Multimorphic P-ROC/P3-ROC, Stern SPIKE/SPIKE 2, LISY, APC and Penny K PKONE. Hobby boards are also supported: FadeCandy/OPC, Pololu Maestro/Tic, I2C servos, StepStick, DMX/OSC/MIDI and others.
- **MPF is not a simulator.** It is a framework for the software of a *physical* machine.
- The usual workflow is to develop on a main computer, then move the game to a smaller computer installed permanently in the cabinet.
- MPF is **event-driven**. Everything that happens posts an event, and events trigger actions such as scoring, lights, or starting modes.
- The project started in May 2014 (Brian Madden and Gabe Knuth). Jan Kantert ran it from 2017 to 2022. Anthony van Winkle wrote the GMC and is the current maintainer. It is volunteer-run, has no official support, and is still "pre-1.0" (the docs describe it as "beta" but stable).

### Architecture: game engine + media controller over BCP

- The **game engine** (MPF itself) and the **media engine** (the "Media Controller") are **two separate processes**. They talk over a TCP socket protocol MPF invented, the **Backbox Control Protocol (BCP)**. The docs cite BCP version 1.1 for Monitor compatibility.
- **0.80:** the media controller is the **Godot Media Controller (GMC)**, a plugin for the Godot game engine (`mpf-gmc`). In 0.80, GMC manages all slides, widgets and sounds.
- **[0.57/LEGACY]:** the media controller was **MPF-MC**, which is Kivy-based (`pip install mpf-mc`).
- The docs mention that you can run the MC on a separate computer, or replace it with Unity or your own software.

**Default TCP ports** (`running/ports.md`, `logs/RE-*`):

| Port | Who listens | Used by |
|---|---|---|
| `5050` | The media controller (MPF-MC; GMC also — the GMC launch guide shows `Connecting BCP to local_display at localhost:5050`) | MPF connects **out** to the MC on this port and keeps retrying until it connects |
| `5051` | MPF game engine | Incoming BCP clients such as **MPF Monitor** (defaults to `localhost:5051`) and `mpf service` |

Changing the port (**[0.57/LEGACY] example**; it uses `config_version=5` and the `mpf-mc:` section, which 0.80 deprecates). You must change it in two places:

```yaml
# config_version=5
bcp:
  connections:
    local_display:
      port: 1234
mpf-mc:
  bcp_port: 1234
```

Valid ports are 1024–65535. **[DOC CONFLICT/STALE]** No page in this section explains how to change the port for GMC. Check the GMC `gmc.cfg` reference.

Port conflicts are documented as RE-MPF_BCP_Server-1 and RE-MPF-MC_BCP_Server-1 ("Failed to bind BCP Socket"). Known offenders: Yahoo Messenger (5050), a Symantec app (5051) and IIS. Firewalls or antivirus can also block the bind.

---

## 2. Philosophy: config files vs code

- The docs claim you can do "90%+" of your programming in **YAML config files**. They describe the configs as a pinball *domain-specific language* (DSL). One or two config lines can stand in for hundreds of lines of code, for example ball tracking, mode stacking or ball devices.
- The stated benefits: productivity, fewer bugs (shared, well-tested code), readability, easier support (you can post a config to the forum), and insulation from MPF internals. The docs say "we provide migration tools".
- **You can still write code.** MPF offers two abstraction levels: *hardware abstraction* and *device abstraction*. You can also access hardware directly for platform-specific features (for example, the P-ROC AUX port), though that code won't be portable. You can add code in several ways:
  - globally, through **custom_code** (formerly "scriptlets"; the `scriptlets` class is deprecated as of 0.57) or code hooks
  - per **mode**, as mode code
  - as new or overloaded **devices**, which can live in your machine folder and be instantiated from config
  - as a whole custom **platform**
- The mix can be any ratio, from 90/10 to 20/80 configs versus code. You can subclass MPF systems (for example, shots) instead of rewriting them.
- Hardware independence: to switch controller platforms you change "a few lines" of config.

---

## 3. Config files and project (machine) folder layout

- Configs are YAML. There are **machine-wide** config files (hardware, switches, lights and so on) and **mode-specific** config files. Modes stack. **Shows** (timed sequences of lights, sounds, slides and so on) are also YAML files.
- Every config file must start with a version line. **MPF 0.57 and later (including 0.80) use config version 6:**

```yaml
#config_version=6
```

  Show files use `#show_version=6`. Some older examples still show `#show_version=5`, and the ports example shows `config_version=5` **[STALE]**.
- A trivial example:

```yaml
game:
  balls_per_game: 3
```

- **Machine folder** (MPF calls it a "machine" folder, not a "game" folder). This is the directory you run `mpf` from. It contains:
  - `config/config.yaml` — the main machine config (the default file `-c` loads)
  - `modes/<mode_name>/...` — mode configs
  - `shows/` — show files
  - `logs/` — MPF log files are written here
  - `monitor/` — MPF Monitor files (`playfield.jpg`, `monitor.yaml`, `settings.ini`)
  - **0.80:** the Godot project (`project.godot`, `addons/mpf-gmc/`, `gmc.cfg`, and Godot `slides/` folders). It lives in the **same folder** by default, or optionally in a `gmc/` subfolder (see §5).
  - Production bundles (`mpf_config.bundle`) if you use `mpf build`.
- Machine folders are portable between OSes (per the tutorial). The docs strongly recommend keeping the machine folder in a **git repository**, both for backup and so GMC developers can clone your project to reproduce bugs.
- Minimal bootstrap, taken from the 0.80 quickstart:

```shell
(mpf) my_project_folder $> mkdir config
(mpf) my_project_folder $> echo "#config_version=6" > config/config.yaml
```

- Tools that help with config editing: the **MPF Language Server** (`mpf-ls`, an LSP providing auto-complete, error highlighting, hover help and go-to-definition in any LSP-capable IDE; installation is covered in the mpf-ls GitHub repo) and `mpf format` (§7).

---

## 4. Installing MPF 0.80 (Python side)

### Supported OS and Python versions

- Supported operating systems: Windows 10/11 (64-bit only); macOS 10.14 through 14 Sonoma (Intel and Apple Silicon); 64-bit Linux (Debian, Ubuntu and others); Raspberry Pi.
- **MPF 0.80: Python 3.10 – 3.14.** Python 3.8 and 3.9 were dropped; 3.13 and 3.14 are officially supported. This is stated in `install/index.md`, the quickstart, `install/0.80.md` and the FAQ.
  - **[DOC CONFLICT]** `install/windows.md` says "0.80 requires Python 3.10 - 3.13, with 3.14 support planned".
  - **[DOC CONFLICT]** The quickstart's link text says "Python 3.13", but the link points to Python 3.14.3.
  - The `latest_versions` include recommends **Python 3.14** as "known-working on Windows and Linux".
- **[0.57/LEGACY] MPF 0.57: Python 3.8 – 3.12.** 3.13 and 3.14 "may work" with 0.57, but MPF-MC doesn't support them (the 0.57.5 release notes add 3.13/3.14 support to MPF only).
  - Other pages say 3.8–3.11 (`mac.md`) or 3.9–3.12 (`windows.md`, because MC audio is broken on Windows with 3.8).
- If you change Python versions, you must reinstall MPF with that version's pip.
- Because 0.80 no longer has Kivy dependencies, it also supports alternative interpreters such as **PyPy**.

### Recommended version set (the `latest_versions` include, "as of February 2026")

- Python 3.14
- MPF 0.80.0 (via pip)
- MPF-GMC 1.0.0 (via the Godot Asset Library)
- Godot Editor 4.6
- MPF Monitor 0.57.2

`install/index.md` says **MPF 0.80.0 requires GMC plugin 1.0.0**. The version conflicts are listed in §13.

### Step 1: Virtual environment (mandatory in practice)

The docs label this **"Do not skip the Virtual Environment"**. On current Debian (12) and Ubuntu (23+), pip refuses to install packages outside a venv, so a venv is *required* on those systems. On a dedicated cabinet PC a venv is technically optional, except on Debian/Ubuntu, but it is still recommended.

```shell
python3 --version                  # confirm 3.10–3.14
python3 -m venv ~/mpfenv           # create (any path/name is fine)
python3.13 -m venv ~/mpfenv        # or pick a specific interpreter if you have several
. ~/mpfenv/bin/activate            # Linux (POSIX "dot" form); Mac: source ~/mpfenv/bin/activate
deactivate                         # leave the venv
```

- Windows: `mpfenv\Scripts\activate.bat` (cmd) or `mpfenv/Scripts/Activate.ps1` (PowerShell).
- Once the venv is active, the prompt shows `(mpfenv)`, and `python` refers to the interpreter that created the venv.
- For a dedicated machine, the docs suggest adding the activate line to your bash/zsh profile so it runs at login.
- On Linux, add your user to the **`dialout`** group so MPF can talk to USB serial hardware. The docs say this is needed *regardless of MPF version*, including 0.80:

```shell
sudo usermod -a -G dialout your_username
```

  (This command appears in the Xubuntu page. The Linux index page gives the requirement but no command.)

### Step 2a: Standard install (pip)

```shell
pip install mpf --pre          # docs: "install MPF 0.80 with the latest dev build"
pip install --upgrade mpf      # update
mpf --version                  # verify
```

- **[DOC CONFLICT]** The docs still use `--pre` even though 0.80.0 is a final release. `--pre` lets pip pick pre-release builds. To pin an exact version, the FAQ shows the pattern `pip install mpf==<version>` (its example is `pip install mpf==0.56.0.dev33`).
- If you're upgrading an existing 0.57 venv, you *can* run `pip install --upgrade --pre mpf`. The docs instead recommend a **new, separate venv for 0.80**, so you can go back to 0.57 if needed.
- Pros listed in the docs: fast startup, easy upgrades, smallest disk footprint. Cons: needs a local Python and a venv, and you can't modify MPF.
- **pipx:** the Linux page says "we no longer suggest pipx". **[STALE]** The same page still mentions "the final two pipx commands".

### Step 2b: Expert install (editable clone)

```shell
git clone https://github.com/missionpinball/mpf
cd mpf
git checkout 0.80.x
pip install -e .
# update later with: git fetch && git pull  (inside the repo)
```

- `pip list` will show MPF running from the repo folder.
- Git remotes from the quickstart (updated August 2026):
  - MPF: tag `v0.80.0` on branch `0.80.x`. `0.81.0` is in testing on branch `dev`.
  - mpf-gmc: branch `main`, version `1.0.0`.
  - mpf-monitor: branch `1.0.x`, version `1.0.0.dev1`.
- The contributor guide adds: fork the repo and clone your fork, then `pip3 install -e .`, then run the tests with `python3 -m unittest discover -s mpf.tests`. Work from `dev` in most cases.

### Linux / Ubuntu / Raspberry Pi notes (mostly [STALE] 0.57 material)

The only Linux-specific requirement stated for 0.80 is the `dialout` group. The Linux pages themselves are flagged as 0.57/legacy guides:

- **`install/linux/index.md` [0.57/LEGACY]**
  - Says it "needs to be updated", and points to the GitHub Actions `build_wheels.yml` for the "real" build steps.
  - Describes the `mpf-debian-installer` (0.55.x): `chmod +x install && sudo ./install`, plus `./install-proc` for P-ROC.
  - The manual method is `pip3.x install mpf[all] mpf-mc mpf-monitor`, with `export PATH="$PATH:/home/user/.local/bin"` if `mpf` isn't found.
  - Upgrade: `pip3 install mpf[all] mpf-mc --pre --upgrade`. Pin: `pip3 install mpf[all]==x.yy.z`. Uninstall: `pip3 uninstall mpf-mc mpf`.
  - P-ROC fix: if `pinproc` isn't found, edit `install-proc` to use `python3 setup.py install --user`.
  - The page also advises: "MPF 0.80 requires Python 3.10+, so you may wish to start with a Python that can be used in either version."
- **`install/linux/raspberry.md` (updated Jan 2024) [STALE]**
  - Targets a **Pi 5 with Raspberry Pi OS Bookworm** (which "appears to have the power to run both MPF and MPF-MC").
  - The Pi 5 has **no analog audio jack**, so you need a USB audio interface.
  - Says pip wheels of MPF/MPF-MC "are not able to run on Raspberry Pi", so it installs in editable mode.
  - Uses `pyenv` with **Python 3.9.18** and the **0.56.x** branches. These don't satisfy 0.80's Python 3.10+ requirement.
  - Still useful parts:
    - apt dependencies: `sudo apt update && sudo apt upgrade`, then `libssl-dev libncurses-dev libffi-dev libreadline-dev libbz2-dev libsqlite3-dev liblzma-dev tk-dev` plus gstreamer/SDL2/ffmpeg dev packages (the SDL/gstreamer/ffmpeg ones are for MC).
    - Monitor-only deps: `libjpeg-dev libxcb-cursor0 libxkbcommon-x11-0 libxcb-icccm4 libxcb-keysyms1 libxcb-shape0 xsel`.
    - The pyenv install and `.bashrc` lines: `export PYENV_ROOT=...`, `eval "$(pyenv init -)"`, then `pyenv virtualenv <ver> mpf` and `pyenv activate <ver>/envs/mpf` added to `.bashrc`.
    - `export DISPLAY=:0` when launching windowed apps over SSH.
    - Hardening the Pi for cabinet use is "not fully known" and out of scope.
  - **There is no 0.80/GMC-on-Pi guide in this section.**
- **`install/linux/xubuntu.md` [mostly STALE]**
  - Covers an unattended cabinet install on Xubuntu/Lubuntu. **Do not encrypt the home folder**, or auto-login won't work.
  - LightDM auto-login file `/etc/lightdm/lightdm.conf.d/12-autologin.conf`:

    ```
    [Seat:*]
    autologin-user=your_username
    autologin-user-timeout=0
    ```

  - Optional: shorten the network wait by setting `TimeoutStartSec=10sec`.
  - Uses the old 0.55 Debian installer.
  - The **autostart pattern** is still relevant. `~/your_machine_folder/run.sh`:

    ```shell
    #!/bin/bash
    source ~/your_venv_name/bin/activate
    xterm -e "cd /home/your_username/your_machine_folder && mpf both -c config"
    ```

    and `~/.config/autostart/mpf.desktop`:

    ```
    [Desktop Entry]
    Version=1.0
    Name=MPF
    Comment=Mission Pinball
    Exec=/home/your_username/your_machine_folder/run.sh
    Path=/home/your_username/your_machine_folder/
    Terminal=false
    Type=Application
    ```

    (`mpf both` here is written for the legacy MC. See §6 for how `both` behaves with GMC.)
- **Pine64 [STALE, 2016]:** MPF runs, but MPF-MC does not.
- **VirtualBox/Debian VM guide [STALE]:** Covers creating the VM, `sudo`, Guest Additions, and a host-only adapter so you can SSH in. The docs note that a VM **can't emulate ARM/Raspberry Pi**, but can pass through USB/serial for hardware testing.
- **Mac [0.57/LEGACY]:** `brew install SDL2 SDL2_mixer SDL2_image gstreamer` (for MC). `pip install mpf[cli]` adds the text UI. There is also a gstreamer `DYLD_LIBRARY_PATH` workaround.
- **Windows [0.57/LEGACY]:** Don't use the Microsoft Store Python. Install from python.org, and tick "py launcher", "pip" and "Add Python to environment variables".

---

## 5. Installing the Godot Media Controller (GMC) — 0.80

The docs strongly recommend keeping your project in a git repo (see §3).

1. **Install MPF 0.80** as in §4.
2. **Download the Godot Editor** from godotengine.org. The GMC install page says 4.5 or later; the quickstart and `latest_versions` say **4.6**. Put it wherever you keep applications, **not** in your project folder.
3. **Create a new Godot project**, and select your **MPF machine folder** as the project path.
   - Renderer: **Mobile** is recommended for most pinball games. Use **Forward+** for advanced 3D, or **Compatibility** for very low-powered hardware. You can change this later.
4. Create an `addons/` folder in the Godot project root.
   - **Root vs `gmc/` subfolder:** you *can* put the Godot project in a `gmc/` subfolder of the machine folder. Godot can only see files inside its own project folder, so all slides, widgets, sounds and videos must then live under `gmc/` (e.g. `/gmc/slides/`), **not** in MPF mode folders like `/modes/attract/slides/`.
5. **Editor settings** (Editor > Editor Settings > Text Editor > Behavior):
   - **Disable** `Convert Indent on Save`. GMC uses tabs.
   - Enable `Trim Trailing Whitespace on Save`.
   - Enable `Auto Reload Scripts on External Change` if you use VS Code or another external editor.
6. **Install the GMC plugin.** Pick one method:
   - **Asset Library (simplest):** In the Godot editor, open AssetLib, search "GMC", then Download and Install. The result should be `<project>/addons/mpf-gmc`.
     - **[DOC CONFLICT]** The same page says the Asset Library carries GMC **0.1.6** for MPF `0.80.0.dev14`, while `install/index.md` says 0.80.0 needs GMC **1.0.0**.
     - To upgrade: close Godot, delete `addons/mpf-gmc/`, reopen and choose "Open Anyway", reinstall from AssetLib, then reload the project.
   - **Download and copy:** Get the ZIP from github.com/missionpinball/mpf-gmc (Code > Download ZIP, or a release under *Assets > Source code*). Copy `addons/mpf-gmc` into your project's `addons/`. Updates are manual: overwrite the folder.
   - **Git clone plus symlink (expert):**

     ```shell
     git clone https://github.com/missionpinball/mpf-gmc
     # Mac/Linux:
     sudo ln -s /path/to/mpf-gmc/addons/mpf-gmc /path/to/project/addons/mpf-gmc
     # Windows:
     mklink /d "C:\repos\pinballgame\addons\mpf-gmc" "C:\repos\mpf-gmc\addons\mpf-gmc"
     # update: cd mpf-gmc && git fetch && git pull
     ```

     You can check the link with `ls -la addons`. The install is correct when `<project>/addons/mpf-gmc/plugin.cfg` exists.
7. **Activate the plugin.** Expect errors during this step; ignore them.
   - Project > Project Settings > **Plugins**: enable **Godot MC**.
   - Project Settings > **Globals > Autoload**: click the **folder icon** (not "+ Add"), choose **`addons/mpf-gmc/mpf_gmc.gd`**, set Node Name to **`MPF`** (all caps; GMC won't work otherwise), then press + Add. Before Godot 4.3, this tab is called "Autoload".
   - Save, then restart Godot or use *Project > Reload Current Project*.
   - **[DOC CONFLICT]** The quickstart names the file `mpd_gmc.gd`, and a warning on the install page says `mpf_gmc.md`. The correct name, from the step-by-step text, is `mpf_gmc.gd`.
8. **If the project gets corrupted** (a flood of cached autoload errors that survives a restart): remove the project from the Godot Project List, delete the project's `/.godot` folder, and re-import `project.godot`.
9. After a GMC update, errors on the first open are expected. *Project > Reload Current Project* clears them.
10. **Version check:** since `0.80.0.dev9`, MPF checks that the installed GMC version is compatible. dev9 required GMC ≥ 0.1.5.

**First run (quickstart):**

- Press Play in the Godot editor. When asked for a main scene, choose **`addons/mpf-gmc/slides/window.tscn`**. The window shows the MPF logo and "Waiting for MPF...".
- Then, in the venv, in the machine folder, run `mpf -xt` (virtual platform, no text UI). The window should change to "Connected to MPF".
- Either side can start first; each waits for the other.
- Alternatively, configure GMC to launch MPF itself from the "MPF" tab in the Godot editor. The settings are saved to `gmc.cfg`, and the pattern is `<executable_path> <executable_args> <machine_path> <mpf_args>`. Don't combine this with `mpf both`, or you'll get two MPF instances.

---

## 6. Running MPF: every `mpf` command

`mpf` is registered on PATH when you install MPF. Run commands from the **machine folder**, or pass the machine folder as the **first positional argument after the command name, before any dashed options**:

```shell
mpf game ./path/to/machine_folder -P
mpf ./path/to/machine_folder -P        # same thing; bare "mpf" == "mpf game"
```

Single-letter flags can be combined: `mpf game -vVa` is the same as `-v -V -a`. `mpf --version` prints the version.

### Command list

| Command | What it does |
|---|---|
| `mpf` / `mpf game` | Starts the MPF game engine. `game` is the default when no command is given. |
| `mpf both` | Starts MPF and the media controller together. **0.80:** launches your Godot project (needs a Godot executable). **Legacy:** launches MPF-MC. Console output from both is mixed, but the log files stay separate. |
| `mpf mc` | **[0.57/LEGACY]** Starts MPF-MC only. |
| `mpf imc` | **[0.57/LEGACY]** Interactive MC: the MC plus a live YAML editor window for slides and widgets. It doesn't connect to physical hardware (a physical DMD can't be used; test with an on-screen virtual DMD). |
| `mpf monitor` | Starts MPF Monitor (separate install). |
| `mpf service` | Interactive service CLI. Connects over BCP to a *running* game and puts it into service mode. |
| `mpf hardware scan` | Enumerates the configured hardware platforms, dumps their state and exits. Run it **without** MPF already running. |
| `mpf hardware firmware_update` | Updates controller firmware where the platform supports it. Some platforms need config to enable this. |
| `mpf hardware benchmark` | Measures latency and jitter of inputs, outputs and hardware rules (see §7). |
| `mpf diagnosis` | Prints the installed MPF (and MPF-MC) versions, install location, detected machine folder, and **serial ports found** (with desc/hwid). |
| `mpf build production_bundle` | Compiles configs and shows into bundles for production. |
| `mpf format <file.yaml>` | Previews reformatting of a config file; add `--yes` to write the changes. |
| `mpf test <file>` | Runs a single-file test (see §9). |
| `mpf migrate` | Documented as "migrates config and show files built for prior versions". **[DOC CONFLICT]** `install/0.57.md` says 0.57 "Removed the config file migrator (hasn't been used in years)". The 0.57 upgrade to config v6 is a manual guide (`config/instructions/config_v6.md`). |
| `mpf core` | Runs the MPF core modules with no game logic (for external control, e.g. PinMAME). "Not fully implemented yet." |

### `mpf game` flags (these also apply to `mpf both`)

| Flag | Meaning |
|---|---|
| `-a` | Force reload of the config from the YAML files, bypassing the cache (cached in the system temp folder). |
| `-A` | Don't cache the config files. |
| `-b` | Disable BCP, so MPF won't try to connect to a media controller. **Without `-b` and without a running MC, MPF won't finish starting**; it waits for the MC. |
| `-c name[,name2]` | Config file(s) in `config/` (default `config.yaml`; the `.yaml` extension is optional). Use commas with no spaces to merge files, e.g. `-c config,fast`. A full path is also accepted. |
| `-C file` | Override MPF's built-in default config `mpfconfig.yaml`. |
| `-f` | Load all assets at start (useful for validating assets). |
| `-h` | Help. |
| `-t` | **Disable the text UI.** Recommended for debugging (the TUI can hide errors) and for production. |
| `-l path` | Log file path. Default: `logs/<y>-<m>-<d>-<H>-<M>-<S>-mpf-<hostname>.log`. |
| `-v` | Verbose logging **to the log file**. Logs can grow to about 1 MB per minute. |
| `-V` | Verbose logging **to the console**. Not recommended on Windows, where the slow console hurts MPF. |
| `-x` | Ignore `platform:` settings and use the **virtual** platform. |
| `-X` | Use the **smart_virtual** platform. It simulates ball devices and is the one the docs recommend with Monitor. |
| `--vpx` | Use the Virtual Pinball (VPX) platform. |
| `-pit` | Run a platform integration test. |
| `--json-logging` | Write the log file in JSON. |
| `-P` | **Production mode:** suppresses errors, waits for hardware at startup, and tries to exit if startup fails. The docs recommend running it inside a loop (see `finalization/software.md`). |
| `-p` | Pause on exit, so a transient shell window doesn't close on a crash. |
| `--syslog_address` / `--syslog-address` | Log to syslog: `/dev/log` on Linux, `/var/run/syslog` on Mac, or `host:port` over UDP. Both spellings appear in the docs. **[DOC CONFLICT]** |

### `mpf both` extras for GMC (0.80)

```shell
mpf both -tX -g gmc-project/ -G ~/godot_installs/godot.exe
```

- `-g <path>`: the folder containing `project.godot`. Defaults to the current directory; only needed for the subfolder layout.
- `-G <path>`: the Godot executable. By default `both` looks for a Godot executable on PATH. On Windows, the docs suggest renaming `Godot_<version>.exe` to `Godot.exe` and putting it in the folder you run from, or adding its folder to PATH.
- **Don't use `both` if GMC is configured to auto-start MPF.**
- **[0.57/LEGACY]** With `both`, options are passed through to MPF-MC too. Use `-l` for the MPF log and `-L` for the MC log. Quit with `Esc` in the MC window or `Ctrl+C` in the console.

### `mpf mc` flags [0.57/LEGACY]

`-c`, `-C` (overrides `mcconfig.yaml`), `-f`, `-h`, `-l`/`-L`, `-v`, `-V`. It accepts `-a -A -x -X` but ignores them.

### `mpf build` flags

- `production_bundle` creates `mpf_config.bundle` (and, for legacy projects, `mpf_mc_config.bundle`) in the machine folder.
- **Rerun it after any config, mode or show change, and after every MPF upgrade.** The target machine must run *exactly* the same MPF version.
- `-b`: MPF only, no MC. **For 0.80 and later you should always pass `-b`.**
- `-c`: which config files to include.
- `--dest-path`: the `machine_path` to embed in the bundle, if the production path differs from the path on the build machine.

### Typical invocations

```shell
mpf -xt                      # 0.80 dev: virtual HW, no TUI, with GMC started separately
mpf both -X                  # smart virtual + MC in one go
mpf game -t -v -V            # debugging
mpf -b -x                    # engine only, no MC at all
mpf game -P                  # production (run in a restart loop)
```

---

## 7. Tools

### MPF Monitor

- A PyQt6 GUI that connects to a running MPF over BCP on `localhost:5051`.
- It shows devices, events (and lets you **post events with params back to MPF**), modes and variables.
- You can drag switches and lights onto a playfield photo:
  - **left-click** a switch to *tap* it
  - **right-click** a switch to *toggle/hold* it
  - LEDs show their live color
- It reconnects automatically when MPF restarts. It is not a physics simulator.
- **Versions:**
  - Monitor 1.0.0 works with MPF 0.57–0.58 and 0.80–0.81.
  - 0.57.x also works with 0.57 and later.
  - Monitor version numbers are unrelated to MPF's; what matters is the BCP version.
  - 1.0 "can run without needing MPF itself installed". 0.57 and earlier need MPF and run via `mpf monitor`.
  - **[DOC CONFLICT]** `latest_versions` recommends Monitor 0.57.2; the Monitor pages say 1.0.0 is current as of September 2026.
- **Install:** `pip install mpf-monitor`.
- **Setup:**
  1. Create `<machine>/monitor/`.
  2. Add `playfield.jpg`.
  3. Run `mpf monitor` from the machine folder.
  4. Start MPF (before or after the monitor) in another terminal.

  The Inspector window's "Monitor" tab toggles the Device, Event, Playfield, Mode and Variables windows. Device positions are saved as percentages in `monitor/monitor.yaml`. Window layout is saved in `monitor/settings.ini`; the docs recommend **not** committing it to git.
- **CLI options:**
  - `-l logfile` (default `logs/TIMESTAMP-monitor-hostname.log`)
  - `-i img1.jpg,img2.png` (images in `monitor/`; PNG, JPG, BMP, or GIF (first frame only))
  - `-is` (load all images in `monitor/`)
  - `-ip <address>` and `-port <port>` (remote MPF)
- **`monitor.yaml` hidden options.** Never edit the file while Monitor is running.
  - `device_alpha` (0–255, default 220)
  - `device_outline` (px, default 3)
  - `device_size` (e.g. `0.02`)
  - `custom_shape_points` with `shape: CUSTOM` (keep points within about ±0.5)
- **Device Inspector:** while it's on, clicks do **not** reach MPF. Use it to resize, rotate, reshape, delete or "Reset to Defaults" a device (reset can't be undone).
- Filtering accepts regex (start with `/`) or a prefix match (`^`).
- Be careful toggling switches while real hardware is attached; a ball sitting on a switch will confuse MPF.
- Using two switch sources for one switch (hardware + Monitor + keyboard) triggers the harmless warning `Log-SwitchController-1` ("duplicate switch state").

### Service CLI (`mpf service`)

Start the game first (e.g. `mpf both`), then run `mpf service` from the machine folder. The game enters service mode; tab completion works. Commands:

- `list_coils`, `coil_pulse <name>`, `coil_enable <name>` (only if enable is allowed), `coil_disable <name>`
- `list_switches`, `monitor_switches` (stop with Ctrl+C)
- `list_lights`, `light_color <name> <color>`, `light_off <name>`
- `exit` / `quit` (the game resets and starts)

### Hardware benchmark (`mpf hardware benchmark`)

**Disconnect or disable high voltage first.** Wire `s_test1` to `c_coil1`, and `s_test2` to `c_coil2`. Then configure:

```yaml
switches:
  s_test1: {number: }
  s_test2: {number: }
coils:
  c_coil1: {number: }
  c_coil2: {number: , allow_enable: true}
flippers:
  f_flipper: {activation_switch: s_test1, main_coil: c_coil2}
hardware_benchmark:
  coil1: c_coil1
  coil2: c_coil2
  switch1: s_test1
  switch2: s_test2
  flipper: f_flipper
```

(The docs write this in block style; it is condensed here.) MPF pulses `c_coil1`, which triggers `s_test1`. The hardware rule then fires `c_coil2`, which triggers `s_test2`. MPF repeats this and reports timing statistics.

### Other tools

- **`mpf format`**: reformats and lints YAML (for example, list indentation, `True` becomes `true`). It shows a diff and writes only with `--yes`.
- **Showcreator** (github.com/missionpinball/showcreator): generates light shows by sweeping shapes over the LED positions stored in `monitor/monitor.yaml`.
  - Windows: `led.exe`. Mac: `led mac x64.app`.
  - **Linux has no binary.** Install BlitzMax, clone the whole repo, open `led.bmx` in MaxIDE, and build to get `./led`. It asks for the `monitor.yaml` path on the console.
  - An alternative tool is `mpfLightAndShowGenerator`.
- **Language server (mpf-ls)**: see §3.
- **Machine fuzzer** (afl-based): exists but is undocumented.
- **iMC**: legacy only (see §6).
- Planned tools (not built): a GUI config builder, show and slide tools, and so on.

---

## 8. Logging and troubleshooting

### Standard debugging procedure (`troubleshooting/general_debugging.md`)

1. **Turn off the text UI** with `mpf both -t`. The TUI can hide crashes.
2. **Run MPF and the MC separately** so their logs don't mix: `mpf game -t` in one terminal, and the MC (legacy `mpf mc`, or Godot) in another.
3. **Increase verbosity** with `mpf game -t -v -V` (or `mpf both -t -v -V`). Scroll up to find the first error. The docs say this is fine during development but shouldn't be used in production.
4. **Read the `logs/` folder.** MPF and the MC write separate logs, with more detail than the console.
5. **Enable `debug: true`** on the suspect device or platform. It's cheap on devices; on platforms it can produce many lines and cost performance.

   ```yaml
   switches:
     my_switch:
       number: 42
       debug: true
   p_roc:
     debug: true
   ```

### Reading errors

MPF exceptions are chained. **Read from the bottom up**: the bottom is the most general error, and the entries above it are more specific. Example: `Failed to configure switch s_door_back` at the bottom, caused by `Cannot find board for switch 0-7` above it, which means a node board is missing.

### Error codes (`logs/`)

MPF gives common errors IDs; there are about 200, and few are documented. Look them up by ID:

- **CFE-coils-1**: a coil has no `number:`. For an unwired coil, use `number:` (blank) plus `platform: virtual`.
- **CFE-ConfigValidator-1**: a device that needs player variables is defined in a non-game mode (`game_mode: false`). Attract, match and high score modes aren't game modes. Use machine variables (`action: add_machine`/`set_machine`) or `persist_state: false`.
- **CFE-ConfigValidator-2**: unknown setting name. Causes: a typo (it's case-sensitive), a setting copied from another device type, wrong indentation, or a config from a different MPF version.
- **CFE-ConfigValidator-4**: invalid validator in a config spec. It's an MPF bug unless you wrote custom specs.
- **CFE-ConfigValidator-6**: a referenced device wasn't found. Causes: a typo, copy-pasted doc examples with hidden devices (use "Click to show full config"), or the wrong device type.
- **CFE-ConfigValidator-9**: a required setting is missing.
- **CFE-ConfigValidator-12**: expected a dict (e.g. `show_tokens`), got a list or the wrong indentation.
- **CFE-ConfigValidator-13**: can't convert to boolean. Don't quote `"false"`. Old `repeat: -1` should become `repeat: false`.
- **CFE-DeviceManager-3**: device config isn't a dict. You usually forgot the device name level, e.g. `switches: number: 1`.
- **CFE-show-1**: invalid show. Each show file holds exactly one show (the filename is the show name), and every step needs a leading `-`.
- **CFE-(Smart_)Virtual_Platform-1**: a switch in `virtual_platform_start_active_switches` isn't defined. Use a YAML list or a comma-separated list; space-separated lists were removed in 0.54.
- **RE-MPF_BCP_Server-1 / RE-MPF-MC_BCP_Server-1**: can't bind port 5051/5050 (see §1).
- **RE-P-Roc-1**: a P3-ROC firmware ≤ 2.14 bug with `pulse_power` plus hold rules. Remove `pulse_power` or upgrade the firmware.
- **RE-P-Roc-2**: `OSError: Error in WriteData`. Likely a bad USB cable or power supply.
- **RE-P-Roc-3**: `pinproc` can't be imported.
- **Log-SwitchController-1**: duplicate switch state. Harmless: MPF ignores the repeat. Seen with smart_virtual, with multiple switch sources, and with P-ROC debounced switches.

### YAML parse errors

`ValueError: YAML error found in file ... Line 22, Position 10: mapping values are not allowed here`: the actual problem is at or near that line.

- Use the language server to find it.
- `mpf format` can reformat the file.
- Or use the ruamel tool: `pip3 install ruamel.yaml.cmd==0.2`, then `yaml round-trip your_file.yaml` to preview and `--save` to apply. **Back up or commit first.**

### Install problems

- **ruamel.yaml `VersionConflict`**: caused by mismatched `mpf` / `mpf-mc` / `mpf-monitor` versions, or a system ruamel. Check with `pip3 list`. The docs' fix is `pip3 uninstall mpf mpf-mc mpf-monitor` then reinstall. Better still, use a clean venv. **[STALE]** This advice dates from the 0.53 era.
- **Sanity checks:**
  - Run `mpf diagnosis`.
  - Run the demo_man example that matches your MPF version.
  - Run the unit tests: `python3 -m unittest discover -s mpf.tests` (and, **[LEGACY]**, `-s mpfmc.tests`).

### Segfaults and hangs

Find the PID with `ps aux | grep mpf`. Then:

```shell
sudo gdb python3 <pid>
(gdb) thread apply all bt
(gdb) thread apply all py-bt
```

Send the full output to the developers. A PyCharm debugger-attach video also exists.

### Memory leaks

Post the event `debug_dump_stats` (not in production mode). It dumps registered event handlers, and in the legacy MC also slides, widgets, objects and clock events. Dump once at start and again a few minutes later, then compare, looking for handler counts that keep growing and duplicated slides or widgets.

**[0.57/LEGACY]** The documented trigger is a `keyboard:` mapping (`d: {event: debug_dump_stats}`), but `keyboard` is a **deprecated section in 0.80**.

### Asking for help (forum or GitHub Discussions)

Include:

- `mpf diagnosis` output
- only the relevant config snippets (a git repo link is ideal)
- a log from `mpf both -v -V` with `debug: true` on the relevant devices
- the error message
- reproduction steps, ideally a minimal config or a **single-file test**

Bugs go to GitHub issues: `mpf`, `mpf-mc`, `mpf-monitor` or `mpf-docs`.

---

## 9. Testing

- `testing/index.md` is an **incomplete placeholder (TODO)**.
- It describes automated tests that script actions and assert on state (e.g. "push start, then check a ball ejected"), recommends a TDD approach, and recommends **fuzz tests** (random switch hits) that you "set up EARLY and run OFTEN".
- It points to the legacy tutorial's unit-testing chapter, the developer site's machine-test docs, and an example (`BnD/tests/test_bnd.py`).

**Single-file tests (`mpf test <file>`).** One YAML file holds the machine config, `##! mode: name` sections, `##! show: name` sections, then `##! test` followed by `#!` commands:

```yaml
# machine-wide config here (normally config/config.yaml)
##! mode: some_mode
# mode config here
##! show: some_show
# show here
##! test
#! start_game
#! advance_time_and_run 1
#! post some_event
```

The available commands are the methods of `MpfDocTestCase` (mpf/tests/MpfDocTestCase.py) with the `command_` prefix removed. The docs prefer single-file tests as bug reproductions.

Other options:

- The **Platform Integration Test** runner (`-pit`, new in 0.57.1) runs automated test games on physical hardware.
- MPF's own suite: `python3 -m unittest discover -s mpf.tests`.

---

## 10. Migrating 0.57 → 0.80 (`install/0.80.md`)

The release notes recommend a **stepwise upgrade**: go to **0.57.5** first, test, then move to 0.80.0. They also say non-MC changes were backported to 0.57.5, so 0.80's changes are limited to the GMC integration. The migration page is dated Feb 15, 2026 and still talks about `0.80.0.dev14` **[STALE]**.

### Python and versions

- 3.8 and 3.9 are dropped. Reinstall MPF with the new Python's pip.
- MPF checks GMC compatibility (since dev9).

### Media sections

- GMC owns all slides, widgets and sounds.
- `slides:` / `widgets:` are deprecated.
- `sound_system:` / `sounds:` are deprecated. You can still refer to sounds by **filename**; for per-sound settings, use a GMC `MPFSoundAsset` resource.
- Audio **"tracks" are now "buses"**: in `sound_player:`, change `track: music` to `bus: music`.
- Sound pools: use Godot's `AudioStreamRandomizer`, optionally inside an `MPFSoundAsset`.
  - Unsupported workaround: `pip install mpf-mc` into the 0.80 venv so it injects the `sound_pools:` config.
  - Pool entries must then use sound **file names**.

### Config sections you must remove (deprecated since `0.80.0.dev12`)

```
animations, assets:bitmap_fonts, assets:images, assets:sounds, assets:videos,
bitmap_fonts, effects, image_pools, image_templates, images, images_frame_skips,
keyboard, kivy_config, mc_custom_code, mpf-mc, playlist_player,
playlist_player_actions, playlists, slides, sound_loop_player,
sound_loop_player_actions, sound_loop_sets, sound_system, sounds, track_player,
transitions, widget_styles, widgets
```

(Note that `keyboard` and `mpf-mc` are in this list, which affects the legacy port-change and debug-dump examples above.)

### Built-in mode changes

- **Bonus:** in `bonus.yaml` entries, `event: bonus_item_name` becomes `entry: bonus_item_name`. The per-item events are now one event:
  - 0.57: `completed_ramps{hits=3, score=3000}`
  - 0.80: `bonus_entry{entry="completed_ramps", hits=3, score=3000}`

  A default Godot bonus slide is provided; copy it to customize.
- **Carousel** (dev10):
  - 0.57: `missionselect_garrus_highlighted{direction=...}`
  - 0.80: `carousel_item_highlighted{carousel="missionselect", item="garrus", direction="forwards"}` (and `carousel_item_selected`)

  Update any custom handlers that listened for the old events.
- **High score:**
  - Name-entry controls are built in. Switches tagged `start`, `left_flipper` and `right_flipper` drive them automatically. Otherwise post `text_input{action:left|right|select}` (see `event_player` in MPF's `high_score.yaml`).
  - The events `high_score_award_display`, `(award_name)_award_display` and `(category_name)_award_display` are collapsed into **`high_score_award_display`**, with params `award`, `category_name`, `player_num`, `player_name` and `value`.
  - Default Godot slides are provided. Copies with the same names in your slides folder override them.
- **Tilt:** 0.57 had the slides `tilt_warning_1`, `tilt_warning_2` and `tilt`. 0.80 has one `tilt` slide for all three cases (see `slide_player` in `tilt.yaml`).

---

## 11. Version history highlights

Version numbers use semver (MAJOR.MINOR.PATCH, not decimals: 0.30 is newer than 0.3). Minor versions can change configs; patch versions are bug fixes only.

- **0.80.0 (Apr 25 2026)**
  - MPF-MC is replaced by **GMC**.
  - Python 3.8/3.9 dropped; 3.13/3.14 supported.
  - Some events collapsed into generic ones (bonus, carousel, high score).
  - Otherwise functionally the same as 0.57.5.
- **0.57.5 (Apr 25 2026)**
  - The last 0.57 release and the recommended stepping stone.
  - Python 3.13/3.14 for MPF (not for MC).
  - New options:
    - `sequence_shots: allow_multiple_active`
    - `multiballs: restart_grace_period`
    - score reel chime events
    - image `mag_filter`/`min_filter`
  - OPP incandescent lights use three-part numbering.
  - Event-loop change for Python 3.14.
  - random_event_player fixes.
  - **Breaking:** Pillow 10.4.
- **0.57.4 (Jan 19 2026)**
  - New **Shaker** device.
  - Virtual platform behaviors: `virtual_platform_add_ball_to_device`, `virtual_platform_remove_ball_from_device` and `virtual_platform_set_switch`.
  - Carousel `wrap_items`.
  - FAST: Stepper, 1313 EXP shaker board, `fast_net: mute_unconfigured_switches`, audio volume machine vars.
  - Pin2DMD HD (256×64) and ZeDMD.
  - Attract mode now inherits from Carousel.
  - Shot name added to shot-group hit events.
  - Crash reporter defaults to `never`.
  - Validation error numbers de-duplicated.
  - Many fixes: counters, audits, FAST port detection.
  - Spike, LISY and PKONE tests disabled under Python 3.12.
- **0.57.3 (Sep 2024)**
  - `min_mpf_version` config option.
  - FAST EXP `ignore_led_errors`.
  - High score filler names.
- **0.57.2 (Jul 2024)**
  - Ball search overhaul.
  - Switch options `ignore_during_ball_search:` and `playfield:`.
  - Spinner `max_events_per_second`.
  - OPP `WING_SOL_8`.
- **0.57.1 (May 2024)**
  - Python 3.10/3.11.
  - Segment display `update_method`.
  - Auditor "missing switches" report.
  - **Platform Integration Test** runner.
  - Light chain service menu.
- **0.57.0 (Mar 10 2024)**
  - **config_version=6 / show_version=6.** Pure-YAML spec: numeric colors with leading zeros (e.g. `"005599"`) and relative times (`"+1"`) must be quoted, and `omap` is replaced by `dict`.
  - FAST platform rewritten (Neuron and Retro).
  - asyncio event loop.
  - RGBW mapping.
  - `timed_enable_events` on coils.
  - `scriptlets` deprecated in favor of `custom_code`.
- **0.56 (Jan 2023)**
  - FAST V2 controllers.
  - OPP servos and pulse_power.
  - Coil `timed_enable`.
  - Multiball ball-save hurry-up.
  - Production bundle options.
- **0.55 (Jun 2021)**
  - Python 3.8/3.9 added.
  - VPE support, PKONE, production bundles, `mpf hardware benchmark`, crash reporter.
  - Coil `max_hold_duration`.
- **0.54 (Nov 2020)**
  - `ball_locks` removed (use `multiball_locks` / `ball_holds`).
  - Space-separated lists removed.
  - The diagnostics menu moved under service mode.
- **0.53 (Jan 2020)**
  - `repeat: -1` becomes `repeat: false`.
  - ball_save `active_time` changed from ms to seconds.

Docs for older versions: archive.org bundles exist for v0.33 and v0.50–v0.56. You can also find them under the "Assets" link on each GitHub release.

---

## 12. Quick "which docs are legacy?" checklist

**Current for 0.80:**

- `install/index.md`
- `start/quickstart.md`
- `install/0.80.md`
- `gmc/installation.md`
- `running/commands/both.md` (GMC section)
- `tools/build.md` (the `-b` note)
- `tools/monitor/*`

**Legacy (0.57/MPF-MC) or stale:**

- `install/0.57.md`, `mac.md`, `windows.md`
- `linux/index.md`, `raspberry.md` (Python 3.9, 0.56 branches), `xubuntu.md` and `pine64.md` (0.55 Debian installer)
- the virtual-machine guide
- `running/commands/mc.md`, `imc.md`, `tools/imc.md`
- `running/ports.md` (`mpf-mc:` section)
- the memory-leak `keyboard:` trigger
- `running/index.md`, which still presents `mpf both`/`mpf mc` in MPF-MC terms and mentions pre-0.30 history
- `features.md` (mentions the iMC and keyboard interface)
- the MPF-MC unit tests
- the tutorial link from the home page (0.56/0.57; "Tutorial for MPF 0.80 coming soon")

---

## 13. Notable contradictions and gotchas found

1. **GMC autoload filename:** `mpf_gmc.gd` is correct. The quickstart says `mpd_gmc.gd`, and a warning says `mpf_gmc.md`. The Node Name **must** be `MPF`.
2. **GMC version for 0.80.0:** `install/index.md` and `latest_versions` say 1.0.0. The Asset Library note says 0.1.6 (for dev14), and the migration page says ≥ 0.1.5 (for dev9).
3. **Godot version:** 4.5+ (GMC install) versus 4.6 (quickstart and latest_versions).
4. **Python for 0.80:** 3.10–3.14 in most pages; 3.10–3.13 in `windows.md`.
5. **Monitor version:** 0.57.2 (latest_versions) versus 1.0.0 (Monitor pages); the quickstart points at the `1.0.0.dev1` branch.
6. **`install/index.md`** says 0.80.0 is the current stable, while its own banner says "0.80 coming soon". It also still says `pip install mpf --pre` installs "the latest dev build".
7. **`mpf migrate`** is documented, but `install/0.57.md` says the migrator was removed.
8. The quickstart names the venv `mpf` but uses the Windows activation path `mpfenv/Scripts/Activate.ps1`.
9. **No 0.80-specific Raspberry Pi or Linux cabinet guide** is in this section. The Pi page targets Python 3.9 and 0.56.
10. **Without `-b`, MPF blocks at startup** until a media controller connects on 5050.
11. **The production bundle must match the exact MPF version.** Rebuild it on every MPF upgrade, and use `-b` for 0.80.
12. **`-V` on Windows** slows MPF significantly.
13. `gmc/installation.md` contains a stray git merge-conflict marker (`>>>>>>> e6e7384f8`) after the Windows `mklink` example.

---

## Sources (relative to `docs/`)

`index.md`; `start/index.md`, `start/features.md`, `start/media_controller.md`, `start/config_files.md`, `start/dsl_vs_programming.md`, `start/quickstart.md`; `install/index.md`, `install/0.80.md`, `install/0.57.md`, `install/virtual-environments.md`, `install/mac.md`, `install/windows.md`, `install/linux/index.md`, `install/linux/raspberry.md`, `install/linux/xubuntu.md`, `install/linux/pine64.md`, `install/virtual-machine/index.md`, `install/virtual-machine/why-use-vm.md`, `install/virtual-machine/basic-guide.md`; `gmc/installation.md`; `running/index.md`, `running/mpf.md`, `running/ports.md`, `running/commands/{index,both,build,core,diagnosis,format,game,hardware,imc,mc,migrate,monitor,mpf,service,test}.md`; `tools/index.md`, `tools/build.md`, `tools/format.md`, `tools/hardware.md`, `tools/imc.md`, `tools/service_cli.md`, `tools/test.md`, `tools/showcreator.md`, `tools/language_server/index.md`, `tools/monitor/{index,installation,running,devices-and-using,customization}.md`; `troubleshooting/{index,general_debugging,attaching_a_debugger,reading_errors,debugging_mpf_install,debugging_segfaults,debugging_yaml_parse_errors,debugging_memory_leaks,common_problems_and_solutions}.md`; `logs/index.md` and all `logs/CFE-*`, `logs/RE-*`, `logs/Log-SwitchController-1.md`; `testing/index.md`; `faq/{index,general,game,help,installation}.md`; `versions/{index,understanding,docs,release_notes,roadmap,release_checklist}.md`; `about/{index,authors,license,help,help_docs,contributing_to_mpf}.md`; include `../includes/latest_versions.md`.

Also checked briefly for context (outside the assigned section): `tutorials/legacy_mc/2_creating_a_new_machine.md` (machine folder and `#config_version=6`) and `gmc/guides/launching-the-mpf-game-with-godot.md` (GMC on port 5050, auto-launch of MPF).
