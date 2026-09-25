# Game Select and Terminator 2 (1991) Rules

This document plans a second selectable game on the same cabinet: Terminator 2:
Judgment Day. It covers the new top-level Game Select mode that chooses
between Matrix and Terminator 2, the physical shot mapping needed to run a
second ruleset on one playfield, and the full Terminator 2 rule set in the
same depth as `docs/11-rules-act-1.md`.

Status (2026-09-25): this is a planning document, not yet implemented. Three
points are confirmed with the user; everything else below is a proposal
pending review, marked "(proposed)" where it matters most.

Confirmed with the user:

- Terminator 2 runs on the existing cabinet and reuses the existing physical
  shots (Trinity Ramp, Sentinel Ramp/VUK/magnet, Deja Vu VUK, Real World Ramp,
  Ammo Lock, Agents pop-ups, Matrix Team drops, EMP standups), reskinned. No
  new hardware is assumed.
- A new top-level Game Select mode sits above the existing Act select. Choosing
  Matrix drops into Act select (I/II/III) as it works today. Choosing
  Terminator 2 goes straight into its own chapter structure, because T2 has
  only one film's worth of rules so far, exactly as Act select today "steps
  straight out" when only Act I has rules (section 5 of docs/11).
- This session's deliverable is this design document only. No code or config
  changes are made here.

Film references are from recall of Terminator 2: Judgment Day (1991, dir.
James Cameron) and cover only its well-known, widely documented plot beats
(the mall pursuit, the flood-channel chase, the Pescadero breakout, the Dyson
confrontation, the Cyberdyne raid, the steel mill finale). No specific
dialogue is quoted here; any line put on screen should be checked against the
film before use, exactly as docs/11 already asks for Matrix clips.

## 1. Required prerequisite: de-couple hardware from theme

This is the one piece of real engineering work this plan depends on, and it
also touches the existing Matrix code.

Today, per docs/11 section 11, each playfield switch's `events_when_activated`
already carries the Matrix name (`trinity_ramp_hit`, `sentinel_ramp_hit`, and
so on), and `act_one`'s modes listen to those names directly. That is fine for
one ruleset. It does not work for two: a second ruleset cannot listen for
`trinity_ramp_hit` without a hidden dependency on Matrix's name for a shot it
calls something else.

Proposed fix, needed before any T2 mode is built:

1. Rename every shared switch's `events_when_activated` in `config/config.yaml`
   (and `config/playfield_pending.yaml`) to a physical, theme-neutral name,
   for example `ramp_1_hit` instead of `trinity_ramp_hit`, `vuk_1_ball_entered`
   instead of `deja_vu_vuk_active`. This is a rename only; no device, wiring or
   coil rule changes.
2. Each ruleset's modes subscribe to the physical event and re-post their own
   themed event for their own scoring and display layer (`act_one` posts
   `trinity_ramp_hit` from `ramp_1_hit`; a T2 mode posts `future_war_ramp_hit`
   from the same `ramp_1_hit`).
3. Only one ruleset's modes are ever running at a time (Game Select gates
   which set loads), so both can react to the same physical event with no
   conflict.

This is a real refactor of the existing Act I config and is worth doing as its
own piece of work before T2 rule-writing starts, not folded silently into the
first T2 commit.

## 2. Game Select

A new mode, `game_select`, runs once per game before any player's first ball,
ahead of `act_select`.

- Sequence: attract to start button pressed to `game_select` to (if Matrix)
  `act_select` to Act I/II/III, or (if Terminator 2) straight into T2's
  chapters.
- Controls mirror `act_select`: flippers step between the two games, start
  confirms. No confirmation in a timeout (proposed: 15 s, shorter than Act
  select's 30 s, because there are only two choices) starts Matrix, as the
  finished, better-tested game (proposed default; confirm with the user).
- The choice is machine-wide for the game in progress, not per player, the
  same as Act select today: one game, one ruleset, for every player in it.
- Sets a machine variable, `game_choice` (`matrix` or `t2`), and posts
  `game_matrix_selected` or `game_t2_selected`. `act_select` is changed to
  only start on `game_matrix_selected`.
- Display: reuses the `act_select` widget pattern (whole-stage clock plus the
  option on offer), retitled. Confirm whether it needs its own widget scene or
  can take T2/Matrix logo tokens on the existing one.
- `base` becomes the shared HUD shell for both games (player, ball, score are
  game-agnostic); the parts of the HUD that are Matrix-specific (`act`, the
  FREED roster, the power station cells) only populate when `game_choice` is
  `matrix`, and T2 populates its own equivalents (`chapter`, the SAVED roster,
  a launch-site counter) when `game_choice` is `t2`. Whether that is one
  `base.tscn` with conditional panels or two base slides is a display
  decision, not a rules one; flagging it here so it is not missed.

## 3. Structure at a glance (Terminator 2)

```
  Game Select (before Act select): Matrix, or Terminator 2
                                        |
        always on: Endoskeletons, Arsenal Lock drain save, Displacement, Vision
                                        |
  Command scoop starts the next chapter, in film order
   Ch1 Arrival -> Ch2 Pescadero Break-Out -> Ch3 The Choice: Dyson -> Ch4 Cyberdyne Raid
                                        |
  Multiballs lit by their own features, any time no other multiball runs
     Future War Multiball (Future War lock)    T-1000 Multiball (T-1000 gate)
                                        |
  Each chapter and multiball completed lights one name in the SAVED roster
                                        |
        four names SAVED -> Judgment Day (T2 wizard) -> future T2 acts
```

## 4. Physical shot mapping

Every row keeps the existing device and its existing mechanical behaviour
(lock counts, hold times, magnet duration, drop bank size). Only the name,
scoring and story meaning change.

| Physical device | Matrix identity | Terminator 2 identity | T2 story meaning |
| --- | --- | --- | --- |
| Smart drop + scoop | Mission Drop + Mission scoop | Perimeter Drop + Command scoop | Breaching the next objective; starts each chapter |
| 3-position lock ramp | Trinity Ramp | Future War Ramp | Sarah's recurring flash-forward: surviving Hunter-Killer sorties |
| Ramp + VUK pair | Deja Vu Ramp + VUK | Displacement Ramp + VUK | Time-displacement arrivals (both Terminators arrive naked in a lightning field) |
| Ramp + 3 standups | Real World Ramp + standups | Pescadero Ramp + Ward standups | Escaping the mental hospital |
| Ramp, VUK, magnet, 2 entrance targets, boss target | Sentinel toy set | T-1000 toy set (T-1000 Ramp/VUK/magnet, Cruiser targets, Semi Grille) | The T-1000's pursuit by cruiser and tanker truck |
| 3 pop-ups + scoop | Agents + Agents Coming scoop | Endoskeletons + Assembly Line scoop | Skynet's mass-produced units |
| Lock + target | Ammo Lock + target | Arsenal Lock + target | The gun-store arsenal montage; same drain-save mechanic |
| 5-bank drop targets | Matrix Team drops | Cyberdyne Lab drops | Wiping the lab's systems during the raid |
| 4 standups | EMP standups | Launch Site standups | Nuclear launch sites from Sarah's nightmare; lights Vision, and later arms/disarms Judgment Day |
| Lanes/spinners | (unnamed) | Freeway lanes/spinners | Cosmetic only |
| Left/right flipper buttons (mode input) | Blue Pill / Red Pill | Kill Dyson / Spare Dyson | Sarah's choice at gunpoint in Dyson's house |

## 5. Ball count

Inherited from the shared hardware, not a T2-specific decision: 7 balls
installed, at most 6 balls in play (Judgment Day), `virtual_only` lock
counting, one multiball at a time with a `mb_pending` queue, exactly as
docs/11 sections 2 to 3 already establish for the cabinet.

## 6. Always-on features (T2 base mode)

| Feature | Rule | Score |
| --- | --- | --- |
| Endoskeletons (3 pop-ups) | Hit a raised one: "Terminator Down". All three down: "Skynet's Down". Raised at the start of every ball. | 10,000 each, 50,000 all down |
| Assembly Line scoop | All three down: raises them again. Otherwise a small award. | 50,000 or 5,000 |
| Arsenal Lock | Drain-save, identical mechanic to Ammo Lock. Stands down during Chapter 4's lock phase. | 15,861 per lock |
| Displacement VUK | "Displacement" award. | 2,570 |
| Vision (proposed, reskin of Oracle) | The four Launch Site standups, any order, light it; the Displacement VUK collects a random award. Once Judgment Day is lit, the Command scoop starts it instead of a chapter, mirroring the Mission scoop's Act I behaviour. | 25,000, 75,000 or 150,000 |
| Freeway lanes/spinners | Inlanes and every spinner. | 100 |

## 7. Chapters

Chapters play in film order. A chapter is played when it ends, including by a
drain; it is completed when its goal is met, and only completion saves a
name. This section reassigns which original chapter *shape* each T2 chapter
uses (hurry-up, choice-into-multiball, skill rounds, lock-into-multiball); the
film's actual event order is followed, not the Matrix chapter numbering.

### Chapter 1: Arrival (film: the mall, then the flood channel)

Single-ball hurry-up, matching Ch1 Trinity's Escape's shape.

1. **The mall:** three ramp shots, any ramps, inside 40 s (proposed). Represents
   John evading the T-1000 posing as a police officer. 50,000 per shot.
2. **The flood channel:** the Displacement VUK, inside 20 s (proposed).
   Represents the T-800 pulling John onto the motorcycle. Pays 250,000 plus
   25,000 per second left.

- Either timer running out: T-1000 gets away clean, played but not completed.
- Completion saves **JOHN**.

### Chapter 2: Pescadero Break-Out (film: breaking Sarah out of the hospital)

Lock-then-multiball shape, matching Ch4 Rescue Morpheus's opening two beats.

1. **Getting in:** the Command scoop holds the ball; three Ward standup hits
   (any order) represent getting past the orderlies. 50,000 each.
2. **Break-Out Multiball:** 3 balls, 20 s ball save (proposed). Jackpot on the
   Pescadero Ramp, 100,000. Super jackpot: all three Ward standups again
   during the multiball, 500,000, once.
- The super jackpot saves **SARAH**. The chapter ends when the multiball does.

### Chapter 3: The Choice: Dyson (film: confronting Miles Dyson)

Binary choice, matching Ch2 Red Pill's shape exactly.

1. **At gunpoint:** the Command scoop keeps the ball. Left flipper: Kill.
   Right flipper: Spare. No input in 10 s (proposed): Spare, since that is
   what happens in the film.
   - **Kill:** "That's not who you are." 5,000, and the chapter ends, played
     but not completed. No skill round follows.
   - **Spare:** the skill round below runs.
2. **Cyberdyne Lab bypass:** single-ball skill round (proposed: 30 s). All
   five Cyberdyne Lab drops, representing Dyson walking them through his own
   building's security. 150,000.
- Completing the bypass saves **DYSON**. Sparing him is required for
  completion; killing him is not recoverable this chapter.

### Chapter 4: Cyberdyne Raid (film: the break-in, the firefight, Dyson's sacrifice)

Three-stage escalating multiball, matching Ch4 Rescue Morpheus's Lobby/
Rooftop/Helicopter shape.

| Stage | Balls | Goal | Score |
| --- | --- | --- | --- |
| Break-In | 3 | Every guard: the four Launch Site standups and the three Endoskeletons (raised again whenever all three are down) | 75,000 per guard |
| Firefight | 4 (add a ball) | The Future War Ramp lights "Hold the line" for 10 s; hit an Endoskeleton while it is lit | 250,000 |
| Escape | 5 (add a ball) | A ball over the T-1000 magnet is caught (the T-1000's cruiser just misses the getaway truck); the magnet lets go after 2 s | 1,000,000 |

- The Escape catch saves **CHIP** (the CPU chip and arm destroyed with the
  building). The chapter ends when the multiball does.
- A drain during the Break-In lock phase ends the chapter, played.

## 8. The two standalone multiballs

Both run whenever T2's features are on, which is every T2 ball except while
Judgment Day runs, mirroring Trinity/Sentinel Multiball's availability rule.

### Future War Multiball (reskin of Trinity Multiball)

- The Future War Ramp lock takes three balls, 10,000 each. The HUD shows the
  count where the power station cells sit for Matrix.
- The third lock requests a 3-ball multiball, 20 s ball save, released from
  the lock. "Resistance Bonus" jackpots on the Future War Ramp, 150,000.
- Three jackpots (proposed) save **RESISTANCE**.

### T-1000 Multiball (reskin of Sentinel Multiball)

- Four hits across the two Cruiser targets open the way ("It's found you!",
  100,000). A ball into the T-1000 VUK while it is open requests the
  multiball: 3 balls, 20 s ball save.
- Jackpots on the T-1000 Ramp and the Semi Grille, 150,000. Three jackpots
  (proposed) save **SKYNET** (meaning Skynet's agent was driven off, a
  temporary win, not its final defeat, which is reserved for the wizard mode).
- Add-a-ball, once per multiball: hit the two Cruiser targets and the Semi
  Grille to light it, then shoot the T-1000 VUK. 10 s save on the added ball.
  Peaks at 4 balls.
- The gate closes and the hit count resets when the multiball ends, and also
  at ball end, so all four hits and the VUK shot must come on one ball.

## 9. SAVED roster

| Name | Player variable | Saved by |
| --- | --- | --- |
| JOHN | `saved_john` | Chapter 1 |
| SARAH | `saved_sarah` | Chapter 2 |
| DYSON | `saved_dyson` | Chapter 3, Spare path only |
| CHIP | `saved_chip` | Chapter 4 |
| RESISTANCE | `saved_resistance` | Future War Multiball |
| SKYNET | `saved_skynet` | T-1000 Multiball |

- Each name pays 250,000 once and adds one to `saved_count`, mirroring
  `freed_count`.
- Judgment Day lights at 4 names (500,000), with the same operator setting
  pattern as `the_one_threshold` (proposed name: `judgment_day_threshold`,
  4, 5 or 6).

## 10. Judgment Day (T2 wizard mode)

Starts from the Command scoop once lit. While it runs, chapters, the Future
War lock and the T-1000 gate are off, mirroring The One's exclusivity rule.

| Stage | Balls | Goal | Score |
| --- | --- | --- | --- |
| 1. Freeway | 2 | The T-1000 Ramp, 6 hits (proposed) as the tanker chase spills onto the freeway | 100,000 per hit |
| 2. Steel Mill Arrival | 4 | The Semi Grille shot knocks the T-1000 down; it gets back up 1 s later, mirroring the Agent-rise timing in The One | 500,000 per hit |
| 3. Molten Steel | 6 | The T-1000 magnet catch pushes it toward the vat; every ramp becomes a super jackpot while it is down | 1,000,000 per super jackpot |
| 4. Self-Sacrifice | any | The four Launch Site standups, in sequence, as the T-800 lowers itself into the steel to destroy the last chip | 5,000,000 |

- Runs until the last Launch Site standup is hit. Carries on single-ball if
  the multiball drops to one ball, and survives ball end exactly as The One
  does (`judgment_day_stage`, `judgment_day_progress`, resuming with that
  stage's balls served again).
- Flippers stay live throughout, matching The One's reasoning: disabling them
  mid-multiball reads as a fault, not a story beat.
- Clearing stage 4 ends T2 for the game (there is no Act II yet for this
  ruleset; see section 12). If the game ends first, T2 stays incomplete for
  that player.

## 11. HUD variables (Terminator 2)

| Variable | Set by |
| --- | --- |
| `chapter` | The current chapter number or "JUDGMENT DAY" once the wizard starts |
| `objective` | Shared with Matrix; each chapter, multiball and wizard stage sets it |
| `future_war_locked` | Future War Ramp lock count, shown where `balls_locked` sits for Matrix |
| `saved_*` | Section 9 |

Stage widgets are shared with Matrix as-is: `countdown`, `chapter_card`,
`mode_banner` and `act_select`'s pattern all take plain text/label tokens
already, so no new widget scenes are needed for T2's own timers and callouts.
`pill_choice` is reused verbatim for the Kill/Spare choice; only its tokens
change (labels, not the scene). This is worth confirming against the actual
widget scenes before implementation, since docs/11 section 9 describes them
as taking tokens but the T2-specific text has not been laid out against them.

## 12. Film clips (placeholders, to be shot-listed later)

| Clip | Used for |
| --- | --- |
| `mall_pursuit` | Chapter 1 start |
| `flood_channel_rescue` | Chapter 1 complete |
| `pescadero_breakin` | Chapter 2 start |
| `pescadero_breakout` | Break-Out Multiball start |
| `dyson_confrontation` | Chapter 3 choice |
| `dyson_spared` | Chapter 3, Spare path |
| `cyberdyne_breakin` | Chapter 4 start |
| `cyberdyne_firefight` | Chapter 4, Firefight stage |
| `dyson_sacrifice` | Chapter 4 complete |
| `future_war_flash` | Future War Multiball start |
| `t1000_reveal` | T-1000 Multiball start |
| `freeway_chase` | Judgment Day, Freeway stage |
| `steel_mill_arrival` | Judgment Day, Steel Mill Arrival stage |
| `molten_steel` | Judgment Day, Molten Steel stage |
| `t800_farewell` | The Self-Sacrifice stage |

Exactly as docs/11 section 10 notes for Matrix: each entry needs an `expire`
so a missing clip leaves the stage rather than blocking it, and every quoted
line should be checked against the film before it goes on screen; none is
quoted in this document.

## 13. Implementation (proposed mode map)

| Mode | Priority | Starts on | Logic |
| --- | --- | --- | --- |
| `game_select` | 2000 | before `act_select`, once per game | `code/game_select.py` |
| `base` | 100 | every ball, both games | YAML, with T2/Matrix HUD panels gated on `game_choice` |
| `t2_main` | 200 | every ball while `game_choice` is `t2` | `code/t2_main.py`: chapter order, Command scoop, multiball queue, roster, Judgment Day resume |
| `future_war_lock`, `t1000_gate` | 250 | `t2_features_start` | YAML |
| `t2_ch1_arrival`, `t2_ch2_pescadero`, `t2_ch3_dyson`, `t2_ch4_raid` | 300 | `start_ch1` to `start_ch4` from `t2_main` | YAML |
| `t2_ch2_breakout_mb`, `t2_ch4_raid_mb` | 310 | `start_breakout_mb`, `start_raid_mb` | YAML |
| `future_war_mb`, `t1000_mb` | 320 | `start_future_war_mb`, `start_t1000_mb` | YAML |
| `judgment_day` | 400 | `start_judgment_day_mb` | `code/judgment_day.py` |

This mirrors docs/11 section 11's table and priority scheme exactly, so the
existing `act_one`/`the_one` code is a direct template for `t2_main`/
`judgment_day`.

## 14. Still to decide

- **The section 1 hardware refactor** is the one item that must be settled
  and built before any T2 mode can be written; everything else in this
  document assumes it is done.
- **Game Select's timeout and default** (proposed 15 s, default to Matrix):
  confirm with the user.
- **Whether `base` is one slide with conditional panels or two slides**
  (`base_matrix`, `base_t2`): a display decision, not covered here.
- **Scores throughout are placeholders**, at the same scale as Act I's
  placeholders, for balancing once both games are playable.
- **All proposed timer lengths** (marked "(proposed)" above) need the same
  kind of build-time decision Act I's timers went through.
- **A future second T2 act** (a further Terminator film) is structurally
  possible, the same way Act II/III sit above Act I today, but is out of
  scope until T2's own Act I is built and played.
