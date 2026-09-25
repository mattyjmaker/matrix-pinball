# Game Select and Terminator 2 (1991) Rules

The cabinet runs two games on one playfield. This document covers the Game
Select that chooses between them before the first ball, the generic hardware
vocabulary both games share, and the Terminator 2: Judgment Day rule set,
in the same depth as `docs/11-rules-act-1.md`. Every number below is the value
in the code.

Status (2026-09-25): implemented in `config/` and `modes/`, covered by
`tests/test_game_select.py` and `tests/test_t2.py`, and drawn on the HUD in
`gmc/`. As with Act I: scores and timers are placeholders at the VPX scale
for balancing once the machine is playable; the hardware behind each shot is
on the virtual platform until built.

Agreed with the user:

- Terminator 2 reuses the existing physical shots under its own names. No
  new hardware.
- A top-level Game Select sits above the Matrix's Act select. Choosing the
  Matrix runs Act select as before; choosing Terminator 2 goes straight into
  its chapters, since T2 has one film's worth of rules.
- One generic vocabulary for the hardware, everywhere (section 1).
- Game Select times out after 15 s and defaults to the Matrix.

Decided during the build, not yet reviewed by the user, each marked "(build)"
where it first appears: every T2 timer, count and score; that chapter 2 has
no timer on its first phase; that chapter 4 has a lock phase mirroring Act
I's; that Judgment Day's stage 2 is four hits and stage 4 is the four launch
sites in order; that the T2 HUD reuses the Matrix's lock cells and stage
zones; and the on-screen text throughout.

Film references are from recall of Terminator 2: Judgment Day (1991, dir.
James Cameron) and cover only its well-known plot beats (the mall pursuit,
the flood-channel chase, the Pescadero breakout, the Dyson confrontation, the
Cyberdyne raid, the steel mill finale). No dialogue is quoted; check any line
against the film before it goes on screen, as docs/11 asks for Matrix clips.

## 1. One generic vocabulary for the hardware

Every switch, coil, device and event names what the feature is, never what a
game calls it, in `config/config.yaml`, `config/playfield_pending.yaml`, the
keyboard map and the tests. Each game's modes listen to the same events and
keep the film's names in their display text, mode names and comments. Each
renamed config entry carries a `# was ...` comment with the prior Matrix
name. The Matrix mapping is docs/11 section 11; T2's is section 4 below.
`tests/test_shots.py` fails if a Matrix word gets into a hardware name.

The playfield, as the user described it:

| Hardware name | What it is |
| --- | --- |
| `left_lock_ramp`, `left_lock` | The left ramp, whose return path to the flippers has a post that rises to hold balls. The count is ramp entries while the post is up, assumed full at three |
| `middle_loop_ramp`, `middle_loop_vuk` | The middle loop ramp and the VUK it pairs with |
| `right_loop_ramp` | The loop on the far right: up and in front of the backboard, onto the upper playfield from the left |
| `backboard_ramp` | Next to the platform toy: up into the backboard and behind it, out at the top left of the upper playfield |
| `upper` | The upper playfield: three standups (`upper_target_1..3`) and a mini left flipper. Both the right loop ramp and the backboard ramp feed it |
| `platform` | The toy: two targets on a rising platform (`platform_target_1..2`), two front targets that lower and rise to block the path (`platform_gate`), a magnet (`platform_magnet`), and a subway under the raised platform to the middle loop VUK. `bd_platform_vuk` stands in for the subway until the toy is built |
| `popups`, `popup_scoop` | Three pop-up drop targets and the scoop that raises them |
| `mode_drop`, `mode_scoop` | The 1-bank smart drop and the scoop behind it that starts a game's modes |
| `five_bank`, `three_bank` | The 5-bank and 3-bank drop targets. The three-bank has no rules yet |
| `pop_target_1..4`, `pop_bumper_1` | The standups and pop bumper in the pop bumper area |
| `right_outlane_lock` | The single-ball lock at the bottom right outlane, with its standup and rollover |
| `kickback_target` | Relights the left outlane kickback |
| Flippers | Left, right, upper right, and the upper playfield's left. The upper two are not modelled yet (hardware rules, pending wiring) |

Still modelled provisionally, marked `TODO(hardware)` in
`config/playfield_pending.yaml`: the left lock's three count switches (the
real mech has a post and no position switches), the platform VUK (the real
toy has a subway to the middle loop VUK), the platform gate's energised
state, and the platform raise coil, which no rule drives yet.

## 2. Game Select

`modes/game_select` (priority 2000, `code/game_select.py`) holds
`ball_starting` on every player's first ball with `use_wait_queue`.

- **Player 1's first ball:** the choice is offered. Flippers step between
  MATRIX and TERMINATOR 2, start confirms, and after **15 s** with no
  confirmation the Matrix starts. While the select is up the start button
  does not add a player; adds work again once the ball is in play.
- The choice is written to the machine variable `game_choice` (`matrix` or
  `t2`) and posted as `game_selected`. It is one per game of pinball: every
  later player's first ball skips the screen and gets the same game.
- Each player's `game` variable is set to the choice, which is what the HUD
  reads (section 11).
- **Hand-over.** For the Matrix the mode posts `start_act_select` and keeps
  the ball held until `act_select` stops, so Act select behaves exactly as
  before (docs/11 section 5) but no longer holds `ball_starting` itself.
  Terminator 2 has no pre-ball select, so the mode steps straight out.
- `act_one` starts only while `game_choice` is `matrix`; `t2_main` only
  while it is `t2`. Everything under either controller is gated by it.
- Display: the `game_select` widget (`gmc/widgets/game_select.tscn`), the
  `act_select` widget's layout with the option on offer read from the player
  variable `game_option` and the clock driven by `game_select_show`.

## 3. Structure at a glance (Terminator 2)

```
  Game Select (before the first ball): Matrix, or Terminator 2
                                        |
       always on: Endoskeletons, Arsenal Lock drain save, Displacement, Vision
                                        |
  Command scoop starts the next chapter, in film order
   Ch1 Arrival -> Ch2 Pescadero Break-Out -> Ch3 The Choice: Dyson -> Ch4 Cyberdyne Raid
                                        |
  Multiballs lit by their own features, any time no other multiball runs
     Future War Multiball (left lock)          T-1000 Multiball (platform gate)
                                        |
  Each chapter and multiball completed lights one name in the SAVED roster
                                        |
          four names SAVED -> Judgment Day (T2 wizard) -> T2 complete
```

## 4. Shot mapping

Every row keeps the device and its mechanical behaviour. Only the name,
scoring and story meaning change.

| Hardware name (section 1) | Matrix identity | Terminator 2 identity | T2 story meaning |
| --- | --- | --- | --- |
| `mode_drop`, `mode_scoop` | Mission Drop + Mission scoop | Perimeter Drop + Command scoop | Breaching the next objective; starts each chapter |
| `left_lock_ramp`, `left_lock` | Trinity Ramp and lock | Future War Ramp and lock | Sarah's recurring flash-forward: surviving Hunter-Killer sorties |
| `middle_loop_ramp`, `middle_loop_vuk` | Deja Vu Ramp + VUK | Displacement Ramp + VUK | Time-displacement arrivals (both Terminators arrive in a lightning field) |
| `right_loop_ramp`, `upper_target_1..3` | Real World Ramp + standups | Pescadero Ramp + Ward standups | Escaping the mental hospital |
| `backboard_ramp` | Sentinel Ramp | T-1000 Ramp | The T-1000's pursuit; the ramp beside the toy |
| `platform` (gate, two targets, magnet, VUK/subway) | Sentinel Boss toy | T-1000 toy: Cruiser targets (gate), Semi Grille (platform targets), T-1000 magnet, T-1000 VUK | The T-1000's pursuit by cruiser and tanker truck |
| `popups`, `popup_scoop` | Agents + Agents Coming scoop | Endoskeletons + Assembly Line scoop | Skynet's mass-produced units |
| `right_outlane_lock` + target | Ammo Lock + target | Arsenal Lock + target | The gun-store arsenal; same drain-save mechanic |
| `five_bank` | Matrix Team drops | Cyberdyne Lab drops | Getting through the lab's security |
| `three_bank` | (unused) | (unused; candidate for a T2-only feature) | |
| `pop_target_1..4` | EMP standups | Launch Site standups | Nuclear launch sites from Sarah's nightmare; light Vision, and later disarm Judgment Day |
| Lanes/spinners | (unnamed) | Freeway lanes/spinners | Cosmetic only |
| Left/right flipper buttons (mode input) | Blue Pill / Red Pill | Kill Dyson / Spare Dyson | Sarah's choice at gunpoint in Dyson's house |

## 5. Ball count

Inherited from the shared hardware: 7 balls installed, at most 6 in play
(Judgment Day), `virtual_only` lock counting, one multiball at a time with a
`mb_pending` queue, exactly as docs/11 sections 2 to 3 establish. The
stacking rule is the same: a multiball requested during another waits and
starts when it ends; the Command scoop does not start a chapter during a
multiball; a queued chapter multiball (Break-Out, Raid) dies with its chapter
at ball end.

## 6. Always-on features (base mode)

`modes/base` runs for both games and holds the mechanics under generic
names; each game names them on screen. Scores as docs/11 section 3.

| Feature (T2 name) | Hardware and rule | Score |
| --- | --- | --- |
| Endoskeletons (3 pop-ups) | Hit a raised one; all three down pays extra. Raised at the start of every ball. | 10,000 each, 50,000 all down |
| Assembly Line scoop | The pop-up scoop: all three down raises them again (`popup_scoop_reset`), otherwise a small award. | 50,000 or 5,000 |
| Arsenal Lock | The right outlane lock drain save, identical mechanic to Act I's Ammo Lock. Stands down during Chapter 4's lock phase. | 15,861 per lock |
| Displacement VUK | The middle loop VUK award. | 2,570 |
| Vision | The mystery: the four pop area targets, any order, light it; the middle loop VUK collects a random award. (Act I's Oracle on the same rule.) | 25,000, 75,000 or 150,000 |
| Freeway lanes/spinners | Inlanes and every spinner. | 100 |

## 7. Chapters

Chapters play in film order from the Command scoop. A chapter is **played**
when it ends, including by a drain; it is **completed** when its goal is met,
and only completion saves a name.

### Starting a chapter

- The Perimeter Drop (mode drop) sits in front of the Command scoop.
  Knocking it down (5,000) sets `mode_ready`.
- Every ball into the scoop is held while `t2_main` decides. With `mode_ready`
  and no chapter or multiball running, it starts the next chapter, raises the
  drop again and releases the ball after 2 s (Chapter 3 keeps it for the
  choice). Otherwise it pays 10,000 and releases the ball after 0.75 s.
- After Chapter 4 has been played, the scoop replays the first chapter not
  yet completed. Once Judgment Day is lit, the scoop starts it instead.
- Between chapters the controller sets `objective` to "KNOCK DOWN THE
  PERIMETER DROP: <next>" or "SHOOT THE COMMAND SCOOP: <next>", and
  `chapter` to "CHAPTER <n>".

### Chapter 1: Arrival (film: the mall, then the flood channel)

Single-ball hurry-up; the T-1000 is the clock.

1. **The mall:** three ramp shots, any ramps, inside 40 s (build). 50,000 per
   shot.
2. **The flood channel:** the Displacement VUK, inside 20 s (build). Pays
   250,000 plus 25,000 per second left.

- Either timer running out: the T-1000 gets away, played but not completed.
- Completion saves **JOHN**.

### Chapter 2: Pescadero Break-Out (film: breaking Sarah out)

1. **Getting in:** the ball is released after the intro; hit the three Ward
   standups (upper playfield targets), any order, no timer (build). 50,000
   each. The third requests Break-Out Multiball. A drain first ends the
   chapter, played.
2. **Break-Out Multiball:** 3 balls, 20 s ball save (build). Jackpot: the
   Pescadero Ramp (right loop ramp), 100,000. Super jackpot: all three Ward
   standups again, 500,000, once.

- The super jackpot saves **SARAH**. The chapter ends when the multiball does.

### Chapter 3: The Choice: Dyson (film: Dyson at gunpoint)

1. **At gunpoint:** the scoop keeps the ball. Left flipper: kill. Right
   flipper: spare. No input in 10 s (build): spare, which is what happens in
   the film.
   - **Kill:** 5,000, the ball is released and the chapter ends, played but
     not completed.
   - **Spare:** the ball is released, the five-bank resets and the bypass
     starts.
2. **Cyberdyne Lab bypass:** all five Cyberdyne Lab drops (the five-bank)
   inside 30 s (build). 150,000.

- Completing the bypass saves **DYSON**. Running out of time ends the chapter,
  played.

### Chapter 4: Cyberdyne Raid (film: the break-in, the firefight, the escape)

1. **Dyson's access:** the Displacement VUK lights the Arsenal Lock.
2. **Arm up:** lock three balls at the Arsenal Lock (right outlane lock),
   50,000 each. It holds one ball physically; the count is virtual.
3. **Raid Multiball:** 3 balls, 20 s ball save, released from the lock
   (build).

| Stage | Balls | Goal | Score |
| --- | --- | --- | --- |
| Break-In | 3 | Every guard: the four Launch Site standups and the three Endoskeletons (raised again whenever all three are down) | 75,000 per guard |
| Firefight | 4 (add a ball) | The Future War Ramp (left lock ramp) lights "Hold the line" for 10 s; hit an Endoskeleton while it is lit | 250,000 |
| Escape | 5 (add a ball) | A ball over the T-1000 magnet is caught as the cruiser just misses the getaway truck; the magnet lets go after 2 s | 1,000,000 |

- The Escape catch saves **CHIP**. The chapter ends when the multiball does.
- A drain during the lock phase ends the chapter, played.

## 8. The two standalone multiballs

Both run whenever T2's features are on (`t2_features_start`), which is every
T2 ball except while Judgment Day runs.

### Future War Multiball (the Matrix's Trinity Multiball on the same hardware)

- The left lock takes three balls, 10,000 each. The HUD's lock cells
  (`balls_locked`) show the count.
- The third lock requests a 3-ball multiball, 20 s ball save, released from
  the lock. "Resistance Bonus" jackpots on the Future War Ramp (left lock
  ramp), 150,000.
- Three jackpots (build) save **RESISTANCE**.

### T-1000 Multiball (the Matrix's Sentinel Multiball on the same hardware)

- Four hits across the two Cruiser targets (platform gate) open the way ("It
  has found you", 100,000). A ball into the T-1000 VUK (platform VUK) while it
  is open requests the multiball: 3 balls, 20 s ball save.
- Jackpots on the T-1000 Ramp (backboard ramp) and either Semi Grille target
  (platform targets), 150,000. Three jackpots (build) save **SKYNET**,
  meaning Skynet's agent was driven off; its defeat is the wizard mode's.
- **Add-a-ball**, once per multiball: hit both Cruiser targets and a Semi
  Grille target to light it, then shoot the T-1000 VUK. 10 s save on the added
  ball. Peaks at 4 balls.
- The gate closes and the hit count resets when the multiball ends, and at
  ball end, so the four hits and the VUK shot must come on one ball.

## 9. SAVED roster

| Name | Player variable | Saved by |
| --- | --- | --- |
| JOHN | `saved_john` | Chapter 1 |
| SARAH | `saved_sarah` | Chapter 2 |
| DYSON | `saved_dyson` | Chapter 3, spare path only |
| CHIP | `saved_chip` | Chapter 4 |
| RESISTANCE | `saved_resistance` | Future War Multiball |
| SKYNET | `saved_skynet` | T-1000 Multiball |

- Each name pays 250,000 once (`name_saved`, argument `who`) and adds one to
  `saved_count`.
- **Judgment Day lights at 4 names** (500,000). The operator setting
  `judgment_day_threshold` takes 4, 5 or 6.

## 10. Judgment Day (T2 wizard)

Starts from the Command scoop once lit. While it runs, chapters, the Future
War lock and the T-1000 gate are off. `code/judgment_day.py`, the shape of
`the_one.py`.

| Stage | Balls | Goal | Score |
| --- | --- | --- | --- |
| 1. The Freeway | 2 | The T-1000 Ramp (backboard ramp), 6 hits (build) | 100,000 per hit |
| 2. The Steel Mill | 4 | A Semi Grille target (either platform target), 4 hits (build) | 500,000 per hit |
| 3. Molten Steel | 6 | The magnet takes a ball and the T-1000 is down for 5 s; an 8 s ball save covers every drain. Then 6 balls, and every ramp is a super jackpot. 3 (build) light the launch sites | 1,000,000 per super jackpot |
| 4. Self-Sacrifice | any | The four Launch Site standups (pop area targets) in order, 1 to 4; a hit out of order does nothing (build) | 5,000,000 on the fourth |

- **Runs until Judgment Day is averted.** It carries on single-ball when the
  multiball drops to one ball, and survives ball end: the stage and its
  progress are stored per player (`judgment_day_stage`,
  `judgment_day_progress`) and resume on that player's next ball, with that
  stage's balls served again. If the game ends first, T2 stays incomplete.
- Averting Judgment Day sets `t2_complete`, sets `chapter` to COMPLETE, ends
  T2 for that player and leaves the remaining balls in play under the base
  mode. A player with `t2_complete` gets the base mode only.

## 11. HUD and the Terminator 2 look

Each game has its own gameplay slide. The Matrix keeps `slides/base/base.tscn`
(digital rain, the sonar trace, phosphor green). Terminator 2 has
`slides/base_t2/base_t2.tscn`: the T-800's view. Near-black with a deep red
cast that is brightest at the centre, scanlines, a faint targeting grid and a
slow interference band (`assets/shaders/t800_vision.gdshader`); white and grey
readout text with red rules and headings; a red glow behind the score; and a
targeting reticle on the idle stage (`assets/shaders/reticle.gdshader`: two
rings, gapped crosshair, corner brackets, ticks, a sweeping marker and a
pulsing centre) over an "ANALYSIS RUNNING" number-lock readout. The same
`stage.gd`, `roster_entry.gd` (with `prefix = "saved"`), `power_stations.gd`
and `trace_readout.gd` scripts drive it, so the two slides share behaviour
and differ only in look. Both scripts now read their variable's current value
when the slide is created, since the slide is rebuilt every ball.

`config.yaml`'s `slide_player` plays `base` or `base_t2` on
`mode_base_started` by `machine.game_choice`, and swaps them on
`game_selected` if player 1's choice went the other way from the slide
already up.

| Variable | Set by | Shown |
| --- | --- | --- |
| `game` | Game Select, per player | (kept for the HUD; the slide swap is driven by `game_choice`) |
| `chapter` | `t2_main` and `judgment_day`: "CHAPTER 1" to "CHAPTER 4", "JUDGMENT DAY", "COMPLETE" | The red marker at the top, where the Matrix's ACT marker sits |
| `objective` | Each chapter, multiball, wizard stage and the controller between chapters | The objective line above the score |
| `balls_locked` | The Future War lock count | The lock cells, headed FUTURE WAR LOCK |
| `saved_*` | Section 9 | The SAVED roster |

T2 has its own widget set in `gmc/widgets/`, the Matrix widgets' layouts in
the T2 palette, so the three stage zones of docs/11 section 9 hold:

| Widget | Zone | Matrix equivalent |
| --- | --- | --- |
| `t2_countdown` | Top | `countdown`; the clock part is `assets/parts/t2_clock.tscn` (white digits, grey churn, red bar, red digits in the last 5 s) |
| `t2_card` | Middle | `chapter_card`, with a red edge and top rule |
| `t2_banner` | Bottom | `mode_banner`, with red rules and a red detail line |
| `dyson_choice` | Whole stage | `pill_choice`, which could not be reused because its labels are authored text: TERMINATE (left flipper, red) or STAND DOWN (right flipper, steel) |
| `game_select` | Whole stage | `act_select`. Plays before the game is chosen, on whichever slide is up |

The rules of docs/11 section 9 apply unchanged: a mode cannot show its own
ending (so Chapter 1's clip and the kill and failed-bypass callouts play from
`t2_main`, and the finale from `base`), a live clock is switched with
`action: update`, and no event argument is called `name` (`name_saved` uses
`who`).

## 12. Film clips

Listed in `gmc/video/manifest.txt`; `tools/check_video.py` reports each one
missing until it is cut. Every entry has an `expire`.

| Clip | Used for |
| --- | --- |
| `mall_pursuit` | Chapter 1 start |
| `flood_channel_rescue` | Chapter 1 complete (from `t2_main`) |
| `pescadero_breakin` | Chapter 2 start |
| `pescadero_breakout` | Break-Out Multiball start |
| `dyson_confrontation` | Chapter 3 choice |
| `dyson_spared` | Chapter 3, spare |
| `cyberdyne_breakin` | Chapter 4 start |
| `cyberdyne_firefight` | Chapter 4, Firefight stage |
| `dyson_sacrifice` | Chapter 4 complete |
| `future_war_flash` | Future War Multiball start |
| `t1000_reveal` | T-1000 Multiball start |
| `freeway_chase` | Judgment Day start |
| `steel_mill_arrival` | Judgment Day, Steel Mill stage |
| `molten_steel` | Judgment Day, the T-1000 down |
| `t800_farewell` | Judgment Day averted (from `base`) |

## 13. Implementation

### Modes

| Mode | Priority | Starts on | Logic |
| --- | --- | --- | --- |
| `game_select` | 2000 | `ball_starting` on ball 1, every player | `code/game_select.py` |
| `base` | 100 | every ball, both games | YAML |
| `t2_main` | 200 | `ball_started` while `game_choice` is `t2` and `t2_complete` is 0 | `code/t2_main.py`: chapter order, Command scoop, multiball queue, roster, Judgment Day resume |
| `future_war_lock`, `t1000_gate` | 250 | `t2_features_start` | YAML |
| `t2_ch1_arrival`, `t2_ch2_pescadero`, `t2_ch3_dyson`, `t2_ch4_raid_lock` | 300 | `start_t2_ch1` to `start_t2_ch4` from `t2_main` | YAML |
| `t2_ch2_breakout_mb`, `t2_ch4_raid_mb` | 310 | `start_breakout_mb`, `start_raid_mb` | YAML |
| `future_war_mb`, `t1000_mb` | 320 | `start_future_war_mb`, `start_t1000_mb` | YAML |
| `judgment_day` | 400 | `start_judgment_day_mb` | `code/judgment_day.py` |

Multiballs never start themselves: a lock posts `request_<name>_mb` and
`t2_main` posts `start_<name>_mb` when nothing else is running. Chapters post
`t2_chN_completed` for the roster and `t2_chN_ended` when played. Device
names shared with Act I (`raid_lock` and `rescue_lock`, `breakout` and
`unplugged`) are distinct because MPF device names are machine-wide.

### Testing

    python -m unittest discover -s tests -t .

`tests/test_game_select.py` covers the offer, stepping, confirming without
adding a player, the timeout, the Act select hand-over and a second player
getting the same game. `tests/test_t2.py` plays every chapter, both
standalone multiballs, the multiball queue, the roster threshold and Judgment
Day (including out-of-order launch sites, the down ball save, resuming after
a drain and T2 complete), and checks that the Matrix's modes do not react to
the shared hardware during a T2 game. The Act I tests choose the Matrix at the
select and pass unchanged in behaviour.

## 14. Still to verify

- **The display on the cabinet.** Every T2 scene and shader was rendered in
  Godot 4.7.2 (OpenGL, under Xvfb, with the real fonts) at 1920x1080 and
  reviewed: the idle slide, the Chapter 1 clocks, the Dyson choice, the
  Firefight stack of clock, card and banner, Judgment Day and the finale.
  Not yet checked: the cabinet's own display, the live slide swap on
  `game_selected` over BCP, and how the film clips sit over the red slide.
- **Booting on the real FAST hardware**, as for Act I.
- **Scoring balance**, once the machine is playable.
- The hardware assumptions in section 1.
