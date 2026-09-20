# 05 — Media (Godot Media Controller) and the Show System

Practical reference for MPF 0.80 (released 25 April 2026) with the Godot Media Controller (GMC), the MPF show system, and a short summary of the legacy Kivy MPF-MC. It is drawn only from the MPF docs source (`dev` branch). Where the docs contradict each other or leave something out, this is flagged with **[DOC NOTE]**.

---

## 1. The big picture

### 1.1 Game engine versus media controller

MPF has always been two separate processes:

- **The MPF game engine** (Python). It runs the rules and modes, talks to the hardware (switches, coils, lights) and runs shows.
- **A media controller (MC).** It renders graphics and plays sound.

They talk over **BCP (Backbox Control Protocol)**, a TCP socket protocol that MPF created (`docs/mc/index.md`, `docs/start/media_controller.md`). The docs give two reasons for the split. First, each process can use its own CPU core. Second, the MC can be swapped out: Unity, C# and Lua MCs exist, and you can write your own ("listen for incoming BCP connections and then parse the commands", `mc/creating_your_own.md`).

`mc/index.md` says there are two official media controllers:

| | Legacy MPF-MC | GMC (MPF-GMC) |
|---|---|---|
| Tech | Python + Kivy (SDL2, GStreamer, OpenGL) | Plugin (addon) for the Godot 4 game engine |
| MPF versions | up to 0.57 (0.57.5 is the last) | 0.80+ |
| How content is defined | YAML (`slides:`, `widgets:`, `sounds:` …) | Godot scenes (`.tscn`) and resources (`.tres`) edited visually in the Godot editor |

### 1.2 What changed in 0.80

From `versions/release_notes.md` and `install/0.80.md`:

- 0.80.0 replaced MPF-MC with GMC. According to the release notes, changes that are *not* about the media controller were backported to 0.57.5. The 0.80 changes are "limited to the GMC integration replacing the legacy MPF-MC".
- Python 3.8 and 3.9 are dropped. 3.10–3.14 are supported. 3.13 and 3.14 are newly official.
- Some events were collapsed into generic versions so they are easier to use from Godot (bonus, carousel, high score; see §9).
- The recommended upgrade path is stepwise: 0.57.5 first, test, then 0.80.0.

### 1.3 Why Godot (from `gmc/index.md`)

- The downloadable binaries work on every platform, so there is no pip/Kivy/gstreamer/SDL install pain.
- Slides are edited visually with drag-and-drop and real-time feedback, and components are reusable.
- Everything is scriptable (GDScript) directly in slides.
- It is backed by the full Godot documentation and community. It performs well, and custom builds can be stripped down for low-power hardware.

---

## 2. Versions and installation

### 2.1 Version matrix

The shared include `includes/latest_versions.md` (February 2026) lists this as the known-good full install:

- Python 3.14
- MPF 0.80.0 (via pip)
- **MPF-GMC 1.0.0** (via the Godot Asset Library)
- **Godot Editor 4.6**
- MPF Monitor 0.57.2

`install/index.md`: "MPF 0.80.0 requires the Godot MPF-GMC plugin to be version `1.0.0`." `start/quickstart.md` also lists Python 3.13, MPF-GMC 1.0.0 (branch `main`), Godot 4.6 and MPF Monitor `1.0.0.dev1` (branch `1.0.x`).

`install/0.80.md`: from `0.80.0.dev9` onwards, MPF **checks that the installed GMC version is compatible** (dev9 needed GMC ≥ 0.1.5).

> **[DOC NOTE]** Several version statements are out of date:
> - `gmc/installation.md` says "the latest 2026 development release of MPF (0.80.0.dev14) requires GMC plugin version 0.1.6" and "Download Godot 4.5+".
> - `install/0.80.md` still calls 0.80 "upcoming", recommends `0.80.0.dev14`, and is dated Feb 15 2026.
> - `start/quickstart.md` disagrees with the MPF Monitor version above.
>
> For a new build, use MPF 0.80.0, GMC 1.0.0 and Godot 4.6.

### 2.2 Install MPF 0.80

Follow the normal MPF install guide. If you already have 0.57, `pip install --upgrade --pre mpf` works. The docs recommend a **separate virtual environment** for 0.80 so that you can go back to 0.57.

> **[DOC NOTE]** The per-OS guides (`install/linux`, `install/mac.md`, `install/windows.md`) are still headed "MPF 0.80 is Coming Soon" and describe 0.57 with the legacy MC. The Linux guide's note about adding your user to the `dialout` group still applies to 0.80.

### 2.3 Create the Godot project

1. Download the Godot editor (4.5+; 4.6 per the version matrix) from godotengine.org. Keep it outside your game folder.
2. Create a **New Project** in Godot and choose your **MPF machine folder** as the project path.
3. Choose a renderer. **Mobile** is recommended for most pinball games. Use **Forward+** for advanced 3D and **Compatibility** for very low-powered hardware. You can change this later.
4. In the Godot project folder, create an `addons/` folder.

**Root project or `gmc/` subfolder?** Some people keep the Godot project in a `gmc/` subfolder of the MPF machine folder so the Godot FileSystem panel stays tidy. The catch is that **Godot can only see files inside its own project folder**. In that layout, all slides, widgets, sounds and videos must live under `gmc/` (for example `gmc/slides/`), **not** in the MPF mode folders (`modes/attract/slides/`). With the root layout, per-mode `slides/` and `sounds/` folders work.

### 2.4 Recommended Godot editor settings

In *Editor → Editor Settings → Text Editor → Behavior*:

- **Disable** `Convert Indent on Save`. GMC is tab-indented, and auto-convert causes grief. You can switch Indent to Spaces if you prefer spaces for your own code.
- Enable `Trim Trailing Whitespace on Save`.
- If you use VS Code or another external editor, enable `Auto Reload Scripts on External Change`.

### 2.5 Install the GMC plugin (three ways)

1. **Asset Library (simplest).** In the editor, open **AssetLib** (top centre), search "GMC", then Download and Install. Check that `addons/mpf-gmc` now exists. *To upgrade:* close Godot, delete `addons/mpf-gmc/`, reopen and choose "Open Anyway" at the missing-dependency warnings, reinstall from AssetLib, then reload.
2. **Download ZIP.** From `https://github.com/missionpinball/mpf-gmc` choose Code → Download ZIP and copy `addons/mpf-gmc` into your project's `addons/`. Every update is manual: repeat the copy.
3. **Git clone (expert).** Run `git clone https://github.com/missionpinball/mpf-gmc`, then either **symlink** or copy the folder:
   - macOS/Linux: `sudo ln -s /path/mpf-gmc/addons/mpf-gmc /path/pinballgame/addons/mpf-gmc`
   - Windows: `mklink /d "C:\repos\pinballgame\addons\mpf-gmc" "C:\repos\mpf-gmc\addons\mpf-gmc"`
   - To update, run `git fetch && git pull` in the clone. If you copied instead of symlinking, copy again.

Either way, the file `<project>/addons/mpf-gmc/plugin.cfg` should exist when the plugin is in the right place. The quickstart gives a fourth source: the GitHub *Releases* page (Assets → Source code).

**After updating GMC**, expect errors the first time you open the project. Use *Project → Reload Current Project* to clear them. If things are still badly broken ("In Case of Catastrophe"), remove the project from Godot's Project List, delete the project's `.godot/` folder, and re-import `project.godot`.

### 2.6 Activate the plugin (required for every install method)

Expect transient errors during this step.

1. *Project → Project Settings → Plugins*: tick **Godot MC**. If it isn't listed, `addons/` is in the wrong place.
2. *Globals* tab (called "Autoload" before Godot 4.3) → *Autoload*. Click the **folder icon** (not "+ Add" yet), select `addons/mpf-gmc/mpf_gmc.gd`, set **Node Name = `MPF`** (all caps), then press **+ Add**.
3. Save and restart Godot.

> **Warning:** the autoload *must* be named `MPF`. GMC components refer to each other by that name.
>
> **[DOC NOTE]** Typos in the docs: the warning box in `gmc/installation.md` says `mpf_gmc.md`, and `start/quickstart.md` says `addons/mpf-gmc/mpd_gmc.gd`. The correct file is `mpf_gmc.gd`.

There is a Windows setup video at `https://www.youtube.com/embed/IO3U1SMZ5-A`. It covers creating the project, installing GMC, three audio buses, Git LFS for large media, and `gmc.cfg`.

The docs also warn: **keep your project in a git repository.** GMC is new, and developers can reproduce your issues much faster if they can clone your game.

---

## 3. Initial project setup (`gmc/setup.md`)

### 3.1 Main scene = the Window

Every slide, widget and UI file in Godot is a **scene**. The **main scene** of a GMC project is the **Window** scene, which:

- initialises GMC,
- opens the connection to MPF, and
- mounts the "display" scenes, one for each screen.

For a single screen, use the bundled scene. Go to *Project Settings → Application → Run → Main Scene* and choose `res://addons/mpf-gmc/slides/window.tscn`. The quickstart also says that when you first press Play, Godot prompts for a main scene and you pick the same file. For multiple screens you build your own Window scene (§6).

### 3.2 Window size

*Project Settings → Display → Window*: set Viewport Width and Height to your display resolution. With several displays, use the bounding box that contains all of them. This also draws layout guides in the scene editor. Untick **Resizable** now. Fullscreen, borderless and position come later.

### 3.3 Audio buses and `gmc.cfg`

Godot mixes audio through **buses** that feed the *Master* bus. MPF 0.5x called these "tracks". In the **Audio** tab at the bottom of the editor, use *Add Bus* to create `music`, `effects` and `voice` (the names are case sensitive).

Godot buses can't carry custom properties, so GMC reads their playback behaviour from **`gmc.cfg`** (INI format) in the project root:

```ini
[sound_system]
music={"type": "solo"}
effects={"type": "simultaneous", "simultaneous_sounds": 3, "default": true}
voice={"type": "sequential"}
```

### 3.4 First slide and first run

1. Create a `slides/` folder, either in the project root or in `modes/attract/slides/`.
2. Right-click the folder → *Create New → Scene*. Name it `attract` and set **Root Type** to the custom class **`MPFSlide`**.
3. Add a `ColorRect` sized to the window, then a `Label` with the text "Welcome to GMC!", centred, with a font size of about 100 px under *Theme Overrides*.
4. In `modes/attract/config/attract.yaml`:

```yaml
slide_player:
    mode_attract_started: attract
```

5. Press **Play** in the editor (top right). A window appears showing the MPF logo, which is GMC's default startup slide ("Waiting for MPF…").
6. In a terminal with your virtual environment activated, in the machine folder, run `mpf -xt` (`-x` = virtual hardware, `-t` = no text UI). Godot should show "Connected to MPF", then your attract slide.

**Headless or command-line Godot:** run the godot executable from inside the project folder. Add `-f` for fullscreen. On macOS, symlink the binary first: `sudo ln -s /Applications/Godot.app/Contents/MacOS/Godot /usr/local/bin/godot`.

> **Tip:** if you forget to make `MPFSlide` the root, add an `MPFSlide` node, right-click it and choose *Make Scene Root*.

---

## 4. How MPF and GMC connect (BCP, ports, launching)

### 4.1 Connection behaviour

From `gmc/guides/launching-the-mpf-game-with-godot.md`:

- You can start MPF and Godot in either order. "Both programs will wait for each other."
- **Do not pass `-b`** to `mpf`. That flag tells MPF there is no media controller (no BCP).
- While MPF waits, it logs `Connecting BCP to local_display at localhost:5050 ....`

Default ports (`running/ports.md`, `config/bcp.md`):

- **5050**: the media controller listens here and MPF connects to it (`bcp: connections: local_display`, `host: localhost`, `port: 5050`, `required: true`, `exit_on_close: true`).
- **5051**: MPF's own BCP server (`servers: url_style`, `127.0.0.1:5051`). MPF Monitor and the service CLI use it. The MC does not.

```yaml
bcp:
  connections:
    local_display:
      host: localhost
      port: 5050
      type: mpf.core.bcp.bcp_socket_client.BCPClientSocket
      required: true
      exit_on_close: true
  servers:
    url_style:
      ip: 127.0.0.1
      port: 5051
      type: mpf.core.bcp.bcp_socket_client.BCPClientSocket
  debug: false
```

> **[DOC NOTE]** `running/ports.md` explains port changes only for legacy MPF-MC (`mpf-mc: bcp_port:`), and `mpf-mc` is on the 0.80 list of deprecated sections. **There is no documented way to change GMC's listening port.** GMC's own BCP server can be overridden (`GMCServer` script override, §8.4), and its logging is `logging_server`. Running MPF and the MC on different computers (`mc/mpf_and_mc_different_machines.md`) is only documented for MPF-MC. It sets `host:` in the `bcp:` connection and warns that BCP has no security.

### 4.2 Three ways to run

1. **Editor plus manual MPF.** Press Play in Godot and run `mpf <folder> -v -t` (or `mpf -xt`) in the terminal.
2. **Godot launches MPF.** Use the **"MPF" tab** next to "Scene" in the editor. The settings are saved to the `[mpf]` section of `gmc.cfg`, and pressing Play then runs:

   ```shell
   <executable_path> <executable_args> <machine_path> <mpf_args>
   ```

   | key | meaning |
   |---|---|
   | `spawn_mpf` (bool, default false) | The "Launch MPF with GMC" checkbox |
   | `executable_path` | Python interpreter, the venv `mpf` executable/symlink, or a precompiled MPF binary |
   | `executable_args` | For example `-m mpf` when the executable is Python. MPF arguments do *not* go here |
   | `machine_path` | MPF machine folder (the one containing `config/` and `modes/`). Defaults to the GMC project folder |
   | `mpf_args` | For example `-x`, `-vV`, `-P` (production), `-l <file>`, `-a` |
   | `virtual` (bool) | Appends `-x` |
   | `verbose` (bool) | Appends `-vV` |

   Caution: the editor misbehaves if you edit `gmc.cfg` by hand while also using the MPF tab. Save, then reload the editor.
3. **Exported executable (production).** The editor is heavy and needs someone to press Play, so for the real machine you export:
   - Install the export templates once (*Editor → Manage Export Templates*, download from a mirror or install from a file).
   - *Project → Export*, choose the target OS, **embed the PCK**, and pick the architecture. The docs' example is **arm64 for a Raspberry Pi**.
   - You can develop on a PC, export for the machine's architecture, and copy the binary across. Use `chmod +x` on Linux.
   - The executable contains all assets, including sounds, so nothing needs copying into MPF folders.
   - **You must re-export after every change to the Godot project.**

> **[DOC NOTE]** There is no documented autostart or boot-script recipe for launching the exported GMC plus MPF on a cabinet. The docs only say that you "want to start things automatically in a scripted mode". MPF's `-P` production flag is mentioned only in passing.

---

## 5. `gmc.cfg`: the GMC configuration file

`gmc.cfg` lives in the project root, uses INI format, and has these sections: `[filter]`, `[gmc]`, `[keyboard]`, `[mpf]` and `[sound_system]`.

- **Godot strips comments** from this file whenever it rewrites it.
- **Local overrides:** a `gmc.local.cfg` in the Godot *User Data* folder overrides any key. Commit `gmc.cfg` to git and keep per-machine settings, such as the MPF executable path and log levels, in the local file.

### 5.1 `[gmc]`

- `content_root`: a folder prepended to the root content folders. For example, with `content_root` set to `content`, GMC looks in `/content/slides` and `/content/sounds`. Mode subfolders are still scanned.
- `exit_on_esc`: when true, the GMC process quits when Escape is pressed.
- Log levels:
  - Keys: `logging_global`, `logging_game`, `logging_server` (BCP traffic), `logging_process` (the MPF subprocess), `logging_media`, `logging_sound_player`.
  - Values: 0 = use global, 1 = VERBOSE, 10 = DEBUG, 20 = INFO, 25 = LOG, 30 = WARNING, 40 = ERROR.
  - Editor/debug builds default to INFO. Production builds default to LOG.
- Script overrides such as `GMCServer="custom_code/my_custom_bcp.gd"` (§8.4).

```ini
[gmc]
logging_global=20
logging_sound_player=10
```

### 5.2 `[keyboard]`: simulating switches and events

This replaces MPF-MC's `keyboard:` YAML section, which is deprecated.

```ini
[keyboard]
1=["switch", "s_switch_1"]              ; hold key = switch active, release = inactive
enter=["switch", "s_start_button"]
6=["switch", "s_drop_1", "active"]      ; explicit action: press only, release does nothing
shift+6=["switch", "s_drop_1", "inactive"]
x=["switch", "s_trough_6", "toggle"]
m=["event", "start_mode_multiball"]     ; post an MPF event
d=["event", "drop_bank_left_complete"]
```

Keys can be single characters, named keys (`enter`, `tab`), or modifier combinations (`shift+2`, `ctrl+enter`). The inline `;` comments above are only illustrative: Godot removes comments from `gmc.cfg`.

### 5.3 `[sound_system]`

Each key is the name of a Godot bus, and the value is a dictionary:

- `type`: `"solo"`, `"sequential"` or `"simultaneous"`.
  - `solo`: one sound at a time. A new sound **replaces** the current one.
  - `sequential`: one at a time. New sounds **queue**.
  - `simultaneous`: many at once.
- `simultaneous_sounds`: the maximum number of concurrent sounds on a simultaneous bus. Extra sounds are **dropped, not queued**.
- `default`: exactly one bus can be the default. It is used when `sound_player` doesn't set `bus:`.
- `duck_default`: exactly one bus can be the default ducking target.

### 5.4 `[filter]` and `[mpf]`

`[filter]` is covered in §6.4 and `[mpf]` in §4.2.

---

## 6. Displays, windows, DMD looks and segment displays

### 6.1 Node model

- **`MPFWindow`** is the root of the main (entry) scene. It takes no parameters. Its size comes from *Project Settings → Display → Window → Size*. It must have at least one `MPFDisplay` child.
- **`MPFDisplay`** is one per logical screen. You can also split one monitor into several displays. Every `MPFDisplay` must be a **first-level child** of the `MPFWindow`. **The node name is what MPF's `target:` refers to.** Its parameters are:
  - `is_default`: the display used when `slide_player` has no `target:`. Only one display may be default, otherwise GMC throws an error. If none is set, the first child is the default.
  - `initial_slide`: the scene shown while GMC waits for MPF. The default is `addons/mpf-gmc/slides/startup.tscn`.
  - `allow_empty` (default false): when false, the display keeps showing the last slide after it is removed, until a new slide arrives. This avoids a blank flash between one mode stopping and the next starting. Set it to true to allow an empty screen.
- Each display has its own **slide stack** and a special **`_overlay`** slide that always sits on top (§7.3).

### 6.2 Multiple monitors (`gmc/guides/spanning-multiple-monitors.md`, `gmc/reference/mpf-window.md`)

This setup is marked **work in progress**, and the developers want feedback from people who use it.

1. *Project Settings → Display → Window* with Advanced Settings on:
   - Viewport W/H = the bounding box of all screens
   - Initial Position Type = **Absolute**
   - Resizable off, Borderless on
   - Window Width/Height Override = the viewport size
   - **Embed Subwindows off**

   The docs' example is two 1600×900 screens, giving 3200×900.
2. Create your own Window scene with an `MPFWindow` root in `/slides/`. The easiest way is to *Duplicate* `res://addons/mpf-gmc/slides/window.tscn` **and move the copy out of `addons/`**. Right-click it and choose **Set as Main Scene**.
3. Add a main `MPFDisplay` (for example `primary`) with `is_default` on and the size of the main monitor.
4. For each further monitor:
   - Add a plain Godot **`Window`** node (not `MPFWindow`) under the root.
   - Set Initial Position = Absolute, Position = offset from the top-left of the main monitor, and Size = the screen size.
   - Under Flags, turn on Transient, Unresizable and Borderless.
   - Put an `MPFDisplay` child inside it (for example `mini-display`).
5. Target displays from MPF:

```yaml
slide_player:
    mode_attract_started:
        attract_main_slide:
            target: primary
        attract_mini_slide:
            target: mini-display
```

Expect to adjust display positions when you move from your development PC to the real cabinet hardware.

### 6.3 Pinning the window to a monitor

In the simpler `MPFWindow` approach, you lock the top-left of the window to the primary monitor with Initial Position Type = Absolute. You "may also need to adjust the window position and fullscreen modes, depending on your operating system."

### 6.4 DMD looks: window filters (`gmc/guides/window-filters.md`)

Filters are shaders applied to the whole GMC window, and so to every display. They are set in `gmc.cfg`:

```ini
[filter]
filter="virtual_dmd"
columns=120
rows=45
hardness=5
spacing=2
```

| filter | effect | params |
|---|---|---|
| `virtual_dmd` | Pixelates to a grid and overlays round dots (the colour-DMD look). "Most popular" | `color=Color(r,g,b,a)` (all four floats required, default white), `columns` (128), `rows` (32), `hardness` (5.0; 0 = all black, try ≥1.5), `spacing` (2.0; 1.0 = no dots) |
| `dmd_dots` | Dots without pixelating the content, for pixel-art content | same as `virtual_dmd` |
| `pixelate` | Blocks only, no dots. "Useful … if you are rendering to an *actual* DMD" | `columns`, `rows` |
| custom | Any **CanvasItem** shader. Create a `Shader` resource and set `filter="res://shaders/my_awesome_shader.gdshader"`. Other keys in the section set the shader's `uniform` parameters | shader-defined |

The docs say these shaders were tested but "not tried out in the wild".

> **[DOC NOTE]** DMD and segment gaps:
> - **Physical DMDs with GMC are not documented.** Under MPF-MC, the MC rendered a `dmd` display and sent frames to a physical mono or RGB DMD (`mc/displays/dmd.md`, `rgb_dmd.md`, config `dmds:`/`rgb_dmds:`). No GMC page explains how GMC feeds a physical DMD. The only hint is the "rendering to an actual DMD" line under `pixelate`. If your machine uses a real DMD, confirm support with the MPF community before relying on it.
> - **Segment displays:** `segment_displays:` and `segment_display_player:` are MPF core configs and are not in the deprecated list, so physical segment displays driven by MPF should still work. The legacy MC's **Segment Display Emulator widget** (virtual segments on an LCD) has **no GMC equivalent documented**. With GMC you would build one in Godot, for example with an `MPFVariable` and a segment font; this is not covered in the docs.
> - `window-filters.md` puts its first INI example in a ```` ```yaml ```` fence. It is INI.

---

## 7. Slides

### 7.1 Files and naming (`gmc/slides.md`)

- Every slide is a `.tscn` scene with an **`MPFSlide`** root node.
- GMC scans `/slides/**` in the project root (or under `content_root`) and every `/modes/<mode>/slides/**` folder, and maps each slide **by filename**. **Slide names must be unique across all folders, and cannot contain spaces.**

```yaml
# /slides/base.tscn and /modes/skillshot/slides/skillshot_overlay.tscn
slide_player:
    mode_base_started: base
    skillshot_hit:
        skillshot_overlay:
            action: remove
```

- If you copy one of GMC's built-in slides (bonus, high score, tilt, …) into your own slides folder **under the same name, your copy overrides the default**.

### 7.2 Slide stack, priority and context

- **Stack.** Each display keeps a stack sorted by priority, highest on top. It is re-sorted whenever a slide is added or removed. Transparency works: a partly transparent overlay slide shows the slides beneath it, and those keep updating.
- **Priority.** A slide gets the priority of the mode that played it. `priority:` in `slide_player` **adds to** the mode priority. `slide_player` in the machine-wide config uses priority 0, and shows use the show's priority.
- **Context.** Each slide records the context that created it, normally the mode name. When a mode stops, MPF posts a *clear* for that context, and **slides, widgets, sounds, lights and shows started by that mode are removed**. To make a slide outlive its mode, give it another context. The docs call this `custom_context` in `slides.md` and `context:` in `mpf-slide.md`. If the context is not a mode name, you must remove the slide yourself.
- **Key.** This defaults to the file name. Set a `key` to run several instances of the same slide and address each one for update or remove.

> **[DOC NOTE]** `custom_context` versus `context` naming is inconsistent between pages.

### 7.3 Widgets and the `_overlay` slide

**`MPFWidget`** scenes are "mini-slides" with an `MPFWidget` root. They are played onto an existing slide with `widget_player:`. They have the same `context`, `key` and `priority` parameters, the same lifecycle animations, and the same `action: method` hook as slides. **If the slide a widget is on is removed, the widget goes with it**, whatever its context.

- `widget_player` **without** `slide:` puts the widget on whichever slide is currently active. It dies with that slide.
- `slide: _overlay` (note the leading underscore) puts it on the display's permanent overlay, above all slides. It is unaffected by slides coming and going.

`widget_player` actions in 0.80 (`config/widget_player.md`):

| action | meaning |
|---|---|
| `play` | default; add the widget |
| `remove` | take it off |
| `update` | tells Godot to redraw the widget on the next idle frame |
| `preload` | load it in advance so the first play is fast |
| `animation` | play an AnimationPlayer animation; `from_start` restarts it |
| `method` | call a custom method |

The legacy actions `add`, `remove` and `update` are MPF-MC only.

### 7.4 `slide_player:` reference (GMC version, `gmc/reference/slide_player.md`)

Actions:

| action | behaviour |
|---|---|
| `play` (default) | Add the slide to the stack. It is visible only if it has the highest priority |
| `remove` | Remove it. The next-highest slide shows |
| `method` | Call the GDScript method named in `method:` on the slide instance (§7.6) |
| `queue` | Add to the end of the slide queue. Queued slides play one after another. **Give queued slides an `expire:`, or the queue never advances** |
| `queue_first` | Add to the front of the queue; plays after the queued slide currently showing |
| `queue_immediate` | Replace the currently playing queued slide at once; the rest of the queue follows |
| `update` | Re-evaluate the slide's variables and conditionals with new tokens and event args. Used in the bonus guide |

Other settings:

- `expire:` is a time string. The timer starts when the slide enters the stack, even if it isn't on top.
- `max_queue_time:` discards a queued slide that hasn't played within this time.
- `priority:` is added to the mode priority.
- `target:` is the display name (an `MPFDisplay` node name). The docs say it "will be renamed to `display:` in the future".
- `tokens:` is a dictionary passed to the slide. It is used by `MPFVariable`/`MPFConditional` (Event Arg type) and by custom methods.
- **Order matters.** Several slides under one event are processed in the order listed. To swap slides with the same key in one event, list `action: remove` before `action: play`.

> **[DOC NOTE]** Problems on the slide_player reference page:
> - Its "Valid in" table says mode config files: **NO**. That is wrong: every GMC guide uses `slide_player:` in mode configs (for example `attract.yaml`, `bonus.yaml`, `tilt.yaml`).
> - `action:` is described as "play, remove" in one line, but more actions are listed below it, and **`update` is used in the bonus guide without appearing in the action list**.
> - Its `expire:` example is legacy MPF-MC YAML (`slides:` with `widgets:` and `transition_out: wipe`).
> - The `remove` example uses `transition: fade`, and `target:` mentions "slide_frame" widgets. These are also legacy.
>
> **In GMC, transitions are built with AnimationPlayer lifecycle animations (§7.5), not with `transition:` YAML.**

### 7.5 Lifecycle animations (`gmc/guides/animating-slides-widgets.md`)

States:

- **CREATED**: instantiated and added.
- **ACTIVE**: on top of the stack.
- **INACTIVE**: was on top, now covered by another slide.
- **REMOVED**: taken off.

To animate them:

1. Add an `AnimationPlayer` to the scene.
2. Assign it to the root `MPFSlide`/`MPFWidget` **Animation Player** property.
3. Create animations named exactly `created`, `active`, `inactive` or `removed`.

For example, a `created` animation that keyframes *Visibility → Modulate* alpha from 0 to 1 gives a fade-in.

Rules:

- A slide that is created *and* goes straight to the top plays `active`, which takes precedence over `created`.
- **Removal onto a higher-priority slide:** the new slide's `created`/`active` animation plays while the old slide waits underneath, and the old slide's `removed` animation **does not play**.
- **Removal onto a lower-priority slide:** the new slide's `created`/`active` animation **does not play**. It sits underneath until the old one leaves.
- GMC posts **`slide_<name>_created`, `slide_<name>_active`, `slide_<name>_inactive`, `slide_<name>_removed`** back to MPF. `inactive` is new in 0.80. `_removed` is posted *after* the removal animation, so you can chain "play the next slide" from it. Widgets post `widget_<name>_active` and `widget_<name>_removed`.

> **[DOC NOTE]** `mpf-slide.md` and `mpf-widget.md` list only created, active and removed. The guide adds `inactive`.

### 7.6 Custom slide methods (GDScript)

Detach the `MPFSlide` script from the root node, attach a new script, and make it **`extends MPFSlide`** (or `extends MPFWidget`):

```gdscript
## multiball_base_slide.gd
extends MPFSlide

func explode(_settings, _kwargs):
    $AnimationPlayer.play("explode")
```

```yaml
slide_player:
    jackpot_counter_complete:
        multiball_base_slide:
            action: method
            method: explode
```

Custom methods **must take two parameters**. Prefix them with `_` if unused, which silences Godot's warning.

- `settings` (Dictionary): the `slide_player` entry, for example `priority` and `action`, plus `settings.tokens`.
- `kwargs` (Dictionary): the triggering event's arguments. For example, `player_score` provides `kwargs.value`, `prev_value`, `change` and `player_num`. Check the MPF log for the args each event carries.

### 7.7 Displaying MPF data: GMC node classes

All of these are custom nodes that you add in the Scene panel.

**`MPFVariable`** (extends `Label`) displays and auto-updates game data:

- `variable_type`: `Current Player` (default), `Player 1`…`Player 4`, `Machine`, or `Event Arg`. Player-specific variables support a **maximum of 4 players**.
- `variable_name`: for example `score`, `ball`, `number` (the player number), or a machine variable.
- `comma_separate` and `min_digits` (left-pads with zeros).
- `template_string`: `%`-style, e.g. `"Ball %s"`, `"%sX"`.
- `format_string`: `{}`-style. It combines the slide_player settings, tokens and event args into one dictionary and ignores `variable_name`. If both format and template strings are set, `format_string` wins.
- `min_players` / `max_players`: show only in games with at least or at most N players.
- `initialize_empty`: start blank. Does not affect player or machine variables, or args from the triggering event.
- `update_event`: an event that refreshes the variable. Event Arg type only.

**`MPFConditional`** shows or hides itself when `variable_name` compared with `condition_value` (`condition_type`, default Equals) is true.

- It also has `min_players`/`max_players` and `variable_type`.
- **It does not subscribe to changes.** It evaluates only when first rendered and on `action: update`.

**`MPFConditionalChildren`** shows the direct child **whose node name equals the variable's value**. `condition_value` is ignored. A child named `__default__` (two underscores each side) is the fallback.

- Example: variable `ball` with children "1", "2", "3".
- Example: Event Arg `hero` with `tokens: {hero: batman}` shows the child named "batman".

**`MPFChildPool`** picks one child to show each time the pool enters the tree.

- `playback_method`: `Random`, `Random No Repeat`, `Random Force All` (every child once before any repeats), or `Sequential`.
- `track_per_player`, `reset_on_game_end`.
- `child_method`: called on the chosen child, e.g. `"play"` for video.
- `call_child_method_in_editor`.
- Children need `show()` and `hide()`. `Node2D`, `Node3D` and `Control` already have them.

**`MPFCarousel`** works with MPF's Carousel mode. Its child node names must match `selectable_items`, and `carousel_name` must be the MPF **mode name**. One carousel per mode. When several carousel modes run, the highest-priority one wins.

```yaml
# modes/attract/config/attract.yaml
mode:
    start_events: mode_attract_started
    stop_events: mode_attract_will_stop
    game_mode: false
    code: mpf.modes.carousel.code.carousel.Carousel
mode_settings:
    selectable_items:
        - gameover
        - title
        - last_game_scores
    next_item_events: s_flipper_right_active
    previous_item_events: s_flipper_left_active
```

**`MPFTextInput`** is an on-screen keyboard used for high score entry.

- It is driven by `text_input` events with `action: left|right|select`. The high score mode already binds these to switches tagged `left_flipper`, `right_flipper` and `start`.
- Choosing END posts `text_input_<input_name>_complete` with a `text` argument. `input_name` defaults to `high_score`.
- Other parameters: `allowed_characters` (default A–Z), `allow_space`, `max_length` (10), `preview_character`, `display_node` (a Label or RichTextLabel), `grid_width`, `character_appearance`/`special_appearance` (`LabelSettings`), `highlight_color`.

```yaml
event_player:
  s_my_additional_left_control_active:
    text_input:
      action: left
  s_another_select_button_active:
    text_input:
      action: select
```

**`MPFVideoPlayer`** (extends Godot `VideoStreamPlayer`):

- `hide_behavior`: `Restart` (default), `Pause`, or `Continue`. It fires when the node or an ancestor changes visibility.
- `end_behavior`: `Nothing`, `Remove Slide/Widget`, or `Post Event`. `Post Event` posts `video_finished` to MPF.
- `events_when_stopped`: custom events posted when the video ends.
- Inherited properties: `stream`, `autoplay`, `loop`, `expand` (scale to the node; otherwise native size), `volume_db`, `audio_track`, and **`bus`** (the video's audio goes through a Godot bus, so ducking applies).

**`MPFEventHandler`** subscribes to any MPF event over BCP and calls `call_method(event_args_dict)` either on its **Parent** or on each direct **Child** (`handler_direction`). The node must be a direct parent or child of the nodes it calls.

**`MPFLogger`**: add it to a scene and list GMC nodes in its `loggers` array to get per-node logs at `log_level`. Rename your nodes, because the logs are prefixed with node names.

> **[DOC NOTE]** In `mpf-video-player.md`, `end_behavior` refers to an `events_when_finished` option, but the parameter is documented as `events_when_stopped`. `MPFCarousel` still says the carousel mode posts "an event with the name of the carousel mode and the item". In 0.80 that is the consolidated `carousel_item_highlighted{carousel, item, direction}` event (see §9).

### 7.8 Worked example: base slide with score, ball and player (`gmc/guides/base-slide-with-score.md`)

1. In `base.yaml`, add `slide_player: {mode_base_started: base}`. Create `modes/base/slides/base.tscn` with an `MPFSlide` root.
2. Add a `Sprite2D` background (Texture → Quick Load).
3. Add an `MPFVariable` named "score": Current Player / `score`, Comma Separate, Min Digits 2, a large font with an outline.
4. Add an `MPFVariable` named "ball": Template String `"Ball %s"`. Style it with a reusable **Theme** resource (for example `body_md.tres`) with a Label font and a 40 px size.
5. Add an `MPFVariable` named "player": variable `number`, template `"Player %s  "`, **Min Players 2**, so it appears only in multiplayer games.
6. Put player and ball inside an `HBoxContainer` so the ball label slides right when the player label appears.

### 7.9 Worked examples: bonus and tilt

**Bonus** (`gmc/guides/bonus_mode.md`, `gmc/reference/bonus.md`). GMC ships a default `bonus.tscn`; the guide rebuilds it.

```yaml
# modes/bonus/config/bonus.yaml
mode_settings:
    bonus_entries:
        - entry: loops_completed
          text: "Ranger Loops"
          player_score_entry: ranger_loops_count
          score: 10_000
slide_player:
    mode_bonus_started: bonus
    bonus_start:
        bonus:
            action: update
            tokens:
                entry: initial
    bonus_entry:
        bonus:
            action: update
```

The slide is an `MPFConditionalChildren` (Event Arg `entry`) with these children:

- `initial`, showing "End of Ball %s".
- `__default__`, holding Event Arg `text` and `score` with Initialize Empty on.
- `subtotal`, `multiplier` (template `%sX`) and `total`.

The bonus entry options are:

- `entry`: required. `subtotal`, `multiplier` and `total` are reserved names.
- `score`: required; can be dynamic.
- `player_score_entry`: the score is multiplied by this player variable.
- `reset_player_score_entry`.
- `skip_if_zero`: default true.
- `skip_if_negative`.
- `text`.

If the multiplier is 1, the subtotal and multiplier entries are skipped.

**Tilt** (`gmc/guides/tilt_mode.md`). 0.80 has **one** `tilt.tscn` slide, which receives a `text` token: "WARNING" on the first warning, "DANGER" on the second, "TILT" on tilt.

- *Approach 1:* provide your own `tilt.tscn` with an Event Arg `MPFVariable` named `text`.
- *Approach 2:* override the mode's slide_player with `_overwrite: True` and write your own entries. The docs suggest `tilt_clear` as the removal event.
- With `warnings_to_tilt` greater than 3, add entries for the higher warnings yourself, e.g. `tilt_warning_3: {tilt: {expire: 1s, tokens: {text: UH OH}}}`.

---

## 8. Sound, events, and custom code

### 8.1 Where sounds live and how they're named (`gmc/sound.md`)

Sounds (files and resources) go in `/sounds/**` or `/modes/<mode>/sounds/**`, and are referenced by **filename without extension**:

```yaml
sound_player:
    mode_frenzy_started:
        frenzy_background_music:
            bus: music
            fade_in: 500ms
            fade_out: 1s
    drop_targets_complete: small_explosion_one
```

Anything derived from Godot `AudioStream` in a sounds folder can be played:

- `AudioStreamRandomizer`: a pool with weights, random or sequential or no-repeat order, and random pitch and volume.
- `AudioStreamPolyphonic`: stacks several playbacks in one stream.
- `AudioStreamSynchronized`: layered or synchronized stems.
- `AudioStreamPlaylist`: playlists with shuffle, crossfade and loop.

(The docs describe the last two as "coming in Godot 4.3", which is now out of date.)

### 8.2 `MPFSoundAsset` resource

Create it with right-click → *Create New → Resource → MPFSoundAsset* in a sounds folder, and save it under the name you'll use in `sound_player`. The values you set are defaults, and `sound_player` can override them.

- `stream`: WAV, OGG, or any AudioStream resource. You can create one in place, e.g. a *New AudioStreamRandomizer*, so pool and settings live in one file.
- `bus`
- `fade_in` / `fade_out`: **float seconds**.
- `start_at`: seconds.
- `max_queue_time`: seconds. −1 queues forever, 0 means don't queue. Applies to sequential buses only.

GMC maps sound files first, then resources, so **a resource with the same name as a file overrides that file**. That lets you add settings to `explosion.wav` by creating `explosion.tres`.

```yaml
sound_player:
    villain_advance: villain_advance_callouts   # an MPFSoundAsset wrapping a randomizer
```

> **[DOC NOTE]** The class is called `MPFSoundAsset` in the nav and title but `MPFSound` in the body of `mpf-sound-asset.md` and `sound.md`, and the `get_sound_instance` return type is `MPFSound`. The body also calls it a "Node class", but it is used as a **Resource**. Its fade times are floats in seconds, while `sound_player` takes MPF time strings.

### 8.3 `sound_player:` in 0.80 (`config/sound_player.md`)

- **`bus:`** is new and replaces the deprecated `track:`. Migrate `track: music` to `bus: music`.
- Actions:
  - `play`
  - `stop`
  - `stop_looping`
  - `load` / `unload`
  - **`replace`** (new): stops everything on the bus and plays this sound.
- Other options that still apply: `block`, `delay`, `events_when_played`, `events_when_stopped`, `events_when_looping`, `fade_in`, `fade_out`, `key`, `loops`, `max_queue_time`, `pan`, `priority`, `start_at`, `volume`.
- **Not implemented in 0.80:** `about_to_finish_time`, `events_when_about_to_finish` and `mode_end_action`. The docs also say you should add explicit stop entries yourself if you need a sound to stop when a mode or show ends.

> **[DOC NOTE]** Ducking in GMC is barely documented. The only mention is `duck_default` in `[sound_system]` ("sound playback trigger using ducking settings"). No page shows the ducking keys for `sound_player` or `MPFSoundAsset` under GMC. The legacy docs (`mc/sound/ducking.md`, `config/sound_ducking.md`) describe `target`, `delay`, `attack`, … for MPF-MC tracks.
>
> Using legacy `sound_pools:` in MPF YAML is an **unsupported hack**. You `pip install mpf-mc` into the venv so that it injects the config spec, and the pools must use the actual file names. Use `AudioStreamRandomizer` instead.

### 8.4 Events between MPF and Godot (`gmc/guides/mpf-events-and-godot.md`, `gmc/reference/mpf-gmc.md`)

**MPF to Godot:**

1. `MPFVariable` picks up player and machine variables automatically.
2. For anything else, post a custom event, for example with dynamic args:

```yaml
event_player:
  send_gas_to_godot:
    set_gas_value:
      gas_value:
        value: current_player.gas
        type: int
```

3. Catch it with an `MPFEventHandler` (Event Name `set_gas_value`, Direction Parent/Children, Call Method `update_gas_progress_bar`):

```gdscript
func update_gas_progress_bar(event_args):
  if (event_args["gas_value"] > 10):
    self.value = 10
  else:
    self.value = event_args["gas_value"]
```

4. Or subscribe in code with `MPF.server.add_event_handler("event", callable)`, which receives a `payload` dictionary. Unsubscribe with `remove_event_handler`.
5. Or post an event named **`options`** from MPF and connect to the `MPF.server.options(payload)` signal. It is a generic channel that needs no handler setup.

**Godot to MPF** (this is rare, because the game logic belongs in MPF):

```gdscript
func send_lap_time_to_mpf():
    var kwargs = {"lap_time_str": my_lap_time.text, "lap_time_delta": lap_time_delta}
    MPF.server.send_event_with_args("lap_time_from_godot", kwargs)
```

`MPF.server.send_event("name")` sends an event with no arguments. The key `name` is reserved in BCP and is ignored inside args. `MPF.server.set_machine_var(name, value)` writes a machine variable.

> **[DOC NOTE]** The guide's no-args example calls `send_event_with_args("lap_time_from_godot")` with no dictionary; `send_event` is correct there. The text also misspells it as `send_events_with_args`.

**The `MPF` singleton (autoload)** has these submodules:

- **`MPF.game`**
  - Signals: `credits`, `game_started`, `player_added(total_players)`, `player_update(variable_name, value)`, `volume(bus, value, change)`.
  - Properties: `active_modes`, `audits`, `machine_vars`, `player` (current player dict), `players`, `settings`.
- **`MPF.media`**
  - Catalogs the media on startup and handles `slides_play`, `widgets_play` and `sounds_play`.
  - Methods: `get_slide_instance(name, preload_only)`, `get_widget_instance(…)`, `get_sound_instance(…)`.
- **`MPF.server`** (BCP)
  - Signals: `bonus(payload)`, `clear(mode_name)`, `carousel_item_highlighted(payload)`, `options(payload)`, `player_var(value, prev_value, change, player_num)`, `service(payload)`.
  - Methods: those above.
- **`MPF.util`**: `comma_sep(int)`, `find_parent_slide(node)`, `pluralize("Shot%s Remaining", n)`.
- **`MPF.log`**: logging.

**Advanced overrides** (`gmc/guides/advanced-custom-code.md`): you can extend the core classes **`GMCUtil`, `GMCLogger`, `GMCGame`, `GMCServer`, `GMCMedia`**. They load in that order, and earlier ones can't reference later ones. Register the override in `gmc.cfg`:

```gdscript
# /custom_code/my_custom_bcp.gd
extends GMCServer

func on_connect():               # virtual hook
    print("Connection established, running custom startup flow.")

func set_machine_var(name: String, value) -> void:
    super()
    print("Machine var %s updated to value: %s" % [name, value])
```

```ini
[gmc]
GMCServer="custom_code/my_custom_bcp.gd"
```

GMC also has a built-in **Service** slide. It posts `service_trigger` events and uses the `MPF.server.service` signal.

---

## 9. Migrating a 0.57 MPF-MC project (`install/0.80.md`)

**Deprecated config sections: remove them** (from 0.80.0.dev12):

`animations`, `assets:bitmap_fonts`, `assets:images`, `assets:sounds`, `assets:videos`, `bitmap_fonts`, `effects`, `image_pools`, `image_templates`, `images`, `images_frame_skips`, `keyboard`, `kivy_config`, `mc_custom_code`, `mpf-mc`, `playlist_player`, `playlist_player_actions`, `playlists`, `slides`, `sound_loop_player`, `sound_loop_player_actions`, `sound_loop_sets`, `sound_system`, `sounds`, `track_player`, `transitions`, `widget_styles`, `widgets`.

`slide_player`, `widget_player` and `sound_player` **stay** and are "very similar" (`config/index.md`). They now reference Godot scene and resource names.

**Changes to the built-in modes:**

- **Bonus:** `event:` becomes `entry:`. The event `completed_ramps{hits=3, score=3000}` becomes `bonus_entry{entry="completed_ramps", hits=3, score=3000}`. There is a new `text:` option.
- **Carousel:** `missionselect_garrus_highlighted{direction}` becomes `carousel_item_highlighted{carousel="missionselect", item="garrus", direction}`, and likewise `carousel_item_selected`.
- **High score:**
  - The flipper and start controls are built in through the switch tags `start`, `left_flipper` and `right_flipper`.
  - `high_score_award_display`, `(award)_award_display` and `(category)_award_display` are collapsed into one `high_score_award_display` event with the args `award`, `category_name`, `player_num`, `player_name` and `value`.
  - Default Godot slides are provided. Copying them under the same name overrides them.
- **Tilt:** `tilt_warning_1`, `tilt_warning_2` and `tilt` slides become a single `tilt` slide with a `text` token.

---

## 10. The show system

Shows are run by the **MPF game engine**, not the MC. They are sequences of timed **steps**, and each step can do anything a **config player** can do. When a step contains media actions (slides, widgets, sounds), MPF sends those actions over BCP to the media controller as the step plays. With GMC, a show's `slides:` and `sounds:` entries name GMC `.tscn` slides and sound files or resources. Light shows, on the other hand, are pure MPF and don't touch the MC. (There have been no separate "light shows" and "display shows" since MPF 0.30.)

### 10.1 Show format (`shows/format.md`)

```yaml
##! show: my_show
- time: 0
  lights:
    led1: red
- time: +1
  lights:
    led1: off
- time: +1
```

- Each step is a YAML list item (`- ` with a space). The keys in a step must be aligned.
- **`time:`** is when the step *starts*.
  - The first step is `time: 0`.
  - A plain number means seconds. Time strings such as `1s`, `1000ms` and `1.0` also work.
  - **Absolute** times (`4`) are measured from the start of the show. **Relative** times (`+1`, `+250ms`) are measured from the previous step. You can mix them.
  - If a step has no `time:`, `+1` is assumed.
- **`duration:`** is how long the step lasts, as an alternative to `time:`. You can mix the two, but not a `time:` *after* a step that has `duration`.
- If you use `time:`, give the **last step a `duration`**, because otherwise its length is unclear.
- **`duration: -1`** holds the step forever, until the show or its mode stops. Use it for "flash then stay on".
- **Precision** is limited to MPF's tick rate: 60 fps, about 16 ms.
- **Speed** is a playback multiplier set when the show is played. It can change while the show runs.

> **[DOC NOTE] Important syntax change.** A warning box in `format.md` says that from MPF 0.57 (including 0.80), "you need to add quotes around time values which are not zero, e.g. `time: "1"`, `time: "+1"` but `time: 0`". Almost every example in `docs/shows` (including this page) still shows **unquoted** `+1` and `+250ms`, and the warning says those examples use the pre-0.57 syntax. **Quote non-zero `time:` values** (`time: "+1"`) to be safe.

```yaml
#show_version=5
# "flash then hold" – with 0.57+ quoting
- time: 0
  lights:
    led1: red
- time: "+250ms"
  lights:
    led1: off
- time: "+250ms"
  lights:
    led1: red
  duration: -1
```

### 10.2 What can go in a step (`shows/content.md`)

Anything that has a config player. Each `xxx_player:` config section corresponds to an `xxx:` key in a show step:

| config section | show-step key |
|---|---|
| `light_player:` | `lights:` |
| `show_player:` | `shows:` (shows in shows) |
| `sound_player:` | `sounds:` |
| `slide_player:` | `slides:` |
| `widget_player:` | `widgets:` |
| `event_player:` | `events:` |
| `random_event_player:` | `random_events:` |
| coils/drivers, flashers, GI, BCP commands, segment displays, variable player, … | per the config player |

The per-player docs are in `docs/config_players/`.

Example with multiple lights and a token:

```yaml
shows:
  rainbow:
    - lights:
        (leds): red
    - lights:
        (leds): orange
    - lights:
        (leds): purple
      duration: 3s
show_player:
  play_rainbow_show_on_targets:
    rainbow:
      show_tokens:
        leds: l_target1, l_target2
```

### 10.3 Where shows are defined

**Standalone files** (`shows/file_shows.md`):

- One show per `.yaml` file in a `shows/` folder at the **machine root or mode root**. It does *not* go inside `config/`. Subfolders are allowed.
- The filename is the show name.
- **The first line must be `#show_version=5`.**
- Names must be unique machine-wide. Use lowercase with underscores. **No dashes**, because names must be valid Python identifiers.

**Inline in configs** (`shows/config_shows.md`), using a `shows:` section in a machine or mode config:

```yaml
shows:
  flash_red:
    - time: 0
      lights:
        led1: red
    - time: +1
      lights:
        led1: off
    - time: +1
```

Once loaded, file shows and config shows behave the same. File shows can be loaded and unloaded dynamically. MPF keeps one **global** list of shows, so a duplicate name silently overwrites the earlier show.

The docs also say you can't reference slides or widgets that were *defined inside* show sections from outside the show. That is a legacy MPF-MC concern, since GMC slides are scenes anyway.

### 10.4 Playing shows: `show_player:` (`config/show_player.md`, `config_players/show_player.md`)

```yaml
show_player:
  some_event: your_show_name          # express form
  some_other_event:
    another_show:
      speed: 2
      sync_ms: 500
      loops: 0
```

`action:` values:

| action | behaviour |
|---|---|
| `play` | default |
| `stop` | stops the show and **undoes** what it did |
| `pause` / `resume` | hold at the current step / continue |
| `advance` / `step_back` | move one step manually |
| `update` | not implemented |
| `queue` | listed but undocumented |

Settings:

- **`loops`**
  - The default is **`-1`, meaning shows loop forever unless told otherwise**. `loops: 0` plays once. `loops: 1` plays twice.
  - A show with a single step always has `loops` forced to 0.
- `speed`: a multiplier; can be dynamic.
- `priority`: added to the mode priority. It affects everything the show does, including lights, slides and sounds.
- `key`: identifies an instance. The key defaults to the show name, so a second play of the same show without a key replaces the first. Give distinct keys to run several instances at once and stop them separately. Keys are local to one show_player, so different modes don't collide.
- `show_tokens` (§10.5).
- `sync_ms` (§10.7).
- `manual_advance: true`: steps advance only on `action: advance`.
- `start_step`: can be dynamic.
- `start_running: false`: plays the first step and then pauses; use `resume` to continue.
- `block_queue: true`: for **queue events** such as `mode_x_stopping`, the event is held until the show finishes. **Never combine this with `loops: -1` or a final `duration: -1`, or the machine hangs.**
- Events:
  - `events_when_played`, `_stopped`, `_completed`: the show ended naturally, including after N loops, but not on each loop.
  - `_looped`, `_paused`, `_resumed`, `_advanced`, `_stepped_back`.
  - `_updated`: a placeholder.

```yaml
show_player:
  start_my_show1:
    your_show_name:
      action: play
      key: show1
      show_tokens:
        leds: my_led1
  start_my_show2:
    your_show_name:
      action: play
      key: show2
      show_tokens:
        leds: my_led2
  stop_my_show1:
    show1: stop
```

**Shows started from a mode's `show_player` stop automatically when that mode stops.**

> **Gotcha** (`shows/playing.md`): always stop shows you no longer need. The docs give an example with segment displays. A show that writes the player number to a segment display is overwritten by another show. When a new game starts, the old show "resumes", but because the value hasn't changed, MPF thinks the display is still correct and doesn't redraw it.

**Shows in shows** (`shows/shows_in_shows.md`): a parent show can act as a playlist or controller for other shows.

```yaml
- duration: 3s
  shows:
    attract_show_collectlights:
      loops: 1
      speed: 10
      show_tokens:
        color: blue
- duration: 3s
  shows:
    attract_show_collectlights:
      loops: 1
      speed: 10
      show_tokens:
        color: red
```

### 10.5 Show tokens (`shows/tokens.md`)

Any word in **parentheses** in a show is a placeholder. When the show starts, MPF does a find-and-replace using `show_tokens`. Token names are arbitrary (`(corndog)` works), and one show can have several tokens.

```yaml
##! show: color_cycle
- time: 0
  lights:
    (led): (color1)
- time: 1
  lights:
    (led): (color2)
```

```yaml
show_player:
  some_event:
    color_cycle:
      loops: -1
      show_tokens:
        led: led_02              # a device name…
        color1: green
        color2: blue
  another_event:
    color_cycle:
      show_tokens:
        led: tag1                # …or a TAG (expands to every light with that tag)
        color1: ("green" if (current_player.score) > 1000 else "yellow")   # conditional
        color2: blue
```

Dynamic token values:

- **Event args:** use the bare argument name, e.g. `txt: (number)` on `player_turn_started`.
- **Player variables:** `(current_player.ball)`, or a specific player with `players[<0-based index>].<var>`.
- **Game, machine and settings:** `game.<var>`, `machine.<var>`, `settings.<var>`. See `config/instructions/dynamic_values.md`.
- **Python formatting:** e.g. `txt: "{(current_player.ball):d}"`.

**Shots and shot profiles** pass tokens to the show for each state. Profile-level `show_tokens`, such as a colour, combine with shot-level ones, such as the LED:

```yaml
shot_profiles:
  different_blink_color_profile:
    states:
      - name: purple
        show: flash_color
        show_tokens:
          color: ff00ff
      - name: green
        show: flash_color
        show_tokens:
          color: 00ff00
shots:
  my_first_shot:
    profile: different_blink_color_profile
    switch: my_switch_1
    show_tokens:
      led: my_led_1
```

GMC side: tokens given to `slide_player`/`widget_player` (the `tokens:` key, which is different from `show_tokens:`) show up in `settings.tokens` for custom methods, and are read by Event Arg `MPFVariable`/`MPFConditional*` nodes.

### 10.6 Built-in default shows (`shows/default_shows.md`)

Show names are lowercase.

| show | behaviour | light tokens | other tokens |
|---|---|---|---|
| `on` | light at its `default_on_color`, duration −1 (until stopped) | `light`/`lights`/`led`/`leds` | — |
| `off` | force off, duration −1 (useful to beat a lower-priority show) | same | — |
| `flash` | 1 s on / 1 s off in `default_on_color`; set the rate with `speed` | same | — |
| `led_color` | like `on` but with a colour | same | `color` (required) |
| `bl_color` | "blinkenlights" colour, like `led_color` | also `blinkenlight`/`blinkenlights` | `color` |
| `flash_color` | flash with a colour | `light`/`lights`/`led`/`leds` | `color` (e.g. `00FF00-f1s` = green with a 1 s fade) |

```yaml
show_player:
  my_triggering_event:
    flash:
      speed: 10            # 100 ms on / 100 ms off
      show_tokens:
        lights: my_flashing_light, my_other_flashing_light
```

For simple flashing, `flasher_player` is suggested as a more concise option. For complex light shows there is the **MPF Showcreator** tool (`tools/showcreator.md`).

### 10.7 Synchronising shows: `sync_ms` (`shows/sync_ms.md`)

With `sync_ms: N`, a show waits to start until the next exact multiple of N ms from zero, so flashing lights started at different times stay in phase.

- **Set N to one full cycle of the show.** 250 on + 250 off gives `sync_ms: 500`. 200/200 gives 400. 400/250 gives 650.
- Using half a cycle keeps shows in sync but can leave them offset from each other.
- The delay is at most one cycle, which nobody notices in practice.

---

## 11. Development workflow (as the docs describe it)

1. Put the machine folder in **git**. The docs strongly recommend this, and the setup video covers **Git LFS** for media.
2. Organise content:
   - MPF configs go in `config/` and `modes/<m>/config/`.
   - GMC slides go in `slides/` or `modes/<m>/slides/`, sounds in `sounds/` or `modes/<m>/sounds/`. If the Godot project is in a `gmc/` subfolder, keep all GMC content under it. You can also use `content_root`.
   - Shows go in `shows/` or `modes/<m>/shows/`.
3. Set up the `[keyboard]` section of `gmc.cfg` to simulate switches and fire test events.
4. Develop with the editor's Play button and let the MPF tab launch `mpf` in **virtual** mode (`-x`). Alternatively, run `mpf -xt` or `mpf -v -t` yourself.
5. Debug:
   - Raise `logging_*` levels in `gmc.cfg`, or better, in `gmc.local.cfg`.
   - Add `MPFLogger` nodes to see individual slide logs.
   - Look in the MPF log to find event arguments.
   - MPF Monitor connects on port 5051.
6. Use the eye icon in the Scene panel to preview `MPFConditionalChildren`, `MPFChildPool` and `MPFCarousel` children in the editor.
7. For production, **export** a Godot binary for the target OS and CPU (for example arm64 on a Pi), embed the PCK, re-export after every change, copy it to the machine, and run it alongside `mpf` (with `-P` for production).
8. After updating GMC, run *Project → Reload Current Project*. If the project is corrupted, delete `.godot/` and re-import.

> **[DOC NOTE]** "Interactive MC (iMC)" and `mpf both` / `mpf mc` are MPF-MC tools and don't apply to GMC. `running/commands/index.md` notes that "MPF MC is the media controller used before MPF 0.80".

---

## 12. Legacy MPF-MC (0.57): brief summary

This section is here to help you read older forum posts, tutorials (`docs/tutorials/legacy_mc/`) and example configs. Nearly every page under `docs/mc` carries the banner "MPF-MC is being deprecated … for MPF 0.57 and prior".

- **Architecture** (`mc/displays/architecture.md`):
  - One Kivy **window** (`window:` config) shows a **source display**.
  - **Displays** (`displays:`, each with `width`/`height`/`default`) are *logical* canvases with slide stacks. Their origin is bottom-left.
  - **Slides** are defined in YAML `slides:` and made up of **widgets** (text, image, video, shapes, `display` widgets for picture-in-picture, segment display emulator, text input, …).
  - Widget layout used x/y/anchors and percentages, plus `widget_styles`, YAML `animations` with easing, and slide **transitions** (push, move_in, fade, wipe, …).
- **Text placeholders:** `(player|score)`, `(player1|score)`, `(machine|credit_string)`, `(event_arg)`.
- **DMDs:**
  - A `dmd` display (e.g. 128×32) is rendered by the MC and sent to a physical mono or RGB DMD (`dmds:`/`rgb_dmds:`).
  - The docs warn that the DMD rendering cost applies even in virtual mode.
  - The "dot look" on LCDs came from a `color_dmd` effect on a `display` widget.
- **Multiple screens:** Kivy supported only one window, so the workaround was one giant borderless window (`kivy_config:`) containing `display` widgets.
- **Sound:**
  - A custom SDL2/SDL_Mixer/GStreamer engine with up to 8 **tracks**, of type `standard`, `sound_loop` or `playlist`.
  - `sounds:` assets had friendly names; there were `sound_pools:`, ducking (`target`, `delay`, `attack`, …), `sound_loop_sets`, `playlists` and `track_player`.
  - Supported formats: 16-bit WAV, OGG, FLAC.
- **Ports and BCP:** unchanged. MPF-MC listened on 5050 (`mpf-mc: bcp_port`), and MPF also served 5051. Other MCs (the Unity BCP Server) can be plugged in, and several MCs can be connected through multiple `bcp: connections`.

### Concepts that carry over unchanged to GMC

BCP and the separate processes; ports 5050/5051; `slide_player`/`widget_player`/`sound_player` driven by events; slide priority equal to mode priority plus an offset; per-display slide stacks; context and key based auto-removal when a mode ends; `expire:`; `target:` for picking a display; `slide_<name>_active`/`_removed` events; shows sending media steps to the MC.

### Legacy MPF-MC (0.57) vs GMC (0.80) mapping

| Concern | Legacy MPF-MC 0.57 | GMC 0.80 |
|---|---|---|
| Install | `pip install mpf-mc` (Kivy, SDL, gstreamer) | Godot 4.5+/4.6 plus the `mpf-gmc` addon (AssetLib, ZIP or git) with the `MPF` autoload |
| Launch | `mpf both`, `mpf mc` | Godot editor Play (optionally auto-spawning MPF through the MPF tab / `[mpf]`), or an exported Godot binary |
| Window | `window:` YAML, `kivy_config:` | Project Settings → Display → Window, plus an `MPFWindow` root scene |
| Displays | `displays:` YAML (logical, `default: true`) | `MPFDisplay` child nodes (the node name is the target, `is_default`) |
| Multiple monitors | One huge Kivy window plus `display` widgets | Extra Godot `Window` nodes, each holding an `MPFDisplay` |
| Slides | `slides:` YAML lists of widgets | `.tscn` scenes with an `MPFSlide` root, found by filename in `slides/` folders |
| Widgets (named, reusable) | `widgets:` YAML, `widget_styles:` | `.tscn` scenes with an `MPFWidget` root; Godot Themes for styling |
| Text with variables | Text widget `(player|score)`, `number_grouping`, `min_digits` | `MPFVariable` node (`variable_type`/`variable_name`, `comma_separate`, `min_digits`, template/format strings) |
| Conditional content | `slide_player` / conditional events | `MPFConditional`, `MPFConditionalChildren`, `MPFChildPool` |
| Animation / transitions | `animations:`, easing, `transitions:` / `transition_out:` | Godot `AnimationPlayer` with `created`/`active`/`inactive`/`removed` animations; `action: method` for anything else |
| Custom code | `mc_custom_code:` (Python) | GDScript on slides/widgets (`extends MPFSlide`), `MPFEventHandler`, `MPF` singleton, `GMC*` script overrides |
| Images / video | `images:`, `videos:`, `image_pools:`, video widget | Godot `Sprite2D`/`TextureRect`…, `MPFVideoPlayer` |
| Sound assets | `sounds:` YAML (friendly name to file), `assets:sounds` | Filename in `sounds/` folders, or an `MPFSoundAsset` `.tres` |
| Audio channels | `sound_system:` **tracks** (`track:`) | Godot **buses** plus `[sound_system]` in `gmc.cfg` (`bus:`) |
| Sound pools | `sound_pools:` | `AudioStreamRandomizer` (optionally wrapped in `MPFSoundAsset`) |
| Music playlists / loops | `playlists:`, `playlist_player`, `sound_loop_sets`, `sound_loop_player` | Godot `AudioStreamPlaylist` / `AudioStreamSynchronized` (only mentioned in the docs; no MPF player equivalent documented) |
| Ducking | Per-sound `ducking:` settings | Only `duck_default` is documented (**gap**) |
| Keyboard simulation | `keyboard:` YAML | `[keyboard]` in `gmc.cfg` |
| DMD "dot look" | `color_dmd`/`dmd` effects on display widgets | `[filter]` shaders `virtual_dmd`, `dmd_dots`, `pixelate`, or a custom shader |
| Physical DMD output | MC renders the `dmd` display and sends it to `dmds:`/`rgb_dmds:` | **Not documented for GMC** |
| Virtual segment display | `segment_display_emulator` widget | **Not documented for GMC** (build in Godot) |
| High score entry | `text_input` widget | `MPFTextInput` node plus `text_input{action}` events |
| Carousel events | `<mode>_<item>_highlighted` | `carousel_item_highlighted{carousel,item,direction}` + `MPFCarousel` |
| Bonus events | per-entry events, `event:` | `bonus_entry{entry,…}`, `entry:` + `text:` |
| Tilt slides | `tilt_warning_1`, `tilt_warning_2`, `tilt` | single `tilt` slide with a `text` token |
| Logging | MC log | `[gmc] logging_*`, `MPFLogger` node, `gmc.local.cfg` |
| Shows | MPF core; media steps sent via BCP | **Unchanged**: MPF core; `slides:`/`sounds:` steps now name Godot assets |

---

## 13. Consolidated gotchas and doc issues

1. The autoload **must be named `MPF`**. The correct file is `mpf_gmc.gd`; the docs misspell it as `mpf_gmc.md` and `mpd_gmc.gd` in two places.
2. If the Godot project is in a `gmc/` subfolder, Godot cannot see `modes/*/slides` or `modes/*/sounds`. Keep all GMC content inside the Godot project.
3. Slide, widget and sound names are global and taken from filenames. **They must be unique, and slide names cannot contain spaces.** A resource overrides a sound file with the same name, and your own slide overrides a GMC default slide with the same name.
4. Don't run `mpf` with `-b` (no BCP) when you use GMC.
5. There is **no documented way to change GMC's BCP port** (5050); the `mpf-mc: bcp_port` method is legacy and deprecated.
6. The editor MPF tab and hand edits to `gmc.cfg` conflict. Godot also strips comments from `gmc.cfg`.
7. Exported builds must be **re-exported after every Godot change**. Export templates must be installed, and you must pick the right architecture.
8. `simultaneous` buses **drop** sounds over the limit. `solo` buses **replace** the current sound. `max_queue_time` only matters on `sequential` buses.
9. `about_to_finish_time`, `events_when_about_to_finish` and `mode_end_action` are **not implemented** in 0.80 `sound_player`.
10. `MPFConditional` does not react to variable changes. Use `action: update`, or `MPFVariable`'s `update_event`.
11. `MPFVariable` supports only **4 players** for player-specific variables.
12. Queued slides need `expire:`, or the queue stalls. `allow_empty: false` (the default) keeps the last slide on screen after it is removed.
13. The slide_player reference page has errors:
    - It says `slide_player` is not valid in mode configs, which is wrong.
    - It leaves `update` out of the action list.
    - Its examples use legacy `slides:` and `transition` syntax.
    - It mentions `slide_frame`.
14. Naming mismatches: `MPFSoundAsset` vs `MPFSound`, `events_when_stopped` vs `events_when_finished` (video), and `custom_context` vs `context`.
15. Physical DMDs, virtual segment-display emulation, GMC ducking, and cabinet autostart of the exported binary are **undocumented** for GMC.
16. Show times: **quote non-zero `time:` values** (`time: "+1"`) in 0.57+ and 0.80, even though most examples don't.
17. `show_player` defaults to **`loops: -1`**, so shows loop forever. Use `loops: 0` for one-shot shows. Single-step shows never loop.
18. Never use `block_queue: true` with an infinite show, or the machine hangs.
19. Show names are global. A duplicate name, whether from a file or a config, silently overwrites the earlier one. File names cannot contain dashes. Show files need `#show_version=5` on the first line.
20. Stop shows you no longer need. A stale segment-display show may not redraw when it resumes.
21. Several version statements are stale: GMC 0.1.6, `0.80.0.dev14`, "upcoming 0.80", and "coming in Godot 4.3".

---

## Source documents used

All paths are relative to `mpf-docs-dev/docs/` unless noted.

**GMC:**
- `gmc/index.md`, `gmc/installation.md`, `gmc/setup.md`, `gmc/keyboard.md`, `gmc/slides.md`, `gmc/sound.md`
- `gmc/reference/`: `index.md`, `gmc-cfg.md`, `slide_player.md`, `mpf-slide.md`, `mpf-widget.md`, `mpf-sound-asset.md`, `mpf-video-player.md`, `mpf-variable.md`, `mpf-display.md`, `mpf-window.md`, `mpf-gmc.md`, `mpf-carousel.md`, `mpf-child-pool.md`, `mpf-conditional.md`, `mpf-conditional-children.md`, `mpf-event-handler.md`, `mpf-logger.md`, `mpf-text-input.md`, `bonus.md`
- `gmc/guides/`: `base-slide-with-score.md`, `mpf-events-and-godot.md`, `animating-slides-widgets.md`, `random-sound-pools.md`, `random-slide-children.md`, `bonus_mode.md`, `tilt_mode.md`, `spanning-multiple-monitors.md`, `window-filters.md`, `launching-the-mpf-game-with-godot.md`, `advanced-custom-code.md`

**Context:**
- `start/media_controller.md`, `start/quickstart.md`, `install/0.80.md`, `install/index.md`, `versions/release_notes.md`, `faq/installation.md`, `about/index.md`
- `../includes/latest_versions.md`
- `running/ports.md`, `running/commands/index.md`
- `config/bcp.md`, `config/slide_player.md`, `config/widget_player.md`, `config/sound_player.md`, `config/sound_system.md`, `config/index.md`, `config/switches.md`
- `events/slides/index.md`, `events/slide_slide_inactive.md`, `events/widget_name_active.md`, `events/service_trigger.md`, `events/index.md`
- `game_logic/tilt/overwrite_tilt_slides.md`

**Shows:**
- `shows/index.md`, `shows/format.md`, `shows/content.md`, `shows/file_shows.md`, `shows/config_shows.md`, `shows/shows_in_shows.md`, `shows/tokens.md`, `shows/default_shows.md`, `shows/playing.md`, `shows/sync_ms.md`
- `config/show_player.md`, `config/shows.md`
- `config_players/show_player.md`, `config_players/light_player.md`, `config_players/slide_player.md`, `config_players/sound_player.md`

**Legacy MC** (skimmed):
- Core pages read in full: `mc/index.md`, `mc/mpfmc.md`, `mc/creating_your_own.md`, `mc/mpf_and_mc_different_machines.md`, `mc/multiple_mcs.md`, `mc/unity_bcp_server.md`, `mc/displays/index.md`, `types.md`, `alpha_numeric.md`, `multiple_screens.md`
- Pages read in part: `mc/displays/architecture.md`, `dmd.md`, `rgb_dmd.md`, `lcd.md`, `adding_dot_look_to_lcd.md`, `mc/slides/index.md`, `showing_slides.md`, `transitions.md`, `mc/sound/index.md`, `tracks.md`, `variations.md`, `ducking.md`, `mc/widgets/index.md`, `types.md`, `text/text_dynamic.md`, `segment_display_emulator/index.md`
