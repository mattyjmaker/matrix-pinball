# MPF Game Logic and Playfield Mechanisms: Practical Reference

This reference is condensed from the MPF documentation source (dev branch, i.e. MPF 0.80 with the Godot Media Controller, "GMC"). It covers the `docs/game_logic` and `docs/mechs` sections. It sticks to what the docs say, and it flags contradictions and 0.57-vs-0.80 differences where they show up.

> **The key 0.57 vs 0.80 point for this section:** almost all game-logic YAML is the same in 0.57 and 0.80. That covers modes, shots, logic blocks, ball saves, multiballs, tilt, credits, high scores and all the mech/device configs. What changed is the **display side**. Many examples in these pages still include `slides:`, `widgets:`, `widget_styles:` and inline widget definitions in `slide_player:`, and those are **0.57 (legacy Kivy MC)** syntax. In 0.80, slides are Godot `.tscn` scenes. `slide_player:` still lives in your MPF YAML, but it refers to slide scenes by name and passes `tokens:`. Only one page in this section says so outright (`tilt/overwrite_tilt_slides.md`). The rest were not updated, so treat every `slides:` or `widgets:` block below as 0.57-only. The **bonus mode** config itself also changed in 0.80 (see §9).

---

## 1. Core concept: everything is events

- The docs are firm that all game logic is event-driven. Built-in modules (timers, shots, counters, multiballs, accruals and so on) listen for events, read or modify state, and post their own events. Those events then drive other modules: starting and stopping modes, diverters, multipliers, and so on.
- **Gotcha, "IF event1 AND event2":** events are discrete moments, so you can't AND two events together. Use one of these instead:
  - **Conditional events**, e.g. `some_event{condition}`, which test player, machine or device variables. Examples: `ball_starting{ball==1 and not is_extra_ball}` and `s_target_active{device.shots.my_shot.state_name=='lit'}`.
  - **Logic blocks** (accruals, sequences, counters, state machines) to remember that something already happened.
- Switch events are posted automatically as `<switch_name>_active` and `<switch_name>_inactive`, e.g. `s_your_switch_active`.
- Device state can be read in conditions and dynamic values through `device.<collection>.<name>.<property>`, e.g. `device.counters.my_counter.value`, `device.ball_devices.bd_trough.balls`, `device.shots.x.state_name`. Mode state is `mode.<name>.active`, and player variables are `current_player.<var>`.

---

## 2. Game flow: attract → game → ball start/end → game end

### Built-in modes and priorities

| Mode | Priority | Starts | Stops | Notes |
|---|---|---|---|---|
| `attract` | 10 | `game_ended` or `reset_complete` | when a game starts (the doc says "when the *game_start* mode is posted") | Watches the start button (press/release and hold time) and which other buttons are held at start (e.g. for tournament mode). Posts `request_to_start_game`. Added to `modes:` automatically via `mpfconfig.yaml`. |
| `game` | 20 | `game_start` | `game_ended` | Tracks balls in play, adds players on start presses, restarts the game on a long start press, posts `game_started`, `ball_starting`, `ball_ending`, `ball_ended`, `game_ending`, `game_ended`, handles drains, player rotation and extra balls/shoot again. "Almost never necessary to override." Added automatically. |
| `tilt` | 10,000 | at boot, never stops | n/a | Runs in attract too, so it can catch slam tilts. You **must** add `- tilt` to `modes:`. |
| `bonus` | 500 | automatically at ball end (unless tilted) | after the bonus finishes | Needs a `modes/bonus/config/bonus.yaml` and `- bonus` in `modes:`. |
| `credits` | see contradiction | `reset_complete` | never (`stop_on_ball_end: false`, `game_mode: false`) | Needs a mode folder and `- credits`. |
| `high_score` | 500 in the example | `game_ending, start_high_score` with `use_wait_queue: true` | n/a | Stores scores in `<machine>/data/high_scores.yaml`. |
| `match` | n/a | runs at game end (the example test asserts it runs after the last ball) | n/a | Config in `modes/match/config/match.yaml`. |
| `service` | n/a | n/a | n/a | Add `- service` to `modes:`. |

> **Contradiction (credits):** `game_logic/credits.md` says the credits mode priority is "really high, 11000 by default" and that it starts on `machine_reset_phase_3`. The YAML it quotes from `mpf/modes/credits/config/credits.yaml` shows `priority: 1000010` and `start_events: reset_complete`. Trust the YAML.

### Ball start and end hooks (`game_logic/ball_start_end.md`)

- **No delay at ball start:** hook shows or other players to `ball_started`. The ball ejects immediately. A mode with `start_events: ball_started` is the usual pattern.
- **Ball save on eject:** use `timer_start_events: balldevice_bd_plunger_ejecting_ball` (or `..._ball_eject_success`). The docs say this also works with a mechanical eject.
- **No delay at ball end:** `ball_ended` can't be seen from normal game modes, because they stop at ball end. For short effects, use a mode with `start_events: ball_ending`, `game_mode: false`, and a stop event fired when its show completes. This does **not** delay the next ball.
- **To delay ball start/end** (for long shows): use `queue_relay_player` on the `ball_starting` and `ball_ending` queue events.

```yaml
##! mode: my_mode
mode:
  start_events: ball_will_start     # in normal mode use ball_started instead
  priority: 200
queue_relay_player:
  ball_starting:
    post: start_ball_starting_show
    wait_for: mode_ball_starting_show_ended
  ball_ending:
    post: start_ball_ending_show
    wait_for: mode_ball_ending_show_ended
show_player:
  flipper_cancel:                 # both flippers skips the show
    ball_starting_show: stop
    ball_ending_show: stop
  start_ball_starting_show:
    ball_starting_show:
      loops: 0
      events_when_stopped: mode_ball_starting_show_ended
  start_ball_ending_show:
    ball_ending_show:
      loops: 0
      events_when_stopped: mode_ball_ending_show_ended
```

To delay only the first ball, use `ball_starting{ball==1 and not is_extra_ball}`. For extra balls only, use `ball_starting{is_extra_ball}`.

- Player lifecycle events: `player_add_request`, `player_added`, `player_turn_will_start`, `player_turn_starting`, `player_turn_started`, `player_turn_will_end`, `player_turn_ending`, `player_turn_ended`, `single_player_ball_started`, `multi_player_ball_started`.
- Start button: tag the switch `start` (`tags: start`). That's what hooks it into the game.

---

## 3. The mode system

### Structure
- Folder layout is `<machine>/modes/<mode_name>/config/<mode_name>.yaml`. The file is named after the mode, not `config.yaml`. Optional subfolders include `shows/`, `sounds/`, `images/` and `code/`, and assets in a mode folder are only available to that mode.
- Every mode must be listed in the machine-wide `modes:` list, with a dash per entry. MPF does not auto-detect mode folders on purpose, so you can keep work-in-progress modes out.
- Modes can sit in nested subfolders, e.g. `modes/band/sq/first_avenue`. Any folder that contains a `config` subfolder is treated as a mode and isn't scanned further.
- **Built-in modes (attract, game, credits, bonus, tilt, high_score, match, service)** merge like this: MPF loads its own `mpf/modes/<mode>/config/<mode>.yaml` first, then merges in yours. That's why your `credits.yaml` or `bonus.yaml` doesn't need a `mode:` section. Use `_overwrite: true` on a section to replace the built-in one rather than merge with it (see the high-score and tilt-slide examples).
- Anything configured in a mode file (variable_player, shots, shows, ball_saves, multiballs, etc.) only exists while that mode runs.

### `mode:` settings (defaults from `config/mode.md`)
| Setting | Default | Meaning |
|---|---|---|
| `priority` | 100 | Higher priority gets display/light priority and can block events from lower modes |
| `start_events` / `stop_events` | None | Events that start or stop the mode |
| `game_mode` | true | Mode may only run during a game |
| `stop_on_ball_end` | true | Mode stops automatically at ball end |
| `restart_on_next_ball` | false | Restarts the mode on the next ball if it was running when the ball ended |
| `use_wait_queue` | false | Holds the event queue (e.g. `game_ending`) while the mode runs |
| `start_priority` / `stop_priority` | 0 | Ordering |
| `code` | n/a | Custom Python class |
| `events_when_started` / `events_when_stopped` | n/a | Events posted on start/stop |

Mode events: `mode_<name>_will_start`, `mode_<name>_starting`, `mode_<name>_started`, `mode_<name>_will_stop`, `mode_<name>_stopping`, `mode_<name>_stopped`.

### Priorities and blocking
- If a base mode scores 10k for a ramp and a higher-priority mode scores 100k for the same event, you get **both** (110k) unless the higher mode's scoring entry is configured to **block** lower modes. Blocking is set per entry.
- Priority also decides which mode's slides and light shows win.

### Design guidance
- Use lots of small modes for anything that temporarily changes rules, scoring or device behaviour: skill shot, combos, lock progress, "shot lit" modes and so on. The docs say dozens of running modes has no performance cost.
- **The "mode as super logic block" pattern** (`modes_as_game_logic.md`): a `managers_choice_lit` mode enables the shot. Three award modes (base 301, timed 302, multiball 303) each listen for the lit shot's hit event and block the lower modes. Stacking the modes then picks the right award without any if/then logic.

---

## 4. Shots, shot groups, shot profiles, sequence shots

### Shots
- A shot is a switch (or several) the player aims for: a target, lane, ramp, loop, toy, VUK, pop bumper and so on.
- **Gotcha:** to make the same physical shot behave differently in different modes, **define a separate, distinctly named shot in each mode** (e.g. one in base, another in multiball), each with its own profile.

```yaml
##! mode: inlanes
shots:
  my_shot:
    switch: lane_l          # or `switches:`; or `hit_events:` for non-switch triggers
    show_tokens:
      light: lane_l
```

- The default profile has two states, `unlit` then `lit`. The first hit posts `shot_my_shot_unlit_hit` and the second posts `shot_my_shot_lit_hit`.
  - *Doc inconsistency:* the text shows a `shot_` prefix, while the event list shows `(shot_name)_hit`, `(shot_name)_(state)_hit`, `(shot_name)_(profile)_hit` and `(shot_name)_(profile)_(state)_hit`. The worked examples use `shot_outlane_left_hit{state=="unlit"}`, where the shot itself is named `shot_outlane_left`, so the event is just `<shot_name>_hit`.
- Monitorable properties are `device.shots.<name>.state` (an index starting at 0) and `.state_name`.
- Other options used in examples: `profile:`, `advance_events:`, `show_tokens:`.

### Shot profiles
```yaml
shot_profiles:
  lane_profile:
    states:
      - name: unlit
        show: "off"
      - name: lit
        show: "shot_lit"     # show receives the shot's show_tokens
```
- A hit advances the profile unless `advance_on_hit: false`. The shot stays at its last state unless `loop: true`.
- **Recommended practice** (`integrate_shots_with_...md`):
  1. For **state indication**, give each profile state a show. It's restored automatically on player change and mode restart, so lights never drift out of sync.
  2. For **hit feedback**, use `show_player` on the `(name)_hit` event with `loops: 0`. This also handles cleanup.

### Shot groups
```yaml
shot_groups:
  sg_lanes:
    shots: shot_outlane_left, shot_inlane_left, shot_inlane_right, shot_outlane_right
    rotate_left_events: s_flipper_left_active     # lane change
    rotate_right_events: s_flipper_right_active
    reset_events:
      sg_lanes_lit_complete: 1s                    # reset 1s after all lit
    enable_events: ball_started
    disable_events: ball_ending
```
- Events: `(group)_complete`, `(group)_(state)_complete`, `(group)_hit`, `(group)_(state)_hit`. Property: `device.shot_groups.<name>.common_state` (None if the shots differ).

### Sequence shots (ordered switches with a timeout)
```yaml
sequence_shots:
  ramp:
    switch_sequence: s_ramp_entry, s_ramp_success
    sequence_timeout: 3s        # posts ramp_hit
```
- **Gotcha:** despite the name, sequence shots **can't go in shot_groups**. Wrap one in a regular shot with `hit_events: ramp_hit`.
- For loops, orbits and ramps (`mechs/loops.md`), play an "entry" sound on `s_ramp_entry_active` and a success sound on `ramp_hit`. *Doc bug:* that page's own YAML uses `s_ramp_success` as the event key, not `ramp_hit`.

### Shots vs logic blocks
The docs' rule of thumb: use shots and shot groups for "switch hits that change lights". Use logic blocks once you need conditions (e.g. balls locked) or triggers that aren't switches (e.g. locks).

### Skill shot recipe (`skill_shot.md`)
A `skill_shot` mode (priority 500, starts on `ball_started`, stops on `skill_success` or `skill_failed`) with:
- Three lane shots on a `skill_shot_profile` (unlit → flashing → lit, `loop: true`). The first shot gets `advance_events: mode_skill_shot_started` so it starts in the flashing state.
- A shot group rotated by the flippers.
- A timer that starts on `balldevice_<plunger>_ball_eject_success`, `end_value: 5`.
- A **state machine** (`start` → `success` or `failed`) to avoid a race between the "flashing hit" and "unlit hit" events. `success` is reached via `skill_shot_flashing_hit`. `failed` is reached via `skill_shot_unlit_hit` or `timer_skill_shot_timeout_complete`.
- *Doc inconsistency:* the prose says `skill_shot_lit_hit`, but the YAML uses `skill_shot_flashing_hit`, which is correct for that profile.

---

## 5. Logic blocks

There are four types. All can be enabled, disabled and reset by events, and all can live in modes.

| Type | Purpose | Key settings |
|---|---|---|
| **Counter** (`counters:`) | Count one or more events up to a value | `count_events`, `starting_count`, `count_complete_value`, `direction: up/down`, `events_when_hit`, `events_when_complete`, `persist_state`, plus an optional multi-hit grouping window |
| **Accrual** (`accruals:`) | Several events, **any order** | `events:` list, `events_when_complete` |
| **Sequence** (`sequences:`) | Several events, **strict order**. Out-of-order events are ignored, not reset. | `events:` list, `events_when_complete` |
| **State machine** (`state_machines:`) | Arbitrary finite state machine | `states:` (with `label`, `show_when_active`, `events_when_started/stopped`), `transitions:` (`source`, `target`, `events`, `events_when_transitioning`) |

```yaml
counters:
  super_jets:
    count_events: sw_pop
    events_when_hit: pop_hit
    starting_count: 75
    count_complete_value: 0
    direction: down
    events_when_complete: super_jets_start
accruals:
  three_shots:
    events: [shot1_hit, shot2_hit, shot3_hit]
    events_when_complete: enable_winning_shot
sequences:
  finish_world_tour:
    events: [shot_north_america_hit, shot_south_america_hit, shot_europe_hit, shot_australia_hit]
    events_when_complete: wt_done
```

### Events and properties
- Events: `logicblock_<name>_hit`, `logicblock_<name>_updated`, `logicblock_<name>_complete`. The integration pages also use `counter_<name>_hit` in a variable_player.
- **`_updated` vs `_hit`:** `_updated` fires on every change **and when the block is restored on mode restart**, so its handlers must be idempotent. Use it for shows, lights and slides. Use `_hit` for things that should happen once, such as scoring or callouts. Example: `logicblock_my_counter_hit{remaining == 5}`.
- Properties:
  - `device.counters.X.value` / `.enabled` / `.completed`
  - `device.accruals.X.value[i]` (a per-step 0/1 list) and `device.sequences.X.value` (the number of steps completed). *Note:* the sequences page says `value` is a list like accruals, but its test and scoring examples treat it as an integer count.
  - `device.state_machines.X.state` (a string)

### THE common gotcha: "my block only works once"
By default a block doesn't reset on completion (the docs say you must "first set `reset_on_complete` to True"), and `disable_on_complete` defaults to `true`. For a repeating block, set `reset_on_complete: true` **and** `disable_on_complete: false`, unless something else re-enables it. On the other hand, if you want to query `.completed` in a condition, you need `reset_on_complete: false`, or the block resets instantly.

### Persisting state
- Since MPF 0.50, logic block state is only stored in a player variable when `persist_state: true`. The variable is called `<block>_state`. Without that, the value isn't saved under any name, and you read it via `device.counters.<name>.value`.

### Integrations
- **Lights:** `light_player:` keyed on a bare condition, e.g. `"{device.counters.my_counter.value > 1}": {l_light: green}`.
- **Shows:** `show_player: logicblock_my_counter_updated{enabled}: my_show: {start_step: value + 1, key: ...}`. A single show with one step per count, with `key` so the new show replaces the previous one.
- **Slides:** the page says the MC "cannot subscribe to the counter value", so copy it into a player variable with `variable_player: counter_my_counter_hit: my_counter: {action: set, int: (count)}` and show `(player|my_counter)`. That note is from the 0.57 MC era. The player-variable approach still works in principle, but the slide side is Godot in 0.80.
- **Scoring from block state:** e.g. `score: 10000 * (device.counters.my_counter.value + 1)`, or add up accrual `value[0..2]`.

---

## 6. Scoring, player variables, timers

### Scoring (`variable_player:`)
```yaml
player_vars:
  multiplier: {value_type: int, initial_value: 1}   # otherwise it starts at 0
##! mode: my_mode
variable_player:
  s_your_switch_active:
    score: 100
  increment_multiplier:
    multiplier: 1                       # add
  mode_my_mode_started:
    multiplier: {int: 1, action: set}   # reset per ball
  score_something:
    score: 100 * current_player.multiplier * current_player.mode_multiplier
  score_something{mode.super_extraball.active and current_player.loops_made > 2}:
    score: 1000000
```
- Player variables are per player and carry across balls. The docs suggest defining them all centrally in the machine config under `player_vars:` (types `str`, `int`, `float`). Strings are set with `action: set` and `string: 'Scene 1'`.
- Player variables are effectively global to your config, so be careful where they get changed.
- Events: `player_<var>` (e.g. `player_score`), which can be used as a condition. Example: `award_events: player_score{value>=140000}` awards an extra ball on score.
- **SS-style score queues with chimes:** `score_queues: score: {chimes: c_chime_1000, c_chime_100, c_chime_10, None}` plus `score_queue_player: score_2k: {score: 2000}`.

### Timers
- Timers count up or down with `tick_interval`, and are controlled via `control_events` (start, stop, restart, reset, and so on). Events: `timer_<name>_started`, `_tick`, `_complete`, `_stopped`, `_paused`, `_time_added`, `_time_subtracted`.
- To show a timer on screen, copy the ticks into a player variable on `timer_<name>_tick`, e.g. `int: device.timers.your_timer.ticks % 60` for seconds.

### Timed switches and combo switches
- **Combo switches:** MPF's built-in `mpfconfig.yaml` defines `both_flippers` (tag_1 `left_flipper`, tag_2 `right_flipper`), which posts **`flipper_cancel`**. You only get it if you **tag your flipper switches `left_flipper` / `right_flipper`**. Override by copying the section into your config, e.g. to add `max_offset_time`. Events: `<combo>_both`, `_one`, `_inactive`, `_switches_1`, `_switches_2`.
- **Timed switches:** a built-in flipper-cradle timed switch posts `flipper_cradle` after about 3s held and `flipper_cradle_release` afterwards (again, only with the flipper tags). Cradling also pauses the ball-search timer.

---

## 7. Ball saves, ball search, ball tracking

### Ball saves (`ball_saves:`)
```yaml
ball_saves:
  default:
    active_time: 10s
    hurry_up_time: 3s
    grace_period: 2s
    enable_events: mode_base_started
    timer_start_events: balldevice_bd_plunger_ball_eject_success   # don't start the timer while the ball sits in the shooter
    disable_events: ball_will_end
    auto_launch: true
    balls_to_save: 1          # -1 = unlimited
    early_ball_save_events: s_left_outlane_active, s_right_outlane_active   # treat outlanes as drains for quicker saves
```
- Events: `ball_save_<name>_enabled`, `_disabled`, `_timer_start`, `_hurry_up`, `_grace_period`, `_saving_ball`. Use these to flash a "shoot again" light.
  - *Doc inconsistency:* `ball_start_end.md` names the save `ball_save_ball_save` and hooks `ball_save_ball_save_ball_save_timer_start`, which doubles the name. It also says the hurry-up covers "the last 2s" when `hurry_up_time: 3s`.
- **Plunger without a lane switch:** start the save timer from a `playfield_active`-tagged switch, not `ball_starting` or the trough eject (`mechanical_no_switch.md`).
- **Center post / mechanical ball save:** configure it as a **diverter** (`type: pulse`, up and down coils), so ball search and service mode support come free. Raise it on `ball_save_default_timer_start` and lower it on `ball_save_default_disabled` via `event_player`.
- **Kickback:** pair it with a short ball save enabled on `kickback_<name>_fired` (see §12).

### Ball search
- **Off by default** for safety ("coils can seriously injure humans"). Enable it per playfield:
```yaml
playfields:
  playfield:
    enable_ball_search: true
```
- Runs in phases 1 to 3 of increasing intensity. Early phases pulse pop bumpers and empty ball devices. Later phases may reset drop targets. After that, the ball is marked lost and a new ball is served.
- Tuning: `ball_search_timeout`, `ball_search_interval`, and per-device `ball_search_order`. Flippers are excluded by default, so add `include_in_ball_search: true` to upper-playfield flippers if needed. For a standalone coil, use `pulse_events: ball_search_phase_<n>_searches`.
- **Critical:** tag every playfield switch that isn't bound to a device (targets, inlanes, outlanes, ramps, rollovers) with `playfield_active`. **Don't tag the plunger lane switch.** Each activation resets the ball-search timer. Search runs while MPF thinks balls are loose, including after a tilt, and stays paused while a flipper is held.
- Events: `ball_search_started`, `ball_search_stopped`, `ball_search_failed`.

### Ball tracking (`game_logic/ball_tracking.md`, `mechs/playfields/*`)
- Four parts are always active, game or no game: the Ball Controller, ball devices, playfields (a special ball device), and diverters (which route balls to devices that request them).
- **Playfield balls vs balls in play:** they differ during a tilt (balls in play is 0 while balls are still rolling), with multiple playfields, and when a ball is locked (the playfield has 0 balls, but one is still "in play").
- **How eject confirmation to the playfield works:**
  - If the playfield is empty, the first `playfield_active` switch hit confirms the eject.
  - If balls are already on the playfield, MPF can't tell which ball made the hit, so it **falls back to the eject timeout**.
  - This is why adding balls in multiball can take about 10s: the default `eject_timeouts` is 10s. **Tune `eject_timeouts` on your launcher.**
- **Multiple playfields:** name the tag `<playfield_name>_active` (e.g. `upper_playfield_active`) and assign each device's playfield explicitly. Otherwise you get `unexpected_ball_on_<pf>` events, ball search at the wrong time, and broken tracking. Use `playfield_transfers:`, or a ball device that captures from one playfield and ejects to another.

---

## 8. Multiballs, locks, holds

### Multiballs (`multiballs:`)
- Each multiball is named. Types include run-until-one-ball-left and timed. Multiball saves use `shoot_again: 15s` or similar. Multiballs can stack.
- Key settings: `ball_count`, `ball_count_type: total` (or add), `shoot_again`, `start_events`, `ball_locks:` (the **devices** to release balls from). Any shortfall is made up from the playfield's `default_source_device`.
- Events: `multiball_<name>_started`, `_ended`, `_shoot_again`, `_shoot_again_ended`, `_lost_ball`, `_hurry_up`, `_grace_period`, `_restart_grace_period_started`, `_restarted`, plus `ball_save_<mb>_timer_start` and `ball_save_<mb>_add_a_ball_timer_start`.
- Properties: `device.multiballs.X.balls_added_live`, `.balls_live_target`, `.enabled`, `.shoot_again`.

### Multiball locks (`multiball_locks:`): balls that are taken out of play
Counting strategies:
- `virtual_only`: the count goes up per lock, per player, whatever is physically in the device. The docs call this "usually the best option for modern machines".
- `physical_only`: the count always equals the balls physically present. Other players can "steal" locked balls. This is for EM and early SS machines.
- `min_virtual_physical`: like physical, but a player's lock always counts even if the ball is later ejected.
- `no_virtual`: forgets everything on player change.

When a ball is locked, a new ball is served from `default_source_device`. The exception is when the lock device is full, in which case the lock device ejects instead. Locks can be relit by using the `locked_ball` event as a disable event and another event as the enable event. Events: `multiball_lock_<name>_locked_ball`, `multiball_lock_<name>_full`. Property: `locked_balls`.

**Virtual lock with no physical lock** (a counter on any shot or device-entered event):
```yaml
multiballs:
  3balls_multiball:
    ball_count: 3
    ball_count_type: total
    shoot_again: 30s
    start_events: logicblock_mb_counter_complete
counters:
  mb_counter:
    count_events: balldevice_bd_middle_ramp_ball_lock_ball_entered
    count_complete_value: 3
```

**Physical lock (traditional)**: define the lock `ball_device`, list it in the multiball_lock's `lock_devices`, and start the multiball on the lock's `full` or `locked_ball` event.
- **Cheat sheet (gotcha):** set `replace_balls_in_play: true` on the lock and `balls_to_replace:` equal to **(lock capacity minus 1)** on the multiball. The two only work **as a pair**. Used alone, they give wrong ball counts. If the multiball doesn't start automatically when the last ball enters, **the game gets stuck with no ball on the playfield**.
- How claiming works: a ball entering a non-trough device is offered to locks. If something claims it, the device holds it and a new ball is requested. If not, the ball is ejected. Balls in play never changes; the "inactive ball" just moves from the trough to the lock.
- *Note:* the traditional-lock page names `replace_balls_in_play` and `balls_to_replace` but doesn't say exactly which section each belongs in beyond "multiball_locks and multiballs". Check the config reference.

**Several lock devices in sequence**: one mode per lock (`restart_on_next_ball: true`). Each is started by the previous lock's `multiball_lock_<prev>_full` and stopped by `multiball_my_multiball_started`, and each lock has `reset_count_for_current_player_events: multiball_my_multiball_started`. A multiball mode then uses `ball_locks: bd_lock1, bd_lock2, bd_lock3`. Locks and multiballs are **independent** devices that you tie together with events.

### Ball holds (`ball_holds:`): hold temporarily, still in play
- Used to hold a ball during a show or video mode. Balls in play is **not** reduced, and if every other ball drains the player's ball does **not** end. Not for multiball locks.
- Events: `ball_hold_<name>_held_ball`, `_full`, `_balls_released`. Property: `balls_held`.
- A `queue_relay_player` on `balldevice_bd_scoop_ball_eject_attempt` gets the same effect: the eject is delayed until a show finishes.
- *Naming note:* `mechs/scoops.md` links to a "ball_lock device" (`config/ball_locks.md`). That is legacy naming. The game-logic docs use `multiball_locks` and `ball_holds`.

- *"Add-a-ball" multiball* and *video modes*: those pages are empty stubs ("Help us to write it").

---

## 9. Bonus, extra balls, achievements, high scores, match, credits, replays

### End-of-ball bonus
Steps (per the docs):
1. Create `modes/bonus/config/bonus.yaml`.
2. Add `- bonus` to `modes:`. It starts automatically at ball end unless tilted, at priority 500.
3. Count things during play with `variable_player`.
4. Define `mode_settings:`.

**0.57 syntax (as in `game_logic/bonus/*`):**
```yaml
mode_settings:
  display_delay_ms: 1s
  hurry_up_delay_ms: 0
  bonus_entries:
    - event: bonus_ramps            # one event posted per entry
      score: 400
    - event: bonus_castles
      score: 200
      player_score_entry: castles_captured   # score × player var
    - event: bonus_dropbanks
      score: device.counters.dropbank_completions.value * 20
```
- Behaviour: pause at ball end, then post each entry's event at `display_delay_ms` intervals. Zero-score entries are skipped by default. If the player variable `bonus_multiplier` isn't 1, it posts `bonus_subtotal` then `bonus_multiplier`. Finally it posts `bonus_total`, adds the total to the score, and starts the next ball.
- Options include resetting variables after the award, showing zero entries, hurry-up on `flipper_cancel`, and waiting for an event before ending.

**0.80 change (from `gmc/reference/bonus.md`):** the per-entry events are **gone**. Everything is posted as a single **`bonus_entry`** event. `event:` becomes **`entry:`**. The reserved entry values are `subtotal`, `multiplier` and `total`. There's a new `text:` option, plus `reset_player_score_entry`, `skip_if_zero` (default true) and `skip_if_negative`. The GMC ships a default `bonus.tscn`, driven by `slide_player: mode_bonus_started: bonus`, `bonus_start` (update with `tokens: {entry: initial}`) and `bonus_entry` (update). **The bonus examples in `game_logic/bonus` are 0.57-only.**

### Extra balls
- Named `extra_balls:` devices, each awardable once by default (up to x per device). `extra_ball_groups:` can cap the total.
- Example: score-based EM style, `award_events: player_score{value>=140000}`.
- Events: `extra_ball_<name>_awarded`, `_lit`, `_award_disabled`, `extra_ball_awarded`, `extra_ball_group_<name>_awarded`, `_lit`, `_unlit`, `_lit_awarded`, `_award_disabled`.

### Achievements and achievement groups
- Per-player goals, usually with a light. States: `disabled`, `enabled`, `started`, `stopped`, `selected`, `completed`. Property: `device.achievements.X.state`.
- Groups (e.g. TAF Mansion Awards) can randomly select an incomplete member, rotate the selection on an event (pop hits), post an event when all are complete (for a wizard mode), and start the selected achievement. Properties: `enabled` and `selected_member`. See cookbook `TAF_mansion_awards`.

### High scores
- Built-in mode. Categories can be any player variable (`categories: !!omap` with a list of award names each), with `defaults:`, `vars:` (extra player vars stored alongside), `enter_initials_timeout` and `award_slide_display_time`. Scores persist in `data/high_scores.yaml`.
- Machine variables are created for attract displays: `<category><n>_label`, `_name`, `_value`, `_<vartype>_<var>` (e.g. `score1_name`, `loops1_value`).
- **EM machines or no display:** set `player_vars: initials: {value_type: str, initial_value: AAA}`, and the mode stops asking for initials.
- The example's `text_input` initials widget and `slides:` are **0.57 MC** syntax.
- *Doc inconsistency:* the text mentions `loop1_*` machine variables, while the category and attract example use `loops1_*`.

### Match
Built-in `match` mode. `mode_settings: non_match_number_step: 10`. Events are `match_has_match` and `match_no_match`, with `match_number0..3` and `winner_number` args. Use a queue_relay_player to hold until the slide goes.

### Coins and credits
- Create `modes/credits/config/credits.yaml`, add `- credits` to `modes:`, and put the `credits:` section in the **machine** config:
```yaml
credits:
  max_credits: 12
  free_play: false
  service_credits_switch: s_service_coin
  switches:
    - switch: s_coin_left
      type: money          # label for earnings reports only
      value: .25
  pricing_tiers:
    - price: .50           # first tier = game price (required)
      credits: 1
    - price: 2
      credits: 5
  fractional_credit_expiration_time: 15m
  credit_expiration_time: 2h
  persist_credits_while_off_time: 1h
  free_play_string: FREE PLAY
  credits_string: CREDITS
```
- **A game always costs 1 credit per player.** Change pricing through money-per-credit, not credits-per-game. The pricing-tier discount state resets when ball 2 starts.
- Machine variables: `credits_string`, `credits_value`, `credits_whole_num`, `credits_numerator`, `credits_denominator`, `credit_units`. Events: `credits_added`, `not_enough_credits`, `max_credits_reached`, `enabling_free_play`, `enabling_credit_play`, `player_added`. Control events: `enable_free_play`, `enable_credit_play`, `toggle_credit_play`.
- Earnings are logged in `data/earnings.yaml`. Expose prices to operators through `settings:` entries and reference them as `price: settings.credits_price_one_credit`.

### Replays
The page is an empty stub.

### Service mode
Add `- service` to `modes:` and tag switches `service_door_open` (plus `power_off`), `service_enter`, `service_esc`, `service_up` and `service_down`. Map keyboard keys for development. Add operator `settings:` (label, values, default, key_type, sort). The example also defines a `sound_system` with an `sfx` track and `widget_styles`. Those are MC-era (0.57) display and sound requirements, so check the GMC docs for their 0.80 equivalents.

---

## 10. Tilt

- Add `- tilt` to `modes:`. Tag the tilt bob `tilt_warning` and the slam switch `slam_tilt`. Three paths:
  - **slam_tilt:** clears credits and ends the game.
  - **tilt:** an instant tilt, rarely used.
  - **tilt_warning:** gives `warnings_to_tilt` warnings, then ends the ball.
- Warnings reset on `reset_warnings_events` (default ball end, can be changed to game end). They're stored in the player var named by `tilt_warnings_player_var` (default `tilt_warnings`).
- Defaults you can override in `modes/tilt/config/tilt.yaml`: `multiple_hit_window: 300ms`, `settle_time: 5s`, `warnings_to_tilt: 3`. These can be linked to operator `settings:` (e.g. `warnings_to_tilt: settings.warnings_to_tilt`).
- Properties: `mode.tilt.tilt_settle_ms_remaining` and `tilt_warnings_remaining`. The page's prefix line wrongly says this is for "ball devices".
- Ball search stays active after a tilt until all balls drain.
- **Slides, 0.57 vs 0.80:** in 0.57 you override `slides:` with `_overwrite: true` in the tilt mode, and slam-tilt slides need a higher priority than the `tilt` slide. In **0.80**, GMC ships `tilt.tscn`, which expects a `text` token ("WARNING", "DANGER", "TILT"). You either replace `tilt.tscn` or override the tilt mode's `slide_player`. With more than 3 warnings, the extra warnings have no default slide. The GMC guide says the tilt config settings **did not change** between 0.57 and 0.80.

---

## 11. Coils, switches and lights: the foundations for mechs

### Coils
- Define every coil in `coils:`. Devices (flippers, autofires, ball devices, diverters) then reference them.
- **`default_pulse_ms` defaults to 10ms. That's deliberately safe and "almost certainly too low."** Start low and increase. Examples range from 14ms (new Williams flipper at 70V) to over 100ms (a 1974 EM). Pulse strength depends on the coil, voltage, current, mech wear and temperature.
- **`allow_enable: true` is required** before any coil can be held on (flipper hold windings, long releases, lights on drivers). MPF refuses to enable a coil without it.
- **`default_hold_power` (0.0 to 1.0)** is the PWM hold after the pulse. For single-wound flippers, start around 0.125 and raise it until holds survive ball hits. Dual-wound hold windings can run at full power, **unless** you run them above their design voltage (e.g. 48V Stern coils at 70V). In that case, lower it.
- `default_pulse_power` gives PWM during the pulse, on some platforms. It lets you use longer, softer pulses, which suits drop target resets.
- `default_recycle: true/false` is a cool-down after a pulse, which stops a chattering switch from effectively holding a coil on. Keep it enabled. Fine tuning is platform specific (OPP `recycle_factor`, FAST `recycle_ms`).
- Pulses over about 255ms count as "enabled" on most platforms. Dual-wound vs single-wound: most new builds use **dual-wound with software power→hold timing** (simple, safe, less EMI). Single-wound PWM saves a driver per mech but needs hold tuning and may buzz.
- **Wiring:** coil diodes must be reversed (stripe to high voltage). Dual-wound coils have three lugs. Find the power winding (roughly 2 to 20 Ω) and the hold winding (roughly 50 to 200 Ω) with a meter, discard the highest reading pair, and connect HV to the common lug. **Establish common ground between logic and HV** before powering coils. The docs call floating grounds the most common cause of dead driver boards.

### Switches
- `switches:` entries take `number`, `type: NC` (**optos are normally closed**, unless an opto board inverts the signal; try NC first), `tags`, `debounce` (`quick`, `normal` or `auto`), and `ignore_window_ms`.
- Hardware debounce of about 2 to 4ms is normal, and going over about 4ms risks missed hits. For repeat hits such as swinging targets, use **`ignore_window_ms`** (a few hundred ms is fine). It doesn't affect hardware rules; use coil `recycle` for those. A standup example uses `debounce: quick`, `ignore_window_ms: 1000ms`.
- Special tags: `start`, `left_flipper` / `right_flipper`, `playfield_active`, `tilt_warning`, `slam_tilt`, and the `service_*` tags.
- Matrix switches need a diode per switch. Optos need current-limited emitters: 56 to 68 Ω at 1/2 W for 5V, or 220 Ω at 1 W for 12V, which runs hot. They also need direct inputs (they can't go in a matrix without extra logic).
- *Doc defect:* the YAML example in `mechs/switches/index.md` is garbled in the source.

### Lights
- Since 0.50, LEDs, matrix lamps, GI and flashers are all `lights:`, distinguished by `subtype` (`led`, `matrix`, `gi`) or `platform: drivers`.
- WS2812 needs `type: grb` (WS2811 is `rgb`). RGBW needs explicit channels, or chaining with `start_channel` / `previous` (0.54+). `light_stripes:` (spelled like that) defines a whole strip.
- Flashers and GI on drivers: a coil with `allow_enable: true`, then a light with `number: <coil>` and `platform: drivers`. Use `flasher_player:` to flash.
- Use white LEDs under coloured inserts. Run serial LEDs at about 5.5V with their own ground run (still a common ground). Budget roughly 60mA per LED.

---

## 12. Playfield mechanisms: how to configure each

### Flippers
```yaml
switches:
  s_left_flipper: {number: 1, tags: left_flipper}    # tags enable flipper_cancel & cradle events
coils:
  c_flipper_left_main: {number: 0, default_pulse_ms: 20}
  c_flipper_left_hold: {number: 1, allow_enable: true}
flippers:
  left_flipper:
    main_coil: c_flipper_left_main
    hold_coil: c_flipper_left_hold          # omit for single-wound
    activation_switch: s_left_flipper
    # enable_events: machine_reset_phase_3  # bench-test trick only
```
- **Single-wound:** a single `main_coil` with `allow_enable: true` and `default_hold_power: 0.125` on the coil. (*Doc typo:* "a value of 2 is 25%" should be 0.25.)
- **By default, flippers are only enabled during a game** (enable on `ball_started`, disable on `ball_will_end` and `service_mode_entered`). For bench testing without a trough or game, add `enable_events: machine_reset_phase_3`.
- When flippers are enabled, the switch **debounce is forced to `quick` and coil recycle is disabled**, whatever you configured.
- **Upper or secondary flippers** are configured the same way, with their own enable and disable events (e.g. `enable_upper_flippers`). They're excluded from ball search unless `include_in_ball_search: true`.
- **EOS switches are optional** with MPF, which uses timed power→hold. If present, you can use `eos_switch`, `use_eos: true`, `repulse_on_eos_open: true` and `eos_active_ms_before_repulse: 500`. That re-pulses on a knockdown, which lets you run lower hold PWM. Don't just cut EOS wires on an existing game that relies on them. The docs recommend wiring EOS anyway, for diagnostics.
- **Weak flippers:** define a second set of flipper devices on the same coils with `main_coil_overwrite: {pulse_power: 0.3}` (or `pulse_ms`), and toggle the sets with enable and disable events.
- **Temporarily disabled flippers:** the example uses a mode with timers that post `flipper_off` / `flipper_on`. Watch out: it posts `flippers_on` and `flippers_off` (plural) while the flippers listen for `flipper_on` and `flipper_off`, so it's inconsistent.
- Delayed, inverted, no-hold, reversed and multiple-flipper pages are **empty stubs**.

### Autofire coils: slingshots, pop bumpers
- Autofire coils are hardware rules that fire the coil with no host round-trip, since the host path is about 10ms or more. MPF still gets the switch event for scoring and sound.
```yaml
autofire_coils:
  ac_slingshot_left:
    coil: c_sling_left          # default_pulse_ms ~15 in example
    switch: s_sling_left        # both sling switches wired in parallel to one input
  ac_popbumper_left:
    coil: c_popbumper_left      # default_pulse_ms ~23 in example
    switch: s_popbumper_left
```
- Autofires are enabled on `ball_started` and disabled on `ball_will_end` and `service_mode_entered`. Debounce defaults to `quick` and recycle to `true` if unspecified. Override with `switch_overwrite` or `coil_overwrite`. Tune feel and sound with `default_pulse_ms` and `default_pulse_power`.
- **Gotchas from the Cobra/OPP example:**
  - A playfield with a `default_source_device` must exist for autofires to work.
  - On OPP the coil and switch must be on the **same board**, or an error is raised when the rule is enabled, not at startup.
  - Rules persist in the controller, so power-cycle it after changing them.
  - *Doc defect:* that example's YAML has broken indentation.
- Pop bumper hardware notes: a leaf switch closed by the skirt pin needs precise adjustment. A diode is only needed in a matrix. The page has drill, stencil and part numbers.

### Kickbacks and kicking targets
```yaml
kickbacks:
  ac_kickback:
    coil: c_kickback
    switch: s_kickback
ball_saves:
  kickback_ball_save:
    active_time: 5s
    enable_events: kickback_ac_kickback_fired   # covers a missed kick
    auto_launch: true
    balls_to_save: 1
```
Kicking targets use the same `kickbacks:` device. Event: `kickback_<name>_fired`.

### Drop targets
```yaml
drop_targets:
  front:  {switch: s_drop_front}
  middle: {switch: s_drop_middle}
  back:   {switch: s_drop_back}
drop_target_banks:
  vuk_bank:
    drop_targets: front, middle, back
    reset_coils: c_drop_reset          # put the shared reset coil on the BANK
    reset_on_complete: 1s
    reset_events:                      # retry resets for flaky mechs
      ball_started.1: 0
      ball_started.2: 1s
      ball_started.3: 2s
      machine_reset_phase_3: 0
```
- A single target can have its own `reset_coil`, and there may also be a knockdown coil.
- Events: `drop_target_<name>_down`, `_up`, `drop_target_bank_<name>_down`, `_up`, `_mixed`. Bank properties: `complete`, `down`, `up`.
- **Unreliable resets:** fix the mechanics and power first. Then try `psus: default: release_wait_ms: 50` (default 10). Try longer pulses with `default_pulse_power` of 0.5 to 0.8. Or reset several times; MPF skips the reset if the targets are already up.

### Standup, vari and spinner targets
- **Standups** are just switches, usually shots. Set `debounce: quick` and use `ignore_window_ms` against swing re-hits.
- **Vari-targets:** there's no config example (one switch per position plus a reset coil).
- **Spinners:** `spinners: basic_spinner: {switch: s_my_spinner, active_ms: 500}`. Events: `spinner_<name>_hit`, `_active`, `_inactive`, `_idle`, and labelled variants. Count spins with a variable_player or a counter on `spinner_<name>_hit`.

### Ball devices (troughs, plungers, scoops, VUKs, saucers, locks)
- A ball device is anything that holds and releases a ball. It's a state machine: idle, missing_balls, waiting_for_ball, waiting_for_ball_mechanical, ball_left, wait_for_eject, ejecting, failed_eject, eject_confirmed.
- Devices are chained by `eject_targets` (default: playfield). The playfield's `default_source_device` is where new balls come from. The minimal loop is **trough → plunger → playfield → (drain) → trough**.
- Key settings:
  - `ball_switches` (the count of switches sets capacity) or `entrance_switch` + `entrance_switch_full_timeout` + `ball_capacity`
  - `eject_coil`, `eject_coil_jam_pulse`, `jam_switch`, `eject_coil_enable_time`
  - `eject_targets`, `eject_timeouts`, `confirm_eject_type` (`target` by default, or `switch` with `confirm_eject_switch`)
  - `mechanical_eject`, `player_controlled_eject_event`
  - `tags` (`trough`, `home`, `drain`)
  - `debug: true`
- **Tag meanings:**
  - `trough`: may hold many balls.
  - `home`: balls here are "home". At startup and game end, MPF ejects balls from any device that isn't home, and a game can only start with all balls home.
  - `drain`: a ball entering means a live ball drained.
  - All three are needed on a modern single trough.
- Events: `balldevice_<name>_ball_enter`, `_ball_entered`, `_ball_eject_attempt`, `_ejecting_ball`, `_ball_eject_success`, `_ball_eject_failed`, `_ball_missing`, `_broken`, `_ball_count_changed`, `balldevice_captured_from_<pf>`, `balldevice_balls_available`. Properties: `balls`, `available_balls`, `state`.

#### Recommended modern trough + plunger (the most common new-build setup)
```yaml
switches:
  s_trough1: {number: 2, type: NC}      # NC for opto troughs; omit type for mechanical
  s_trough2: {number: 3, type: NC}
  s_trough3: {number: 4, type: NC}
  s_trough4: {number: 5, type: NC}
  s_trough5: {number: 6, type: NC}
  s_trough6: {number: 7, type: NC}
  s_trough_jam: {number: 8, type: NC}
  s_plunger: {number: 10}
  s_launch_button: {number: 11}
virtual_platform_start_active_switches: s_trough1, s_trough2, s_trough3, s_trough4, s_trough5, s_trough6
coils:
  c_trough_eject: {number: 4, default_pulse_ms: 20}
  c_plunger: {number: 5, default_pulse_ms: 20}
ball_devices:
  bd_trough:
    ball_switches: s_trough1, s_trough2, s_trough3, s_trough4, s_trough5, s_trough6, s_trough_jam  # include the jam switch
    eject_coil: c_trough_eject
    tags: trough, home, drain
    jam_switch: s_trough_jam
    eject_coil_jam_pulse: 15ms      # usually SHORTER than normal (normal pulse would kick 2 balls)
    eject_targets: bd_plunger
    eject_timeouts: 3s              # docs: ~2-4s for a trough
  bd_plunger:
    ball_switches: s_plunger        # the ball-present switch, NOT the launch button
    eject_coil: c_plunger           # omit for a purely mechanical plunger
    mechanical_eject: true          # spring plunger present (manual or combo)
    player_controlled_eject_event: s_launch_button_active   # or _inactive to launch on release
    eject_timeouts: 3s              # docs: ~3-5s for a plunger
playfields:
  playfield:
    default_source_device: bd_plunger
    tags: default
    enable_ball_search: true        # optional, off by default
```
Then tag every other playfield switch `playfield_active`.

Why each piece matters:
- **`virtual_platform_start_active_switches`** only applies with virtual or smart-virtual hardware. It pre-fills the trough so you can test without the machine.
- **`eject_timeouts` is the most important tuning value.** The default is 10s. Set it to the longest time a failed eject could take to fall back (roughly 2 to 4s for the trough, 3 to 5s for the plunger). The trough needs it too, because a player can plunge before the ball ever settles on the shooter switch.
- `player_controlled_eject_event` only ejects when MPF has enabled it, so posting that event at other times is harmless.
- **`confirm_eject_type: switch`** is only valid if the exit switch is always hit, can't be rolled back through, and no other ball can hit it. The docs say "almost never used."
- If the plunger ejects into another device (e.g. `bd_cannon`), set `eject_targets` on the plunger.
- In a two-stage drain (System 11), put the plunger in the `eject_targets` of the *second* device.

#### Plunger variants
| Type | Configure as |
|---|---|
| Spring plunger with lane switch | `ball_switches: s_plunger_lane`, `mechanical_eject: true`, no coil. It is the `default_source_device`. |
| Spring plunger, **no lane switch** | **Not a ball device.** The lane counts as part of the playfield. Set `default_source_device: bd_trough`. Start ball-save timers from `playfield_active` switches. What happens if MPF boots with a ball in the lane is a TODO in the docs. |
| Coil-fired launcher or catapult | `ball_switches`, `eject_coil`, `player_controlled_eject_event` |
| Combo (spring + autolaunch) | Coil-fired config **plus `mechanical_eject: true`** |

*Doc defect:* every plunger guide's "complete config" is captioned "standard coil-fired plunger", even in the mechanical and combo guides. The mechanical guide's version also includes an unused `s_launch_button`.

#### Older trough styles
- **Two coils, one switch per ball (System 11, early WPC):**
  - `bd_drain`: `ball_switches: s_drain`, `eject_coil: c_drain_eject`, `eject_targets: bd_trough`, `tags: drain`.
  - `bd_trough`: `ball_switches: s_trough1..3`, `eject_coil: c_trough_release`, `eject_targets: bd_plunger_lane`, `tags: home, trough`, `eject_timeouts: 3s`.
  - Release pulses over 255ms need `allow_enable: true` (e.g. `default_pulse_ms: 1000`).
- **Two coils, one trough switch (Gottlieb System 3):**
  - `bd_trough` uses `entrance_switch: s_trough_enter`, `entrance_switch_full_timeout: 500ms` and `ball_capacity: 3`. Optionally add `eject_coil_enable_time: 100ms`.
  - **Set `machine: balls_installed: 4`** so MPF can reconcile counts at boot when the entrance switch isn't active.
  - *Doc inconsistencies:* the prose says to add `default_pulse_power` for long releases, but the YAML uses `default_hold_power: 0.25`. The steps use `bd_plunger_lane`, but the complete config uses `bd_plunger`.
- **Classic single ball with shooter lane (EM to early-80s):**
  - `bd_drain` (`ball_switches: s_drain`, `eject_coil`, `eject_targets: bd_plunger_lane`, `tags: drain, home, trough`, `eject_timeouts: 3s`)
  - `bd_plunger_lane` (`mechanical_eject: true`, `eject_timeouts: 5s`)
  - `default_source_device: bd_plunger_lane`
- **Classic single ball, no shooter lane:** only `bd_drain`, with `default_source_device: bd_drain`.
- **Stern Spike trough on a non-Spike platform:** its switches are read over SPI (a 74HCT165), so you need the `spi_bit_bang` platform with `miso`, `cs` and `clock` pins. The docs **advise against buying one** unless you run Spike.
- **Stern opto boards** (515-0173/0174) only cover the first-ball and jam positions and invert the signal (no NC needed). Configure the trough as a mechanical one.
- **Bally/Williams opto boards** need current-limiting resistors on the emitter. **FAST opto boards** connect straight to 12V.

#### Scoops, VUKs, saucers
```yaml
ball_devices:
  bd_scoop:
    ball_switches: s_scoop
    eject_coil: c_scoop_eject        # default_pulse_ms ~20
    eject_timeouts: 1s
```
They eject straight back if nothing claims the ball. To hold for a show, add `queue_relay_player` on `balldevice_bd_scoop_ball_eject_attempt`, or a `ball_holds:` device. To lock for multiball, add a `multiball_locks:` device.

#### Troubleshooting ball devices
- Add `debug: true` to the device (and related switches and coils) and run `mpf both -t -v -V`.
- "Received unexpected ball" is usually harmless, e.g. a drain.
- A wrong ball count usually means a switch is missing from `ball_switches`, or a switch is badly adjusted: you see `State:1` followed immediately by `State:0`. A single ball may also be too light to roll over the eject shaft; add more balls.

### Diverters
- **Enabled** means armed and watching `activation_switches`. **Active** means physically powered. A typical ramp diverter is enabled when the lock is lit, activates on the ramp entry switch, and deactivates after `activation_time` or when the ball passes.
- Diverters are part of ball routing, so MPF sets them when routing ejects. Settings: `feeder_devices`, `targets_when_active`, `targets_when_inactive`. Properties: `active`, `enabled`, `eject_state`. Events: `diverter_<name>_enabling`, `_disabling`, `_activating`, `_deactivating`.
```yaml
dual_wound_coils:
  c_diverter_dualcoil:
    main_coil: c_diverter_upper_right_main
    hold_coil: c_diverter_upper_right_hold      # allow_enable: true
diverters:
  ramp_diverter:
    activation_coil: c_diverter_dualcoil
    type: hold
    activation_time: .5s
    activation_switches: s_r_rampexit, s_l_rampexit
    enable_events: ball_started
    disable_events: ball_ended
  up_down_two_coils:                 # up/down ramp or center post
    activation_coil: c_ramp2_up
    deactivation_coil: c_ramp2_down
    type: pulse
```
- Flippers handle dual-wound coils natively. `dual_wound_coils:` is for other devices.
- **Servo or stepper as a diverter:** map the positions to `diverter_<name>_activating` and `_deactivating` events. MPF doesn't wait for the servo or stepper to reach its position.
- Trap doors, up/down posts, blocking drop targets and toys like the Ringmaster all count as diverters.

### Magnets
```yaml
coils:
  magnet_coil: {number: , default_pulse_ms: 100, default_hold_power: 0.375}
magnets:
  magnet:
    magnet_coil: magnet_coil
    grab_switch: grab_switch
    release_ball_events: magnet_release
    fling_ball_events: magnet_fling
```
- Magnets are strong single-wound coils (roughly 2 to 10 Ω). **Add a diode if the magnet has none.**
- Events: `magnet_<name>_grabbing_ball`, `_grabbed_ball`, `_releasing_ball`, `_released_ball`, `_flinging_ball`, `_flinged_ball`.
- The **Stern Magnet Processor Board** (Metallica coffin) is driven through three `digital_outputs` (D6, D7, STROBE) using shows for the OFF, GRAB, DETECT and HOLD states. If MPF crashes while the board is in HOLD, it stays there until power-off.

### Motors, DC motors, steppers, servos, shakers
- **`motors:`** (position switches): a motor driven via a `digital_output` or driver, with `motor_left_output`, optional `motor_right_output`, `position_switches: !!omap`, `reset_position` and `go_to_position: {event: position}`. Event: `motor_<name>_reached_<position>`. Examples cover a motorised drop bank and the Ghostbusters slimer.
- **`dc_motors:`** need dedicated DC motor hardware (e.g. FAST FP-EXP-0051) and use `control_events` with `duration`, `power` and actions like `reverse_pulse`. The docs warn: **"If you are unsure whether your hardware works together, DO NOT EXPERIMENT."**
- **`steppers:`** home via `homing_mode: switch` + `homing_switch`, with `named_positions: {10: move_to_position_1}`. Position is tracked internally with no feedback.
- **`servos:`** use `positions: {0.0: servo1_down}`, `servo_min` / `servo_max`, `reset_position` and `reset_events`. There's no feedback on arrival, so choreograph with a show that posts the position events.
- **Shakers:** most aren't rated for continuous full power (use 10 to 30% PWM). Either a coil with a low `default_hold_power` driven via coil_player or a show, or the `shakers:` device, which **is only supported on FAST (EXP-1313)**.

### Tilt bob, accelerometers, score reels
- **Tilt bob:** a normal switch with `tags: tilt_warning`, plus `- tilt` in `modes:`.
- **Accelerometers:** `device.accelerometers.X.value` is an (x, y, z) tuple, and events are configured from G thresholds. See the hardware pages for P3-ROC and MMA8451.
- **Score reels (EM):** `score_reels:` (`coil_inc`, `switch_0`, `limit_hi`/`limit_lo`) grouped into `score_reel_groups:` (`reels:` from high to low digit with `None` placeholders, `chimes:`, `lights_tag:`). Event: `reel_<name>_advanced`.

---

## 13. Common gotchas (summary)

1. **Ball search is off by default.** Enable it per playfield, and tag every non-device playfield switch `playfield_active`, but never the plunger lane switch.
2. **Tune `eject_timeouts`.** The 10s default causes slow multiball ball adds and slow eject confirmation whenever balls are already on the playfield.
3. **The trough needs `trough, home, drain` tags.** Include the jam switch in `ball_switches` too. Make the jam pulse shorter than the normal pulse.
4. **Coils default to a 10ms pulse and can't be held without `allow_enable: true`.** If flippers "click but don't move", raise the pulse.
5. **Flippers only work during a game.** For bench testing, use `enable_events: machine_reset_phase_3`.
6. **Tag flipper switches `left_flipper` / `right_flipper`** to get `flipper_cancel` and `flipper_cradle`.
7. **Logic blocks complete once by default.** You need both `reset_on_complete: true` and `disable_on_complete: false`, but `reset_on_complete: false` if you query `.completed`.
8. **Use `_hit` for scoring and `_updated` for lights and shows.** `_updated` re-fires on mode restart.
9. **Scoring stacks across modes** unless the higher-priority entry blocks.
10. **Define distinct shots per mode** for mode-specific behaviour. Sequence shots can't join shot groups directly.
11. **Physical locks:** set `replace_balls_in_play` and `balls_to_replace` (capacity minus 1) together, or the ball count is wrong or the game stalls with no ball.
12. **Built-in modes (tilt, bonus, credits, high_score, match, service) must be listed in `modes:`.** Bonus and credits also need their own mode folders. Attract and game are added automatically.
13. **A plunger with no switch is not a ball device.** Make the trough the source device.
14. **Optos are `type: NC`** unless the opto board inverts.
15. **Autofire and flipper rules override your debounce and recycle settings.** On OPP, the switch and coil for an autofire must be on the same board.
16. **Establish common ground** before powering any coils.
17. **0.80 display:** replace `slides:`, `widgets:` and inline widget YAML from these pages with Godot scenes. `slide_player` stays, using `tokens:`. Bonus entries use `entry:` and the single `bonus_entry` event.

---

## Source documents used

All paths are under `mpf-docs-dev/docs/`.

**game_logic/:** index.md; achievements/index.md, achievement_groups.md; ball_holds.md; ball_locks.md; ball_saves/index.md, center_post.md; ball_search/index.md, configuring_ball_search.md; ball_start_end.md; ball_tracking.md; bonus/index.md, configuring_bonus.md; combo_switches.md; credits.md; extra_balls.md; high_scores/index.md, high_scores_in_ems.md; logic_blocks/index.md, counters.md, accruals.md, sequences.md, state_machines.md, common_problems.md, integrating_logic_block_and_slides.md, integrating_logic_blocks_and_lights.md, integrating_logic_blocks_and_shows.md, persisting_state_in_a_player_variable.md, scoring_based_on_logic_blocks.md; match_mode.md; modes/index.md, attract.md, game.md, credits.md, high_score.md, tilt.md, custom_modes.md, modes_as_game_logic.md; multiballs/index.md, multiball_locks.md, multiball_with_traditional_ball_lock.md, multiball_with_virtual_ball_lock.md, multiball_with_multiple_lock_devices.md, add_a_ball_multiball.md (stub); players.md; replays.md (stub); scoring/index.md, ss_style_score_queues.md; service_mode.md; shots/index.md, shot_group.md, shot_profiles.md, sequence_shots.md, integrate_shots_with_shows_lights_sounds_widgets_or_slides.md; skill_shot.md; tilt/index.md, overwrite_tilt_slides.md; timed_switches.md; timers.md; video_modes.md (stub).

**mechs/:** index.md; accelerometers.md; autofire_coils.md; ball_devices/index.md, troubleshooting.md; coils/index.md, dual_vs_single_wound.md, dual_wound_coils.md, hold_power.md, pulse_power.md, recycle.md; dc_motors.md; diverters/index.md, dual_coil_diverter.md, servo_as_diverter.md, stepper_as_diverter.md, up_down_ramps.md; flippers/index.md, dual_wound.md, single_wound.md, eos_switches.md, enabling_secondary_flippers.md, weak_flippers.md, disabled_flippers.md, delayed/inverted/multiple/no_hold/reversed (stubs); kickbacks.md; lights/index.md, leds.md, ws2812.md, gis.md, flashers.md, matrix_lights.md, coils_as_lights.md, lights_versus_leds.md; loops.md; magnets/index.md, stern_magnet_pcb.md; motors.md; playfields/index.md, ball_tracking.md, playfield_balls_vs_balls_in_play.md, playfield_transfer.md; plungers/index.md, mechanical_with_switch.md, mechanical_no_switch.md, coil_fired.md, auto_manual.md; pop_bumpers/index.md; scoops.md; score_reels.md; servos/index.md, servo_sequence.md; shaker.md; slingshots.md; spinners.md; steppers.md; switches/index.md, mechanical_switches.md, optos.md, debounce.md, breakout_boards.md, proximity_switches.md, reed_switches.md, rollover_switches.md, service_and_door_switches.md, start_tournament_and_launcher_buttons.md, switch_controller.md; targets/index.md, stationary_targets.md, kicking_targets.md, vari_targets.md, drop_targets/index.md, drop_target_bank.md, fixing_drop_target_reset_issues.md; tilt_bob.md; troughs/index.md, modern_opto.md, modern_mechanical.md, two_coil_multiple_switches.md, two_coil_one_switch.md, classic_single_ball.md, classic_single_ball_no_shooter_lane.md, spike_trough.md.

**Cross-checked for 0.80 differences:** config/mode.md (mode defaults); gmc/guides/tilt_mode.md; gmc/guides/bonus_mode.md; gmc/reference/bonus.md; gmc/reference/slide_player.md.
