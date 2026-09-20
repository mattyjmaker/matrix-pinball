# 07 - Programming MPF: Architecture, Custom Code, BCP, Testing and the Events Reference

This file covers the developer side of the MPF docs (`docs/code/**`) and the full built-in event reference (`docs/events/**`). The source is the MPF documentation `dev` branch, which documents MPF 0.80 (released April 2026, uses the Godot Media Controller "GMC"). A few event pages already mention 0.81 features.

> **How reliable is this part of the docs?** Much of `docs/code` was written in the MPF 0.3x-0.5x era and has only been partly updated. It still mentions the Kivy-based MPF-MC, `mpf-mc` repos, `self.machine.leds`, Python 3.4 output and so on. The API reference pages are auto-generated docstrings (signatures plus one-liners), so they are accurate about method names but thin on explanation. Where the docs contradict each other or are clearly stale, this file flags it with **[Contradiction]** or **[Stale]**. Nothing here is invented. Where I built a small example from API signatures because the docs leave one out, it is labelled *illustrative*.

---

## Part 1 - MPF internal architecture

### 1.1 The big picture

MPF is an **event-driven** framework: "just about everything is either posting an event or responding to an event that was posted" (events/index.md). A running MPF has:

- **One machine controller** (`mpf.core.machine.MachineController`), reachable everywhere as `self.machine`. It owns every core controller, device collection, mode and platform.
- **Core controllers**, which are singletons hanging off `self.machine.<name>`: event manager, switch controller, ball controller, mode controller, device manager, platform controller, BCP, and so on.
- **Devices**, both physical (coils, switches, lights, ball devices, flippers) and logical (shots, counters, timers, achievements, multiballs, ball saves). They live in collections at `self.machine.<collection>.<name>`.
- **Hardware platforms**, the interfaces to real controller boards (FAST, OPP, P-ROC, SPIKE, LISY, RPi...) or virtual ones. They live in `self.machine.hardware_platforms['<name>']`.
- **Config players**, which turn config-file entries keyed by event name (`light_player:`, `show_player:`, `variable_player:`...) into actions. They live at `self.machine.<x>_player`.
- **Modes**, which are priority-ordered bundles of config and optional Python code that start and stop on events. They live at `self.machine.modes.<name>`.
- **BCP**, the Backbox Control Protocol. It is a TCP text protocol from MPF (the "pin controller") to the media controller (GMC in 0.80).

### 1.2 The machine controller (`self.machine`)

`class mpf.core.machine.MachineController(options: dict, config: MpfConfig)`, based on `LogMixin`. `options` are the command-line options and `config` is the loaded machine config.

| Method | What it does (per docs) |
|---|---|
| `initialise()`, `initialise_core_and_hardware()`, `initialise_mpf()` | Boot stages: load core modules and hardware, then MPF. |
| `register_boot_hold(hold)` / `clear_boot_hold(hold)` | Hold boot until a component clears its hold. `init_done()` is "called when init is done and all boot holds are cleared". |
| `add_platform(name)` | Makes another hardware platform available. The name must match a file in `mpf/platforms` (without `.py`). |
| `set_default_platform(name)` | The platform used when a device or device class does not name one. |
| `get_platform_sections(platform_section, overwrite)` | Returns the platform for a section. |
| `create_data_manager(config_name)` | Returns a `DataManager` for persistent data. |
| `register_monitor(monitor_class, monitor)` | Central registry (a "dictionary of sets") that monitors use, for example to watch player variables or switches. |
| `reset()` | "Sets up everything from scratch without reloading the config files and assets from disk." Called after a game ends and before attract starts. |
| `run()` | Starts the main run loop. |
| `stop(reason=None)` / `shutdown()` | Graceful exit and shutdown. |
| `add_crash_handler(handler)` | Called on a crash, for example to restore output and logging. |
| `validate_machine_config_section(section)` | Validates a config section. |
| `verify_system_info()` | Dumps Python version, executable, platform and architecture to the log. |

**[Stale]** machine.md says "See the Overview & Tour of MPF code for details", but no such page exists in the current docs tree.

### 1.3 Core components (`self.machine.<name>`)

| Attribute | Class | Role |
|---|---|---|
| `events` | `mpf.core.events.EventManager` | Registers handlers and posts events (see 1.5). |
| `switch_controller` | `mpf.core.switch_controller.SwitchController` | Tracks all switches, receives switch changes from platforms and turns them into events and handlers. |
| `ball_controller` | `mpf.core.ball_controller.BallController` | Tracks all balls: `collect_balls(target='home, trough')`, `are_balls_collected(target)`, `dump_ball_counts()`, `add_captured_ball(source)`, and `request_to_start_game()`, which rejects a start if too many balls are missing. |
| `mode_controller` | `mpf.core.mode_controller.ModeController` | Loads and manages modes: `is_active(mode_name)`, `dump()`, `register_load_method(...)`, `register_start_method(...)` (plugin hooks, where higher priority is called first), `remove_start_method`, `set_mode_state`. |
| `device_manager` | `mpf.core.device_manager.DeviceManager` | Creates devices from config (`create_devices`, `load_devices_config`, `initialize_devices`), wires `control_events` (`get_device_control_events`, `create_machinewide_device_control_events`) and keeps the monitorable-device registry (`register_monitorable_device`, `notify_device_changes`, `get_monitorable_devices`). |
| `platform_controller` | `mpf.core.platform_controller.PlatformController` | Installs **hardware rules** (switch to coil rules executed on the controller board). See 1.8. |
| `bcp` | `mpf.core.bcp.bcp.Bcp` | BCP module. The only documented method is `send(bcp_command, **kwargs)` ("Emulate legacy send"). |
| `light_controller` | `mpf.core.light_controller.LightController` | Light subsystem init and light monitoring. |
| `show_controller` | `mpf.core.show_controller.ShowController` | Show priorities, restores, starting and stopping: `create_show_config(name, priority, speed, loops, sync_ms, manual_advance, show_tokens, events_when_*...)`, `play_show_with_config(config, mode=None, start_time=None)`, `register_show`, `replace_or_advance_show`, `get_next_show_id`. |
| `placeholder_manager` | `mpf.core.placeholder_manager.PlaceholderManager` | Templates and placeholders (the `{...}` dynamic values and conditions). |
| `settings` | `mpf.core.settings_controller.SettingsController` | Operator settings: `add_setting`, `get_setting_value`, `set_setting_value`, `get_settings`, `get_setting_value_label`, `get_setting_machine_var`. |
| `service` | `mpf.core.service_controller.ServiceController` | `start_service()`, `stop_service()`, `is_in_service()`, `get_switch_map()`, `get_coil_map()`, `get_light_map()`, `add_technical_alert(device, issue)`. |
| `auditor` | `mpf.plugins.auditor.Auditor` (plugin) | Audit log of switches, events, player vars and shots: `enable()`, `disable()`, `audit(...)`, `audit_event`, `audit_player`, `audit_shot`, `audit_switch`, `enabled`. |
| `info_lights` | `mpf.plugins.info_lights.InfoLights` (plugin) | Backbox lights for game over, tilt, player up and ball number (EM and early SS style). No public methods are documented. |
| `switch_player` | `mpf.plugins.switch_player.SwitchPlayer` (plugin) | Plays back switch sequences from config, for testing. |
| `text_ui` | `mpf.core.text_ui.TextUi` | The console text UI. `stop()` restores the console. |
| `twitch_bot` | `mpf.plugins.twitch_bot.TwitchBot` | **Removed**. The page warns "removed in MPF 0.58+ and 0.81+". **[Contradiction]**: those version numbers are odd and 0.58 does not otherwise exist in the docs. Either way, treat it as gone in 0.80. |
| `delay` | `mpf.core.delays.DelayManager` | The machine-wide delay manager (modes have their own, `self.delay`). |
| `variables` | (machine variables) | `get_machine_var`, `set_machine_var`, `configure_machine_var` (from variables_in_code.md). |
| `game` | The game mode | `None` when no game is running. `self.machine.game.player` is the current player. |

### 1.4 Boot and reset sequence

From `flowcharts/mpf_boot.md`. This page is outside the code section, but it is the only architecture walkthrough in the docs. **[Stale]**: it still mentions scriptlets and "asset managers".

1. Load `mpf/mpfconfig.yaml`, then the machine config (which may include others).
2. Set the default hardware platform.
3. Load system modules in the order `mpfconfig.yaml` specifies: config_processor, timing, event manager, mode controller, device manager (loads device modules and creates machine-wide devices), switch controller, ball controller, light controller, bcp, logic blocks, variable player/scoring, shot profile manager.
4. Register system events (shutdown, quit...).
5. `init_phase_1`: the event player initialises.
6. `init_phase_2`: ball controller and playfield eject targets, score reels, BCP connections, switch events, and machine-wide device `control_events`.
7. Load plugins.
8. `init_phase_3`: ball locks, diverters register switches, shot profiles.
9. Load scriptlets (now `custom_code`).
10. `init_phase_4`: drop targets read their switches, auditor, OSC, asset loading, and the mode controller loads all modes.
11. `init_phase_5`: machine-wide light scripts and light_player entries.
12. `machine.reset()`, which posts `machine_reset_phase_1` (ball device switches init; BCP sends `reset` to media controllers), then `machine_reset_phase_2` (known-ball count; eject targets), then `machine_reset_phase_3` (reset ball locks, drop targets and banks, multiballs; enable GI; **attract mode starts**, because it is a handler of `machine_reset_phase_3`).

All `init_phase_*` and `machine_reset_phase_*` events are **queue events**, so a handler can hold the phase open. `init_done` marks the end of the one-time boot. The reset phases are posted again on later resets, for example after leaving service mode.

### 1.5 The event system

**Concepts** (events/overview/*.md):

- An event is just a string. You never need to define it ahead of time, and posting one that nobody handles is fine. Names are **not case sensitive** (they are lowercased internally).
- Things *post* events (switches, player-variable changes, timers, modes starting, ball drains...) and things *handle* them. Config players register handlers on the event names you key them with. Devices register handlers for their `*_events:` settings, the "device control events". `events_when_*:` settings let you name the events a device posts.
- Events can carry **keyword arguments**, such as `ball_started` with `ball`, `player`, `balls_remaining` and `is_extra_ball`. The log shows them: `Event: ======'ball_started'====== Args={'player': 2, 'ball': 3}`.
- Events are processed **serially**. If one is posted while another is being handled, it goes on a queue and is processed after the current one.

**Handler priorities** (overview/priorities.md): the default priority is 1. Handlers are called from highest to lowest, and only the order of the numbers matters. **Handlers registered by modes automatically get the mode's priority**, so higher-priority modes see an event first and can "block" it from lower modes.

**Event types:**

| Type | Posted with | Semantics |
|---|---|---|
| Basic | `events.post(event, callback=None, **kwargs)` | Every handler gets the same kwargs. |
| Queue | `events.post_queue(event, callback, **kwargs)` | A handler may register a *wait*, and the callback does not run until every wait is released. `game_ending` is the classic example: match and high score block it until they finish. Config users create these with `queue_event_player:` and `queue_relay_player:`. |
| Boolean | `events.post_boolean(event, callback=None, **kwargs)` | Handlers are called one at a time. **If any handler returns `False`, the rest are skipped**, and the callback still runs with `ev_result=False`. Used by `request_to_start_game`, `player_add_request` and `machine_request_shutdown`. |
| Relay | `events.post_relay(event, callback=None, **kwargs)` | The kwargs a handler returns are passed on to the next handler. Examples: `ball_drain` (a ball save "claims" balls by reducing `balls`), `balldevice_(name)_ball_enter` (`unclaimed_balls`) and `ball_start_target` (`target` can be changed). |
| Async variants | `post_async`, `post_queue_async`, `post_relay_async` | Return an `asyncio` Future that finishes when all handlers are done or the locks are released. `post_relay_async` returns the result. |

The overview says config files only expose basic and queue events. Boolean and relay events, and the async forms, are for Python.

**EventManager API** (`self.machine.events`):

- `add_handler(event, handler, priority=1, blocking_facility=None, **kwargs) -> EventHandlerKey`. **The handler must accept `**kwargs`**; the manager enforces this. Extra kwargs you give here are passed to the handler, and event-level kwargs win if names clash.
- `add_async_handler(...)` registers a coroutine as a handler.
- `replace_handler(event, handler, priority=1, **kwargs)`.
- Removal: `remove_handler(method)` (from every event), `remove_handler_by_event(event, handler)` (ignores kwargs), `remove_handler_by_key(key)`, `remove_handlers_by_keys(list)`, `remove_all_handlers_for_event(event)` (use carefully; it is used for one-shot init events).
- `does_event_exist(name)` returns True if any handler is registered.
- `wait_for_event(name)` and `wait_for_any_event([names])` return Futures, for async code.
- `get_event_and_condition_from_string(s)` splits `"event{cond}"` into the name and a BoolTemplate.
- `process_event_queue()`.

Doc example: `self.machine.events.post_queue('pizza_time', self.pizza_done)`.

**Conditional events** (overview/conditional.md) are what you use in YAML, and the same condition syntax works anywhere an event name is accepted:

```yaml
slide_player:
  ball_started{ball==1}: first_ball_intro
  ball_started{ball>1}: lets_go
  ball_started{current_player.score < 10000 and ball == 3}: you_stink
  ball_started{ball == 3 and device.counters.your_mode_counter.value > 5}: nearly_did_all_modes
```

- Inside a condition you can use the event kwargs, `current_player.x`, `players[i].x`, `machine.x` (machine vars), `game.x`, `settings.x` and `device.<collection>.<name>.<attribute>`.
- Comparisons: `== != > >= < <=`.
- Operators: `+ - * / // % ^` (power), `^=` (bit xor), `not`, `and`, `or`, and parentheses.
- **Subscriptions**: a config player key that is only a condition, for example `"{machine.test_machine_var == 23}": {led4: red}`, is applied while the condition is true and removed when it becomes false. This works for some variables only.

### 1.6 Time, delays and asyncio

There is **no dedicated clock or asyncio architecture page** in the current docs. What they do say:

- The release notes say MPF uses asyncio for async operations and loops, and the 0.57.x line "changed how the MPF event loop is managed" for Python 3.14.
- **DelayManager** (`mpf.core.delays.DelayManager`) is the supported way to schedule callbacks. It has a machine-wide instance at `self.machine.delay`, and each mode has `self.delay`, whose delays are **cancelled automatically when the mode stops**. Methods:
  - `add(ms, callback, name=None, **kwargs)` returns the name or a UUID4.
  - `add_if_doesnt_exist(ms, callback, name, **kwargs)`.
  - `reset(ms, callback, name, **kwargs)` deletes and re-adds.
  - `remove(name)`, `check(name)`, `clear()`.
  - `run_now(name)` runs the callback now and cancels the future run.
- Async helpers:
  - `events.post_async` / `wait_for_event`.
  - `switch_controller.wait_for_switch(switch, state=1, only_on_change=True, ms=0)` and `wait_for_any_switch([...])`, where state 2 means "opposite to current".
  - `Util.race`, `Util.first`, `Util.any`, `Util.cancel_futures`, `Util.raise_exceptions`.
  - `AsyncMode` is the base class of the built-in game, high_score, match and service modes.
- In tests, the clock is a **test clock** that you move with `advance_time_and_run()` (see Part 4).

### 1.7 Devices

- Collections are at `self.machine.<collection>`, for example `self.machine.flippers.right_flipper`. They can be accessed as attributes **or** items (`self.machine.flippers['right_flipper']`). The coils page adds that you "can also get devices by tag or hardware number. See the DeviceCollection documentation", but that page does not exist in the tree.
- "Devices" include logical game-logic objects such as achievements, ball holds, extra balls, counters and timers.
- Common method patterns on device pages:
  - `event_<action>(**kwargs)` is the handler bound to the device's `<action>_events:` control events. For example, `Driver.event_pulse` is what `pulse_events:` calls.
  - `get_placeholder_value(item)` / `subscribe_attribute(item, machine)` make device attributes usable in `{device.x.y.z}` placeholders and subscriptions.
- Machine-wide devices are `SystemWideDevice`s (for example `Driver`). Devices defined in mode configs are created and loaded by `Mode.create_mode_devices()` / `load_mode_devices()`.

API summary of the device collections (methods excluding logging, `event_*` and placeholder boilerplate):

| Collection | Class | Key methods |
|---|---|---|
| accelerometers | `devices.accelerometer.Accelerometer` | `get_level_xyz/xz/yz`, `update_acceleration` |
| accruals / counters / sequences | `devices.logic_blocks.Accrual/Counter/Sequence` | `enable`, `disable`, `hit`/`count`, `complete`, `reset`, `restart`, `get_start_value` (counters also `check_complete`, `stop_ignoring_hits`) |
| achievement_groups | `AchievementGroup` | `enable`, `disable`, `rotate_left/right`, `select_random_achievement`, `start_selected`, `member_state_changed` |
| achievements | `Achievement` | `enable`, `disable`, `start`, `stop`, `complete`, `reset`, `select`, `unselect` |
| autofires | `AutofireCoil` | `enable`, `disable` |
| ball_devices | `ball_device.BallDevice` | `eject(...)`, `eject_all`, `request_ball`, `add_incoming_ball`, `find_path_to_target`, `find_next_trough`, `setup_player_controlled_eject`, `wait_for_ready_to_receive`, `lost_*`, `expected/unexpected_ball_received` |
| ball_holds | `BallHold` | `enable`, `disable`, `release_one`, `release_all`, `release_balls`, `release_one_if_full`, `is_full`, `remaining_space_in_hold`, `reset` |
| ball_routings | `BallRouting` | `enable`, `disable` |
| ball_saves | `BallSave` | `enable`, `disable`, `timer_start`, `early_ball_save`, `delayed_eject` |
| coils | `devices.driver.Driver` | `pulse(pulse_ms=None, pulse_power=None, max_wait_ms=None)`, `enable(pulse_ms, pulse_power, hold_power)`, `disable()`, `get_and_verify_*`. A plain `enable()` without a hold setting needs `allow_enable: True` in config, as a safety measure. |
| combo_switches, timed_switches, state_machines, shot_profiles, sequence_shots | ... | `enable` (sequence_shots also `reset_all_sequences`) |
| digital_outputs | `DigitalOutput` | `enable`, `disable`, `pulse` |
| diverters | `Diverter` | `enable`, `disable`, `activate`, `deactivate`, `reset`, `schedule_deactivation` |
| dmds / rgb_dmds | `Dmd` / `RgbDmd` | `update` |
| drop_targets | `DropTarget` | `knockdown`, `reset`, `enable_keep_up`, `disable_keep_up`, `add_to_bank`, `remove_from_bank` |
| drop_target_banks | `DropTargetBank` | `reset`, `member_target_change` |
| dual_wound_coils | `DualWoundCoil` | `pulse`, `enable`, `disable` |
| extra_balls / extra_ball_groups | `ExtraBall` / `ExtraBallGroup` | `light`, `award`, `is_ok_to_light`, `is_ok_to_award` (groups: `award_lit`, `award_disabled`) |
| flippers | `Flipper` | `enable`, `disable`, `sw_flip`, `sw_release` |
| hardware_sound_systems | `HardwareSoundSystem` | `play`, `play_file`, `text_to_speech`, `set_volume`, `increase/decrease_volume`, `stop_all_sounds` |
| kickbacks | `Kickback` | `enable`, `disable` |
| lights | `devices.light.Light` | `color(...)`, `on`, `off`, `get_color`, `remove_from_stack_by_key`, `clear_stack`, `color_correct`, `gamma_correct`, `get_hw_numbers` |
| light_rings / light_stripes | `LightRing` / `LightStrip` | `color`, `get_token` |
| magnets | `Magnet` | `enable`, `disable`, `grab_ball`, `release_ball`, `fling_ball`, `reset` |
| motors | `Motor` | `go_to_position`, `reset` |
| multiball_locks | `MultiballLock` | `enable`, `disable`, `reset_all_counts`, `reset_count_for_current_player` |
| multiballs | `Multiball` | `enable`, `disable`, `start`, `stop`, `add_a_ball`, `start_or_add_a_ball`, `reset` |
| playfields | `Playfield` | `add_ball`, `add_missing_balls`, `ball_arrived`, ball-search block, unblock, enable and disable handlers |
| playfield_transfers | `PlayfieldTransfer` | `transfer` |
| psus | `PowerSupplyUnit` | `get_wait_time_for_pulse`, `notify_about_instant_pulse` |
| score_queues | `ScoreQueue` | `score` |
| score_reels / score_reel_groups | `ScoreReel` / `ScoreReelGroup` | `set_destination_value`, `wait_for_ready`, `check_hw_switches` / `set_value`, `int_to_reel_list`, `light`, `unlight` |
| segment_displays | `SegmentDisplay` | `add_text`, `remove_text_by_key`, `set_flashing` |
| servos | `Servo` | `go_to_position`, `set_speed_limit`, `set_acceleration_limit`, `reset` |
| shots | `Shot` | `hit()` (the shot must be enabled), `advance`, `jump`, `enable`, `disable`, `reset`, `restart` |
| shot_groups | `ShotGroup` | `enable`, `disable`, `rotate`, `rotate_left/right`, `enable/disable_rotation`, `reset`, `restart` |
| show_queues | `ShowQueue` | `enqueue_show` |
| steppers | `Stepper` | `move_to_position`, `reset`, `stop` |
| switches | `devices.switch.Switch` | `add_handler`, `remove_handler`, `get_ms_since_last_change` |
| timers | `devices.timer.Timer` | `start`, `stop`, `pause`, `reset`, `restart`, `add(ticks)`, `subtract`, `jump(ticks)`, `set_tick_interval`, `change_tick_interval`, `timer_complete` |

### 1.8 Hardware platforms and hardware rules

Platforms live in `self.machine.hardware_platforms['fast']` and so on. Each one is a class that mixes in the capability interfaces from `mpf.core.platform`: `SwitchPlatform`, `DriverPlatform`, `LightsPlatform`, `ServoPlatform`, `StepperPlatform`, `DmdPlatform`, `RgbDmdPlatform`, `SegmentDisplayPlatform` (or `SegmentDisplaySoftwareFlashPlatform`), `HardwareSoundPlatform`, `AccelerometerPlatform`, `I2cPlatform`. The methods they implement follow a common vocabulary: `initialize`, `stop`, `configure_switch`, `configure_driver`, `configure_light`, `parse_light_number_to_channels`, `configure_servo`, `configure_stepper`, `configure_dmd`, `configure_segment_display`, `get_hw_switch_states`, `get_info_string`, `clear_hw_rule` and the `set_*_rule` family.

| Platform key | Class | Capabilities |
|---|---|---|
| `fast` | `platforms.fast.fast.FastHardwarePlatform` | servo, lights, DMD, switches, drivers |
| `opp` | `platforms.opp.opp.OppHardwarePlatform` | lights, switches, drivers |
| `p_roc` / `p3_roc` | `PRocHardwarePlatform` / `P3RocHardwarePlatform` | switches, drivers, DMD and segment displays (P-ROC); I2C and accelerometer (P3-ROC) |
| `spike` | `SpikePlatform` (Stern SPIKE) | switches, lights, drivers, DMD, stepper |
| `lisy` | `LisyHardwarePlatform` | switches, lights, drivers, segment displays, hardware sound |
| `rpi` | `RaspberryPiHardwarePlatform` | switches, drivers, servo, I2C |
| `system11` / `snux` | `System11OverlayPlatform` / `SnuxHardwarePlatform` | overlay for System 11 A/C relay |
| `virtual` | `VirtualHardwarePlatform` | everything (the default when no hardware is present) |
| `smart_virtual` | `SmartVirtualHardwarePlatform` | virtual plus simulated ball movement (`add_ball_to_device`) |
| `virtual_pinball` | `VirtualPinballPlatform` | VPX bridge (`vpx_changed_lamps` etc.) |
| `drivers` | `DriverLightPlatform` | lights on driver outputs |
| `light_segment_displays` | `LightSegmentDisplaysPlatform` | segment displays made from lights |
| `openpixel` / `fadecandy` | `OpenpixelHardwarePlatform` / `FadecandyHardwarePlatform` | LEDs |
| `osc` | `OscPlatform` | lights and switches via OSC |
| `i2c_servo_controller`, `pololu_maestro` | ... | servos |
| `pololu_tic`, `step_stick`, `trinamics_steprocker` | ... | steppers |
| `mma8451` | `MMA8451Platform` | accelerometer |
| `mypinballs` | `MyPinballsHardwarePlatform` | 7-segment |
| `pin2dmd`, `rpi_dmd`, `smartmatrix` | ... | RGB DMD |
| `smbus2` | `Smbus2` | I2C on Linux |
| `spi_bit_bang` | `SpiBitBangPlatform` | switch reading via SPI bit-bang |

**Hardware rules** (`self.machine.platform_controller`) let the controller board fire a coil directly from a switch, with no Python latency. This is how flippers, slingshots and pops work.

| Method | Behaviour |
|---|---|
| `set_pulse_on_hit_rule(enable_switch, driver, pulse_setting=None)` | Always the full pulse, even if the switch is released. |
| `set_delayed_pulse_on_hit_rule(enable_switch, driver, delay_ms, pulse_setting=None)` | As above, with the pulse delayed accurately in hardware. |
| `set_pulse_on_hit_and_release_rule(...)` | Pulse, cancelled when the switch is released. |
| `set_pulse_on_hit_and_enable_and_release_rule(..., pulse_setting, hold_settings)` | Pulse then hold; cancel on release (flipper without EOS). |
| `set_pulse_on_hit_and_release_and_disable_rule(enable_switch, eos_switch, driver, pulse_setting, eos_settings)` | Pulse, cancelled on release or when the EOS/disable switch is hit, with repulse. |
| `set_pulse_on_hit_and_enable_and_release_and_disable_rule(enable_switch, eos_switch, driver, pulse, hold, eos_settings)` | Pulse then hold, switching from pulse to hold at EOS, with repulse when EOS opens. |
| `clear_hw_rule(rule)` | Removes a rule. |

The settings objects are `SwitchRuleSettings`, `DriverRuleSettings`, `PulseRuleSettings`, `HoldRuleSettings` and `RepulseRuleSettings`. Every method returns a `HardwareRule`.

**Custom platforms and custom devices:** the docs have **no how-to** for writing a new hardware platform or a new device class. The only guidance is:

- For custom mechanisms (such as the Demolition Man claw), write a `custom_code` class that drives existing coils and switches (Part 2).
- `add_platform(name)` requires a file in `mpf/platforms`, meaning an MPF source contribution.
- In practice, study the existing platform classes and the mixins above.

### 1.9 Switch controller in depth

`self.machine.switch_controller`:

- `add_switch_handler(switch_name, callback, state=1, ms=0, return_info=False, callback_kwargs=None) -> SwitchHandler`.
  - `state=1` means inactive to active, and `state=0` means active to inactive.
  - `ms` fires only after the switch has been held in that state for that many ms.
  - With `return_info=True`, the callback receives `switch_name`, `state` and `ms`. Otherwise it is called **with no arguments**.
- `add_switch_handler_obj(switch, ...)` is the same but takes a Switch object.
- `remove_switch_handler(switch_name, callback, state=1, ms=0)` only works if you pass exactly the same arguments you registered with. Alternatives: `remove_switch_handler_by_key(key)` / `_by_keys(list)` and `remove_switch_handler_obj(...)`.
- `is_active(switch, ms=None)`, `is_inactive(switch, ms=None)`, `is_state(switch, state, ms=0)`. **[Contradiction]**: the API says these take a Switch *object*, but the Claw example passes switch *names* (`is_active('s_elevator_hold')`).
- `process_switch(name, state, logical=False, timestamp=None)`, `process_switch_by_num(num, state, platform, logical=False, timestamp=None)`, `process_switch_obj(obj, state, logical, timestamp=None)`. These are what platforms, the keyboard and OSC call. `logical=False` means NC switches get inverted.
- `add_monitor(cb)` / `remove_monitor(cb)` receive `MonitoredSwitchChange` objects.
- `get_active_event_for_switch(name)`, `log_active_switches()`.
- `update_switches_from_hw()` re-reads hardware silently. `verify_switches()` compares against hardware and only logs warnings.
- `wait_for_switch(...)` and `wait_for_any_switch(...)` are async.
- `register_switch(switch)`.

### 1.10 Config players and built-in modes

**Config players** (`self.machine.<name>_player`):

| Player | Class | Base |
|---|---|---|
| `blocking_player` | `BlockEventPlayer` | ConfigPlayer |
| `coil_player` | `CoilPlayer` | DeviceConfigPlayer |
| `event_player` | `EventPlayer` | FlatConfigPlayer |
| `flasher_player` | `FlasherPlayer` | DeviceConfigPlayer |
| `hardware_sound_player` | `HardwareSoundPlayer` | DeviceConfigPlayer |
| `light_player` | `LightPlayer` | DeviceConfigPlayer |
| `queue_event_player` | `QueueEventPlayer` | ConfigPlayer |
| `queue_relay_player` | `QueueRelayPlayer` ("blocks queue events and converts them to normal events") | ConfigPlayer |
| `random_event_player` | `RandomEventPlayer` | ConfigPlayer |
| `score_queue_player` | `ScoreQueuePlayer` (SS-style scoring) | ConfigPlayer |
| `segment_display_player` | `SegmentDisplayPlayer` | DeviceConfigPlayer |
| `show_player` | `ShowPlayer` | DeviceConfigPlayer |
| `variable_player` | `VariablePlayer` | ConfigPlayer |

They share a common interface: `play`, `get_express_config`, `get_list_config`/`get_string_config`, `validate_config_entry`, `clear_context` and `handle_subscription_change`.

**[Stale]**: the config players index uses `self.machine.score_player` as an example, but there is no score_player page (scoring is `variable_player`). `event_player` and `variable_player` are both described as "Posts events based on config", a copy-paste docstring.

**Built-in modes** (`self.machine.modes.<name>`):

| Mode | Base | Notable methods |
|---|---|---|
| `attract` | Mode | `start_button_pressed/released`, `result_of_start_request(ev_result=True)`, which posts `game_start` if `request_to_start_game` was approved |
| `game` | **AsyncMode** | `balls_in_play` (settable; setting it to 0 starts ball end), `ball_drained(balls=0)`, `end_ball()`, `end_game()`, `request_player_add()`, `is_game_mode` (False: it *is* the game). `ball_ending()` and `game_ending()` are deprecated since 0.50. |
| `tilt` | Mode (always running, even in attract, to catch slam tilts) | `tilt()`, `tilt_warning()`, `slam_tilt()`, `reset_warnings()`, `tilt_settle_ms_remaining()` |
| `credits` | Mode | `add_credit(price_tiering=True)`, `clear_all_credits`, `enable_credit_play`, `enable_free_play`, `toggle_credit_play` |
| `bonus` | Mode | `hurry_up()` (typically on `flipper_cancel`) |
| `high_score` | AsyncMode | Runs during game ending. |
| `match` | AsyncMode | |
| `carousel` | Mode | Lets the player select another mode. |
| `service` | AsyncMode | |

### 1.11 Config processing

The code docs cover config processing only through method names:

- `MachineController.validate_machine_config_section(section)`.
- The `config_processor` boot module.
- `Mode.get_config_spec()`, which returns the spec for `mode_settings`.
- `Mode.configure_mode_settings(config)`.
- The test helper `add_to_config_validator(machine, key, new_dict)`.
- `FileManager` (`load(filename, verify_version=False, halt_on_error=True)`, `save`, `locate_file`, `get_file_interface`).
- `raise_config_error(msg, error_no, *, context=None)` on every LogMixin class.

The test machine controller notes it "disabled the config file caching", so production MPF caches parsed configs. There is no narrative page on config specs or validation in this section.

### 1.12 Miscellaneous building blocks

- **LogMixin** (`mpf.core.logging.LogMixin`), mixed into most classes:
  - `configure_logging(logger, console_level='basic', file_level='basic', url_base=None)`, with levels `none`, `basic` or `full`.
  - `debug_log`, `info_log`, `warning_log`, `error_log`. Warnings and errors always show.
  - `raise_config_error`, `ignorable_runtime_exception(msg)`, which raises in development and tests but only logs in production.
- **Player** (`mpf.core.player.Player`): one per player, with player variables available as attributes or items.
  - Reading a missing variable creates it with the value 0.
  - Each change posts `player_<var>` with `value`, `prev_value`, `change` and `player_num`. `change` is new minus old, or True/False for non-numeric values.
  - Methods: `enable_events(enable=True, send_all_variables=True)`, `is_player_var(name)`, `send_all_variable_events()`.
  - The game keeps `player_list` for non-current players.
- **DataManager** (`get_data(section=None)`, `save_all(data)`) is key/value persistence.
- **BallSearch** (one per playfield):
  - `enable`, `disable`, `block`, `unblock`, `start`, `stop`, `reset_timer` (called on any playfield switch), `cancel_ball_search`, `give_up` (applies `ball_search_failed_action`).
  - `register(priority, callback, name, *, restore_callback=None)` adds your own search step. **Ball search only waits if the callback returns true**, which matters for custom mechs.
  - `request_to_start_game` returns False while a search is running.
- **RGBColor / RGBAColor**: construct from a name, hex or tuple. Attributes and methods: `red`, `green`, `blue`, `hex`, `rgb`, `name`, `blend(start, end, fraction)`, `add_color(name, color)`, `name_to_rgb`, `hex_to_rgb`, `rgb_to_hex`, `random_rgb`, `string_to_rgb`.
- **Randomizer(items)**: `get_next`, `get_current`, `loop`, `pick_weighted_random(items)`.
- **Util** (`mpf.core.utility_functions.Util`), static helpers:
  - `string_to_ms`, `string_to_secs`, `string_to_list`, `string_to_event_list`, `string_to_class`, `string_to_gain`.
  - `dict_merge`, `get_from_dict`, `set_in_dict`, `keys_to_lower`, `event_config_to_dict`, `convert_to_type`.
  - Hex and PWM converters, `power_to_on_off`, `db_to_gain`, `chunker`.
  - Future helpers: `race`, `first`, `any`, `cancel_futures`.
- **DelayManagerRegistry**: the page is essentially empty.

---

## Part 2 - Writing custom Python code

### 2.1 Config versus code: which to use

MPF's philosophy (code/index.md) is to do as much as possible in config, but mixing in Python is fully supported and does not mean "hacking" MPF. Some people use config for 99% of the machine, and others write all game logic in Python. There are two mechanisms:

| Mechanism | Lives in | Active | Use for |
|---|---|---|---|
| **Mode code** | `modes/<mode>/code/<file>.py`, referenced by `mode: code:` | Only while the mode runs (handlers and delays are cleaned up automatically) | Custom game logic, which is the most common case |
| **Machine-wide `custom_code`** | `custom_code/<file>.py`, listed in the machine config `custom_code:` | Whole MPF lifetime, loaded at boot | Custom hardware and mechanisms that no built-in device covers (the Demolition Man elevator and claw) |

`scriptlets:` is **deprecated since 0.50** and still works for now; use `custom_code:`. `custom_code:` and `scriptlets:` are valid in machine configs only, not mode configs. There are also `mc_custom_code` / `mc_scriptlets` config sections for the old MC, which are outside this section.

A full Python development environment is only needed to work on MPF itself. Small extensions just need a text editor.

### 2.2 Mode code

Folder layout:

```
<mpf-game-folder>
├── config
└── modes
    ├── attract
    └── base
        ├── config
        │   └── base.yaml
        └── code
            └── base.py
```

Minimum class:

```python
from mpf.core.mode import Mode

class Base(Mode):
    pass
```

Wire it up in the mode config. `code:` is `<module>.<Class>`, relative to the mode's `code` folder:

```yaml
mode:
  start_events: ball_starting
  priority: 100
  code: base.Base
```

**Hooks to override** (Mode base class):

- `mode_init()` runs once at MPF boot.
- `mode_will_start(**kwargs)` runs before the mode becomes active.
- `mode_start(**kwargs)` runs every time the mode starts, just after `mode_(name)_started` according to mode_code.md.
- `mode_stop(**kwargs)` runs when the mode stops.

**Do not override `start()` or `stop()`.** You may call them: `start(mode_priority=None, callback=None, **kwargs)` and `stop(callback=None, **kwargs) -> bool`.

**Attributes:**

- `self.config`: the mode's config dict.
- `self.priority`: read only.
- `self.delay`: a DelayManager whose delays are cancelled when the mode stops.
- `self.player`: the current player, auto-updated. `None` outside a game.
- `self.active`.
- `self.is_game_mode`.
- `self.auto_stop_on_ball_end`.
- `self.restart_on_next_ball`: tracked per player in the `restart_modes_on_next_ball` player variable.

**`add_mode_event_handler(event, handler, priority=..., **kwargs)`** is like `events.add_handler`, but the handler is removed automatically when the mode stops. For a handler that should always listen, use `self.machine.events.add_handler()`. **[Contradiction]**: mode_code.md says `self.machine.mode.add_handler()`, which is a typo. Also, the signature shows `priority: int = 0` while the text says "The default is 1". Remember that handlers registered by modes are automatically given the mode's priority (priorities.md).

Documented example (lightly trimmed):

```python
from mpf.core.mode import Mode

class Base(Mode):

    def mode_init(self):
        self.machine.log.info("My custom mode code is being initialized")

    def mode_start(self, **kwargs):
        # needs **kwargs because some events that start modes pass parameters
        self.machine.log.info("My custom mode code is starting")
        self.delay.add(5000, self.my_callback)          # call in 5 s
        self.machine.log.info(self.player.number)
        self.machine.log.info('Score: {}'.format(self.player.score))
        self.add_mode_event_handler('player_score', self.player_score_change)
        self.machine.leds.led01.color('red')            # [Stale] see note

    def my_callback(self):
        self.machine.log.info("My delayed call was just called!")

    def player_score_change(self, **kwargs):
        self.machine.log.info("Player score went up by %s, was %s and is now %s",
                              kwargs['change'], kwargs['prev_value'], kwargs['value'])

    def mode_stop(self, **kwargs):
        self.machine.log.info("My custom mode code is stopping")
```

**[Stale]**: `self.machine.leds` is the pre-0.50 collection name. The current device collection is `lights` (`self.machine.lights.led01.color('red')`, see devices/lights.md). The docs also advise logging instead of `print()`. Mode inherits LogMixin, so `self.info_log(...)` etc. are available too.

### 2.3 Machine-wide custom code

1. Create a `custom_code/` folder in the machine folder with a `.py` file in it. Classes are referenced as `custom_code.<file>.<Class>`.
2. Subclass `CustomCode`:

   ```python
   from mpf.core.custom_code import CustomCode

   class Claw(CustomCode):
       pass
   ```

   The base class gives you `self.machine`, a delay manager and the class name, plus an `on_load()` hook that is called when the class loads.
3. Register it in the machine config:

   ```yaml
   custom_code:
     - custom_code.claw.Claw
   ```

The docs' full Demolition Man claw example shows the idioms you will need for a custom mech. Condensed:

```python
from mpf.core.custom_code import CustomCode

class Claw(CustomCode):

    def on_load(self):
        self.auto_release_in_progress = False
        # ball in elevator if switch active >100 ms
        self.machine.switch_controller.add_switch_handler(
            's_elevator_hold', self.get_ball, ms=100)
        # handle a ball already there at boot
        if self.machine.switch_controller.is_active('s_elevator_hold'):
            self.auto_release_in_progress = True
            self.get_ball()
        # expose an event-driven API for the rest of the game
        self.machine.events.add_handler('light_claw', self.light_claw)

    def enable(self):
        sc = self.machine.switch_controller
        sc.add_switch_handler('s_flipper_lower_left', self.move_left)
        sc.add_switch_handler('s_flipper_lower_left', self.stop_moving, state=0)
        sc.add_switch_handler('s_flipper_lower_right', self.move_right)
        sc.add_switch_handler('s_flipper_lower_right', self.stop_moving, state=0)
        sc.add_switch_handler('s_ball_launch', self.release)
        sc.add_switch_handler('s_claw_position_1', self.stop_moving)
        self.machine.events.post('claw_enabled')   # for slides/shows

    def disable(self):
        self.stop_moving()
        # ...remove_switch_handler(...) for every handler, SAME args as added...
        self.machine.events.post('claw_disabled')

    def move_left(self):
        sc = self.machine.switch_controller
        if sc.is_active('s_claw_position_2') and sc.is_active('s_claw_position_1'):
            return                                   # at left limit
        self.machine.coils['c_claw_motor_left'].enable()

    def stop_moving(self):
        self.machine.coils['c_claw_motor_left'].disable()
        self.machine.coils['c_claw_motor_right'].disable()

    def get_ball(self):
        if not self.machine.game:                    # no game: auto pick-up & drop
            self.auto_release_in_progress = True
        # ...move to pickup position, then do_pickup(): magnet on, elevator motor on,
        #    add handler on 's_elevator_index' -> stop_elevator ...

    def light_claw(self, **kwargs):                  # event handlers take **kwargs
        self.machine.diverters['diverter'].enable()
```

Lessons from the example:

- Switch handler callbacks take **no arguments** unless you set `return_info=True`. Event handlers need `**kwargs`.
- Check `self.machine.game` for `None` to tell attract from game.
- Motors and magnets driven with `coil.enable()` usually need `allow_enable: True` (or a hold power) in the coil config.
- Expose your mechanism to config through events: listen for `light_claw` and post `claw_enabled`/`claw_disabled`. Config players, shows and slides can then use them.

### 2.4 Player and machine variables in code

```python
player = self.machine.game.player   # don't store it; the current player changes
if not player:                      # game or player may be None
    return
self.machine.log.info(player["my_variable"])
player["my_variable"] = 17          # posts player_my_variable

self.machine.log.info(self.machine.variables.get_machine_var("my_variable"))
self.machine.variables.configure_machine_var("my_variable", persist=True, expire_secs=86400)
self.machine.variables.set_machine_var("my_variable", 17)   # posts machine_var_my_variable
```

In modes, use `self.player`. Player variables only exist while a game is running.

**[Contradiction]**: Players.md uses `self.machine.player.foo`. Per variables_in_code.md and the Player class text itself, the current player is `self.machine.game.player`, and `self.machine.player` is not documented anywhere else.

### 2.5 Debugging

debug.md uses PyCharm Community Edition, but any debugger works. It needs MPF installed from source into a venv, not the precompiled binaries. There are two methods:

1. **Attach to process**: start `mpf -t -b` in the activated venv, then use Run, Attach to Process and pick the mpf process.
2. **Launch under the debugger**: run MPF as a script (`python <venv>/lib64/python3.11/site-packages/mpf/__main__.py`) with parameters such as `-b -t` and the working directory set to your machine folder. This also catches code that runs during init.

---

## Part 3 - BCP (Backbox Control Protocol)

BCP is how MPF (the "pin controller") talks to the media controller. In 0.80 that is GMC; historically it was MPF-MC, and Unity backbox implementations also exist. It is designed as an open protocol that carries meaning ("start multiball mode") and not media details. The reference implementation uses a **raw TCP socket**, with latency typically below 1 ms on localhost and below 10 ms on a LAN.

**Wire format:**

- URL-like, UTF-8, one command per line terminated by `\n` (a `\r` is tolerated): `command?param1=value&param2=value`.
- Commands and parameter names are case-insensitive and trimmed. Values are case-sensitive.
- Typed values carry prefixes: `int:5`, `float:`, `bool:`, `NoneType:`. If any value is a list or dict, **all** parameters are JSON-encoded into a single `json:` parameter.
- Percent-encoding (a space is `%20`). Blank lines and lines starting with `#` are ignored. Unknown parameters are ignored. An unknown command gets `error?message=unknown command`.
- Both sides must survive network drops: just reconnect. There is no buffering, and the handshake is not repeated on reconnect.
- Handshake: the pin controller sends `hello?version=1.0`. The MC replies with `hello?version=1.0` or `error?message=unknown protocol version`.
- **Warning:** both sides are synchronised state machines, so infinite loops are possible. `reset` or `hello` halts them.

**Commands:**

| Command | Origin | Parameters | Notes |
|---|---|---|---|
| `hello` | either | `version`, `controller_name`, `controller_version` | When received by the MC it triggers a hard reset. The MC answers with hello or an error. The pin controller must never answer an MC hello (that would loop). |
| `goodbye` | either | none | The sender is shutting down. |
| `error` | either | `message`, `command` | |
| `reset` | pin | none | The MC must reply with `reset_complete`. |
| `reset_complete` | MC | none | |
| `ball_start` | pin | `player_num` (int), `ball` (int) | Sent every ball, including extra balls. |
| `ball_end` | pin | none | Not necessarily the end of the player's turn. |
| `player_added` | pin | `player_num` | Usually only on ball 1. |
| `player_turn_start` | pin | `player_num` | Not sent between extra balls. |
| `player_variable` | pin | `name`, `player_num`, `value`, `prev_value`, `change` | `change` is True for non-numeric values. May be for a non-current player. Filtering is recommended. |
| `machine_variable` | pin | `name`, `value`, `prev_value`, `change` | `prev_value`/`change` are only present on a change. On monitor start, the current values are sent without them. |
| `mode_start` | pin | `name`, `priority` | |
| `mode_stop` | pin | `name` | |
| `mode_list` | pin | `running_modes` (JSON array of `[name, priority]`) | Sent on every mode start or stop, but only to clients monitoring modes. |
| `monitor_start` / `monitor_stop` | MC | `category` | Nothing is streamed unless monitored or registered as a trigger. |
| `register_trigger` / `remove_trigger` | MC | `event` | Ask MPF to forward (or stop forwarding) a named event. |
| `trigger` | either | `name` (+ any) | "Do something", for example MC to pin: flash strobes on the beat. |
| `switch` | either | `name`, `state` (1/0) | MC to pin is the virtual keyboard (`switch?name=start&state=1` then `state=0`). Pin to MC sends switches for video modes, high score entry and service menus, only while needed. |
| `device` | either | `type`, `name`, `changes` (attr, old, new), `state` | Device state changes. |

**[Contradiction]**: `monitor_start`/`monitor_stop` list the valid categories as "events, devices, machine_vars, player_vars, switches, modes, ball, or timer", but the bullet list below that gives `events, devices, machine_vars, player_vars, switches, modes, core_events` (no ball or timer). Separately, `mode_list` refers to the "`mode`" category while the lists say `modes`.

In code: `self.machine.bcp.send(bcp_command, **kwargs)`. The BCP connection events `bcp_connection_attempt` and `bcp_clients_connected` are listed in Part 6. Connection configuration is in `config/bcp.md`, outside this section.

---

## Part 4 - Automated testing of your machine

MPF is developed test-first, with "over 800 unit tests" (each containing dozens of individual tests) across MPF and MPF-MC. The same TestCase classes are available for **your** machine. The doc's pitch: a config change a month from now will silently break an old mode, and tests catch it. A test clock lets "a complete 3-minute game play session" run "in a few hundred milliseconds".

### 4.1 Test class hierarchy

| Class | Bases | Use |
|---|---|---|
| `mpf.tests.MpfTestCase.MpfTestCase` | `unittest.TestCase` | Core base: test clock, mocked hardware, assertions. You point it at a config with `get_machine_path()`/`get_config_file()`. The default platform is `virtual`. |
| `mpf.tests.MpfGameTestCase.MpfGameTestCase` | MpfTestCase | Adds game helpers. `start_game()` hits and releases an `s_start` switch and checks that the game started. `add_player()` also uses `s_start`. |
| `mpf.tests.MpfFakeGameTestCase.MpfFakeGameTestCase` | MpfGameTestCase | Its `start_game(num_balls_known=3)`, `drain_one_ball()` and `drain_all_balls()` **need no ball devices or start button** in the config. |
| `mpf.tests.MpfMachineTestCase.MpfMachineTestCase` | `BaseMpfMachineTestCase` | "MPF only machine test case", the class the tutorial uses to test **your real machine folder and config**. |
| `mpf.tests.MpfBcpTestCase.MpfBcpTestCase` | MpfTestCase | Uses `MockBcpClient` (with `send`, `read_message`, `connect`, `stop`...) so you can test without a real BCP connection. |
| `TestMachineController` | MachineController | Uses TestDataManager, a manually advanced test clock, plugins only if enabled, merges `test_config_patches`, no config caching. |
| `TestDataManager` | DataManager | `save_all()` writes nothing to disk. |

The class relationships are drawn in `code/api_reference/testing_class_api/test_classes.png`.

### 4.2 Key test methods (common to all the classes)

**Configuration overrides:**

- `get_config_file()` returns something like `'my_config.yaml'`.
- `get_machine_path()`: "relative to the MPF package root" for MPF's own tests.
- `get_platform()`: return `'smart_virtual'` to simulate ball movement.
- `get_use_bcp()` defaults to False. `get_enable_plugins()` defaults to False. `get_options()`.

**Time:**

- `advance_time_and_run(delta=1.0)` is in **seconds**. It steps through scheduled delays and timers in order, so you advance 10 s and a 2 s delay fires at the correct point.
- `machine_run()` is the same as `advance_time_and_run(0)`.

**Switches:**

- `hit_and_release_switch(name)` activates and releases with no time between.
- `hit_switch_and_run(name, delta)` leaves the switch active. `release_switch_and_run(name, delta)`.
- `hit_and_release_switches_simultaneously(names)` processes events only at the end, which reproduces races.

**Events:**

- `post_event(event_name, run_time=0)`.
- `post_event_with_params(event_name, **params)`.
- `post_relay_event_with_params(...)` returns the relay result.
- `mock_event(name)` must be called **before** the event is posted. Mocking does not stop other handlers. Re-mock to reset the count. `reset_mock_events()`.

**Game (Game/FakeGame classes):**

- `start_game()`, `add_player()`, `start_two_player_game()`, `stop_game(stop_time=1)`, `drain_one_ball()`, `drain_all_balls()`.
- `fill_troughs()` fills all devices tagged `trough`.
- `set_num_balls_known(n)`, `start_mode(mode)`, `stop_mode(mode)`.

**Assertions:**

- Modes: `assertModeRunning(name)`, `assertModeNotRunning(name)`.
- Events: `assertEventCalled(name, times=None)`, `assertEventNotCalled(name)`, `assertEventCalledWith(name, **kwargs)`.
- Variables: `assertPlayerVarEqual(value, player_var)`, `assertMachineVarEqual(value, machine_var)`, `assertPlaceholderEvaluates(expected, condition)`.
- Game: `assertGameIsRunning()`, `assertGameIsNotRunning()`, `assertPlayerCount(n)`, `assertPlayerNumber(n)`, `assertBallNumber(n)`, `assertBallsInPlay(n)`.
- Balls: `assertBallsOnPlayfield(n, playfield='playfield')`, `assertAvailableBallsOnPlayfield(...)`, `assertNumBallsKnown(n)`.
- Switches: `assertSwitchState(name, state)`.
- Lights: `assertLightColor(light, color)`, `assertNotLightColor`, `assertLightColors(light, color_list, secs=1, check_delta=0.1)`, `assertLightFlashing(light, color=None, secs=1, ...)`, `assertLightOn`, `assertLightOff`, `assertLightChannel(light, brightness, channel='white')`, `assertColorAlmostEqual(c1, c2, delta=6)`.
- Plus all the standard `unittest` assertions.

### 4.3 Step-by-step (from WritingCustomTestsForYourMachine.md)

1. Create a `tests/` folder in the machine folder, next to `config/`, `logs/` and `data/`.
2. Add an **empty `tests/__init__.py`**. Without it, you get "0 tests run".
3. Add a file whose name starts with `test`, for example `tests/test_step_2.py`, with a class whose name starts with `Test` and methods whose names start with `test`. **Each test method runs against a fresh MPF instance** that loads your machine config.
4. Run `python -m unittest` **from the machine folder, not from `tests/`**, or you get config and loading errors.

**[Doc gap]**: the tutorial says "add the following lines to it" but **the code block is missing** from the page. Only the one assertion `self.assertModeRunning('attract')` survives. It is also inconsistent about naming: the text names the method `test_step_2_mpf_startup()`, while the failure output shows `test_mpf_starts (tests.test_step_2.TestTutorialMachine)`. A minimal *illustrative* reconstruction, using only the class path and methods documented in the API reference:

```python
# tests/test_step_2.py  (illustrative, not verbatim from the docs)
from mpf.tests.MpfMachineTestCase import MpfMachineTestCase

class TestTutorialMachine(MpfMachineTestCase):

    def test_mpf_starts(self):
        """Tests Step 2 of the tutorial"""
        self.assertModeRunning('attract')
```

A failing assertion (`assertModeRunning('foo')`) produces `AssertionError: Mode foo not known.` together with the file and line number.

*Illustrative* game-flow test using documented helpers:

```python
from mpf.tests.MpfMachineTestCase import MpfMachineTestCase

class TestMyGame(MpfMachineTestCase):

    def test_jackpot_event(self):
        self.mock_event('jackpot')
        self.hit_and_release_switch('s_start')      # your real start switch
        self.advance_time_and_run(2)
        self.assertModeRunning('base')
        self.post_event_with_params('jackpot', count=1)
        self.assertEventCalledWith('jackpot', count=1)
        self.advance_time_and_run(30)               # let timers expire
```

(Whether `start_game()` is available on `MpfMachineTestCase` is not shown: its documented method list has no `start_game`, while the Game and FakeGame classes do.)

### 4.4 Running MPF's own test suite

(RunUnitTests.md) Activate the venv, `cd` into `<venv>/lib/python3.x/site-packages/mpf/tests`, then run:

- All tests: `python3 -m unittest discover` (you should see dots and then `OK`; "some tests taking more than 0.5s" is fine).
- One file: `python -m unittest test_SegmentDisplay.py`.
- One test: `python -m unittest test_SegmentDisplay.TestSegmentDisplay.test_transitions_with_player` (`<file>.<Class>.<test>`).

**[Stale]**:

- The Linux activation line is written as `mpfenv/bin/activate`, which is missing `source`.
- The "Testing the MPF media controller" section (`python3 -m unittest discover mpfmc/tests`, a Kivy window with sound) refers to the legacy MPF-MC and does not apply to GMC.
- The sample output shows Python 3.4 and "Ran 587 tests".

**Also available:** `mpf test <file>` runs single-file YAML "doc tests" (`##! mode:`, `##! test`, `#! start_game`, `#! advance_time_and_run 1`, `#! post some_event`, `#! assert_...`), defined in `MpfDocTestCase`. See `tools/test.md`, outside this section. The conditional-events examples in the docs are written in this format.

---

## Part 5 - Dev environment and contributing

- **0.80 note** (setup.md): with the standard 0.80 virtual-environment install you usually don't need the special setup. **Do not install the precompiled binaries if you plan to develop.**
- Classic "editable" setup:

  ```shell
  git clone --recursive https://github.com/missionpinball/mpf.git
  virtualenv -p python3 mpf-venv
  source mpf-venv/bin/activate
  pip install -e mpf
  mpf --version
  ```

  **[Stale]**: the page also clones and installs `mpf-mc` and has Kivy reinstall steps for Mac. Those apply to the pre-0.80 Kivy MC, not GMC.
- Contribution workflow:
  1. Make your change and add your name to the `AUTHORS` file.
  2. Write or update unit tests and re-run the whole suite.
  3. Open a pull request, referencing the issue ("fixes #123").
- Python support per the release notes: 0.80 dropped 3.8/3.9 and officially supports 3.13/3.14. The docs' own example paths use 3.11.

---

## Part 6 - Events reference (all built-in events)

Notation:

- **Q** = queue event (handlers can hold it; you can hook it with `queue_relay_player`).
- **R** = relay event. **B** = boolean event (any handler returning False cancels it).
- **MC** = posted by the legacy MPF-MC only. **GMC** = posted by the Godot MC. MC and GMC events are *not* MPF-side events.
- `(name)` = replaced by the device or mode name.
- "none" = no keyword arguments.
- Many device events can be renamed with `events_when_*:`, so the default names below may not match your machine.

Every event page lists its kwargs so you can use them in conditional events (section 1.5) (`event{kwarg==x}`).

### 6.1 Machine, system, init and shutdown

| Event | Meaning | Key kwargs |
|---|---|---|
| `init_phase_1` ... `init_phase_5` | Q. Boot phases (see 1.4). | none |
| `init_done` | One-time boot init done; MPF is ready. | none |
| `machine_reset_phase_1/2/3` | Q. Reset phases, at boot and after service mode etc. Attract starts on phase 3. | none |
| `reset_complete` | The machine reset process is complete. | none |
| `shutdown` | The machine is shutting down; modules clean up. | none |
| `machine_request_shutdown` | **B**, *0.81*. Soft shutdown requested; a handler returning False aborts it. | none |
| `machine_abort_shutdown` | *0.81*. A soft shutdown was blocked by a handler. | none |
| `machine_will_shutdown` | *0.81*. A soft shutdown was not blocked and proceeds. | none |
| `fast_soft_power_switch_active` / `_inactive` | *0.81*. FAST Neuron soft power button pressed or released (via the NET watchdog, not a normal switch). | none |
| `machine_var_(var_name)` | A machine variable was added or changed. | `value`, `prev_value`, `change` |
| `clear` | Tells config players to clear what they run for a key (show or mode end). | `key` |
| `bcp_connection_attempt` | MPF is trying a BCP connection. | `host`, `port`, `name` |
| `bcp_clients_connected` | All outgoing BCP connections are made. | none |
| `master_volume_increase` / `master_volume_decrease` | Change the audio master volume. | `volume` (0.0-1.0) |
| `loading_assets` | The number of assets waiting to load changed. | `loaded`, `remaining`, `total`, `percent` |
| `asset_loading_complete` | The asset manager's queue is empty. It can happen twice with MC plus MPF assets. | none |

### 6.2 Game flow

Order: `request_to_start_game` (B), then `game_start`, `game_will_start`, `game_starting` (Q), `game_started`. At the end: `game_will_end`, `game_ending` (Q), `game_ended`.

| Event | Meaning | Key kwargs |
|---|---|---|
| `request_to_start_game` | **B**. The *only* proper way to start a game; the ball controller, credits and ball search can veto it. | none |
| `game_start` | Starts a game **bypassing** the approvals. Not recommended except in testing. | `buttons` (switches tagged `player` held at start), `hold_time` |
| `game_will_start` | Just before `game_starting`. | none |
| `game_starting` | Q. The game is starting. | `game` (the game mode object) |
| `game_started` | A new game has started. | none |
| `game_will_end` | Just before `game_ending`. | none |
| `game_ending` | Q. Match and high score hold it open. | none |
| `game_ended` | The game has ended. | none |
| `multiplayer_game` | A 2nd player was added (switch to the multi-player score layout). | none |

### 6.3 Ball lifecycle

Order: `ball_will_start`, `ball_starting` (Q), `ball_started`, `ball_start_target` (R), and later `ball_drain` (R), `ball_will_end`, `ball_ending` (Q), `ball_ended`.

| Event | Meaning | Key kwargs |
|---|---|---|
| `ball_will_start` | Just before `ball_starting`. | `ball`, `balls_remaining`, `is_extra_ball`, `player` |
| `ball_starting` | Q. The ball is starting. | same |
| `ball_started` | A new ball has started. | same |
| `single_player_ball_started` / `multi_player_ball_started` | A ball started in a 1-player or multiplayer game. | none |
| `ball_start_target` | R. The new ball is ready to eject; `target` can be changed by handlers. | `target` |
| `balls_in_play` | Balls in play changed and is at least 1 (not necessarily loose on the playfield). | `balls` |
| `ball_drain` | **R**. Ball(s) entered a device tagged `drain`. Balls left in `balls` after the relay are processed as drained (this is how ball saves claim balls). | `balls`, `device` |
| `ball_will_end` | Just before `ball_ending`. | none |
| `ball_ending` | Q. The ball is ending. | none |
| `ball_ended` | The ball ended (the same player may shoot again). | none |
| `collecting_balls` / `collecting_balls_complete` | The ball controller started or finished collecting balls. | none |

### 6.4 Player

| Event | Meaning | Key kwargs |
|---|---|---|
| `player_add_request` | **B**. Request to add a player; any handler can deny it (for example credits). | none |
| `player_will_add` | Just before `player_adding`. | `number` |
| `player_adding` | Q. A player is being added. | `number`, `player` |
| `player_added` | A player was added. | `num`, `player` |
| `player_turn_will_start` | Before a new player's turn (not repeated for extra balls). | `number`, `player` |
| `player_turn_starting` | Q. | `number`, `player` |
| `player_turn_started` | A new player's turn started. | `number`, `player` |
| `player_turn_will_end` | Turn about to end (after all extra balls). | `number`, `player` |
| `player_turn_ending` | Q. | `number`, `player` |
| `player_turn_ended` | Turn totally over. | `number`, `player` |
| `player_(var_name)` | A simple player variable (int, float or str) was created or changed. **Not posted for list or dict variables.** | `value`, `prev_value`, `change`, `player_num` (+ `kwargs`) |
| `player_score` | The `player_(var)` event for `score`. | `value`, `prev_value`, `change`, `player_num` |

**[Inconsistency]**: `player_added` uses `num`, while the other player events use `number`.

### 6.5 Modes

| Event | Meaning | Key kwargs |
|---|---|---|
| `mode_(name)_will_start` | Before `mode_(name)_starting`. | none |
| `mode_(name)_starting` | Q. The mode won't fully start until the queue clears. | none |
| `mode_(name)_started` | The mode has started (after starting). | none |
| `mode_(name)_will_stop` | Immediately before stopping. | none |
| `mode_(name)_stopping` | Q. | none |
| `mode_(name)_stopped` | The mode has stopped. | none |

### 6.6 Switches, playfield and flipper-button helpers

| Event | Meaning | Key kwargs |
|---|---|---|
| `(name)_active` / `(name)_inactive` | A switch became active or inactive. **Only posted if a handler exists or the switch has `debug: True`** (for performance). | none |
| `sw_(tag)` / `sw_(tag)_active` | A switch with this tag became active (same handler/debug caveat). | none |
| `sw_(tag)_inactive` | A tagged switch became inactive. | none |
| `switch_(name)_active` / `_inactive` | **MC**. The MC received a BCP `switch` command (for video modes and menus); only for switches configured to send to BCP. | none |
| `(playfield_name)_active` | The playfield has at least one loose ball. | none |
| `(playfield_name)_ball_count_change` | The live ball count on the playfield changed. | `balls`, `change` |
| `sw_(playfield_name)_active` | The playfield was active though a ball was just removed from it. | `balls` |
| `unexpected_ball_on_(playfield_name)` | A playfield switch was hit but no ball was expected. | none |
| `playfield_transfer_(name)_ball_transferred` | A ball moved between playfields. | `source`, `target` |
| `flipper_cancel` | Both flipper buttons pressed together (needs `left_flipper`/`right_flipper` switch tags; the default bonus hurry-up event). | none |
| `flipper_cradle` | One flipper button held 3 s (same tags; timed_switches). | none |
| `flipper_cradle_release` | Released after a cradle (waits until both are released). | none |
| `(combo_switch)_both` | Switches from group 1 and group 2 both active within `max_offset_time` for `hold_time`. | none |
| `(combo_switch)_one` | One side released for `release_time` while the other is still held. | none |
| `(combo_switch)_inactive` | Both released. | none |
| `(combo_switch)_switches_1` / `_switches_2` | Only that group is active and `max_offset_time` has passed (only with `max_offset_time`). | none |
| `(timed_switch)_active` | A switch has been active for `time`. | none |
| `(timed_switch)_released` | Released after being active for `time`. | none |

**[Contradiction]**: events/index.md says a switch `s_left_slingshot` "will post an event called *switch_s_left_slingshot_active*". The `(name)_active` page (linked from that same sentence) documents the MPF event as `(name)_active`, i.e. `s_left_slingshot_active`. `switch_(name)_active` is documented separately as an MC-only event. Trust the per-event pages.

### 6.7 Ball devices, ball handling and ball search

| Event | Meaning | Key kwargs |
|---|---|---|
| `balldevice_(name)_ball_enter` | **R** on `unclaimed_balls`. Balls entered; unclaimed ones are processed as new balls. They have *not* yet been added to `balls`/`available_balls`. | `device`, `unclaimed_balls` |
| `balldevice_(name)_ball_entered` | Balls entered and were added to `balls`/`available_balls`. | `device`, `new_balls` |
| `balldevice_(name)_ball_count_changed` | The count changed (may also fire without a change). | `balls` |
| `balldevice_(name)_ball_eject_attempt` | **Q**. The eject waits until the queue clears. | `balls`, `mechanical_eject`, `num_attempts`, `source`, `target` |
| `balldevice_(name)_ejecting_ball` | Ejecting right now. | same as eject_attempt |
| `balldevice_(name)_ball_eject_success` | The eject succeeded. | `balls`, `target` |
| `balldevice_(name)_ball_eject_failed` | The eject failed. | `balls`, `num_attempts`, `retry`, `target` |
| `balldevice_(name)_ball_missing` | This device lost a ball (also posts the generic one below). | `balls` |
| `balldevice_ball_missing` | Generic: a device lost a ball. | `balls`, `name` |
| `balldevice_(name)_broken` | The device is broken and no longer operates. | none |
| `balldevice_balls_available` | A device has balls available to eject. | none |
| `balldevice_captured_from_(captures_from)` | A device captured a ball from (captures_from), usually the playfield. | `balls` |
| `ball_search_started` | Ball search began. | none |
| `ball_search_phase_(num)` | Phase (num) started. | `iteration` |
| `ball_search_stopped` | Search stopped (found or gave up). | none |
| `ball_search_failed` | Gave up (posted right after `ball_search_stopped`). | none |
| `ball_search_prevents_game_start` | A start was requested during a search (good for a "looking for ball" slide). | none |
| `cancel_ball_search` | *Post this* to cancel all searches and mark balls lost (a handler-only event). | none |

### 6.8 Ball holds, locks, saves and multiballs

| Event | Meaning | Key kwargs |
|---|---|---|
| `ball_hold_(name)_held_ball` | Held additional balls. | `balls_held`, `total_balls_held` |
| `ball_hold_(name)_full` | The hold is full. | `balls` |
| `ball_hold_(name)_balls_released` | Released balls. | `balls_released` |
| `multiball_lock_(name)_locked_ball` | Locked one more ball. | `total_balls_locked` |
| `multiball_lock_(name)_full` | The lock is full. | `balls` |
| `ball_save_(name)_enabled` / `_disabled` | The ball save was enabled or disabled. | none |
| `ball_save_(name)_timer_start` | The countdown started. Also used for a multiball's built-in ball save. | none |
| `ball_save_(name)_add_a_ball_timer_start` | A multiball add-a-ball save timer started. | none |
| `ball_save_(name)_hurry_up` / `_grace_period` | Entered hurry-up or grace. | none |
| `ball_save_(name)_saving_ball` | Saved ball(s). | `balls`, `early_save` |
| `multiball_(name)_started` | The multiball started. | `balls` |
| `multiball_(name)_shoot_again` | A drain during the MB save timer; balls are re-added. | `balls` |
| `multiball_(name)_shoot_again_ended` | Shoot-again ended. | none |
| `multiball_(name)_hurry_up` / `_grace_period` | The MB ball save entered hurry-up or grace. | none |
| `multiball_(name)_lost_ball` | Lost a ball after the save expired. | none |
| `multiball_(name)_restart_grace_period_started` | About to end, but a restart grace (`restart_grace_period_ms`) began; add-a-ball restarts it. | `grace_period` |
| `multiball_(name)_restarted` | Restarted during the grace period. | none |
| `multiball_(name)_ended` | The multiball ended. | none |

### 6.9 Shots, shot groups, sequence shots, logic blocks and timers

| Event | Meaning | Key kwargs |
|---|---|---|
| `(shot)_hit` | The shot was hit. It is one of four variants posted per hit. | `profile`, `state` |
| `(shot)_(profile)_hit` | Hit with the profile active; may post once per active profile. | `profile`, `state` |
| `(shot)_(state)_hit` | Hit while in the state. The page text says "while in the profile (state)", a wording slip. | `profile`, `state` |
| `(shot)_(profile)_(state)_hit` | Hit with that profile in that state. | `profile`, `state` |
| `(shot_group)_hit` | A member shot was hit. | none |
| `(shot_group)_(state)_hit` | A member shot in (state) was hit. | none |
| `(shot_group)_complete` | All members are in the same state. | `state` |
| `(shot_group)_(state)_complete` | All members are in (state). | none |
| `(sequence_shot)_hit` | The sequence shot was completed. | `elapsed` (added 0.56.1) |
| `logicblock_(name)_hit` | A counter, accrual or sequence was hit (default `events_when_hit`). `counter_(name)_hit` is also still posted for counters but is **deprecated**. | Sequence and accrual: `step`. Counter: `count`, `hits`, `remaining` |
| `logicblock_(name)_updated` | The block advanced, reset or was restored. | `enabled`, `value` |
| `logicblock_(name)_complete` | The block completed (default `events_when_complete`). | none |
| `(logic_block)_timeout` | The block timed out (timeouts are off by default; `logic_block_timeout`). | none |
| `timer_(name)_started` | The timer started. | `ticks`, `ticks_remaining` |
| `timer_(name)_tick` | Counted down or up. | `ticks`, `ticks_remaining` |
| `timer_(name)_time_added` | Ticks were added. | `ticks`, `ticks_added`, `ticks_remaining` |
| `timer_(name)_time_subtracted` | Ticks were removed. | `ticks`, `ticks_subtracted` (positive), `ticks_remaining` |
| `timer_(name)_paused` | Paused. | `ticks`, `ticks_remaining` |
| `timer_(name)_stopped` | Stopped for any reason. | `ticks`, `ticks_remaining` |
| `timer_(name)_complete` | Completed (it may restart depending on its settings). | `ticks`, `ticks_remaining` |

### 6.10 Achievements and extra balls

| Event | Meaning | Key kwargs |
|---|---|---|
| `achievement_(name)_changed_state` | The state changed (disabled, enabled, started, completed or stopped); reposted on the next ball to restore. | `state`, `selected`, `restore` |
| `achievement_(name)_state_(state)` | The achievement entered (state); also on restore or selection change. | `state`, `selected`, `restore` |
| `extra_ball_(name)_lit` | That extra ball was lit. | none |
| `extra_ball_(name)_awarded` | That extra ball was awarded. | none |
| `extra_ball_(name)_award_disabled` | Its award was disabled. | none |
| `extra_ball_awarded` / `extra_ball_award_disabled` | Generic versions. | none |
| `extra_ball_group_(name)_lit` | An EB was lit, **and also at turn start if one is still lit**. Use it for "EB lit" modes and lights. | none |
| `extra_ball_group_(name)_lit_awarded` | Lit *during play* only. Use it for award shows and slides. | none |
| `extra_ball_group_(name)_unlit` | No lit EBs remain (a good stop event). | none |
| `extra_ball_group_(name)_awarded` | An EB from the group was awarded. | none |
| `extra_ball_group_(name)_award_disabled` | An EB would have been awarded but EBs are disabled in settings (give points instead). | none |

### 6.11 Mechanisms

| Event | Meaning | Key kwargs |
|---|---|---|
| `drop_target_(name)_down` / `_up` | The target changed state. | none |
| `drop_target_bank_(name)_down` / `_up` | All targets down, or all up (posted once). | none |
| `drop_target_bank_(name)_mixed` | Mixed state (posted on every member change while incomplete). | none |
| `diverter_(name)_enabling` | Enabling. With `activation_switches:` it activates later, otherwise immediately. | `auto` |
| `diverter_(name)_disabling` | Disabling (same caveat). | `auto` |
| `diverter_(name)_activating` / `_deactivating` | Physically moving. | none |
| `kickback_(name)_fired` | The kickback fired a ball. | none |
| `magnet_(name)_grabbing_ball` / `_grabbed_ball` | Grab started or finished. "Grabbed" means the process completed, **not** confirmation of a ball. | none |
| `magnet_(name)_releasing_ball` / `_released_ball` | Release in progress or done. | none |
| `magnet_(name)_flinging_ball` / `_flinged_ball` | Fling (disable and re-enable briefly) in progress or done. | none |
| `motor_(name)_reached_(position)` | The motor reached a position. | none |
| `reel_(name)_advanced` | A score reel advanced one position. | none |
| `spinner_(name)_active` | An idle spinner was hit and became active. | `label` |
| `spinner_(name)_hit` | Every spinner switch hit. | `hits`, `label` |
| `spinner_(name)_inactive` | No hits for `active_ms`. | `hits` |
| `spinner_(name)_idle` | No hits for `idle_ms` (only if it is set). | `hits` |
| `spinner_(name)_(label)_active` / `_(label)_hit` | Labelled versions (only if labels are defined). | none |

### 6.12 Tilt, credits, bonus, match, high score and carousel

| Event | Meaning | Key kwargs |
|---|---|---|
| `tilt_warning` | A tilt warning. | `warnings`, `warnings_remaining` |
| `tilt_warning_(number)` | Warning number (number). | none |
| `tilt` | The player tilted. | none |
| `tilt_clear` | The settle time after the last tilt hit has passed (holds the next ball to prevent tilt-throughs). | none |
| `slam_tilt` | A slam tilt occurred. | none |
| `credits_added` | Credits or partial credits were added. | none |
| `max_credits_reached` | Credits were added but the maximum was reached. | none |
| `not_enough_credits` | Start was pressed without enough credits (not free play). | none |
| `enabling_credit_play` / `enabling_free_play` | Mode switched; also posted at boot if the credits mode is enabled. | none |
| `bonus_start` | End-of-ball bonus begins (not posted if tilted). | none |
| `bonus_subtotal` | After all bonus entries. The page says it is skipped if the multiplier is 1. | `score` |
| `bonus_multiplier` | The multiplier screen; skipped if the multiplier is 1. | `multiplier` |
| `match_has_match` | Q. At least one player matched. | `match_number0..X`, `match_numberX_won`, `winner_number`, `winners` (>0) |
| `match_no_match` | Q. No matches. | same, `winners` = 0 |
| `high_score_enter_initials` | Request that a player enter a name for a record. | `player_num`, `award`, `value`, `category_name` |
| `high_score_award_display` | Posted for every award earned in every category. **0.80: this replaces the per-category and per-award events.** Filter with `high_score_award_display{category_name=="score"}`. | `player_name`, `award`, `value`, `player_num` (0.80), `category_name` (0.80) |
| `score_award_display`, `(award_name)_award_display`, `(category_name)_award_display` | **Removed in 0.80** (merged into the event above). | (historical) |
| `text_input_high_score_complete` | BCP text-input result for high score; the text is saved to player var `initials`. | none documented |
| `text_input_(name)_complete` | BCP integration for a GMC text input. | none documented |
| `text_input_(key)_complete` / `_abort` | **MC** text_input widget finished or aborted. | `text` |
| `carousel_item_highlighted` | Initial highlight or next/previous. | `carousel`, `item`, `direction` |
| `carousel_item_selected` | An item was selected. | `carousel`, `item` |
| `carousel_items_empty` | No valid selectable items (check `mode_settings` or the dynamic conditions). | `carousel` |

**[Contradiction]**: `bonus_subtotal` says it is "typically posted just before the bonus multiplier screen, so if the bonus multiplier is 1, then this event will be skipped", while `bonus_multiplier` says it is the multiplier screen that is skipped. The subtotal-skipping sentence looks like a copy-paste error.

### 6.13 Service

| Event | Meaning | Key kwargs |
|---|---|---|
| `service_trigger` | **GMC**. Posted by the built-in GMC Service slide. | `action` = `service_exit` / `setting` (+ `variable`, `value`) / `switch_test`, `coil_test`, `light_test` (+ `sort` bool) |

There are no other service-mode events in the event reference. Leaving service mode triggers the `machine_reset_phase_*` events (6.1).

### 6.14 Media controller and display (not MPF-side)

| Event | Source | Meaning |
|---|---|---|
| `mc_ready` | MC | The earliest point to show "boot" slides. |
| `mc_reset_phase_1/2/3`, `mc_reset_complete` | MC | Internal MC reset. |
| `displays_initialized`, `display_(name)_initialized` | MC | Internal startup; don't show slides from these. |
| `display_(name)_ready` | MC | The display target can show slides. |
| `client_connected` | MC | A BCP client connected (`address`, `port`). |
| `client_disconnected` | MC | The BCP client disconnected, also at MC start before connecting (`host`, `port`). |
| `slide_(name)_created` / `_active` / `_removed` | MC and GMC | Slide lifecycle. Slide names must be unique machine-wide. |
| `slide_(name)_inactive` | GMC | The slide is no longer the current slide. |
| `widget_(name)_active` / `_removed` | GMC | Widget lifecycle. |

Many pages still describe the Kivy MC, for example "use the event init_done ... once all the assets set to preload have been loaded" and "Unity 3D backbox controller". Check the GMC docs for the 0.80 equivalents.

### 6.15 Twitch (removed)

`twitch_chat_message` (`user`, `message`, `line_1`..`line_6`, `line_count`), `twitch_command` (`command`, `user`), `twitch_bit_donation` (`bits`, `message`, `user`), `twitch_subscription` (`gift`, `months`, `sub_plan`, `sub_plan_name`, `sub_recipient`, `subscriber_message`, `message`, `user`) and `twitch_raid` (`raid_count`, `raid_user`). The Twitch plugin has been removed (see 1.3), so these pages are historical.

---

## Part 7 - Gotchas and contradictions in one place

1. **Event handlers need `**kwargs`**, and the event manager enforces it at registration. Switch handlers get **no arguments** unless `return_info=True`.
2. **`(name)_active` switch events are only posted if something listens for them** (or the switch has `debug: True`), so don't expect to see them in logs "for free".
3. **`remove_switch_handler` needs the exact same args** (`state`, `ms`) you registered with. Prefer keeping the returned key and using `remove_switch_handler_by_key`.
4. Mode handlers and delays are cleaned up automatically. Machine-wide (`custom_code`) handlers are not.
5. `self.player` / `self.machine.game` can be `None`. Don't cache player objects, because the current player changes.
6. Player-variable events fire only for simple types (int, float, str), not for lists or dicts. Reading an unknown player variable creates it as 0.
7. Use `request_to_start_game`, not `game_start`, to start games. `game_start` bypasses the credit, ball and ball-search checks.
8. Boolean events stop at the first handler that returns False. Relay events pass returned kwargs on down the chain. `ball_drain` is a relay event, which is how ball saves "eat" drains.
9. `advance_time_and_run()` takes **seconds**, while `delay.add()` takes **milliseconds**.
10. Run machine tests with `python -m unittest` **from the machine folder**, and include `tests/__init__.py`.
11. Contradictions and stale spots:
    - The tests tutorial is missing its code block, and its method names are inconsistent.
    - `self.machine.mode.add_handler` is a typo for `self.machine.events.add_handler`.
    - `self.machine.leds` is now `self.machine.lights`.
    - `self.machine.player` should be `self.machine.game.player`.
    - `add_mode_event_handler` has a default priority of 0 in the signature but 1 in the text.
    - The BCP `monitor_start` category list disagrees with itself.
    - `switch_<name>_active` (index page) versus `<name>_active` (event page).
    - `bonus_subtotal` versus `bonus_multiplier` skip wording.
    - `player_added` uses `num` where other player events use `number`.
    - The Twitch "0.58+/0.81+" removal note.
    - `self.machine.score_player` no longer exists.
    - The switch_controller `is_active` signature (object) versus the Claw example (name).
    - The dev-setup page still covers Kivy/`mpf-mc`, and the test-running page covers MPF-MC tests.
    - Missing pages: "Overview & Tour of MPF code" and "DeviceCollection documentation".
12. There is **no documentation** in this section for writing a custom *device class* or custom *hardware platform*, nor a narrative on config specs and validation or on the asyncio clock. Use `custom_code` classes driving existing devices, or read MPF source (`mpf/core/platform.py` mixins, `mpf/platforms/*`).

---

## Source doc paths used

All paths are relative to `mpf-docs-dev/docs/`.

- `code/index.md`
- `code/introduction/`: `index.md`, `machine_code.md`, `mode_code.md`, `variables_in_code.md`, `setup.md`, `debug.md`
- `code/Writing_Tests/`: `index.md`, `RunUnitTests.md`, `WritingCustomTestsForYourMachine.md`
- `code/BCP_Protocol/`: `index.md`, `ball_end.md`, `ball_start.md`, `device.md`, `error.md`, `goodbye.md`, `hello.md`, `machine_variable.md`, `mode_list.md`, `mode_start.md`, `mode_stop.md`, `monitor_start.md`, `monitor_stop.md`, `player_added.md`, `player_turn_start.md`, `player_variable.md`, `register_trigger.md`, `remove_trigger.md`, `reset.md`, `reset_complete.md`, `switch.md`, `trigger.md`
- `code/api_reference/index.md`
- `code/api_reference/core/*.md`: auditor, ball_controller, bcp, device_manager, events, info_lights, light_controller, machine, mode_controller, placeholder_manager, platform_controller, service, settings, show_controller, switch_controller, switch_player, text_ui, twitch_bot, index
- `code/api_reference/devices/*.md` (all 50 device pages plus index)
- `code/api_reference/modes/*.md`: attract, bonus, carousel, credits, game, high_score, match, service, tilt, index
- `code/api_reference/hardware_platforms/*.md` (all 29 platform pages plus index)
- `code/api_reference/config_players/*.md` (all 13 players plus index)
- `code/api_reference/misc_components/*.md`: BallSearch, DataManager, DelayManager, DelayManagerRegistry, FileManager, LogMixin, ModeBaseClass, Players, Randomizer, RGBColor, RGBAColor, UtilityFunctions, index
- `code/api_reference/testing_class_api/*.md`: MockBcpClient, MpfBcpTestCase, MpfFakeGameTestCase, MpfGameTestCase, MpfMachineTestCase, MpfTestCase, TestDataManager, TestMachineController, index
- `events/index.md`, `events/overview/{index,priorities,event_types,conditional}.md`, all ~231 per-event pages in `events/*.md` plus `events/fast/*.md`, and the category indexes `events/*/index.md` (including `queue_events/index.md` and `ball_lifecycle/index.md`)
- Context from outside the section: `flowcharts/mpf_boot.md`, `config/custom_code.md`, `config/scriptlets.md`, `tools/test.md`, `running/commands/test.md`, `versions/release_notes.md` (0.80 notes), and `../mkdocs.yml` (nav)
