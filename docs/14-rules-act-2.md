# Act II Rules: The Matrix Reloaded (2003)

Rules for the second act of the game. Act II is the second film. These rules
are implemented in `config/` and `modes/` and covered by the tests in
`tests/` (section 9). Every number below is the value in the code.

Status (2026-09-28):

- Agreed with the user (first round): Act II is movie 2 and its chapters
  follow the film; Act I's two standalone multiballs stay on the same
  hardware, re-skinned for the second film; a new ALLIES roster qualifies the
  wizard; the wizard plays the Architect's two doors as a choice, both doors
  playable, with the Trinity door the film's path and the higher score.
- Agreed with the user (second round): Act II starts on the ball the EMP is
  fired; Chapter 1 is the dock and then a Temple frenzy; no shot at the
  Architect's doors takes the right door (Trinity); build it all.
- Decided during the build, not yet reviewed by the user: which film beats
  became which chapter, every rule inside a chapter, the roster pairings,
  the one mechanical change to each re-skinned multiball, and every timer,
  count and score. Each is marked "(build)" where it first appears.
- Act I's framework is reused: the Mission Drop and scoop start chapters in
  film order, one multiball at a time with the `mb_pending` queue,
  `virtual_only` lock counting, at most 6 balls in play, a wizard that
  survives ball end. docs/11-rules-act-1.md sections 2 to 5 hold; this
  document states only what differs.
- No new hardware. Act II is the first use of the three-bank.
- Scores are placeholders at Act I's scale, for balancing once the machine
  is playable.

Sources: docs/11-rules-act-1.md and the Act I code (the framework reused
here), the feature list in 09-parts-inventory.md (user-provided), the
hardware vocabulary in 12-rules-terminator-2.md section 1, and the MPF 0.80.0
source. Film scene references are from recall of the film and have not been
checked against a script or the film. No dialogue is quoted; the on-screen
text is written for the game. Check any line against the clip before it
goes on screen, as docs/11 asks for Act I.

## 1. Structure at a glance

```
  Act select (before the first ball) can start here; or the EMP ends Act I
                                        |
            always on: Agents, Ammo Lock drain save, Deja Vu, Oracle
                                        |
  Mission Drop scoop starts the next chapter, in film order
     Ch1 Zion -> Ch2 The Oracle -> Ch3 The Merovingian -> Ch4 The Freeway
                                        |
  Multiballs lit by their own features, any time no other multiball runs
     Logos Multiball (left lock)          Sentinel Hunt (platform gate)
                                        |
  Each chapter and multiball completed lights one name in the ALLIES roster
                                        |
          four ALLIES -> The Architect (Act II wizard) -> Act III (docs/15)
```

### The film, in order, and where each part goes

"Follow the second movie" is read as: the chapters and the wizard together
cover the film from Zion to the cliffhanger, in the film's order (build).

| Film sequence (from recall) | In Act II |
| --- | --- |
| Trinity's motorcycle and the fall (the opening dream) | Act II intro clip |
| Zion: the dock, the Temple | Chapter 1, Zion |
| The Oracle: Seraph's test, the Oracle, then the Burly Brawl | Chapter 2, The Oracle |
| The Merovingian: the chateau, Persephone, the Keymaker | Chapter 3, The Merovingian |
| The garage and the freeway: the Twins, the trucks, Neo arrives | Chapter 4, The Freeway |
| The power plant, the hallway of backdoors, the Architect, Trinity's fall | The Architect (wizard), stages 1 to 4 |
| Neo stops the Sentinels in the real world | The Architect, stage 5; sets Act III |

### Starting Act II

- **From the EMP:** Act II starts on the same ball. The EMP ends Act I and
  sets `act` to `II`; `act_two` starts on `act_one_complete` as well as on
  `ball_started` while `act` is `II`, so the balls left in play after the EMP
  are Act II balls.
- **From the act select:** `AVAILABLE_ACTS` in
  `modes/act_select/code/act_select.py` is now `("I", "II")`, so the select
  shows its screen on each player's first ball (docs/11 section 5): flippers
  step, start confirms, 30 s with no confirmation starts Act I. Skipping Act I
  forfeits everything in it.
- **The intro** (clip `trinity_dream`, card "ACT II / RELOADED") plays once
  per player. After the EMP it waits 8 s so it does not play over the EMP
  clip (build); from the act select it plays at once.
- Nothing carries over from Act I except score. The `freed_*` variables keep
  their values but play no part in Act II. Any Act I multiball still queued
  at the EMP is forfeited, and the controller only ever reads its own act's
  multiballs from `mb_pending`.

## 2. Always-on features

The base mode is unchanged: Agents, the Agents Coming scoop, the Ammo Lock
drain save, the Deja Vu VUK and the Oracle mystery.

## 3. Chapters

Started as in Act I: the Mission Drop lights Mission Ready and the scoop
starts the next chapter in film order. After Chapter 4 has been played the
scoop replays the first chapter not completed; once the Architect is lit,
the scoop starts it instead. Played and completed mean what they mean in
Act I. Act II keeps its own chapter counter, `a2_chapter_next`.

### Chapter 1: Zion (film: the dock, the Temple)

Single ball, two timed stages (build).

1. **The dock** (30 s): the Real World Ramp, the long way onto the upper
   playfield, then any Real World standup. 250,000. A standup without the
   ramp first does not count.
2. **The Temple** (30 s frenzy): every playfield switch (the
   `playfield_active` tag, MPF event `sw_playfield_active`) pays the frenzy
   value, which starts at 5,000 and rises 5,000 with every ramp. The four EMP
   standups (the drums), in any order, light a 500,000 collect on the Deja Vu
   VUK.

- The dock or the Temple running out of time ends the chapter, played but
  not completed.
- The Temple collect completes the chapter and allies **LINK**, the
  Nebuchadnezzar's new operator.

### Chapter 2: The Oracle (film: Seraph, the Oracle, the Burly Brawl)

Built like Act I's Red Pill: a single-ball opening that always leads into a
multiball (build).

1. **Seraph's test** (single ball, 30 s): the Sentinel entrance targets are
   Seraph's guard. Hit them alternately, six times: 50,000 a blow, and
   250,000 for beating him. Two hits on the same side do not count. The
   Burly Brawl follows whether or not Seraph is beaten; beating him raises
   the Brawl's ball save from 20 s to 30 s.
2. **The Burly Brawl** (3 balls): the three Agents are Smith copies. Each
   rises again 1 s after it drops. 25,000 per Smith.
   - After 12 Smiths the Sentinel ramp is lit once: Neo flies out. Super
     jackpot 1,000,000.
- The super jackpot allies **SERAPH**. The chapter ends when the multiball
  does.
- The Seraph mode stays running after its 30 s until the Brawl starts. If
  another multiball is running, the Brawl waits in the queue; if the ball
  ends first, the Brawl is dropped and the chapter counts as played.

### Chapter 3: The Merovingian (film: the chateau to the Keymaker)

Single ball, three timed rounds, built like Act I's Construct: a round lost
on time still moves on (build).

1. **The chateau** (30 s): the weapons on the wall. All three three-bank
   drops, 150,000. The bank is reset when the chapter starts.
2. **Persephone** (30 s): her way through the chateau. The Agents Coming
   scoop, 200,000.
3. **The Keymaker** (20 s): the Deja Vu VUK (his room), then any ramp (a
   backdoor out). 300,000.

- Winning round 3 completes the chapter and allies **PERSEPHONE**.

### Chapter 4: The Freeway (film: the garage to the trucks)

Built like Act I's Rescue Morpheus: a single-ball phase that leads into a
staged multiball (build).

1. **The garage** (single ball, 30 s): the Twins. Knock down all five Matrix
   Team drops; the Twins reset the bank every 8 s. All five down between
   resets reaches the car, 250,000, and starts the Freeway multiball. The
   five-bank has one reset coil for the whole bank, so the Twins "phase
   back" by resetting the bank, not one drop at a time. Running out of time
   ends the chapter, played but not completed.
2. **Freeway multiball** (3 balls, 20 s ball save, 10 s on each added ball):

| Stage | Balls | Goal | Score |
| --- | --- | --- | --- |
| The Twins | 3 | All five Matrix Team drops again | 75,000 per drop |
| The Ducati | 4 (add a ball) | Trinity and the Keymaker against the traffic: the Trinity, Deja Vu and Real World ramps (the three spinner ramps) inside 20 s, any order. Out of time: the three start again | 250,000 per ramp |
| The trucks | 5 (add a ball) | Neo arrives before the trucks collide: the Sentinel ramp | 1,000,000 |

- The trucks stage allies **KEYMAKER**. The chapter ends when the multiball
  does.
- Chapter 4 uses no lock, so the Ammo Lock drain save stays on throughout
  (unlike Act I's Chapter 4).

## 4. The two standalone multiballs, re-skinned

Same hardware and mechanics as Act I's (docs/11 section 6); new names,
callouts, clips and roster names. They run whenever Act II's features are
on, which is every Act II ball except while the Architect runs.

| Act I | Act II | Film link | Allies |
| --- | --- | --- | --- |
| Trinity lock, Trinity Multiball | **Logos lock, Logos Multiball**: Niobe's ship. Three locks on the Trinity Ramp, 10,000 each; 3 balls, 20 s ball save; 150,000 jackpots | Niobe captains the Logos | **NIOBE** at three jackpots |
| Sentinel gate, Sentinel Multiball | **Sentinel Hunt**: the machines searching the tunnels. Four gate hits open it (100,000), the Sentinel VUK starts it; 3 balls plus the add-a-ball; 150,000 jackpots on the Sentinel ramp and boss targets | Gameplay pairing only | **GHOST** at four jackpots |

The one change to each, so they do not replay Act I exactly (build):

- **Logos:** the jackpot starts on the Trinity Ramp and moves to the Deja Vu
  Ramp after every jackpot, then back. The HUD's objective line says which.
- **Sentinel Hunt:** four jackpots to complete, not three.

The Logos lock is a new device, so Act I's Trinity lock count does not carry
over; `balls_locked` is set from the Logos lock whenever its mode starts.

## 5. ALLIES roster

| Name | Player variable | Allied by |
| --- | --- | --- |
| LINK | `allies_link` | Chapter 1 |
| SERAPH | `allies_seraph` | Chapter 2 |
| PERSEPHONE | `allies_persephone` | Chapter 3 |
| KEYMAKER | `allies_keymaker` | Chapter 4 |
| NIOBE | `allies_niobe` | Logos Multiball |
| GHOST | `allies_ghost` | Sentinel Hunt |

- Each name pays 250,000 once and adds one to `allies_count`. The event is
  `ally_joined` with the argument `ally` (never `name`, docs/11 section 9).
- **The Architect lights at 4 names** (500,000). The operator setting
  `architect_threshold` takes 4, 5 or 6.
- **HUD:** the base slide has an ALLIES panel in the same place as FREED,
  built from the same `roster_entry.gd` with `prefix = "allies"`.
  `gmc/slides/base/act_panel.gd` shows FREED while `act` is `I` and ALLIES
  while it is `II` (DEFENDERS takes over in Act III, docs/15). NIOBE and LINK were placeholders in the FREED
  panel that no Act I rule lit; they are now in ALLIES.

## 6. The Architect (Act II wizard)

Starts from the Mission scoop once lit. While it runs, chapters, the Logos
lock and the Sentinel Hunt gate are off. Like The One, it runs until its
last shot, survives ball end (`architect_stage`, `architect_progress`,
`architect_door`) and resumes on the player's next ball with that stage's
balls served again. Stage logic is in `modes/the_architect/code/the_architect.py`.

| Stage | Balls | Goal | Score |
| --- | --- | --- | --- |
| 1. The power plant | 2 | Niobe's crew cuts the power: each of the four EMP standups once | 250,000 each |
| 2. The hallway | 4 | The backdoors: each three-bank drop is a door. The Smiths close every door 6 s after the first one opens, unless all three are open. All three open lights the Keymaker's last door on the Deja Vu VUK | 500,000 per door, 1,000,000 for the last |
| 3. The Architect | any | The **left door** is any left-side shot (Trinity Ramp, Deja Vu Ramp); the **right door** any right-side shot (Real World Ramp, Sentinel ramp). 15 s; no shot takes the right door | |
| 4a. Left door: the Source | 6 | Reload Zion: every ramp is a super jackpot for 30 s, up to four; either ends the stage | 750,000 per ramp |
| 4b. Right door: Trinity | any | Trinity falls: a hurry-up from 5,000,000 falling 100,000 a second to 1,000,000 over 40 s, then holding. The Real World Ramp (Neo flies), then the Sentinel magnet catches a ball for 2 s (Neo catches her) | The hurry-up value |
| 5. Something is different | any | The Sentinel gate opens; the Sentinel VUK stops the Sentinels | 5,000,000 |

- Each multiball stage has a 15 s ball save; the Source's has 20 s.
- **Why a shot, not the flippers, picks the door.** Act I's pill choice uses
  the flippers because it is single ball, with the ball held in the scoop.
  The Architect's choice comes mid-multiball, and holding the flippers for a
  menu would throw balls away (docs/11 section 8 says the same of Neo dying).
  The playfield's two sides are the two doors. The shot that picks a door
  scores nothing else: the Real World Ramp that takes the right door does
  not also count as Neo flying.
- **Both doors are playable.** The left door pays at most 3,000,000. The
  right door is the film's path, adds the magnet catch, and pays up to
  5,000,000. The door taken is kept in `architect_door` (`source` or
  `trinity`) and survives ball end, so a resumed stage 4 is the same door.
- A resumed stage 2 keeps the last door lit if it was; a resumed stage 3
  restarts its 15 s; a resumed stage 4 restarts its clock.
- Stage 5 sets `act` to `III`, ends Act II and starts Act III on the same
  ball, with the remaining balls in play (docs/15-rules-act-3.md, section 1).
- The shaker is not wired yet, so the mode does not drive it.

## 7. Display

- `act` shows `II`, then `III`, on the HUD.
- `balls_locked` drives the power station cells for the Logos lock.
- Stage widgets are Act I's: `countdown` for each timed stage and for the
  Trinity hurry-up (its `value_base` and `value_step` tokens show the
  falling value), `chapter_card` for starts, stages and allies, and
  `mode_banner` for jackpots and callouts.
- One new widget, `gmc/widgets/doors_choice.tscn`, for the Architect's
  stage 3: `pill_choice`'s layout, with a white left door (THE SOURCE, "ANY
  LEFT SHOT") and a green right door (TRINITY, "ANY RIGHT SHOT"). Its clock
  follows `architect_choice_tick`.
- As in Act I, a mode cannot show its own ending, so the callouts for
  anything that ends a mode are played by `act_two` (ally cards, "The dock
  is closed", "The drums fall silent", "The Keymaker is gone", "The Twins
  win") or `base` (the Sentinels clip and "Act II complete").

### Film clips

Listed in `gmc/video/manifest.txt`; every entry has an `expire`.

| Clip | Used for |
| --- | --- |
| `trinity_dream` | Act II intro |
| `zion_dock` | Chapter 1 start |
| `zion_temple` | Chapter 1, the Temple |
| `seraph_test` | Chapter 2 start |
| `burly_brawl` | Burly Brawl start |
| `merovingian` | Chapter 3 start |
| `keymaker` | Chapter 3, round 3 |
| `twins_garage` | Chapter 4 start |
| `freeway_trucks` | Freeway multiball start |
| `neo_flies` | Chapter 4, Neo arrives |
| `logos_mb_intro` | Logos Multiball start |
| `sentinel_hunt` | Sentinel Hunt start |
| `power_plant` | The Architect start |
| `backdoor_hallway` | The Architect, stage 2 |
| `architect_doors` | The Architect, stage 3 |
| `trinity_falls` | The Architect, right door |
| `sentinels_stop` | The Architect, stage 5 |

## 8. Implementation

### Modes

| Mode | Priority | Starts on | Logic |
| --- | --- | --- | --- |
| `act_two` | 200 | `act_one_complete`, and every ball while `act` is `II` | `code/act_two.py` |
| `logos_lock`, `hunt_gate` | 250 | `act_two_features_start` | YAML |
| `a2_ch1_zion`, `a2_ch2_seraph`, `a2_ch3_merovingian`, `a2_ch4_garage` | 300 | `start_a2_ch1` to `start_a2_ch4` from `act_two` | YAML |
| `a2_ch2_brawl_mb`, `a2_ch4_freeway_mb` | 310 | `start_brawl_mb`, `start_freeway_mb` | YAML |
| `logos_mb`, `hunt_mb` | 320 | `start_logos_mb`, `start_hunt_mb` | YAML |
| `the_architect` | 400 | `start_architect_mb` | `code/the_architect.py` |

- **One controller for both acts.** `ActTwo` subclasses Act I's `ActOne`
  (`modes/act_one/code/act_one.py`). Every act-specific name (the chapter,
  multiball and roster tables, the event and variable names, the wizard and
  its setting) is a class attribute that `ActTwo` overrides. Act I's
  behaviour is unchanged; its tests pass as before. `t2_main.py` is a
  separate copy of the same shape and was left alone.
- A chapter whose first phase leads into a multiball is listed in
  `CHAPTER_PHASES` (Act I: chapter 4; Act II: chapters 2 and 4). When that
  phase stops without its multiball running or starting, the chapter ends
  there, and a queued chapter multiball dies with its chapter.
- Chapter events are `start_a2_chN`, `a2_chN_completed` and `a2_chN_ended`.
- The mode scoop's ball hold is `a2_scoop_hold`, released by the same
  `mode_scoop_release` event as Act I's.
- New player variables in `config/config.yaml`: `a2_chapter_next`,
  `a2_intro_played`, `act_finale`, `allies_*`, `allies_count`,
  `architect_lit`, `architect_stage`, `architect_progress`, `architect_door`,
  `architect_value`, `brawl_mb_starting`, `freeway_mb_starting`. New setting:
  `architect_threshold`.
- Keyboard: `z`, `p` and `comma` toggle the three-bank drops for
  `mpf both -X` play (`gmc/gmc.cfg`).

### A timer fix that also applies to Act I

A round lost on time stops its MPF timer at zero, and a later `jump` sets the
value without starting it again. Act I's Construct had this: if sparring ran
out, the jump round had no clock and the chapter ran until the ball drained.
`ch3_construct` and `a2_ch3_merovingian` now `start` the timer after the
`jump`, and `tests/test_act_one.py` has a regression test.

## 9. Testing

    python -m unittest discover -s tests -t .

159 tests when Act II was written (docs/15-rules-act-3.md, section 9, has the
current count), all passing on MPF 0.80.0 and the
smart_virtual platform. `tests/test_act_two.py` covers both ways into Act II,
the intro, every chapter's win, time-out and drain paths, the Brawl queued
behind another multiball, both re-skinned multiballs, the roster threshold
and setting, and the Architect's every stage, both doors, the default door,
the hurry-up floor and resuming after a drain. `tests/test_display.py` checks
the intro card, that an ally card outlives its chapter, the doors clock, the
Trinity hurry-up clock and the Act II finale.

`tests/matrix_test_case.py`'s `start_matrix_game(act=...)` now confirms the
act select, which appears on every Matrix game now that two acts are
offered; the game select and act select tests were updated for that.

## 10. Still to verify

- **The display on the cabinet.** `base.tscn` (with the ALLIES panel),
  `act_panel.gd` and `doors_choice.tscn` load and instantiate in Godot 4.7.2
  headless. They were not rendered: the fonts are Git LFS files and were not
  fetched in the build container. Check the ALLIES panel switching over at
  the EMP, and the doors widget, with `mpf both -X`.
- **Film accuracy** of every scene reference and on-screen line.
- **Scoring balance** once the machine is playable, including whether the
  left door's 3,000,000 against the right door's 5,000,000 is the right gap.
- **The platform magnet during the Trinity catch.** It is modelled as in Act
  I's helicopter catch: a ball over the magnet is grabbed for 2 s. Whether
  the magnet is reachable with the gate up is a hardware question (docs/11
  section 11).
