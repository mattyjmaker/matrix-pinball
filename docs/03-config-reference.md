# 03 — MPF 0.80 Config File Reference (condensed)

> Condensed from the MPF documentation source (`dev` branch = MPF 0.80, released April 2026, which uses the Godot Media Controller "GMC").
> Covers `docs/config/**` (the whole config reference, ~213 pages), `docs/config_players/`, `docs/player_vars/`, `docs/machine_vars/`, `docs/game_vars/`, `docs/reference/`.
> Where the docs contradict themselves or are out of date, it is flagged with **⚠**. Nothing here is invented. If the docs don't say something, this file says so.

---

## Contents

1. [How MPF config files work](#1-how-mpf-config-files-work)
2. [Value types and syntax rules](#2-value-types-and-syntax-rules)
3. [Dynamic values, conditional events and text templates](#3-dynamic-values-conditional-events-and-text-templates)
4. [Config players](#4-config-players)
5. [Categorised index of every config section](#5-categorised-index-of-every-config-section)
6. [Deeper notes and example YAML for the key sections](#6-deeper-notes-and-example-yaml-for-the-key-sections)
7. [Player, machine and game variables](#7-player-machine-and-game-variables)
8. [What's deprecated or changed in 0.80 (GMC)](#8-whats-deprecated-or-changed-in-080-gmc)
9. [Gotchas, contradictions and doc errors](#9-gotchas-contradictions-and-doc-errors)
10. [Source doc paths used](#10-source-doc-paths-used)

---

## 1. How MPF config files work

MPF is mostly "programmed" through YAML config files. There are two kinds (`config/instructions/machine_config.md`, `mode_config.md`):

| Kind | What it is | Typical contents |
|---|---|---|
| **Machine-wide config** | Always loaded. Covers the whole life of the machine, including attract mode. | Hardware, switches, coils, lights, ball devices, playfields, flippers, autofire coils, `game:`, `modes:` list, settings, machine/player var defaults, and so on |
| **Mode config** | One config file per mode (the docs call it e.g. `shoot_here.yaml` for a mode named `shoot_here`). Its contents are **only active while that mode runs**, at that mode's priority. | `mode:` section, shots/shot_groups, logic blocks, timers, config players (scoring, shows, sounds, slides), achievements, extra balls, multiball locks, and so on |

Every config reference page starts with a "Valid in" table: machine config YES/NO, mode config YES/NO (and sometimes "shows"). There are three rough groups:

- **Machine-only** (mostly physical hardware): `hardware`, `switches`, `coils`, `lights`, `ball_devices`, `playfields`, `flippers`, `autofire_coils`, `kickbacks`, `diverters`, `drop_targets`, `magnets`, `servos`, `steppers`, `motors`, `digital_outputs`, `dual_wound_coils`, `psus`, `game`, `machine`, `modes`, `settings`, `player_vars`, `machine_vars`, `credits`, `auditor`, `bcp`, `named_colors`, `light_settings`, `displays`, `dmds`, `rgb_dmds`, `segment_displays`, `blinkenlights`, `score_reels`, `score_reel_groups`, `score_queues`, `playfield_transfers`, `spinners`, `info_lights`, `text_ui`, `logging`, `mpf`, and all the platform sections.
- **Mode-only** (need a player or game): `mode`, `mode_settings`, `shots`, `shot_groups`, `timers`, `achievements`, `achievement_groups`, `extra_balls`, `multiball_locks`, `ball_routings`, `score_queue_player`, `high_score`, `tilt`, `bonus` (via `mode_settings`).
- **Both**: all logic blocks (`accruals`, `counters`, `sequences`, `state_machines`), `ball_saves`, `ball_holds`, `multiballs`, `drop_target_banks`, `combo_switches`, `timed_switches`, `sequence_shots`, `shot_profiles`, `shows`, `show_pools`, `config`, and most config players (`event_player`, `show_player`, `light_player`, `coil_player`, `random_event_player`, `queue_event_player`, `queue_relay_player`, `segment_display_player`, `blinkenlight_player`, `flasher_player`, `display_light_player`, `widget_player`, `sound_player`).

**Registering modes.** The machine config lists the modes that can load (`modes:` is a plain list). Each mode's config has a `mode:` section with `start_events`, `stop_events`, `priority`, and so on (see §6).

**Splitting files: `config:`.** Any config file can list more files to load after it (`config: [machine.yaml, devices.yaml, ...]`). They are merged in list order, and **the later file wins** on conflicts. Included files can include others; each newly found file goes to the end of the list. Paths may be relative, and either slash direction works.

**`#config_version=6`** (`instructions/config_version.md`, `config_v6.md`). The first line of every config file (machine and mode) must be a YAML comment giving the config version. MPF uses it to check the file is compatible:

| MPF version | config_version |
|---|---|
| **0.57+ (so 0.80)** | `#config_version=6` |
| 0.50–0.56 | 5 |
| 0.30–0.33 | 4 |
| 0.20–0.21 | 3 |
| 0.19 | 2 |
| 0.17–0.18 | 1 |

Show files use `#show_version=6`. A migration tool is mentioned but not documented on that page.

**What changed in v6 ("pure YAML").** MPF's old YAML "hacks" were removed:
1. Values starting with `+` must be quoted (`time: "+1"`). In shows, `+1` means "1 s after the previous step" and `1` means "1 s after show start". (Don't quote `time: 0`.)
2. Values made only of digits with a leading zero must be quoted: `color: "000066"`, `number: "0804-1"`. This applies to keys too (`"0804":`).
3. Colour values made only of digits must be quoted: `color: "330000"`.
4. `!!omap` is gone. Remove it, and remove the leading dashes if the items were `key: value` (e.g. `position_switches:` becomes a plain mapping).
5. The high-score data file (`data/high_scores.yaml`) lost its `!!python/tuple` tags. Each entry is now `- - NAME` / `  - score`.

**Case sensitivity** (`case_insensitivity.md`): setting names have been case-sensitive since 0.50. Use lower case for mode, device, timer and other names. Upper case is fine in slide text.

**Common per-device settings.** Almost every device has these:
- `debug: true`: more logging. It can hurt performance.
- `console_log:` and `file_log:` (`none|basic|full`, default `basic`).
- `label:`: the name shown in service mode and reports (default `%`).
- `tags:`
- Hardware devices also take `platform:`, which overrides the default platform when you mix hardware, and `platform_settings:`.

**Overwriting configs**: `instructions/overwrite.md` is an empty stub ("Help us to write it"). The `high_score` example uses `_overwrite: True`, but its meaning isn't documented in this section.

---

## 2. Value types and syntax rules

### YAML basics
`instructions/yaml.md` is mostly a stub. Its one rule: any indent size works, as long as siblings are indented the same, and more indent means a child.

**Lists** (`lists.md`): write them either comma-separated on one line or one `- item` per line. The space after the dash is required.
```yaml
tags: flipper, player          # one-line list
save_events:
  - game_started
  - ball_ended
```
**Lists of lists** (used by logic-block steps) combine the two forms: `- event1, event2` means one step that either event can complete.

### Time strings (`time_strings.md`)
Anywhere a time is needed you can write `500ms`, `500 MS`, `500msec`, `0.5s`, `0.5 sec`, `2m`, `2h` or `2d`. A **bare number uses that setting's default unit**. The reference marks each setting as `time string (ms)` or `time string (secs)`, so a bare `500` means 500 ms on an ms setting but 500 s on a secs setting. Always add the unit.

### Device control events (`device_control_events.md`)
These are settings named `*_events` (`enable_events`, `disable_events`, `reset_events`, and so on):
```yaml
enable_events: ball_started              # single
disable_events: ball_ending, tilt, slam_tilt   # any of these
reset_events:                            # with per-event delays
  ball_starting: 0
  collect_special: .75s
enable_events: ball_started.3            # ".N" raises handler priority by N
score_events: ball_started.2
disable_events: ball_started.1
```
- Any one listed event triggers the action. To require several events, use an accrual or sequence logic block.
- A handler runs at the mode's priority (1 outside modes). Some devices already order their handlers, e.g. disable before enable on the same event.
- **Setting an `*_events` list replaces the default list.** Several pages say this. If you still want the defaults, list them again.

### Colours (`colors.md`, `named_colors.md`, `light_player.md`)
- You can use a name (140 web colours plus your `named_colors:`), a hex value **without `#`** (`ff0000`; `#` starts a YAML comment), a hex value with a brightness percentage (`4a9b22%50`), or a brightness value (`AA`/`120`, applied to all channels).
- Special values: `on` (the light's `default_on_color`, white if unset), `off` (0,0,0, but the show keeps control of the light), and `stop` (releases this player or show's hold on the light so lower-priority colours show through).
- An 8-digit hex value adds alpha (`ff000080`). This is used by the media controller.
- RGB lists (`[24, 65, 226]`) are only valid in `named_colors:` according to light_player.md. **⚠** blinkenlight_player.md and flasher_player.md say lists are allowed.
- Remember to quote all-digit hex values (v6 rule).

### Gain/volume (`gain_values.md`)
Write `0.0`–`1.0`, a decibel value (`-17.5db`, `0.0 db`), or `-inf` (no `db` suffix). A value without `db` is read as linear.

### Gamma (`gamma_correction.md`)
Defaults are 2.5 for RGB LEDs, 2.2 for RGB DMDs and 1.0 for mono DMDs. There's a built-in `dmd_gamma_test` slide for tuning. It was an MPF-MC feature, and whether GMC has it isn't stated.

### Tags (`tags.md`)
- Tags group devices, so light players, shows and so on can target a whole group.
- Switch tags also create events: a switch tagged `start` posts `sw_start` and `sw_start_active`. The prefix is configurable in `mpf:`.
- These events only show in the log or monitor if something handles them or the switch has `debug: true`.
- `*` means "every device of this type" (from 0.56.1).
- Reserved tags are covered in §6 (switches, ball_devices, playfields).

### Templates
Some settings have type `integer or template`, `time string (ms) or template`, `template_str`, `int_or_token`, `ms_or_token` and so on. Those accept a dynamic value (§3) or a show token.

---

## 3. Dynamic values, conditional events and text templates

### Dynamic value placeholders (`dynamic_values.md`)
These are evaluated at runtime and work in templated settings, conditional events and text:

| Placeholder | Meaning |
|---|---|
| `current_player.X` | player var X of the current player (game only), e.g. `current_player.score`, `current_player.ball` |
| `players[N].X` | player var of player N, **0-based** (`players[0].score` = player 1) |
| `game.X` | game var (`max_players`, `num_players`, `balls_per_game`, `balls_in_play`, `tilted`, `slam_tilted`). Shorthand for `mode.game.X` |
| `machine.X` | machine var, e.g. `machine.player1_score`, `machine.credits_string` |
| `settings.X` | operator setting value |
| `device.<type>.<name>.<prop>` | device property, e.g. `device.counters.c.value`, `device.timers.t.ticks_remaining`, `device.ball_devices.lock.balls`, `device.achievements.a.state`, `device.switches.s.state`, `device.playfields.playfield.balls`, `device.flippers.left.enabled`, `device.sequences.x.completed` |
| `mode.<name>.active` | whether a mode is running |

Examples:
```yaml
variable_player:
  collect_hurryup:
    score: 1000 * device.timers.hurryup_clock.ticks_remaining * device.counters.hurryup_multiplier.value
tilt:
  warnings_to_tilt: settings.warnings_to_tilt
counters:
  my_counter:
    count_events: count_up
    count_complete_value: 5 if player.wizard_complete else 3   # ⚠ doc uses "player." here; elsewhere it's "current_player."
```
Devices use consistent property names: anything that tracks a number has `value`, and anything that can be enabled has `enabled`. Each device's page is meant to list its "Monitorable Properties", but only `switches.md` has such a section in this part of the docs.

### Conditional events
Add `{condition}` to an event name, either on the trigger event or on a posted event (event_player, random_event_player, variable_player keys):
```yaml
event_player:
  mode_base_started{current_player.score>10000}:
    - start_mode_superbonusround
  reenable_modes:
    - start_mode_shopping{current_player.cash>=1000}
variable_player:
  player_album_value{value==2}:        # event args usable directly
    album_name:
      string: GOLD
```

### "Subscription" syntax
Supported by some players, e.g. light_player. The action runs while the condition is true and is undone when it turns false:
```yaml
light_player:
  "{current_player.score > 1000000}":
    score_1M: white
```

### Dynamic event names and arguments (event_player)
- `play_show_(current_player.phase_name)` puts a value into the event name. Values are converted to strings, and expressions are allowed.
- Event args can be given as a mapping or inline `{count: 10}`.
- Dynamic arg values use `{value: <expr>, type: int|float|bool|string}`. Without `type:` the value is posted as a string.

### Text templates (`text_templates.md`)
Python format strings inside `{}`: `{machine.player1_score:d}`, `{current_player.score:d}`, `{variable:0>10}`, `{variable:^10}`, `{variable:5.2f}`, `{variable:.3}`.

The machine_vars index says `(machine|my_var)` gives a machine var **as a string** in slides, while `{machine.my_var}` gives **the value** in players such as segment_display_player. **⚠** The `(var)` pipe syntax is MPF-MC-era. GMC text handling is documented in the GMC section, not here.

---

## 4. Config players

(`config_players/index.md`, `config/config_players/index.md`)

A **config player** "plays" an action when an event is posted. The name has nothing to do with human players. Each type is named after what it controls. The same config players run in three places:

| Where | Section name | Example |
|---|---|---|
| Machine config (always active) | `<thing>_player:` | `light_player:` |
| Mode config (active while mode runs, at mode priority) | `<thing>_player:` | `show_player:` |
| Show step | `_player` dropped, plural `s` | `lights:`, `shows:`, `coils:`, `events:`, `sounds:`, `slides:`, `widgets:`, `variables:`, `blinkenlights:`, `flashers:`, `display_lights:`, `random_events:`, `segment_displays:`, `hardware_sounds:`, `playlists:`, `tracks:` |

**Common structure:**
```yaml
<thing>_player:
  <event_name>:              # the trigger event (may be conditional / have .priority)
    <target>:                # device / show / slide / variable name
      <settings>             # "full" config
  <event_name2>: <target>    # "express" (one-line) config = default action
```
- In a config file each player is its own top-level section, so one event can't mix player types there. **In a show step you can combine any number of players in the same step.**
- The **express config** doc page (`instructions/express_config.md`) is only a TODO. From the individual pages, the express (default) actions are:

| Player | Express form means |
|---|---|
| `show_player` | `event: show_name` means play |
| `coil_player` | `event: coil_name` means pulse |
| `light_player` | `light_name: color` (in show steps and under an event) |
| `flasher_player` | `event: light_name` means flash with default `ms: 100ms`, colour `on` |
| `blinkenlight_player` | `blinkenlight: color` means `add` (keyless). `remove`/`stop` as the colour removes the keyless colour |
| `slide_player` | `event: slide` means show/play |
| `widget_player` | `event: widget` means add/play |
| `sound_player` | `event: sound_name`. `sound|block` also blocks lower-priority modes |
| `variable_player` | `score: 1000` means add. `score: 5000|block` |
| `track_player`, `sound_loop_player`, `queue_relay_player` | **no express form** |

- **Priority / blocking.** Mode-based players run at mode priority. Many players accept `priority:` as an offset. `variable_player` and `sound_player` accept `block: true` to stop the same event reaching lower-priority modes.
- **Cleanup.** When a mode or show ends, what it started is usually removed: shows stop, light colours drop off, blinkenlight colours added by that mode are removed. The exception is sounds. They keep playing until they end, and looping sounds stop looping (see sound_player).

**All config players:**
- **MPF core:** `blinkenlight_player`, `coil_player`, `display_light_player`, `event_player`, `flasher_player`, `light_player`, `queue_event_player`, `queue_relay_player`, `random_event_player`, `score_queue_player`, `segment_display_player`, `show_player`, `variable_player`, `hardware_sound_player` (LISY/APC external sound boards).
- **Media (still used with GMC):** `slide_player`, `widget_player`, `sound_player`.
- **MPF-MC-only, deprecated from 0.80:** `playlist_player`, `sound_loop_player`, `track_player`.
- **Removed:** `gi_player`, `led_player`, `matrix_light_player` (0.50, use `light_player`).

---

## 5. Categorised index of every config section

Validity key: **M** = machine config, **m** = mode config, **M/m** = both, **sub** = only used nested inside another section.

### 5.1 Hardware platform & core system
| Section | Valid | Purpose |
|---|---|---|
| `hardware:` | M | Default `platform:` (default `virtual`) and `driverboards:`. Can also set a platform per device class (`coils`, `switches`, `lights`, `dmd`, `rgb_dmd`, `segment_displays`, `servo_controllers`, `stepper_controllers`, `i2c`, `accelerometers`, `hardware_sound_system`) |
| `mpf:` | M | Global MPF internals: `default_pulse_ms` (10), `default_platform_hz` (100), `default_light_hw_update_hz` (50), switch event name patterns (`%_active`, `%_inactive`, `sw_%`), `allow_invalid_config_sections`, `save_machine_vars_to_disk`, `report_crashes`, module/plugin lists |
| `machine:` | M | `balls_installed`, `min_balls` (to start a game), `soft_shutdown_exit_command` (new in 0.81) |
| `psus:` | M | Power supply units for coil power management (`release_wait_ms`, `voltage`, `max_amps` (unused)) |
| `config:` | M/m | Include more config files (see §1) |
| `custom_code:` | M | Register custom Python code classes (replaces `scriptlets:`) |
| `plugins:` | M | Plugin classes to load (default: info_lights, switch_player, auditor) |
| `logging:` | M | Per-module console/file log levels |
| `data_manager:` | M | `use_fsync` for saved data files (auto by OS) |
| `bcp:` | M | BCP connections to media controllers (`connections:` → `bcp_connection`) and listening `servers:` → `bcp_server`. Defaults are in `mpfconfig.yaml` |
| `bcp_connection:` / `bcp_server:` | sub | `type` (class), `host`/`ip`, `port` (5050), `required`, `exit_on_close` |
| `text_ui:` | M | Which player/machine vars the console Text UI shows |
| `virtual_platform_start_active_switches:` | M | Switches that start active on the virtual/smart_virtual platform (e.g. balls in the trough) |
| `smart_virtual:` | M | Smart virtual platform options (simulate manual plunger) |
| `hardware_benchmark:` | M | Stub: coil1/coil2/flipper/switch1/switch2 for a benchmark |
| `vpe:` | M | Stub: Visual Pinball Engine bridge `listen_port` (50051) |

### 5.2 Switches, coils & drivers
| Section | Valid | Purpose |
|---|---|---|
| `switches:` | M | Map switch names to inputs: `number`, `type: NC/NO`, `debounce`, `tags`, events |
| `switch_overwrites:` | sub | Per-device `debounce` override (flippers/autofire) |
| `coils:` | M | Map coil/driver names to outputs: pulse/hold power, safety limits |
| `coil_overwrites:` | sub | Per-device override of `pulse_ms`, `pulse_power`, `hold_power`, `recycle` |
| `dual_wound_coils:` | M | Make a logical coil from main + hold windings (+EOS). Not for flippers |
| `digital_outputs:` | M | Plain on/off outputs mapped to a light or driver output (used by motors, SPI bit bang) |
| `autofire_coils:` | M | Hardware rule: switch → pulse coil (slings, pops) |
| `kickbacks:` | M | Autofire variant for outlane kickbacks (same settings) |
| `flippers:` | M | Flipper hardware rules (main/hold coil, EOS) |
| `combo_switches:` | M/m | Two-switch combos (flipper cancel, super skill shot). Posts `_both`/`_one`/`_inactive` events |
| `timed_switches:` | M/m | Events when a switch is held (or released) for a time. `flipper_cradle` is built in |

### 5.3 Lights & displays
| Section | Valid | Purpose |
|---|---|---|
| `lights:` | M | All lights (LEDs, matrix bulbs, GI, flashers-as-lights): `number` or `channels`/`start_channel`/`previous`, `type`, `subtype`, `default_on_color`, `x/y` |
| `light_settings:` | M | `default_fade_ms`, colour correction profiles |
| `color_correction_profile:` | sub | `gamma` (2.5), `whitepoint`, `linear_slope`, `linear_cutoff` |
| `named_colors:` | M | Your own colour names (RGB list or hex, can include `%brightness`) |
| `light_stripes:` / `light_rings:` | M | Auto-generate `count` lights from a `light_template` (x/y geometry for display_light_player). Stripe lights are named `(stripe)_light_(n)`, 0-based |
| `blinkenlights:` | M | A light that several modes add colours to; cycles through them (`color_duration` or `cycle_duration`, `off_when_multiple`, `priority`) |
| `info_lights:` | M | EM/old-SS status lights (ball in play, player up, match, tilt, game over) |
| `displays:` | M | Logical displays (targets for slides): `width`, `height`, `default`. **⚠** MPF-MC-era page, see §8 |
| `dmds:` | M | Physical mono DMD (brightness, fps, gamma 1.0, shades, source_display) |
| `rgb_dmds:` | M | Physical RGB DMD (hardware_brightness, gamma 2.2, channel_order, source_display) |
| `segment_displays:` | M | Alphanumeric/7-seg displays: `number`, `size`, `update_method`, commas/dots, `default_color` |
| `light_segment_displays:` / `_device` | sub | `platform_settings` for segment displays built from lights (segment-to-light mapping, `type: 7segment/bcd/14segment/16segment`) |
| `neoseg_displays:` | M | Cobra "NeoSeg" serial segment displays (`size`, `start_channel`, `light_template`) |
| `score_reels:` / `score_reel_groups:` | M | EM score reels (coil, position switches, chimes, player tags) |
| `digital_score_reels:` | M | Stub (frames?, reel_count, start_value) |
| `score_queues:` | M | SS-style score queue with chime coils |

### 5.4 Ball handling & playfield devices
| Section | Valid | Purpose |
|---|---|---|
| `playfields:` | M | Playfield(s): `default_source_device`, tag `default`, ball search settings |
| `playfield_transfers:` | M | Move balls between multiple playfields |
| `ball_devices:` | M | Troughs, plungers, VUKs, saucers, locks: ball counting and eject logic |
| `ball_routings:` | m | Route balls from source devices to a target device (stub page) |
| `ball_holds:` | M/m | Hold balls temporarily (not for multiball, doesn't change balls-in-play) |
| `multiball_locks:` | m | Virtual per-player lock counting toward multiball |
| `multiballs:` | M/m | Start/add-a-ball multiball with shoot-again (ball save) |
| `ball_saves:` | M/m | Ball save timer/count |
| `diverters:` | M | Diverters that route balls automatically based on eject targets |
| `drop_targets:` / `drop_target_banks:` | M / M/m | Drop targets, banks, reset/knockdown coils, keep-up |
| `magnets:` | M | Grab/release/fling magnets |
| `spinners:` | M | Spinner hit accrual with active/inactive/idle events |
| `sequence_shots:` | M/m | Ordered switch/event sequences (orbits) posting `<name>_hit` |
| `servos:` / `servo_controllers:` | M | Servos (0.0–1.0 positions mapped to events) / PCA9685 I2C controllers |
| `steppers:` | M | Stepper motors (homing, named/relative positions) |
| `motors:` | M | Motor + position switches using digital outputs (Ghostbusters slimer, Batman claw) |
| `dc_motors:` | M | DC motors on FAST EXP-0051 (control events with power and duration) |
| `shakers:` | M | Shaker motor on FAST EXP-1313 |
| `accelerometers:` | M | P3-ROC / MMA8451 accelerometer tilt events |
| `speedometers:` | M/m | Stub (new 0.56.1): `start_switch`, `stop_switch` |

### 5.5 Game flow, modes & logic
| Section | Valid | Purpose |
|---|---|---|
| `game:` | M | `balls_per_game` (3), `max_players` (4), start/add-player tags or events, start conditions |
| `modes:` | M | List of modes that can load |
| `mode:` | m | The mode's own settings (start/stop events, priority, game_mode, and so on) |
| `mode_settings:` | m | Free-form settings for a specific mode (used by the built-in bonus mode) |
| `shots:` | m | Switch/event targets with profile-driven states and shows |
| `shot_groups:` | m | Groups of shots: rotation, completion events, group hit events |
| `shot_profiles:` | M/m | State lists (+shows) that shots step through |
| `shot_control_events:` | sub | Jump a shot to state N (`events`, `state`, `force`, `force_show`) |
| `accruals:` | M/m | Logic block: all steps in any order |
| `sequences:` | M/m | Logic block: steps in order |
| `counters:` | M/m | Logic block: count events to a target value |
| `counter_control_events:` | sub | `add`/`subtract`/`jump` a counter by `value` on an event |
| `logic_blocks_common:` | sub | Settings shared by all logic blocks |
| `logic_blocks:` | — | Old wrapper (pre-0.50). Now use `accruals:`/`counters:`/`sequences:` at top level |
| `state_machines:` (+`_states`, `_transitions`) | M/m | Finite state machines with shows per state |
| `timers:` / `timer_control_events:` | m / sub | Countdown/count-up timers with tick events |
| `achievements:` / `achievement_groups:` | m | Player-tracked mission states (enabled/selected/started/completed/...) and selectors |
| `extra_balls:` / `extra_ball_groups:` | m / M | Award/light extra balls with per-game/per-ball limits |
| `player_vars:` | M | Initial values/types for player variables |
| `machine_vars:` | M | Initial values/persistence/types for machine variables |
| `shows:` | M/m | Shows defined inline in config (can also be separate show files) |
| `show_pools:` | M/m | Pick one of several shows (`sequence`, `random`, `random_force_next`, `random_force_all`) |
| `show_config:` | sub | Show settings used inside devices (e.g. state machine `show_when_active`) |
| `assets:` | M/m | Per-folder default settings for asset types (images/sounds/videos/shows) |

### 5.6 Built-in modes / machine management
| Section | Valid | Purpose |
|---|---|---|
| `settings:` | M | Operator (service mode) settings, stored as machine vars |
| `credits:` | M | Coin/credit handling, pricing tiers, free play |
| `high_score:` | m | Built-in high score mode categories, defaults, extra vars |
| `tilt:` | m | Built-in tilt mode (warnings, slam tilt, settle time) |
| `bonus` (`mode_settings:` of bonus mode) | m | End-of-ball bonus entries and timings |
| `auditor:` | M | What is audited (switches, shots, events, player vars) to `audits/audits.yaml` |
| `switch_player:` | M | Plugin that replays scripted switch sequences for testing |

### 5.7 Platform-specific
| Section | Purpose |
|---|---|
| `fast:` (`net:`, `exp:`, `exp_int:`, `aud:`) + `fast:exp:board` | FAST Neuron/Nano/retro controllers. **Rewritten April 2026 for 0.57.5 / 0.80** (see §6.1). Old flat `ports:`/`baud:`/`hardware_led_fade_time:` form is kept as "Pre-2024" docs |
| `fast_coils:` / `fast_switches:` | FAST `platform_settings` for coils (`connection`, `recycle_ms`) and switches (`debounce_open`/`debounce_close`) |
| `opp:` / `opp_coils:` | Open Pinball Project serial boards (`ports`, `chains`, `poll_hz`, `incand_update_hz`) / coil `recycle_factor` |
| `p_roc:` / `pd_led_boards:` | Multimorphic P-ROC/P3-ROC (watchdog, DMD timing, lamp strobe) / PD-LED options (WS281x/LPD880x chains, servos, steppers) |
| `pkone:` | Penny K PKONE (`port`, `baud`, `watchdog`) |
| `spike:` / `spike_node:` | Stern SPIKE/SPIKE 2 bridge |
| `lisy:` | LISY/APC (network or serial) |
| `snux:` / `system11:` | System 11 A/C relay handling (with SNUX or APC) |
| `fadecandy:` / `open_pixel_control:` | FadeCandy/OPC LED controllers (hardware gamma/dithering) |
| `smartmatrix:`, `pin2dmd:`, `rpi_dmd:` | RGB DMD hardware |
| `mypinballs:` | MyPinballs segment display controller |
| `raspberry_pi:` | pigpio on a Raspberry Pi (`ip`, `port` 8888) |
| `pololu_maestro:`, `pololu_tic:`/`tic_stepper_settings:`, `trinamics_steprocker:`, `step_stick_stepper_settings:`, `spi_bit_bang:` | Servo, stepper and IO helpers |
| `osc:` | OSC platform (events to send, IPs/ports) |
| `hardware_sound_systems:` / `hardware_sound_player:` | External hardware sound boards (e.g. LISY) |
| `kivy_config:` | Raw Kivy config. MPF-MC only |
| `twitch_client:` | Twitch chat monitor. **Removed in MPF 0.58+ / 0.81+** |

### 5.8 Legacy MPF-MC (pre-0.80) media sections
These are listed under "Legacy Media Controller" in 0.80. GMC projects replace them with Godot scenes. See §8.

`animations`, `bitmap_fonts`, `image_pools`, `images`, `images_frame_skips`, `keyboard`, `mc_custom_code`, `mc_scriptlets`, `mpf-mc`, `playlist_player`, `playlists`, `slides`, `sound_ducking`, `sound_loop_player`, `sound_loop_sets`, `sound_marker`, `sound_pools`, `sound_system`, `sound_system_tracks`, `sounds`, `text_strings`, `track_player`, `video_pools`, `videos`, `virtual_segment_display_connector`, `widget_styles`, `widgets`, `window`.

### 5.9 Deprecated / removed
| Section | Status / replacement |
|---|---|
| `flashers:` | Removed 0.50. Use `coils:` + `coil_player`, or `lights:` (`platform: drivers`) + `flasher_player`/`light_player` |
| `gis:`, `leds:`, `matrix_lights:` | Merged into `lights:` in 0.50 (GI = `subtype: gi`) |
| `gi_player:`, `led_player:` (and `matrix_light_player`) | Removed 0.50. Use `light_player:` |
| `scriptlets:` / `mc_scriptlets:` | Deprecated since 0.50. Use `custom_code:` / `mc_custom_code:` |
| `ball_locks:` | Removed 0.54. Use `ball_holds:` / `multiball_locks:` |
| `logic_blocks:` wrapper | Pre-0.50 nesting. Use the logic-block sections directly |
| `twitch_client:` | Removed in 0.58/0.81 |
| `sound_system: master_volume:` | Deprecated. Use the machine var `master_volume` |

---

## 6. Deeper notes and example YAML for the key sections

### 6.1 `hardware:` and platform (FAST example)
```yaml
#config_version=6
hardware:
  platform: fast          # default platform for all devices (default: virtual)
  driverboards: fast      # fast | pdb | opp | wpc | wpc95 | wpcAlphaNumeric | sternSAM | sternWhitestar
  # per-class overrides are lists of platform names, e.g.
  # lights: fadecandy
fast:
  net:
    controller: neuron    # neuron | nano | sys11 | wpc89 | wpc95
    port: auto
    io_loop:              # max 9 boards; playfield interchange board not listed
      io_0804:
        model: FP-I/O-0804
        order: 1
      io_3208:
        model: FP-I/O-3208
        order: 2
    # watchdog: 500       # ms; ⚠ see §9
  exp:
    port: auto
    boards:
      neuron:
        model: FP-EXP-2000   # Neuron LED ports (on a Pi-direct Neuron use exp_int: instead)
      pf_leds:
        model: FP-EXP-0081
```
- `fast:net:` has `port`, `baud` (921600), `controller`, `io_loop`, `watchdog`, the default quick/normal debounce times (2 ms / 10 ms, from `mpfconfig.yaml`), `mute_unconfigured_switches` (0.57.4+), `gi_hz`/`lamp_hz` (30), and `soft_power_hold_ms`/`soft_power_powerdown_delay` (0.81+).
- `fast:exp:board` has `model`, `address` (the default depends on the model; solder jumpers let you use up to 4 boards of the same model), `led_fade_time` (≤ 8191 ms), `led_hz` (≤ 31.25), `ignore_led_errors`, `breakouts`, and `led_ports`. `led_ports` needs EXP firmware 0.48 and MPF 0.58.0.dev1/0.81.0.dev1: per-port `count` (128 total per group of 4 ports), `type: sk6812|mixed`, `rgbw_numbers`.
- Supported EXP models: 2000, 1313, 0051, 0061, 0071, 0081, 0091.
- `fast:aud:` covers the FAST audio board (amps, volume steps, headphones). See the FAST website for the full list.
- The FAST website (fastpinball.com/mpf/config/) is linked as the authoritative source.
- Other platforms follow the same pattern: `opp: {ports: COM7}` with `driverboards: gen2`, `pkone: {port: com3}`, `p_roc:`, `spike:`, and so on.

### 6.2 `switches:`
```yaml
switches:
  s_start:
    number: "0-0"         # format depends on platform; quote leading-zero/dash values
    tags: start
  s_flipper_left:
    number: 1
    tags: left_flipper
  s_trough1:
    number: 10
    type: NC              # optos: inverts so "active" still means ball present
  s_left_sling:
    number: 20
    debounce: auto        # auto | quick | normal
  s_orbit_left:
    number: 30
    tags: playfield_active
  s_shooter:
    number: 40
    events_when_activated: ball_in_shooter
```
- Every switch posts `<name>_active` and `<name>_inactive`, plus `sw_<tag>` for each tag. These only show in the monitor if something handles them or `debug: true` is set.
- `debounce: auto` uses `quick` when a hardware rule uses the switch, otherwise `normal`.
- `ignore_window_ms` sets a minimum time between activations.
- `ignore_during_ball_search` means hits don't reset ball search. Use with caution.
- `x/y/z` are unused.

**Reserved switch tags:**

| Tag | Used by |
|---|---|
| `playfield_active` (or `<playfield>_active`) | Tells the playfield a ball is loose, and resets ball search. **Don't** put it on switches of devices that already manage this (slings, VUKs, drops). Doing so gives error `CFE-ball_device-13` |
| `start` | Game start. The game starts on **release**, so hold time can be measured. In 0.80 the high score mode also uses it to select or submit |
| `left_flipper`, `right_flipper` | `flipper_cradle` and `flipper_cancel` events. In 0.80 the high score text input (GMC `MPFTextInput`) and service mode also use them |
| `tilt_warning`, `slam_tilt`, `tilt` | Tilt mode |
| `service_esc`, `service_up`, `service_down`, `service_enter`, `service_door_open` / `service_door_closed` | Service mode |
| `no_audit`, `no_audit_free` | Excluded from switch audits (always / only in free play) |

### 6.3 `coils:`
```yaml
coils:
  c_flipper_left_main:
    number: 0
    default_pulse_ms: 30ms
    max_pulse_ms: 100ms
    default_pulse_power: 0.7
  c_flipper_left_hold:
    number: 1
    default_hold_power: 0.25    # 0-1; implies enable is allowed
  c_trough_eject:
    number: 2
    default_pulse_ms: 20ms
  c_diverter:
    number: 3
    allow_enable: true          # needed to hold at 100% without a hold power
```
- `default_pulse_ms` defaults to 10 ms ("extremely weak, set low for safety"). The global default is `mpf: default_pulse_ms: 10`.
- **`allow_enable: true` is required** to enable (hold) a coil at full power. Setting `default_hold_power` (or `max_hold_power`) also allows enabling at that power.
- `max_pulse_ms` makes over-length pulses raise an error.
- `default_recycle` adds a re-fire delay against machine-gunning.
- `psu:` (default `default`) plus `*_max_wait_ms` on devices let MPF stagger pulses for power management.
- Device control events: `pulse_events`, `enable_events`, `disable_events`.
- `default_timed_enable_ms`, `max_hold_duration` and `pulse_with_timed_enable` are listed without explanation.

### 6.4 `lights:` (+ `light_settings`, `named_colors`)
```yaml
light_settings:
  default_fade_ms: 40            # Stern uses ~40ms on modern LED machines
named_colors:
  troll_green: 4a9b22
lights:
  l_shoot_again:
    number: neuron-1-0           # platform-specific
    type: rgb                    # channel order, default rgb (r,g,b,w,+,-)
    tags: inserts
    default_on_color: troll_green
  l_led_chain_1:
    previous: l_shoot_again      # chain; MPF computes the number
    type: grb
  l_gi_1:
    number: G01
    subtype: gi                  # led | matrix | gi, platform dependent
  l_flasher_on_driver:
    number: c_flasher            # a coil name
    platform: drivers            # light backed by a driver
```
- Use **either** `number` **or** `channels` (explicit per-colour numbers), not both. `start_channel` + `type` is another option.
- Chains built with `previous:` let service mode drop broken LEDs and renumber the rest.
- `x`/`y` place lights for `display_light_player`.
- `color_correction_profile` can be set per light.
- **⚠** The docs say "`rgb` for WS2812 and `grb` for WS2811". The neoseg page calls GRB "WS2812 native" ordering (see §9).

### 6.5 `playfields:`
```yaml
playfields:
  playfield:
    default_source_device: bd_plunger   # device that ejects balls onto it (launcher, or trough if none)
    tags: default                       # exactly one playfield must be "default"
    enable_ball_search: true            # off by default; turn on for production
```
- Ball search defaults: `ball_search_timeout` 15 s, `ball_search_interval` 150 ms, phases 1/2/3 repeat 3/3/4 times, `ball_search_wait_after_iteration` 5 s.
- `ball_search_failed_action` is `new_ball` (default) or `end_game`.
- Ball search is blocked on `flipper_cradle` and unblocked on `flipper_cradle_release`.
- The global default is `mpf: default_ball_search: false`.

### 6.6 `ball_devices:`
```yaml
ball_devices:
  bd_trough:
    ball_switches: s_trough1, s_trough2, s_trough3, s_trough4
    eject_coil: c_trough_eject
    eject_targets: bd_plunger
    jam_switch: s_trough_jam
    tags: trough, home, drain
  bd_plunger:
    ball_switches: s_plunger
    eject_coil: c_plunger        # omit for a manual plunger
    mechanical_eject: true       # player can plunge manually
    eject_targets: playfield
  bd_scoop:
    ball_switches: s_scoop
    eject_coil: c_scoop
    eject_timeouts: 3s
```
- One ball switch per ball is assumed. Use `ball_capacity` if the device holds more balls than it has switches.
- NC optos must be `type: NC` in `switches:`.
- Without ball switches, the device counts balls from `entrance_switch` activations.
- **`eject_targets`** lists every device (or `playfield`) this device can eject to *directly*. The first entry is the default target. Diverters use it for automatic routing.
- `eject_timeouts` pairs with `eject_targets` (default 10 s). `ball_missing_timeouts` defaults to 20 s.
- `confirm_eject_type`: `target` (default), `switch`, `event`, or `fake`.
- Retry options: `max_eject_attempts` (0 = forever), `eject_coil_retry_pulse`, `retries_before_increasing_pulse`, `eject_coil_jam_pulse`, `eject_coil_reorder_pulse`.
- Other settings: `hold_coil` and friends for post-style locks, `entrance_count_delay` (500 ms), `auto_fire_on_unexpected_ball` (true), `ejector:` class (`PulseCoilEjector`, `EnableCoilEjector`, `HoldCoilEjector`, `EventEjector`).
- Control events: `eject_events`, `eject_all_events`, `request_ball_events`, `hold_events`, `entrance_events`.
- **Tags:**
  - `home`: balls here are "home", so a game can start. Balls elsewhere are ejected at boot.
  - `drain`: a ball entering means it drained.
  - `trough`: holds balls that aren't in play.
  - `no-eject-on-ballsearch`
- `ball_add_live` is discontinued. Use the playfield's `default_source_device`.
- Many types are listed as "Unknown type" in the reference because it was auto-generated.

### 6.7 `flippers:`
```yaml
flippers:
  left_flipper:
    main_coil: c_flipper_left_main
    hold_coil: c_flipper_left_hold     # omit for single-wound (set hold power on the main coil)
    activation_switch: s_flipper_left
    eos_switch: s_flipper_left_eos     # optional
    use_eos: false
    # enable_events default: ball_started
    # disable_events default: ball_will_end, service_mode_entered
```
- Only for modern controlled flippers. Pre-WPC flipper relays are configured differently (not in this section).
- `main_coil_overwrite` and `hold_coil_overwrite` take `coil_overwrites`. `switch_overwrite` changes debounce.
- `power_setting_name: flipper_power` ties power to an operator setting. `flipper_power` exists by default.
- `repulse_on_eos_open` with `eos_active_ms_before_repulse` (500 ms).
- `sw_flip_events` / `sw_release_events` are software flips and have latency.
- `include_in_ball_search: false` by default. Turn it on for upper flippers.

### 6.8 `autofire_coils:` (and `kickbacks:`)
```yaml
autofire_coils:
  left_sling:
    coil: c_left_sling
    switch: s_left_sling
    coil_overwrite:
      pulse_ms: 20ms
    timeout_watch_time: 1s      # anti machine-gun: >max_hits in watch window
    timeout_max_hits: 5         #   => disable rule for disable_time
    timeout_disable_time: 500ms
kickbacks:
  left_kickback:
    coil: c_kickback
    switch: s_left_outlane
    enable_events: kickback_lit   # kickbacks are autofires, same settings
```
- One switch to one coil. For two sling switches, wire them in parallel onto one input.
- Enable is `ball_started` and disable is `ball_will_end, service_mode_entered` by default.
- `reverse_switch` fires on release (e.g. optos). **⚠** Its description is self-contradictory, see §9.
- `coil_pulse_delay` isn't supported on all platforms.
- `ball_search_order` defaults to 100 (0 excludes the device).

### 6.9 `game:`, `machine:`, `modes:` and `mode:`
```yaml
# machine config
machine:
  balls_installed: 4
  min_balls: 3
game:
  balls_per_game: 3                     # int or template (e.g. settings.balls_per_game)
  max_players: 4
  start_game_switch_tag: start          # default
  add_player_switch_tag: start          # default
modes:
  - base
  - skillshot
  - bonus
```
- `game:` also has `start_game_event`/`add_player_event`, `end_ball_event` (`end_ball`), `end_game_event` (`end_game`), `allow_start_with_loose_balls`, `allow_start_with_ball_in_drain`, and `wait_for_empty_playfields_on_ball_start` (true).

```yaml
#config_version=6
# modes/<name> config, e.g. skillshot.yaml
mode:
  start_events: ball_starting
  stop_events: timer_mode_timer_complete, shot_right_ramp_hit
  priority: 300
  # game_mode: true            # false => may run outside a game (attract); no player access
  # stop_on_ball_end: true
  # restart_on_next_ball: false
  # use_wait_queue: false      # hold game flow (only if started by a queue event like ball_ending)
  # start_priority / stop_priority: fine-tune ordering on shared events
  # events_when_started / events_when_stopped
  # code: file.ClassName       # optional custom Python mode class
```
- **Priority** (default 100) sets the order for blockable events, and it's the base priority for everything the mode plays. It can't be changed while the mode runs. Best practice is 100-point spacing, **between 100 and 1,000,000**, because MPF's built-in modes run below and above that range.
- When stopped, a mode unloads everything it configured.
- `stop_on_ball_end: false` **needs `game_mode: false`**. Add `game_ending` to `stop_events`, or MPF asserts "Mode X is not supposed to run outside of game".
- `restart_on_next_ball` tracks modes in the player var `restart_modes_on_next_ball`.
- The `mode_settings:` section is free-form (used by bonus).

### 6.10 `ball_saves:`
```yaml
ball_saves:
  default:
    active_time: 10s          # 0/omitted = unlimited; includes hurry_up_time, excludes grace
    hurry_up_time: 2s         # posts ball_save_(name)_hurry_up
    grace_period: 2s          # hidden extra time
    enable_events: mode_base_started
    timer_start_events: balldevice_bd_plunger_ball_eject_success
    auto_launch: true
    balls_to_save: 1          # -1 unlimited
    # early_ball_save_events: s_left_outlane_active
    # only_last_ball, eject_delay, delayed_eject_events, ball_locks, source_playfield
```
- Enabling starts the timer unless `timer_start_events` is set.
- Default `disable_events` are `ball_will_end, service_mode_entered`.
- **The timer is not reset per drain.** Total time counts from the first start, even with `balls_to_save: 3`.

### 6.11 `shots:`, `shot_profiles:`, `shot_groups:`
```yaml
shot_profiles:              # machine or mode
  lit_flash:
    states:
      - name: unlit
        show: "off"
      - name: lit
        show: flash
        show_tokens: {color: red}
    loop: false              # true => wrap last→first (toggle shots)
    advance_on_hit: true
    block: false             # ⚠ doc says default false, then says "default is true"
shots:                       # mode config
  lane_l:
    switch: s_lane_l         # or switches:, or hit_events:
    profile: lit_flash       # default profile: "default" (unlit→lit, "off"/"on" shows)
    show_tokens:
      leds: l_lane_l
  lane_r:
    switch: s_lane_r
    profile: lit_flash
    show_tokens:
      leds: l_lane_r
shot_groups:
  lanes:
    shots: lane_l, lane_r
    rotate_left_events: sw_left_flipper
    rotate_right_events: sw_right_flipper
    reset_events: lanes_lit_flash_lit_complete
```
- **Shots:**
  - Each shot tracks one profile per mode. The highest-priority mode's profile drives the show.
  - State is stored in the player var `(shot)_(profile)` unless `player_variable:` is set.
  - `persist_enable` is true by default.
  - `advance_events` moves the state without posting hit events.
  - `control_events` jump to state N (0-based).
  - `delay_switch` blocks hits for a time after another switch.
  - If any `enable_events` are set, the shot starts disabled. Otherwise it starts enabled. `start_enabled` overrides this.
- **Events:** hitting `left_lane` (profile `skill`, state `lit`) in group `lanes` posts `lanes_skill_lit_hit`, `lanes_skill_hit`, `lanes_hit`, `left_lane_skill_lit_hit`, `left_lane_skill_hit` and `left_lane_hit`. When all group shots share a state, it posts `(group)_(profile)_(state)_complete`.
- **Profile options:**
  - `block: false` lets a hit also advance the same shot in lower modes (e.g. skill shot plus base lanes).
  - `show_when_disabled`, `rotation_pattern` (e.g. `L, L, R, R`), `state_names_to_not_rotate`.
  - Per-state `show`, `show_tokens`, `speed`, `loops` (-1), `priority`, `sync_ms`, `manual_advance`, `start_step`.
- **Shot groups:** `enable/disable/reset/restart/rotate*/enable_rotation/disable_rotation_events`. A group has no enabled state of its own except for rotation. Disabled shots still rotate.

### 6.12 Logic blocks: `counters:`, `accruals:`, `sequences:`, `state_machines:`
```yaml
counters:
  ramp_count:
    count_events: shot_ramp_hit
    count_complete_value: 5         # int or template
    # starting_count: 0, count_interval: 1, direction: up|down, multiple_hit_window: 0
    control_events:
      - event: add_five
        action: add                 # add | subtract | jump
        value: 5
    events_when_complete: ramps_done   # default logicblock_ramp_count_complete
    disable_on_complete: false      # default true!
    reset_on_complete: true
    persist_state: true             # keep across balls in (name)_state player var
accruals:
  lanes_done:
    events:                         # every step in any order; comma = OR within a step
      - lane_l_hit
      - lane_r_hit
sequences:
  combo:
    events:                         # steps in exact order
      - shot_a_hit
      - shot_b_hit, shot_c_hit
```
- **Common logic-block settings (`logic_blocks_common`):**
  - `enable_events`, `disable_events`, `reset_events`, `restart_events`
  - `events_when_complete` (default `logicblock_(name)_complete`) and `events_when_hit` (default `logicblock_(name)_hit`)
  - `disable_on_complete` (true), `reset_on_complete` (true), `persist_state` (false), `start_enabled`
  - With no `enable_events`, a logic block auto-enables when the player's ball starts.
- **Counters no longer store their value in player vars.** To get a player var back, add `variable_player: logicblock_X_updated: {X_count: {int: value, action: set}}`.
- Accruals have `advance_random_events`.
- **State machines** have `states:` (the first must be `start`, or set `starting_state`), per-state `events_when_started`/`events_when_stopped`/`show_when_active`, and `transitions:` (`source`, `target`, `events`, `events_when_transitioning`). In a machine config the state persists across games. In a mode config it's per player and resets each game.

### 6.13 `timers:`
```yaml
timers:
  hurry_up:
    start_value: 15
    end_value: 0
    direction: down
    tick_interval: 1s           # time string or template (template must evaluate to float SECONDS)
    start_running: false
    restart_on_complete: false
    control_events:
      - event: mode_hurry_started
        action: start
      - event: hurry_bonus_hit
        action: add
        value: 5
```
- Actions: `add`, `subtract`, `jump`, `start`, `stop`, `reset`, `restart`, `pause` (value in real seconds; 0 = pause indefinitely), `set_tick_interval`, `change_tick_interval` (multiplier), `reset_tick_interval`.
- Events: `timer_(name)_tick`, `_complete`, `_started`, `_stopped`, `_paused`, `_time_added`, `_time_subtracted`.
- `max_value` caps the value. `bcp: true` sends timer events to the media controller.
- The tick value is stored in the player var `(mode)_(timer)_tick`.

### 6.14 Multiball: `multiball_locks:`, `multiballs:`, `ball_holds:`
```yaml
multiball_locks:            # mode config
  bunker:
    lock_devices: bd_bunker
    balls_to_lock: 3
    # balls_to_replace: -1 (always replace), locked_ball_counting_strategy: virtual_only
multiballs:
  main_mb:
    ball_count: 3            # int or template
    ball_count_type: total   # total | add
    shoot_again: 20s         # multiball ball-save (default 10s)
    start_events: multiball_lock_bunker_full
    ball_locks: bd_bunker    # eject from these first
    # add_a_ball_events, add_a_ball_shoot_again (5s), start_or_add_a_ball_events,
    # hurry_up_time, grace_period, replace_balls_in_play, restart_grace_period (0.57.5+)
ball_holds:
  scoop_hold:
    hold_devices: bd_scoop
    balls_to_hold: 1
    release_one_events: intro_show_done
```
- Locks post `multiball_lock_(name)_locked_ball` (arg `total_balls_locked`) and `multiball_lock_(name)_full`.
- Lock counts are virtual and per player. If another player emptied the lock, the multiball adds balls from the trough instead.
- Ball replacement uses queue events, so it can be paused with `queue_relay_player`.
- Multiballs with no `enable_events` auto-enable when their mode starts.
- `ball_holds` are for temporary holds (intro shows, video modes). They don't affect balls-in-play.

### 6.15 `variable_player:` (scoring)
```yaml
variable_player:              # mode config for player vars
  shot_target_hit:
    score: 1000                     # add
  shot_ramp_hit:
    score: 10000
    ramps: 1
  ramp_timeout:
    ramps:
      int: 0
      action: set
  super_ramp_hit:
    score:
      int: 25000 * current_player.ramps
      block: true                   # stop lower-priority modes scoring this event
  sw_jets:
    score: 500|block                # shorthand
  treasure_found:
    treasure_name:
      string: RUBY
  give_p2_points:
    score:
      int: 1000
      player: 2                     # doc example: event "add_score_to_player_2"
  machine_event:
    my_machine_counter:
      int: 1
      action: add_machine           # REQUIRED for machine vars (add_machine | set_machine)
```
- **Player-var entries only work in mode configs.** Machine-var entries (with `action: add_machine`/`set_machine`) also work in the machine config.
- `int:` wins over `float:` if both are present. `string:` is `template_str`.
- A player var that doesn't exist yet is created on first use.
- The default action is `add`.

### 6.16 `event_player:`, `random_event_player:`, `queue_event_player:`, `queue_relay_player:`
```yaml
event_player:
  ball_starting:
    - cmd_flippers_enable
    - cmd_drop_targets_reset
  mode_shoot_here_started: cmd_upper_target_reset
  start_mode_battle{device.achievements.ironthrone.state=="completed"}: start_mode_victory_lap
  mode_dynamo_started:
    set_dynamo_round:
      round_number: {value: device.counters.dynamo_rounds.value, type: int}
    reset_tokens:
      priority: 50                  # post order
random_event_player:
  mystery_award:
    events:                         # list = equal odds; dict = weights; conditions allowed
      award_points: 50
      award_eb{current_player.eb_count < 1}: 5
    fallback_event: award_points    # if all conditional entries false
    # force_different: true, force_all: true, scope: player|machine, disable_random
queue_event_player:
  some_event:
    queue_event: my_queue
    events_when_finished: my_queue_done
queue_relay_player:
  game_ending:                      # must be a QUEUE event
    post: start_my_end_mode
    wait_for: my_end_mode_done      # if never posted, MPF waits forever
```

### 6.17 `show_player:`
```yaml
show_player:
  mode_base_started: attract_lights       # express = play
  shot_ramp_hit:
    ramp_flash:
      loops: 0                            # -1 forever (default); 0 = play once
      speed: 2                            # template allowed (0.56.1+)
      priority: 10                        # added to mode priority
      sync_ms: 500
      show_tokens:
        leds: l_ramp_arrow
      key: ramp_flash_1                   # to run multiple instances / stop one
  stop_ramp_flash:
    ramp_flash_1: stop
  mode_my_mode_stopping:
    outro_show:
      block_queue: true                   # hold the queue event until the show ends
```
- Actions: `play` (default), `stop` (undoes everything the show did), `pause`, `resume`, `advance`, `step_back`, `update` (not implemented), `queue`.
- Other settings: `manual_advance`, `start_running` (false = play the first step, then pause), `start_step`, and `events_when_played/stopped/completed/looped/paused/resumed/advanced/stepped_back/updated`.
- A show's key defaults to its name. Keys are scoped per show_player, so modes don't collide.
- **Never combine `block_queue` with `loops: -1` or a final `duration: -1`.** The machine hangs.
- A one-step show forces `loops: 0`.
- `show_queue:` is marked "Is this still a thing? Need to confirm, June 2023".

### 6.18 `light_player:` (and show `lights:`)
```yaml
light_player:
  some_event:
    l_led1:
      color: red
      fade: 200ms
      priority: 10
    l_led2: off
    inserts: 0000ff          # tag
  all_on:
    "*": on                  # every light (not a glob)
shows:
  stoplight:
    - duration: 1s
      lights:
        (leds): green-f200ms # short fade syntax color-f<time>
    - duration: 1s
      lights:
        (leds): red
```
- If a light is named directly and also matched by a tag under the same event, whichever is set last wins.
- Use `stop` to release a light back to lower priorities, e.g. a "lightning flash" show.

### 6.19 Other config players (brief)
- **`coil_player:`**: `action: pulse|on|enable|off|disable`, plus `pulse_ms`, `pulse_power`, `hold_power`, `max_wait_ms`. Show section `coils:`.
- **`flasher_player:`**: `ms` (100 ms) and `color` (`on`). Show section `flashers:`.
- **`blinkenlight_player:`**: `action: add|remove|remove_mode|remove_all`, `color`, `key`. Colours a mode added are removed when the mode ends and **not** restored when it restarts.
- **`segment_display_player:`**:
  - Actions: `add`, `remove`, `flash`, `no_flash`, `flash_match`, `flash_mask`, `set_color`.
  - Settings: `text` (text templates), `priority`, `key`, `expire`, `flashing`, `flash_mask` (`FFFF____`), `color`.
  - Transitions: `transition` / `transition_out` of type `push`, `cover`, `uncover`, `split` or `wipe`, with `direction` and extra `text`.
- **`display_light_player:`**: maps a display's content onto lights with `x`/`y`. `lights: "*"` or a tag, `action: play|stop`, `bcp_connection` (`local_display`).
- **`score_queue_player:`**: mode-only. `score: 2000` (setting named `int`) feeds a `score_queues:` chime queue.
- **`hardware_sound_player:`**: `action: play|play_file|text_to_speech|set_volume|increase_volume|decrease_volume|stop`, plus `track`, `value`, `sound_system`.
- **`slide_player:` / `widget_player:` / `sound_player:`**: still used with GMC (see §8).

### 6.20 `settings:` (operator/service settings)
```yaml
settings:
  replay_score:
    label: Replay Score
    values:                 # value: label  (value stored in a machine var)
      500000: "500000 (default)"
      1000000: "1000000"
    default: 500000         # must be one of values
    key_type: int           # str (default) | float | int | bool (0.58/0.81; use True/False)
    sort: 100
    # machine_var: other_name    (default: setting name)
```
- Settings are read with `settings.<name>` in templates, e.g. `tilt: warnings_to_tilt: settings.warnings_to_tilt` or a timer's `tick_interval`.
- Use `key_type: int` or `float` if you want to do maths with the value.
- The built-in `flipper_power` setting exists.

### 6.21 `player_vars:` / `machine_vars:` (declaring defaults)
```yaml
player_vars:                 # machine config: initial value for every new player
  ramps:
    initial_value: 0
  album_name:
    initial_value: NONE
    value_type: str          # int (default!) | float | str; no auto-detection
machine_vars:
  master_volume:
    initial_value: 0.8
    value_type: float
    persist: true            # default true: saved to data/machine_vars.yaml
```

### 6.22 `high_score:` (built-in mode, mode config)
```yaml
#config_version=6
high_score:
  _overwrite: true
  categories:                # ordered: category -> list of award labels
    score:
      - GRAND CHAMPION
      - HIGH SCORE 1
      - HIGH SCORE 2
    loops:
      - LOOP CHAMP
  defaults:
    score:
      - BRI: 4242
      - GHK: 2323
      - JK: 1337
    loops:
      - JK: 42
  vars:                      # 0.56.1+: extra values saved with each entry
    loops:
      - player: number
      - machine: credits_string
  # reverse_sort: [fastest_time], enter_initials_timeout: 20s,
  # award_slide_display_time: 4s (set 0 if no award slide), reset_high_scores_events
```
**⚠** The official example still uses `#config_version=5` and `categories: !!omap` with `- score:` list items. The block above is the v6 form, as described in `config_v6.md`. In 0.80, initials are entered through GMC's `MPFTextInput` using the `left_flipper`, `right_flipper` and `start` tags.

### 6.23 `tilt:` (built-in mode)
```yaml
tilt:
  warnings_to_tilt: 3              # int or template
  multiple_hit_window: 300ms
  settle_time: 5s                  # wait before next ball can start
  reset_warnings_events: ball_will_end
  # tilt_warning_switch_tag: tilt_warning, tilt_switch_tag: tilt, slam_tilt_switch_tag: slam_tilt
  # tilt_events / tilt_warning_events / tilt_slam_tilt_events, tilt_warnings_player_var: tilt_warnings
```

### 6.24 `credits:` (built-in mode)
```yaml
credits:
  free_play: false                 # default yes
  max_credits: 12
  service_credits_switch: s_esc
  switches:
    - switch: s_left_coin
      type: money
      value: .25
  pricing_tiers:                   # first tier = regular price; 1 credit per game/player always
    - price: .50
      credits: 1
    - price: 2
      credits: 5
  events:
    - event: replay
      type: replay
      credits: 1
  credit_expiration_time: 2h
  fractional_credit_expiration_time: 15m
  persist_credits_while_off_time: 1h
  free_play_string: FREE PLAY
  credits_string: CREDITS
```
- The price is changed through the money-to-credits ratio, not credits per game.
- The pricing tier discount resets when ball 2 starts.

### 6.25 Bonus mode (`mode_settings:` in the bonus mode)
```yaml
mode_settings:
  display_delay_ms: 2s
  hurry_up_delay_ms: 500ms          # 0 = jump to last
  hurry_up_event: flipper_cancel
  # end_bonus_event, keep_multiplier: false
  bonus_entries:
    - event: alien_bonus            # show a slide on this event
      score: 25000
      player_score_entry: aliens    # multiplied by this player var
      # reset_player_score_entry, skip_if_zero (true), skip_if_negative
    - event: quarter_bonus
      score: current_player.quarters * current_player.album_value
```

### 6.26 Other mechanisms (short)
- **`diverters:`**:
  - `activation_coil`, `deactivation_coil`, `type: hold|pulse` (hold needs hold power or `allow_enable`), `activation_time`.
  - `activation_switches` install a hardware rule once the diverter is enabled.
  - `targets_when_active` / `targets_when_inactive` and `feeder_devices` drive automatic routing.
  - Enabling is not the same as activating.
- **`drop_targets:` / `drop_target_banks:`**:
  - Switch active means the target is down.
  - Put the reset coil on the **bank**, not on each target, or it pulses once per target.
  - `reset_on_complete: 500ms` on banks. `enable_keep_up_events` holds the reset coil.
  - Use shots for drop-target lights.
- **`magnets:`**: `grab_switch`, `grab_time` (1.5 s), `release_time` (500 ms), `fling_*`. Activation times over 255 ms at 100 % power need `allow_enable`.
- **`servos:`**: `positions: {0.1: servo_down}`, `servo_min`/`servo_max`, `reset_position` (0.5), and reset events including `ball_starting` by default.
- **`steppers:`**: `homing_mode: hardware|switch`, `named_positions`, `relative_positions`, `pos_min`/`pos_max`.
- **`segment_displays:`**:
  - `number`, `size` (7), `update_method`, `integrated_commas`/`integrated_dots`, `use_dots_for_commas`, `default_color` (per digit), `default_transition_update_hz` (30).
  - **`update_method` defaults to `stack`**. That creates variable subscriptions, which can bloat memory. The docs say `replace` will become the default, and "if unsure, use `replace`".
- **`combo_switches:`**: `switches_1`/`tag_1`, `switches_2`/`tag_2`, `hold_time`, `max_offset_time` (-1 = unlimited), `release_time`, and `events_when_both`/`one`/`inactive`/`switches_1`/`switches_2`.
- **`timed_switches:`**: `switches` or `switch_tags`, `time`, `state: active|inactive`, `events_when_active`/`events_when_released`.
- **`achievements:`**:
  - States: disabled, enabled, selected, started, stopped, completed.
  - Control events: `enable_events`, `start_events`, `complete_events`, `select_events`, and so on. `complete_events` only works from `started`.
  - `show_when_<state>` with `show_tokens`. `restart_on_next_ball_when_started`, `enable_on_next_ball_when_enabled` (true), `restart_after_stop_possible` (true).
  - Default events: `achievement_(name)_state_(state)`.
  - Groups: `rotate_left_events`/`rotate_right_events`, `select_random_achievement_events`, `start_selected_events`, `auto_select`, `events_when_all_completed`.
- **`extra_balls:`**: `award_events`, `light_events`, `max_per_game` (1), `group`. Tracked in the player var `extra_balls_awarded` / `extra_ball_(name)_awarded`.
- **`auditor:`**: `audit: [shots, switches, events, player]`, `events`, `player` vars, `num_player_top_records`, `save_events` (`ball_ended`).

---

## 7. Player, machine and game variables

### 7.1 Player variables
- Player variables are per-player values such as score, ball, and anything you create. You can create them on the fly, usually with `variable_player`. Set typed defaults in `player_vars:`.
- A change posts `player_(var_name)`, which is usable with conditions like `player_album_value{value==2}`.
- Read them with `current_player.X` or `players[i].X`.
- Most machines end up with far more custom player vars than built-in ones.

**Built-in player variables** (`player_vars/`):

| Var | Meaning |
|---|---|
| `score` | The player's score |
| `ball` | Current ball number. It doesn't change when an extra ball is played |
| `number` | Player number, 1-based |
| `index` | Player index, 0-based (use `number` for display) |
| `extra_balls` | Extra balls remaining, awarded after the current ball drains |
| `extra_ball_(name)_awarded` | Times this extra ball was awarded this game (0/1 by default) |
| `(logic_block)_state` | Dict with a logic block's state (enabled/complete) when `persist_state` is used |
| `(mode)_(timer)_tick` | Current tick of a mode timer, e.g. `mode1_my_timer_tick` |
| `random_(x).(y)` | Internal state for random pickers |
| `restart_modes_on_next_ball` | Internal list of modes to restart (mode.md calls it `_restart_modes_on_next_ball`) |

Other player vars mentioned elsewhere in this section:
- `(shot)_(profile)`: shot state
- `tilt_warnings`: tilt mode
- `bonus_multiplier`: bonus mode
- `extra_balls_awarded`: extra_balls dict

### 7.2 Machine variables
- Machine variables are machine-wide values: credits, last game's scores, high scores, settings.
- With `persist`, they're saved to `<machine>/data/machine_vars.yaml`. They can carry an **expiration time**, e.g. credits only persist for a few hours.
- Change events: `machine_var_(var_name)`.
- Read them with `machine.X`, or `{machine.X}` / `(machine|X)` in text.
- Define them in `machine_vars:`. Change them with `variable_player` using `add_machine`/`set_machine`.
- Every `settings:` entry is also a machine var.

**Built-in machine variables** (`machine_vars/`):

| Group | Variables |
|---|---|
| MPF/host info | `mpf_version`, `mpf_extended_version` (includes show and BCP versions), `python_version`, `platform`, `platform_machine` (32/64 bit), `platform_release`, `platform_system` (Linux/Windows/Mac), `platform_version` |
| Last game scores | `player1_score`, `player2_score`, ... Updated at game end, persisted, and meant for attract mode |
| High scores | `<category><position>_label` (e.g. `score1_label` = "GRAND CHAMPION"), `<category><position>_name`, `<category><position>_value`, `<category><position>_<player\|machine>_<var>` (extra `vars:`) |
| Credits (not on free play) | `credit_units` (internal LCD units, not for display), `credits_numerator`, `credits_denominator`, `credits_whole_num`, `credits_value` ("2 1/2"), `credits_string` ("CREDITS 2 1/2" or "FREE PLAY") |
| MPF-MC (pre-0.80 only) | `mc_version`, `mc_extended_version` (set after MC connects) |
| Platform-specific | `fast_(dmd\|net\|rgb)_firmware`, `fast_(x)_model`, `lisy_hardware`, `lisy_version`, `lisy_api_version`, `p_roc_version`, `p_roc_revision`, `p_roc_hardware_version`, `pkone_firmware`, `pkone_hardware` |
| Other | `master_volume` (replaces `sound_system: master_volume`, MPF-MC era) |

### 7.3 Game variables
- Game variables are built into the game. **You can't define new ones.** Read them with `game.X`, which is shorthand for `mode.game.X`. They're only available during a game.

| Var | Meaning |
|---|---|
| `max_players` | Max players allowed |
| `num_players` | Players currently in the game |
| `balls_per_game` | Balls per player (usually 3 or 5) |
| `balls_in_play` | Balls currently in play |
| `tilted` | True if tilted |
| `slam_tilted` | True if slam tilted |

---

## 8. What's deprecated or changed in 0.80 (GMC)

The config index says:
> "Prior to MPF 0.80, the standard media controller was 'mpf-mc'. ... Developers upgrading from pre-0.80 to GMC will need to replace the features implemented in these configs with equivalents in Godot or a custom media controller. `slide_player`, `sound_player`, and `widget_player` ... are very similar between pre-GMC and GMC eras."

- **Legacy MPF-MC sections to replace with Godot:** `slides:`, `widgets:`, `widget_styles:`, `animations:`, `images:`, `image_pools:`, `images_frame_skips:`, `videos:`, `video_pools:`, `bitmap_fonts:`, `text_strings:`, `sounds:`, `sound_pools:`, `sound_loop_sets:`, `sound_marker:`, `sound_ducking:`, `sound_system:` / `sound_system_tracks:`, `playlists:`, `playlist_player:`, `sound_loop_player:`, `track_player:`, `window:`, `keyboard:`, `mpf-mc:`, `mc_custom_code:`, `mc_scriptlets:`, `virtual_segment_display_connector:`. Also `kivy_config:`, which the index lists under platforms but which is MPF-MC's Kivy.
- **`sound_system:`** has an explicit warning: "Deprecated in MPF 0.80 — MPF 0.80 uses GMC, which manages audio outside of YAML configuration files ... should be removed for projects upgrading to MPF 0.80 and Godot."
- **`sound_player:` stays, with 0.80 changes:**
  - New `bus:` setting.
  - `track:` is **deprecated, use `bus`**.
  - New `action: replace` (stops everything on the bus, then plays).
  - **Not implemented in 0.80:** `about_to_finish_time`, `events_when_about_to_finish`, `mode_end_action`.
  - Other actions: `play`, `stop`, `stop_looping`, `load`, `unload`. Settings: `block`, `delay`, `fade_in`/`fade_out`, `loops`, `max_queue_time`, `pan`, `priority`, `start_at`, `volume`, `key`, `events_when_*`.
- **`sounds:`** also gained `bus:` (0.80), and `track:` is deprecated. **⚠** Yet the page is filed under Legacy and still says "only available if you're using MPF-MC", so it's unclear whether `sounds:` asset entries still matter under GMC.
- **`widget_player:` actions in 0.80:** `play` (default), `remove`, `update` (Godot redraws next idle frame), `preload`, `animation` (calls play on an AnimationPlayer; `from_start` restarts it), `method` (calls a method on a child). Legacy ≤ 0.57 actions were `add`/`remove`/`update`. Other settings: `key`, `slide`, `target` (overrides `slide`), `widget_settings` (e.g. `z`).
- **`slide_player:`**: `action: play|remove`, `priority` (added to mode priority; machine-wide = 0), `target` (display or slide_frame), `expire`, `show`, `force`, `transition`/`transition_out`, `tokens`, `background_color`. It links to a GMC tutorial ("Slide with Score, Player, and Ball"). Inline slide definitions with `widgets:` are an MPF-MC feature.
- **Media config players deprecated from 0.80:** `playlist_player`, `sound_loop_player`, `track_player`.
- **Machine vars:** `mc_version` and `mc_extended_version` only exist pre-0.80.
- **Tags:** `start`, `left_flipper` and `right_flipper` now also drive the built-in high score entry (GMC `MPFTextInput`).
- **Still ambiguous in these pages:** `displays:`, `dmds:`, `rgb_dmds:` and the `(machine|var)` text syntax are all written for MPF-MC. The docs don't say how they apply under GMC; check the GMC section.
- **Also in the dev docs (post-0.80, i.e. 0.58/0.81 dev):**
  - `machine: soft_shutdown_exit_command`
  - FAST `soft_power_*`
  - FAST net watchdog default changed from 1000 to 500
  - `settings` `key_type: bool`
  - neoseg `*-rg-swapped` sizes
  - FAST EXP `led_ports` (needs 0.58.0.dev1/0.81.0.dev1 and EXP firmware 0.48)
  - `twitch_client` removed

---

## 9. Gotchas, contradictions and doc errors

**Config-format traps**
1. **Use `#config_version=6`** (and `#show_version=6`). Many examples in the docs still show `=5` and `!!omap`: `high_score`, `motors` (`position_switches: !!omap`), `smartmatrix`, `switch_player`, `widget_player`, a slide show example, and even `config_version.md`'s own snippet. Don't copy them. Convert `!!omap` to plain mappings and quote `+` times.
2. Quote all-digit or leading-zero values (colours like `"330000"`, numbers like `"0804-1"`). Never put `#` in hex colours.
3. Setting names are case-sensitive.
4. **Add units to times.** A bare number uses the setting's default unit, which can be ms or s.
5. **Setting any `*_events` list replaces its defaults.** For example, flipper `enable_events` defaults to `ball_started`, and servos reset on `ball_starting` unless you override the list.
6. **Adding `enable_events` makes the device start disabled** (shots, logic blocks). Without them it auto-enables. Multiballs auto-enable when their mode starts.
7. **Logic blocks default to `disable_on_complete: true`.** A counter that should repeat needs `disable_on_complete: false`.
8. Counters no longer save state in player vars. See §6.12 for the variable_player workaround.

**Runtime traps**
9. `variable_player` for **player** vars only works in mode configs. Machine vars need `action: add_machine`/`set_machine`, and then the action is mandatory.
10. Queue traps: a `queue_relay_player` whose `wait_for` event never posts, or `show_player` `block_queue` with an infinitely looping show, **hangs the machine**.
11. `stop_on_ball_end: false` needs `game_mode: false` plus `game_ending` in `stop_events`, or MPF asserts.
12. Keep mode priorities between 100 and 1,000,000.
13. Ball save time is **not** reset per drain.
14. Hardware-rule traps:
    - Coils won't hold on without `allow_enable` or a hold power.
    - Diverters of `type: hold` need a hold power.
    - Magnets over 255 ms at full power need `allow_enable`.
15. The `start` switch triggers on **release**.
16. Don't tag device switches (slings, VUKs) `playfield_active`. It causes error `CFE-ball_device-13`.
17. One playfield must carry `tags: default`. `enable_ball_search` is off by default: turn it on in production, and be careful while developing because coils can hurt you.
18. Put drop target reset coils on the **bank**, not on each target.
19. `segment_displays: update_method` defaults to `stack`, which can bloat memory. The docs recommend `replace` and warn that the default will change.
20. A `timer tick_interval` template must evaluate to float **seconds** (`0.5`), not `"500ms"`.
21. Switch and tag events only appear in logs or the monitor if they're handled or the switch has `debug: true`. They are always posted.

**Contradictions / errors in the docs** (⚠)
- **`slide_player` "Valid in" table** says mode configs: **NO**. That contradicts normal use: the bonus docs tell you to put a slide_player in the bonus mode, and priority text refers to mode slide_players. Treat it as a table error.
- **`variable_player` "Valid in"** says machine "YES(NOTE)". The note: player vars are mode-only, machine vars are allowed machine-wide.
- **`shot_profiles: block`** is listed as "Default: `false`", but the text says "The default value is true if you don't specify this".
- **`autofire_coils`/`kickbacks` `reverse_switch`** says "If you want to reverse that ... set this to False. ... Default is False." It should say `true` to reverse.
- **LED channel order:** `lights.md` says "`rgb` for WS2812 and `grb` for WS2811". `neoseg_displays.md` calls GRB the "WS2812 native" ordering. Verify on your hardware.
- **RGB list colours:** light_player says `[r,g,b]` lists aren't allowed (only in `named_colors`). blinkenlight_player and flasher_player say they are.
- **FAST net `watchdog`:** "Default: `500`", then "The default is 1 second". The note says the default was 1000 until 0.58/0.81. `pkone:` watchdog text refers to "the FAST controller" (a copy-paste).
- **`credits`:** the structured default for `credit_expiration_time` and `fractional_credit_expiration_time` is `0`, but the prose says 2 hours and 15 minutes. The `events:` sub-setting is documented as `award:` but the examples use `credits:`.
- **`dynamic_values.md`:** the if/else example uses `player.wizard_complete`, while everywhere else says `current_player.X`. Its tilt example defines `warnings_to_tilt` but the text says "a setting called tilt_warnings".
- **`variable_player`:** an example adds `bonus: 10` and the text says "20". The expanded example repeats the `aliens:` key (invalid YAML duplication).
- **`queue_event_player`:** the config page says it can be used in shows (`queue_events:`). The config_players page says "not valid in shows".
- **`sound_loop_player`** show section is called `sound_loops:` on one page and `sounds_loop_sets:` on another (legacy anyway).
- **`config_players/hardware_sound_player.md`** says it's an MPF-MC player. It's actually for external hardware sound (LISY/APC).
- **`hardware:` `accelerometers:`** option links to "DMD Platforms" (a copy-paste).
- **`mode.md`** calls the player var `_restart_modes_on_next_ball`. The player_vars page says `restart_modes_on_next_ball`.
- **Stubs or incomplete pages:**
  - `instructions/yaml.md`, `overwrite.md`, `express_config.md` (TODO)
  - `ball_routings.md`, `extra_ball_groups.md` ("where you..."), `digital_score_reels.md`, `image_pools.md`, `video_pools.md`, `speedometers.md`, `vpe.md`, `hardware_benchmark.md`
  - `show_player: show_queue:` ("Is this still a thing?")
  - Many `ball_devices` settings typed as "Unknown type"
- The `fast:` page keeps a "Pre-2024" section with the old flat `ports:` / `hardware_led_fade_time:` form. Use the `net:`/`exp:`/`aud:` structure for 0.80.

---

## 10. Source doc paths used

All paths are relative to `mpf-docs-dev/docs/` (plus `../mkdocs.yml` for nav and `../includes/` for snippets).

- `reference/index.md`
- `config/index.md`, `config/config_players/index.md`
- `config/instructions/*.md`: `index`, `yaml`, `config_version`, `config_v6`, `machine_config`, `mode_config`, `debug`, `overwrite`, `case_insensitivity`, `tags`, `dynamic_values`, `device_control_events`, `time_strings`, `text_templates`, `colors`, `express_config`, `lists`, `gamma_correction`, `gain_values`
- `config/*.md` (all 200+ section pages), including: accelerometers, accruals, achievement_groups, achievements, animations, assets, auditor, autofire_coils, ball_devices, ball_holds, ball_locks, ball_routings, ball_saves, bcp, bcp_connection, bcp_server, bitmap_fonts, blinkenlight_player, blinkenlights, bonus, coil_overwrites, coil_player, coils, color_correction_profile, combo_switches, config, counter_control_events, counters, credits, custom_code, data_manager, dc_motors, digital_outputs, digital_score_reels, display_light_player, displays, diverters, dmds, drop_target_banks, drop_targets, dual_wound_coils, event_player, extra_ball_groups, extra_balls, fadecandy, fast, fast_coils, fast_switches, flasher_player, flashers, flippers, game, gi_player, gis, hardware, hardware_benchmark, hardware_sound_player, hardware_sound_systems, high_score, image_pools, images, images_frame_skips, info_lights, keyboard, kickbacks, kivy_config, led_player, leds, light_player, light_rings, light_segment_displays, light_segment_displays_device, light_settings, light_stripes, lights, lisy, logging, logic_blocks, logic_blocks_common, machine, machine_vars, magnets, matrix_lights, mc_custom_code, mc_scriptlets, mode, mode_settings, modes, motors, mpf, mpf-mc, multiball_locks, multiballs, mypinballs, named_colors, neoseg_displays, open_pixel_control, opp, opp_coils, osc, p_roc, pd_led_boards, pin2dmd, pkone, player_vars, playfield_transfers, playfields, playlist_player, playlists, plugins, pololu_maestro, pololu_tic, psus, queue_event_player, queue_relay_player, random_event_player, raspberry_pi, rgb_dmds, rpi_dmd, score_queue_player, score_queues, score_reel_groups, score_reels, scriptlets, segment_display_player, segment_displays, sequence_shots, sequences, servo_controllers, servos, settings, shakers, shot_control_events, shot_groups, shot_profiles, shots, show_config, show_player, show_pools, shows, slide_player, slides, smart_virtual, smartmatrix, snux, sound_ducking, sound_loop_player, sound_loop_sets, sound_marker, sound_player, sound_pools, sound_system, sound_system_tracks, sounds, speedometers, spi_bit_bang, spike, spike_node, spinners, state_machine_states, state_machine_transitions, state_machines, step_stick_stepper_settings, steppers, switch_overwrites, switch_player, switches, system11, text_strings, text_ui, tic_stepper_settings, tilt, timed_switches, timer_control_events, timers, track_player, trinamics_steprocker, twitch_client, variable_player, video_pools, videos, virtual_platform_start_active_switches, virtual_segment_display_connector, vpe, widget_player, widget_styles, widgets, window
- `config/fast/fast_net.md`, `fast_exp.md`, `fast_exp_board.md`, `fast_aud.md`
- `config_players/*.md` (index + all 21 player pages)
- `player_vars/*.md` (index + 10 var pages), `machine_vars/*.md` (index + 31 var pages), `game_vars/*.md` (index + 6 var pages)
- `../includes/game_var.md`, `player_var.md`, `machine_var.md`, `config_section.md`, `template_setting.md`
