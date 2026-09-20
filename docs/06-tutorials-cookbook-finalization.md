# 06 – Tutorial, Cookbook, Game Design, Flowcharts, Finalization & Community

*Practical digest of the MPF documentation (dev branch = MPF 0.80, GMC era) for someone building a real machine. Sources: `docs/tutorials`, `docs/cookbook`, `docs/examples`, `docs/game_design`, `docs/flowcharts`, `docs/finalization`, `docs/machine_management`, `docs/community`, `docs/showcase`, `docs/welcome_wall.md`.*

---

## 0. First, the big caveat: the tutorial is written for the legacy MC (0.56/0.57)

- The only tutorial in the docs lives under `docs/tutorials/legacy_mc/`. The site home page (`docs/index.md`) lists it as **"Tutorial for MPF 0.56/0.57"** and says **"Tutorial for MPF 0.80 coming soon!"**. No GMC version of the tutorial exists yet.
- Every tutorial page includes a banner (`includes/tutorial.md`): *"It's been awhile since this tutorial has been updated. If you find anything that is no longer relevant, please let us know, or better yet, edit or update it yourself!"*
- `docs/versions/index.md` says: **0.57 is the current long-term-support (LTS) version; 0.80 is the "next-generation" version.**
- What still carries over to 0.80: everything that is **MPF game-engine YAML**: switches, coils, flippers, playfields, ball devices, autofire coils, modes, `variable_player`, shots, shot profiles, shot groups, show files with `lights:`, `show_player`, logic blocks.
- What does **not** carry over directly: everything that is **MPF-MC (Kivy) display config**. That covers `displays:`, `slides:` with `widgets:`, `widget_player:`, `widgets:`, the `keyboard:` section, `mpf mc`, and slide-based show steps. With GMC, slides are Godot scenes (`.tscn`, root type `MPFSlide`). `slide_player` still names the slide, which GMC loads from the mode's `slides` folder. Score text comes from `MPFVariable` nodes, and keyboard mapping lives in `gmc.cfg` `[keyboard]`. The step-by-step notes below mark each MC-specific item as **[legacy MC]**.

---

## 1. Condensed walkthrough of the official tutorial (20 steps)

The tutorial builds a *Demolition Man*-style config step by step. It works on the virtual platform with no hardware. Each step has a matching folder in the `mpf-examples` repo (`tutorial/step_N`). That repo is itself flagged as out of date (see §5).

### Step 1 – Install MPF
- **What you do:** install MPF on your everyday computer (Windows/Mac/Linux), not the final SBC. Check with `mpf --version`.
- **Key point:** you do not need a physical machine. The "virtual" platform is not an emulator, but you can toggle switches and watch lights, including against a playfield image in MPF Monitor.
- **Outdated bits:** it says to install "both MPF and the MPF-MC". Under 0.80 you would install GMC/Godot instead (see the GMC install docs). The page is also missing its version number ("This tutorial is written for MPF versions ." — the variable is empty). It shows `MPF v0.51.3` as example output and points to the Google Group banner for the latest version.

### Step 2 – Create your machine folder
- **What you build:** a machine folder (it's a "machine", not a "game", because in MPF a "game" is a game in progress). Put it under Git; the docs strongly recommend GitHub, SourceTree or GitHub Desktop, or a local git-gui repo.
- **Key config:** `config/config.yaml` containing just:
  ```yaml
  #config_version=6
  ```
  Config version 6 is used by MPF 0.57 and newer. There must be no spaces around `=`.
- **Run:** `mpf -b` from the machine folder root. `-b` means "no BCP/media controller". Stop with Ctrl+C.
- **What you learn:** the text UI (active modes, switches, ball counts, player, CPU/mem). Common errors:
  - "Config file version mismatch" means the `#config_version` line is missing.
  - "Could not find machine folder: 'None'" means you're in the wrong directory, e.g. inside `config/`.
  - Hanging at `Connecting BCP to 'local_display' at localhost:5050...` means you forgot `-b`.

### Step 3 – Get flipping
- **Key config:**
  ```yaml
  switches:
    s_left_flipper:
      number: 0
      tags: left_flipper      # enables the flipper_cancel combo event
    s_right_flipper:
      number: 1
      tags: right_flipper
  coils:
    c_flipper_left_main:
      number: 0
    c_flipper_left_hold:
      number: 1
      allow_enable: true      # safety: coils can't be held on without this
    c_flipper_right_main:
      number: 2
    c_flipper_right_hold:
      number: 3
      allow_enable: true
  playfields:
    playfield:
      tags: default
      default_source_device: None   # use None in steps before 8
  flippers:
    left_flipper:
      main_coil: c_flipper_left_main
      hold_coil: c_flipper_left_hold
      activation_switch: s_left_flipper
      enable_events: machine_reset_phase_3   # TEMPORARY – removed in step 10
    right_flipper:
      main_coil: c_flipper_right_main
      hold_coil: c_flipper_right_hold
      activation_switch: s_right_flipper
      enable_events: machine_reset_phase_3
  ```
- **Hardware section examples:** these are illustrations only; the docs say not to copy them.
  - `hardware: {platform: fast, driverboards: fast}` + `fast: ports: ...`
  - `p_roc` + `wpc`
  - `p3_roc` + `pdb`
  - `virtual_pinball` for VPX
  - The full sample is a FAST WPC config in a real *Demolition Man*, with numbers like `SF4` and `FLLM`.
- **What you learn:**
  - Naming convention: `s_` for switches, `c_` for coils, `l_` for lights (helps autocomplete).
  - Names are case-sensitive (since 0.50).
  - YAML rules: spaces, not tabs; consistent indentation; no space before a colon; a space after it.
  - `-t` shows the log instead of the text UI.
  - `-x` selects the virtual platform and `-X` the smart virtual platform. If you use either, your physical hardware won't respond.
  - **Real-machine gotcha:** close the coin door. On Williams/Stern machines the coin door switch cuts coil power.
  - The docs recommend the MPF language server for VS Code/PyCharm.

### Step 4 – Adjust flipper power
- **Key config:** `default_pulse_ms:` on the **coil** (not the flipper). The default is 10 ms, which is deliberately weak. Try 20 and tune from there. Real machines vary: 12–14 ms on some, 60–70 ms on others, and over 100 ms on a 1974 Big Shot.
- For **single-wound** coils, tune `default_hold_power:` (0.0–1.0). Start at 0.125–0.25 and raise it until the hold doesn't break when a ball hits.
- **What you learn:** the same tuning applies to every coil. Revisit it once ramps are installed.

### Step 5 – Add a display **[legacy MC]**
- **Legacy content:** `mpf mc` opens an 800×600 window, configured like this:
  ```yaml
  displays:
    window:
      width: 800
      height: 600
  slides:
    welcome_slide:
      widgets:
        - type: text
          text: PINBALL!
          font_size: 50
          color: red
        - type: rectangle
          width: 240
          height: 60
  slide_player:
    init_done: welcome_slide
    mode_attract_started: attract_started
  ```
  The MC concepts are PowerPoint-like: slides, widgets and transitions. Widget order sets the stacking; the first widget in the list is on top. `mpf both` launches the engine and the MC together.
- **Under 0.80/GMC:** the engine-side idea (a `slide_player` keyed on events such as `mode_attract_started`) remains. The slide content, however, is built in the Godot editor. You can run MPF and Godot separately (either order; each waits for the other). Alternatively, configure the Godot project to launch MPF itself, or use `mpf both -g <godot project> -G <godot exe>`.
- **Gotcha:** don't use `mpf both` with a Godot project that is set to auto-start MPF. You'll get two MPF instances (`running/commands/both.md`).

### Step 6 – Keyboard control **[legacy MC]**
- **Legacy content:**
  ```yaml
  keyboard:
    z:
      switch: s_left_flipper
    '?':
      switch: s_right_flipper
  ```
  The MC window must have focus. Watch out for Num Lock on Windows 10. Modifier keys make distinct mappings.
- **Key lesson:** keyboard keys **do not fire physical flippers**. Flippers, slings and pops run as **hardware rules** on the controller, so only the real switch triggers them.
- **Under GMC:** the mapping moves to `gmc.cfg`, for example `[keyboard]` with `z=["switch", "s_left_flipper"]`, `x=["switch","s_trough_6","toggle"]`, `m=["event","start_mode_multiball"]`. Alternatively, use MPF Monitor and click switches.

### Step 7 – Add your trough
- Pick your trough type from the Troughs/Ball Drains docs; there are many variants and each has its own guide. Add `debug: true` to the device and run with `-v` to see verbose ball-device logs.
  ```yaml
  ball_devices:
    bd_trough:
      ball_switches: s_trough1, s_trough2, s_trough3, s_trough4, s_trough5, s_trough6, s_trough_jam
      eject_coil: c_trough_eject
      tags: trough, home, drain
      jam_switch: s_trough_jam
      eject_coil_jam_pulse: 15ms
      debug: true
  ```
- Don't test yet; it needs the plunger lane.

### Step 8 – Add your plunger lane
- The plunger lane is a ball device, even if it's just a divot with no switch. MPF's ball tracking must know where every ball is.
- Add `eject_targets: bd_plunger` to the trough. On two-stage drains, such as System 11, add it to the device that feeds the plunger. Set the playfield's `default_source_device: bd_plunger`.
- Test with `mpf -vbt`. Common count problems:
  - Missing entries in `ball_switches`.
  - Opto trough switches missing `type: NC`.
  - A single ball too light to hold the switch; add more balls.

### Step 9 – Add the start button
- ```yaml
  switches:
    s_start:
      number: 11
      tags: start               # MPF uses the tag, not the name
    s_right_inlane:
      number: 12
      tags: playfield_active    # confirms balls reached the playfield
  ```
- Tag every switch a loose ball can hit with `playfield_active`. **Do not** tag ball-device switches or autofire switches (slings, pops); MPF handles those.

### Step 10 – Run a real game
- Temporary `[legacy MC]` slide: `ball_started:` with a `PLAYER (number) BALL (ball)` text widget.
- Seed virtual balls and add keyboard toggles:
  ```yaml
  virtual_platform_start_active_switches:
    - s_trough1
    - s_trough2
    - s_trough3
  ```
- **Remove `enable_events: machine_reset_phase_3` from the flippers.** Otherwise they won't re-enable for ball 2, because that setting overrides the default enable-on-ball-start.
- Defaults: 4 players max and 3 balls per game (change these in `game:`).
- Behaviour to expect:
  - A coil-fired plunger holding a ball at boot fires immediately, because the plunger isn't tagged `home`.
  - Balls entering unconfigured devices get stuck.
- The smart virtual platform (`-X`) simulates the trough-to-plunger ejects.
- **Contradiction:** the "with physical hardware" instructions say to run *without* `-x/-X`, but the example command shown is `mpf both -X`. The troubleshooting line `mpf both -t -v -V -X` is also virtual-only. On real hardware, drop the `-X`.

### Step 11 – Add the rest of your coils & switches
- Work down the operator's manual. At this stage, tags only matter for `playfield_active`. Don't tag ball-device, drop-target, kickback, trough or shooter-lane switches with it. Don't bother with pulse times yet.

### Step 12 – Add the rest of your ball devices
- Minimum settings per device: `ball_switches`, `eject_coil` and `eject_timeouts`.
- `eject_timeouts` is critical. Set it to the longest time a failed eject could take to fall back in. Guidance: 500–750 ms for simple kickouts, 2–3 s for VUKs.
- Non-`home` devices auto-eject at boot. Tune pulse strength in `coils:`, not in the device.
  ```yaml
  ball_devices:
    bd_plunger:
      ball_switches: s_plunger_lane
      eject_timeouts: 3s
      eject_coil: c_plunger_eject
      player_controlled_eject_event: sw_launch
    bd_lower_vuk:
      ball_switches: s_bottom_popper
      eject_coil: c_bottom_popper
      eject_timeouts: 2s
    bd_elevator:
      ball_switches: s_elevator_hold
      mechanical_eject: true
      eject_timeouts: 500ms
  ```

### Step 13 – Add autofire devices (slings, pops)
- ```yaml
  autofire_coils:
    left_slingshot:
      coil: c_left_slingshot
      switch: s_left_slingshot
  ```
- Autofires are active only while a ball is in play. They switch off automatically in attract mode and on tilt.

### Step 14 – Add your first mode ("base")
- **Folder layout:** `modes/base/config/base.yaml`. Put the file in `config/`, not in `modes/base/`. Don't name the mode "game", which is a built-in mode.
  ```yaml
  #config_version=5        # (sic – see gotchas; use 6)
  mode:
    start_events: ball_starting
    priority: 100
  ```
- Register the mode in the machine config: `modes:` followed by `- base`. The dash matters, because it lets lists merge across config files.
- Keep your priorities between 100 and 1,000,000. Built-in modes: attract is 10 and game is 20.
- **Why the slide plays on `mode_base_started` instead of `ball_starting`:** a mode's config is only active while the mode runs. The event that starts the mode has already happened by the time the mode is listening.
- **[legacy MC]:** the score slide uses `text: (score)`, `PLAYER (number)` and `BALL (ball)` with `number_grouping` and `min_digits`. The GMC equivalent is the guide `gmc/guides/base-slide-with-score.md`: `slide_player: mode_base_started: base` plus a `base.tscn` using `MPFVariable` nodes (Variable Type "Current Player", name `score`, Comma Separate, Min Digits 2).

### Step 15 – Add scoring
- `variable_player:` adds to or subtracts from any player variable, not just score. Switches post `(name)_active` and `(name)_inactive` events.
  ```yaml
  # machine config
  player_vars:
    potato:
      initial_value: 0
  # modes/base/config/base.yaml
  variable_player:
    s_right_inlane_active:
      score: 100
    s_left_flipper_active:
      score: 1000
      potato: 1
    s_right_flipper_active:
      potato: -2
  ```
- Player variables are per-player and are destroyed at game end. Quote any text containing a colon (`'POTATO VALUE: (potato)'`). Higher-priority modes can block lower-mode scoring.

### Step 16 – Attract mode display show
- Extend the built-in attract mode with `modes/attract/config/attract.yaml` and `modes/attract/shows/attract_display_loop.yaml`. Show files start with `#show_version=5`.
  ```yaml
  show_player:
    mode_attract_started: attract_display_loop
  ```
- Shows started from a mode stop automatically when that mode stops. The show steps use `slides:` with widgets and transitions **[legacy MC]**.
- `(machine|player1_score)` shows the last game's score through a machine variable.
- Show steps use `duration:`; playback speed can be scaled at play time.

### Step 17 – Add lights / LEDs and an attract light show
- Show `lights:` values:
  - `0` / `ff` for matrix lamps.
  - Colour names or hex for RGB, e.g. `red`, `ff6600`, `lime`.
- Only lights that change need listing in each step.
- To run two shows on one event, either add a `.1` suffix to the event key or nest the shows:
  ```yaml
  show_player:
    mode_attract_started:
      attract_display_loop:
        speed: 1
      attract_light_show:
        speed: 4
  ```
- A YAML key can't take both a scalar value and child settings. That is why `mode_attract_started.1: attract_light_show` with `speed: 4` indented under it fails.
- Build complex attract shows from many small shows at different speeds, like *Demolition Man*'s.

### Step 18 – Add your first shot
- ```yaml
  shots:
    my_first_shot:
      switch: s_right_inlane
      show_tokens:
        light: l_light_quick_freeze   # or led: ...
      profile: my_first_profile
  shot_profiles:
    my_first_profile:
      states:
        - name: unlit
          show: off
        - name: flashing
          show: flash
        - name: lit
          show: on
      loop: true
  ```
- Each hit posts three events: `my_first_shot_hit`, `my_first_shot_my_first_profile_hit` and `my_first_shot_my_first_profile_<state>_hit`. Score by state using those events.
- Shot state is per player, and shots only work during a game. Before 0.30 shots could be machine-wide; now they belong in modes (use base for always-on).
- A higher-priority mode (`mode2`, priority 200) can apply its own profile to the same shot. `block: true` suppresses the lower profile, and its events.
- **[legacy MC]:** the mode2 banner uses `widgets:` and `widget_player:`.
- **The page is unfinished:** it ends with "(not done writing yet...)", leaving show tokens, shot groups, advancing and reset events to be written.

### Step 19 – Testing your machine
- MPF supports automated Python machine tests: hit switches, then assert coils, lights, modes and display text. Every tutorial step has tests in `mpf-examples`.
- The link given (`developer.missionpinball.org/.../writing_machine_tests.html`) is an old developer-site URL. Current docs live under `docs/testing`.

### Step 20 – Next steps
- MPF Monitor, the service CLI (`mpf service`), the rest of the mechs, and more game logic/modes. There are also videos on structuring modes and on developing without hardware.

---

## 2. Cookbook recipe catalogue

All recipes are mode-based. Most mark files with `#config_version=5`, and many contain **[legacy MC]** `slides:`/`widgets:` blocks. Where a recipe says its runnable config is in `mpf-examples/cookbook/...`, remember that repo is flagged out of date.

| Recipe | What it achieves | Key config idea |
|---|---|---|
| **TAF Mansion Awards** (`TAF_mansion_awards.md`, needs ≥0.33) | 12 awards: selected one flashes, completed ones solid; pops re-randomise; the lit chair or swamp collects; Tour the Mansion after all 12. | `achievements:` (show_when_selected `flash`, show_when_completed `on`, `events_when_started` == `complete_events` so the award completes as it starts); an `achievement_groups:` with `auto_select`, `select_random_achievement_events: sw_jet` (a tag on the pops), `start_selected_events`, enable/disable via `light_chair`/`unlight_chair`; two helper modes `chair_lit` (indefinite) and `chair_lit_3s` (a `timers:` with end_value 3) that cancel each other; a trick where 2 of 12 achievements have **no** `enable_events` (so they are enabled immediately and one gets auto-selected), then a persistent `counters:` posts `initialize_mansion` to enable the other 10. Steps 7, 8b, 9 and 10 are **TODO**. |
| **AFM Super Jets** (`AFM_super_jets.md`) | 100 pop hits (persisting across balls) start Super Jets (3M per hit, with lower scoring blocked); then 25 hits within a ball restart it; lane completions add 50k per jet hit, capped at 40 completions. | `counters:` with `persist_state: true` (100 hits) and `false` (25 hits); `enable_events: mode_base_started{current_player.sj_active>0}`; a player var `sj_active` set via `variable_player` (`int: 1, action: set`); `score: 3000000\|block`; a dynamic score `1000000 + (device.counters.lb_rollover_complete_count.value * 50000)`; a `shot_groups` lane change with flipper rotation. **Buggy as written** (see gotchas). |
| **Rollover Lanes with Lane Change** (Indiana Jones, `rollover_lanes_with_lane_change.md`) | I-N-D-Y lanes light when rolled; flippers rotate them; completing all of them awards 10k and +1 bonus multiplier, then they reset. | A `shot_profiles` where the first state is **off** (rollover lanes are "lit" when the lamp is off); a `shot_groups` with `rotate_left_events`/`rotate_right_events` and `reset_events: top_lane_group_hit_complete`; the group posts `(group)_(state)_complete`. |
| **Batman '66 GADGET** (`B66_gadget.md`, needs ≥0.53) | 6 targets spell GADGET; hitting an already-lit letter awards an adjacent unlit one ("friendly neighbour"); completion awards a gadget and resets. | An `accruals:` logic block (`reset_on_complete: true`, `disable_on_complete: false`); `event_player` **conditional events** on `device.accruals.gadget_accrual.value[i]`; a tokenised flash show `(gadget_letter_made_led)` ending with `duration: -1`; a `show_player` with `key:` and `show_tokens`; `config:` includes that split the mode across files; player vars `gadgets_earned`/`gadgets_available` kept machine-wide so they survive mode stops. Its example link is marked TODO. |
| **Dual launch devices** (`dual_launch.md`) | Two plungers/troughs; the ball launches from whichever side's launch button is pressed first. | Override the built-in `game` mode: `modes/game/config/game.yaml` with `code: modes.game.code.game.MyGameName`, and a Python subclass of `mpf.modes.game.code.game.Game` that overrides `_start_ball()` using `Util.race()` on two `wait_for_switch` futures and then `playfield.add_ball(source_device=...)`. This shows how to change a default without rewriting it. |
| **Sequential Drop Banks** (`sequential_drop_banks.md`) | Drops must be hit in order; the correct one flashes; a wrong target gets reset back up. | A profile with `advance_on_hit: false` (off → lit/flash → down/on); each shot advanced by its predecessor's `_lit_hit`; a `sequences:` logic block; `event_player` posting `reset_drop_N` on `drop_N_off_hit`; `drop_targets:` with `reset_events` including `reset_drop_N`; scoring on `logicblock_drop_sequence_hit`/`_complete`. |
| **Skillshot with Lane Change** | A random lane lit at ball start; the flippers move it until plunge; hitting it scores 20k. | `random_event_player` choosing `advance_skillshot_*`; `shot_groups` with `disable_rotation_events: s_plunger_lane_inactive`; `variable_player: skillshot_lit_hit`; end the mode on `skillshot_hit` or on `playfield_active` with a 1 s delay (`stop_mode_skillshot\|1s`) so the award isn't lost. |
| **Skillshot with Auto-Rotate** | The lit target cycles every 500 ms until the ball leaves the plunger, then flashes. | `timers:` with `tick_interval: 500ms` and `control_events` stopping on `s_plunger_lane_inactive`; shot group `rotate_events: timer_skillshot_rotate_tick`; on `timer_..._stopped`, conditional events `{device.shots.skillshot_drop_1.state==1}` advance only the "on" shot to "lit". |
| **Multiple Timed Shots** | Succeed if all 3 shots are lit (3 s timers) at the same time. | Three countdown `timers:` restarted by `timerN_start`; `event_player` conditional events such as `timer_t1_started{device.timers.t2.running and device.timers.t3.running}`. |
| **Top Lanes with Multiplier** (Heavy Metal Meltdown J-A-M) | Completing the lanes steps the playfield multiplier 1× → 2×, 3×, 4×, 5×, 10×; the flippers change lanes; ball end resets. | A `counters:` with `events_when_hit` and conditional `JAM_lanes_done{count==N}` setting the `pf_multiplier` player var; `score: 1000 * current_player.pf_multiplier`; per-level light shows. |
| **Long-press Start to end game** | Hold start for 5 s to end the game. | `timed_switches: game_cancel: {switch_tags: start, time: 5s, events_when_active: end_game}`. Works on ball 1 as well; doesn't skip bonus or high score. |
| **Mystery Awards** | Hold the ball in a scoop, pick a weighted random award without repeats, and release when the award video ends. | `ball_holds:` (enable on the qualifying event, disable during multiball, `release_one_events: end_mystery`); `random_event_player` on `ball_hold_mystery_scoop_held_ball` with weights and `force_all: true`; slides with `expire: 5s`, whose `slide_..._removed` events post `end_mystery` **[legacy MC slide syntax]**. |
| **Lit Lane Rotation** (`lanes_mode.md`, Indiana Jones) | A longer tutorial-style version of lane change: default profile, rotation, delayed reset, scoring (unlit 5k / lit 100 / complete 10k), and a completion light show at speed 20 with 10 loops and priority +1. | `shot_groups` `reset_events: {indy_lanes_lit_complete: 1s}` (a delayed event); mode priorities are additive (`priority: 1` in a base-100 mode gives 101). Notes that the final hit scores 15k (5k + 10k). |
| **Carousel mode selection** | Scroll through modes with the flippers, select with start or launch. | `mode: code: mpf.modes.carousel.code.carousel.Carousel`, `use_wait_queue: true`, and `mode_settings:` (`selectable_items`, `select_item_events`, `next_item_events`, `previous_item_events`); events `carousel_(item)_highlighted` and `_selected`; recommends rotating on `*_inactive` flipper events so `flipper_cancel` can select; `block_events: flipper_cancel` plus `release_events`. Slides are **[legacy MC]**. |
| **Drain all balls and serve one back** (`fake_ball_save.md`) | End a mode (e.g. a timed multiball) by disabling flippers, slings and pops, draining everything, playing a video, then serving a new ball without ending the player's ball. | Autofires/flippers with custom `enable_events`/`disable_events`; a "fake" `ball_saves:` (`auto_launch: false`, `balls_to_save: 1`); `queue_relay_player` on `balldevice_bd_trough_ball_eject_attempt` waiting for the show to end; shows with `events_when_stopped`. The author calls it "just an example of how I did it". |

The cookbook index lists "Sequential Drop Bank Targets" and "Sequential Drop Banks" as two entries, but both point to the same page.

---

## 3. Game design guidance (`docs/game_design`)

The section assumes your hardware (especially ball devices) is already configured. It includes videos on mode structure, state machines and events.

**Mode selection (`mode_selection.md`)**
- A selection/qualify mode usually runs all the time. It:
  - tracks what can be qualified (usually nothing while a game mode is running);
  - shows progress or the current selection;
  - starts a mode and then waits;
  - shows which modes are complete.
- If modes can be selected independently, you may need two selection modes.
- **"Hit shot X times"** (Batman DK, Star Wars): per-mode `counters:` with `persist_state: true`, `enable_events: enable_qualify` and `disable_events: disable_qualify`. On completion they post `disable_qualify, start_mode_left_ramp`, and the mode posts `enable_qualify` when it finishes.
- **Carousel:** it doesn't track completion, so pair it with a second tracking mode. A selected "character" can change counters, e.g. `starting_count: 2 if current_player.selected_character == "character1" else 0`.
- **Achievement groups** give a flexible rotating selection (`rotate_right_events: s_action_button_active`, `start_selected_events: hit_scoop`).
- **Select before ball 1:** a mode with `game_mode: false` and a `queue_relay_player` on `player_turn_starting{player.ball==0}` that waits for `selection_mode_ended`.
- **Using start as a select button:** set `game: add_player_switch_tag: add_player`, then map `s_start_active: sw_add_player` in the modes where adding players should still work.

**Wizard modes (`wizard_modes.md`)**
- Achievement states run disabled → enabled → selected → started/stopped → completed. Once completed, the state is final.
- Wiring patterns:
  - enable the achievement from a counter;
  - start the mode on `achievement_X_state_enabled`;
  - start the achievement on `mode_X_started`;
  - complete it on a logic-block completion;
  - stop it on `mode_X_will_stop`.
- Use `restart_after_stop_possible` and `restart_on_next_ball_when_started` to control replay.
- Conventions: mini-wizards end on their goal; end-of-game wizards play until drain and restart on the next ball; multiball wizards run until one ball is left.

**Ball end and game end modes**
- A custom ball-end mode uses `start_events: ball_ending`, `use_wait_queue: true`, a priority (which orders the ball-end modes) and a `stop_events` it must eventually post. Otherwise the game hangs.
- Game-end modes are the same, but use `game_ending` and `game_mode: false`.
- Alternative: `queue_relay_player: ball_ending{current_player.ball==3}: {post: start_your_mode, wait_for: mode_your_mode_stopped}`.
- Built-ins: bonus, high score, match.

**Other modes:** credits (active both in and out of games), attract, tilt (runs all the time; can remove credits on slam tilt), and service (always running, so it can take over).

**Mode layering (`mode_layering.md`)**
- Three categories:
  - **Field** modes: non-intrusive qualifiers and accruals.
  - **Mission** modes: partial takeover. "Game mode" is avoided as a name because `game` is reserved.
  - **Wizard** modes: full takeover.
- Three helper modes:
  - **field.yaml** imports all field configs through `config:`.
  - **global.yaml** swaps field ↔ mission and holds persistent qualifiers (pops, multiball locks).
  - **base.yaml** swaps global ↔ wizard and holds always-persistent items (achievements, ball saves, combos).
- Mechanism: each mission or wizard mode sets `events_when_started: mode_type_mission_started` (or `..._wizard_started`) and the matching `events_when_stopped`. The helper uses guarded restarts:

```yaml
# modes/global/config/global.yaml
mode:
  start_events: start_mode_global
  stop_events: stop_mode_global, ball_will_end
event_player:
  mode_global_started: [start_mode_field]
  mode_global_will_stop: [stop_mode_field, stop_missions]
  mode_type_mission_started: [stop_mode_field]
  mode_type_mission_stopped{not mode["global"].stopping}: [start_mode_field]
```

---

## 4. Flowcharts summary (`docs/flowcharts`)

- **Boot (`mpf_boot.md`):**
  - Load `mpfconfig.yaml`, then the machine config, then set the platform.
  - Load system modules: config processor, timing, events, mode controller, device manager, switch/ball/light controllers, BCP, logic blocks, variable player, shot profiles.
  - Post `init_phase_1` through `init_phase_5`. Plugins load before phase 3 and scriptlets before phase 4. In phase 4 the auditor initialises and modes load.
  - `reset()` posts `machine_reset_phase_1/2/3`. Phase 3 resets drop targets, enables GI and **starts attract**. That is why the tutorial's temporary flipper enable used `machine_reset_phase_3`.
- **Game start (`game_start.md`):**
  - The game starts when the start button is **released**, which allows long-press features.
  - Attract posts the boolean event `request_to_start_game`. Any component can veto it: the ball controller if balls are missing or not home, the credits module if there are no credits.
  - If nothing vetoes: `game_start` → game mode → queue event `game_starting` (auditor enables, score reels reset) → first player added → `game_started` → `player_turn_start()`.
- **Ball start (`ball_start.md`):** `player_turn_started` → ball incremented → queue event `ball_starting` (a hook for cut-scenes, tilt settle and so on) → `ball_started`. At that point shots, autofires, flippers, locks and multiballs enable. Then `playfield.add_ball()` makes the trough feed the plunger, which launches on the player-controlled eject event.
- **Mode start and stop (`mode_start.md`, `mode_stop.md`):**
  - Start: devices created → stop events registered (mode priority +1) → start_methods → control_events → queue event `mode_X_starting` → timers → `mode_X_started` → `mode_start()` in custom code.
  - Stop is the reverse: switch handlers, timers and delays removed → queue event `mode_X_stopping` → `mode_X_stopped` → mode devices removed → `mode_stop()`.
- **Ball end (`ball_end.md`):** ball enters a `drain`-tagged device → relay event `ball_drain` (ball save can "take" balls) → `balls_in_play` hits 0 → queue event `ball_ending` → `ball_ended`. From there: shoot again if there's an extra ball; `game_ending` if it's the last ball of the last player; otherwise rotate player.
- **Soft shutdown (`soft_shutdown.md`):**
  - Post `request_soft_shutdown`. The boolean event `machine_request_shutdown` can be blocked, which posts `machine_abort_shutdown`. Otherwise `machine_will_shutdown` fires, subsystems exit and the loop ends.
  - An optional `machine: soft_shutdown_exit_command` runs a script.
  - The FAST Neuron's soft-power button triggers this natively (`fast_soft_power_switch_active/inactive`, `fast:net:soft_power_hold_time`).

---

## 5. Examples & learning resources (`docs/examples`)

- **Test configs:** MPF's thousands of self-tests are the most reliable examples, because they run automatically on every change.
  - MPF tests: `mpf/tests/machine_files`.
  - Legacy MC tests: `mpfmc/tests/machine_files`.
  - Search GitHub within the `missionpinball` org for something like `ball_search:`, filtered to YAML.
- **mpf-examples repo:** `demo_man`, `mc_demo`, `tutorial`/`tutorial_step_XX` and `wpc_template`. It is flagged: *"As of this writing (June 2023), the mpf-examples repo is a bit out of date."* It has one branch per MPF version, and the MC Demo page says the dev branch is 0.57.
- **Demo Man:** `mpf both -X`. Keys:
  - `S` start, `L` launch, `X` left sling, `1` drain.
  - `Z` and `/` are the flippers during high-score entry.
  - Without `-X` you get P-ROC errors.
- **Real projects:**
  - Brooks 'n Dunn (`github.com/gabeknuth/bnd`); has good test examples.
  - Mass Effect 2 on a SPIKE GoT cabinet (`github.com/avanwinkle/masseffect2`).
  - The MPF Showcase.
  - A GitHub code search for `driverboards:` in YAML returns about 112 public MPF configs.

---

## 6. Finalization / deployment checklist (making it arcade-ready)

The docs admit this section is mostly unfinished: *"Most of this is unfinished: See Help us to write it."* `ball_search.md`, `os.md`, `switches.md` and `operator_settings.md` are placeholders. The checklist below combines what **is** documented, with source paths.

### 6.1 Host computer & OS
- **Host computer** (`finalization/host_computer.md`): pick an OS you know. Don't use Linux if you've never used it; a $150 PC beats a $50 SBC headache. The best computer is one you already have. MPF behaves identically on Windows, Mac and Linux, so you can swap the computer later without config changes. The rest of the page is headings only.
- **Operating system** (`finalization/os.md`): a stub. The planned topics are "freezing it, lock down, recovery, auto booting".

### 6.2 Power on and power off (`finalization/power.md`)
- Pinball players just flip the power switch, so plan for unclean shutdowns.
- **Option 1: shutdown controller.** Scott Danesi's Computer Start-up and Shutdown Controller (CSSC, part #600-0322-00) triggers a PC shutdown on mains-off. The PC then needs power until shutdown finishes, from a separate outlet or a UPS. It's most useful with older Windows; journalling filesystems (ext4, ReFS) matter less.
- **Linux with systemd:** set `HandlePowerKey=ignore` in `/etc/systemd/logind.conf`. Install `acpid` and create `/etc/acpi/events/powerbtn`:
  ```bash
  event=button[ /]power
  action=/sbin/poweroff
  ```
- **Option 2: read-only filesystem.** Build an embedded image (OpenEmbedded/Yocto) mounted read-only. Add a separate journalling partition for audits, high scores and logs, and expect it to break: provide a wipe/reset mechanism.
- **MPF-triggered shutdown:** a custom `shutdown_computer` mode plus a Python class (`mode: code: shutdown_computer.shutdown_computer`). Holding left flipper + start for 5 s (`combo_switches` with `hold_time: 5s`, `events_when_both: shutdown_host_computer`) calls `os.system('shutdown ...')`. **The sample code has bugs:**
  - Windows branch: `shutdown_str == ...` is a comparison, not an assignment.
  - Log line: `self.os_type` should be `self.OS_type`.
  - Linux branch: `shutdown -t 0` is probably meant to be `shutdown -h now`/`-P`.
- **FAST Neuron:** use the soft-power flow in §4.

### 6.3 Auto-launch on boot
Documented only in `install/linux/xubuntu.md`, which is an older 0.33/0.55-era guide.
1. Install Xubuntu/Lubuntu. **Do not encrypt the home folder**, or auto-login breaks.
2. Auto-login: create `/etc/lightdm/lightdm.conf.d/12-autologin.conf`:
   ```ini
   [Seat:*]
   autologin-user=your_username
   autologin-user-timeout=0
   ```
3. Create `run.sh` in the machine folder:
   ```bash
   #!/bin/bash
   source ~/your_venv_name/bin/activate
   xterm -e "cd /home/your_username/your_machine_folder && mpf both -c config"
   ```
4. Create `~/.config/autostart/mpf.desktop`:
   ```ini
   [Desktop Entry]
   Version=1.0
   Name=MPF
   Comment=Mission Pinball
   Exec=/home/your_username/your_machine_folder/run.sh
   Path=/home/your_username/your_machine_folder/
   Terminal=false
   Type=Application
   ```
5. If you use a SmartMatrix RGB DMD: `sudo usermod -a -G dialout your_username`.
6. The same guide suggests shortening `TimeoutStartSec` in the networking service to about 10 s, for faster boot without a network.

**GMC-era adjustments** (from `gmc/guides/launching-the-mpf-game-with-godot.md` and `running/commands/both.md`):
- In production, don't run the Godot editor. **Export** the Godot project (install export templates once; Project → Export; embed the PCK; choose the architecture, e.g. arm64 for a Raspberry Pi; `chmod +x` on Linux).
- Re-export after **every** Godot change. The exported executable contains all assets.
- Launch the exported binary and MPF from your autostart script, or have the GMC project spawn MPF. Never do both, or you get two MPF instances.
- The docs don't publish a GMC-specific systemd or autostart script; you have to adapt the XFCE recipe yourself.

### 6.4 Production mode & performance (`finalization/software.md`, `running/commands/game.md`)
- Run `mpf build production_bundle`. It creates `mpf_config.bundle` and `mpf_mc_config.bundle` (YAML only, no media). **Rebuild after every config, mode or show change.**
- Launch with **`-P`** (production mode). It:
  - uses the pre-compiled bundles for a fast cold start (the YAML cache doesn't help on read-only systems);
  - skips expensive validation and reduces debug output;
  - tries to keep running rather than exit on some errors;
  - waits for hardware at start;
  - **exits if init fails within 30 s**.
  
  The docs therefore recommend running MPF **inside a loop**, or rebooting on failure. Example: `mpf game ./path/to/machine_folder -P`.
- Use **`-t`**: the text UI costs performance.
- Install `uvloop` on Linux (`pip3 install uvloop`); MPF uses it automatically.
- Optional: PyPy, about 10× faster in benchmarks (`pypy -m pip install mpf`, `pypy -m mpf game`). It works for MPF but not for the legacy Kivy MC; GMC isn't mentioned in that section.
- Assets:
  - match audio sample rate to the hardware;
  - use images and videos at native resolution;
  - re-encode video to a codec the target can decode efficiently.
- The "install the latest Python" advice cites Python 3.4–3.6 speed gains and is stale.

### 6.5 Ball devices, ball search, switches
- **Ball devices** (`finalization/ball_devices.md`): the default `eject_timeouts` of **10 s** for playfield ejects causes slow multiball ejects. Measure the longest time a ball can fall back, and set `eject_timeouts` to that value, never lower; lower values risk two balls in the plunger lane. `confirm_eject_switch` is an option but may need a hardware change. Timeouts don't matter for device-to-device ejects such as trough → plunger.
- **Ball search:** a "help us write it" placeholder. See the `ball_search:`/ball-device docs elsewhere.
- **Switches:** a placeholder. It points to the switch debounce docs and notes that broken-switch detection is still to be written.

### 6.6 Coin, credits, audits, service (`machine_management/*`, `game_design/other_modes.md`, `game_logic/credits.md`)
- **Credits:** add `- credits` to `modes:` and create `modes/credits/config/credits.yaml`. Machine-wide config:
  ```yaml
  credits:
    max_credits: 12
    free_play: false
    service_credits_switch: s_service_coin
    switches:
      - switch: s_coin_left
        type: money
        value: .25
    pricing_tiers:
      - price: .50
        credits: 1
      - price: 2
        credits: 5
    fractional_credit_expiration_time: 15m
    credit_expiration_time: 2h
    persist_credits_while_off_time: 1h
    free_play_string: FREE PLAY
    credits_string: CREDITS
  ```
  The credits module vetoes `request_to_start_game` when there are no credits.
- **Auditor:**
  - Configured in the `auditor:` section: `save_events`, `num_player_top_records` (default 10), and `audit:` (shots/switches/events/player).
  - Tracks switch counts, event counts, shots, and the average, top-10 and total of player vars.
  - Default reset events: `auditor_reset,factory_reset`.
  - **Path contradiction:** the config reference says audits save to `/audits/audits.yaml`, but the Service Mode page says `data/audits.yaml`.
- **Service mode** (`machine_management/service_mode.md`), menus:
  - **Utilities / Reset:**
    - Coin Audits → `data/earnings.yaml`
    - Factory Reset → `machine_vars.yaml` persisted vars back to `initial_value`
    - Credits → `credit_units` set to 0
    - High Scores → `data/high_scores.yaml` back to the `defaults:` in `high_score.yaml`
    - Game Audits
  - **Adjustments:** configured `settings`.
  - **Audits:** "To be completed".
  - **Diagnostics:** switch, light and coil tests.
- **Safety warning:** with `service` in `modes`, opening the coin door shows "coil power off", but on most controllers **that is only a message**. The exception is FAST's smart power filter board, which lets MPF control 48 V. **You must wire the coin-door interlock so high voltage is actually cut.**
- **Operator settings:** placeholder page.
- **End-game niceties:** long-press start to end a game (cookbook); high score and match modes (game design).

### 6.7 Updating
- Nothing in these sections covers field updates of a deployed machine. The relevant practices from these docs:
  - keep the machine folder in Git (tutorial step 2), so you can pull or clone to the cabinet PC;
  - machine folders are portable across OSes;
  - rebuild the production bundle, and re-export the Godot project, after any change;
  - match mpf-examples and MPF versions (mismatches cause startup errors).

### 6.8 Condensed go-live checklist
1. Coil pulse times and hold power tuned; coin-door interlock physically cuts HV.
2. All `playfield_active` tags correct; `eject_timeouts` measured per device; ball search configured.
3. `enable_events: machine_reset_phase_3` removed from flippers.
4. Credits mode, or `free_play: true`; auditor, high score and service modes in `modes:`.
5. Unclean-shutdown strategy chosen: CSSC plus UPS, or a read-only root with a data partition, or soft shutdown.
6. `mpf build production_bundle`; run `-P -t` in a restart loop; Godot exported (GMC).
7. Auto-login plus an autostart entry, or a script; no home-folder encryption.
8. `uvloop` installed; assets at native resolution and sample rate.
9. Git tag or commit of the shipped version.

---

## 7. Community resources (as stated in `docs/community/index.md`)

- **MPF Users Google Group:** https://groups.google.com/g/mpf-users. Public and permanent, so it shows up in search, but "not super active these days". Most hardware vendors now run their own private Slack groups.
- **GitHub Discussions:** https://github.com/orgs/missionpinball/discussions. Integrated with code, commits and issues, with threading and upvotes.
- **GitHub (all MPF projects, including the docs):** https://github.com/missionpinball; docs source at https://github.com/missionpinball/mpf-docs.
- **PinDevCon:** June 2023 at the Northwest Pinball & Arcade Show, organised by FAST but open to all platforms. Talk videos are at https://fastpinball.com/pindevcon/, including Brian Madden's MPF "under the hood" deep dive (YouTube `4KOpcgxJer4`).
- **Discord:** not mentioned anywhere in the docs source. I found no Discord link, so none is given here.
- Many tutorial and cookbook pages still say "post to the mpf-users Google group" or "the forum", both of which link to the community page.
- **Showcase (`showcase/_add_yours.md`):** to list your machine, copy `_TEMPLATE.yaml` in the mpf-docs repo's root `showcase/` folder. Fields include name, acronym, team, location, started/finished, youtube_video_ids, documentation_link, code_link, controller and description (example: `brooks_and_dunn.yaml`). Then open a PR. The showcase index is generated at build time, so it isn't in the source tree.
- **Welcome Wall (`welcome_wall.md`):** a sandbox page for first-time doc editors. It shows Markdown basics and `--8<-- "file.md"` snippet includes from `/includes`. PRs are reviewed by maintainers ("Do you want to be an MPF maintainer? We could use the help.").

---

## 8. Gotchas, outdated and contradictory items

1. **The tutorial is legacy-MC (0.56/0.57).** No 0.80/GMC tutorial exists yet. Steps 5, 6, 10, 14, 15, 16 and 18 contain MC-only display and keyboard config.
2. **Config version inconsistency:** step 2 says `#config_version=6`, but the mode files in steps 14–18, the attract config and almost every cookbook recipe use `#config_version=5`. Use 6. Show files use `#show_version=5`.
3. **Step 1** has an empty version string ("written for MPF versions ."), an example `MPF v0.51.3`, and says to install MPF-MC.
4. **Step 10:** the "physical hardware" example uses `mpf both -X`, which is actually virtual. On real hardware, omit `-x/-X`.
5. **Step 18** is unfinished ("not done writing yet"). It also renames things mid-page:
   - the flipper switches become `s_flipper_lower_left_active`;
   - the mode2 snippet defines `my_first_shot_mode2` but the explanation says `my_first_shot`;
   - it refers to a "`scoring:` section" (the old name for `variable_player:`) and to a light show from "Step 18" that was actually step 17.
6. **Step 19** links to the defunct `developer.missionpinball.org`.
7. **AFM Super Jets recipe bugs:**
   - `autofire_coils:` is mis-indented under `ball_devices:`;
   - the setup mode is headed `super_jets_startup` but named `super_jets_setup`;
   - the event_player listens for `Super_Jets_Go_Again` while the counter posts `Super_Jets_Resume_Go`;
   - the posted `start_mode_super_jets` isn't used by the mode (it starts on `Super_Jets_Go`/`Super_Jets_Resume_Go` directly);
   - several blocks have stray indentation.
8. **Skillshot recipes** use `mode_skillshot_started` and `stop_mode_skillshot`. The mode is actually named `skillshot_with_lane_change` / `skillshot_with_auto_rotate` (the auto-rotate shot correctly uses `mode_skillshot_with_auto_rotate_started`), and the stop events are `stop_mode_skillshot_with_*`. Align the names.
9. **Lanes mode:** the show_player uses `indy_lanes_default_lit_complete`, but the reset and scoring use `indy_lanes_lit_complete`. It also says "`light_player:` entry" while showing `show_player:`.
10. **Carousel (Doctor Who)** uses `transitions:` where the first example uses `transition:`, and uses `stop_events: carousel_item_selected` without a condition.
11. **TAF recipe:** steps 7 and 9–10 are TODO, and there are two "Step 8" headings. Its `chair_lit` `start_events` include `mode_mansion_awards_started`, but the prose says `ball_starting`.
12. **Shutdown mode Python** has bugs (`==` vs `=`, `os_type` vs `OS_type`), and its Linux command is questionable.
13. **Finalization and machine management are mostly stubs:** ball search, OS, switches, operator settings, host computer, service-mode audits. The only auto-boot recipe is the old Xubuntu/XFCE one, which uses `mpf both -c config` (legacy MC semantics).
14. **Audit file path** conflicts: `/audits/audits.yaml` vs `data/audits.yaml`.
15. **Coin door "coil power off" is a display message only** unless your power hardware actually cuts HV (FAST smart power filter is the exception).
16. **`software.md`:** the Python 3.4–3.6 advice is stale, and the PyPy note only mentions Kivy MC.
17. **mpf-examples** is out of date (June 2023 note), and its dev branch targets 0.57. Tutorial step folders and cookbook "runnable configs" may need fixes on 0.80.
18. **No Discord** is referenced in the docs. The Google Group itself says it's quiet.

---

## Source doc paths used

(relative to `mpf-docs-dev/docs/`, plus `../includes` and `../mkdocs.yml`)

- `tutorials/legacy_mc/index.md`, `1_install_mpf.md` … `20_next_steps.md` (all 20 steps); `../includes/tutorial.md`, `../includes/todo.md`; `../mkdocs.yml` (nav/redirects); `index.md` (tutorial 0.80 "coming soon")
- `cookbook/index.md`, `TAF_mansion_awards.md`, `AFM_super_jets.md`, `rollover_lanes_with_lane_change.md`, `B66_gadget.md`, `dual_launch.md`, `sequential_drop_banks.md`, `skillshot_with_lane_change.md`, `skillshot_with_auto_rotate.md`, `multiple_timed_shots.md`, `long_presssing_start_to_end_game.md`, `carousel.md`, `fake_ball_save.md`, `mystery_award.md`, `top_lanes_with_multiplier.md`, `lanes_mode.md`
- `examples/index.md`, `demo_man.md`, `mc_demo.md`, `mpf-examples.md`, `tests.md`
- `game_design/index.md`, `mode_selection.md`, `wizard_modes.md`, `ball_end_modes.md`, `game_end_modes.md`, `other_modes.md`, `mode_layering.md`
- `flowcharts/index.md`, `mpf_boot.md`, `game_start.md`, `ball_start.md`, `mode_start.md`, `mode_stop.md`, `ball_end.md`, `soft_shutdown.md`
- `finalization/index.md`, `ball_devices.md`, `ball_search.md`, `host_computer.md`, `os.md`, `power.md`, `software.md`, `switches.md`
- `machine_management/index.md`, `auditor.md`, `service_mode.md`, `operator_settings.md`
- `community/index.md`, `showcase/_add_yours.md`, `welcome_wall.md`
- Cross-referenced for GMC/production context: `versions/index.md`, `gmc/guides/base-slide-with-score.md`, `gmc/guides/launching-the-mpf-game-with-godot.md`, `gmc/reference/gmc-cfg.md` ([keyboard]), `running/commands/both.md`, `running/commands/game.md`, `running/commands/index.md`, `install/linux/xubuntu.md`, `game_logic/credits.md`, `config/auditor.md`
