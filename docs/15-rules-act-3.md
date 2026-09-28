# Act III Rules: The Matrix Revolutions (2003)

Rules for the third and last act of the game. Act III is the third film.
These rules are implemented in `config/` and `modes/` and covered by the
tests in `tests/` (section 9). Every number below is the value in the code.

Status (2026-09-28):

- Agreed with the user: Act III is movie 3; its chapters are Mobil Avenue,
  Club Hel, the Siege of Zion and the Hammer, in film order, with the
  Machine City and Neo against Smith as the wizard; Act I's two standalone
  multiballs are re-skinned a third time; a DEFENDERS roster qualifies the
  wizard; beating the wizard completes the Matrix and the player plays on in
  the base mode. The Matrix Resurrections (2021) is not included.
- Decided during the build, not yet reviewed by the user: every rule inside
  a chapter, the roster pairings, the one mechanical change to each
  re-skinned multiball, that Act III starts on the ball Act II ends (as Act
  II does after Act I), and every timer, count and score. Each is marked
  "(build)" where it first appears.
- The framework of Acts I and II is reused unchanged: docs/11-rules-act-1.md
  sections 2 to 5 and docs/14-rules-act-2.md section 8 hold. This document
  states only what differs.
- No new hardware.
- Scores are placeholders at the scale of the earlier acts, for balancing
  once the machine is playable.

Sources: docs/11 and docs/14 and their code, the feature list in
09-parts-inventory.md (user-provided), and the MPF 0.80.0 source. Film scene
references are from recall of the film and have not been checked against a
script or the film. No dialogue is quoted; the on-screen text is written for
the game. Check any line against the clip before it goes on screen.

## 1. Structure at a glance

```
  Act select (before the first ball) can start here; or the Architect ends Act II
                                        |
            always on: Agents, Ammo Lock drain save, Deja Vu, Oracle
                                        |
  Mission Drop scoop starts the next chapter, in film order
   Ch1 Mobil Avenue -> Ch2 Club Hel -> Ch3 The Siege of Zion -> Ch4 The Hammer
                                        |
  Multiballs lit by their own features, any time no other multiball runs
     APU Corps (left lock)                Sentinel Swarm (platform gate)
                                        |
  Each chapter and multiball completed adds one name to the DEFENDERS
                                        |
       four DEFENDERS -> The Machine City (Act III wizard) -> the Matrix complete
```

| Film sequence (from recall) | In Act III |
| --- | --- |
| Neo trapped at Mobil Avenue, the Trainman | Chapter 1, Mobil Avenue |
| Club Hel: the fight to reach the Merovingian, the standoff that frees Neo | Chapter 2, Club Hel |
| The siege of the dock: the APUs, the Kid, Mifune | Chapter 3, The Siege of Zion |
| Niobe flies the Hammer through the tunnels; the EMP in the dock | Chapter 4, The Hammer |
| Neo and Trinity fly to the Machine City; Neo's offer; Smith in the rain | The Machine City (wizard) |

### Starting Act III

- **From Act II:** Act III starts on the same ball (build). The Architect's
  last shot sets `act` to `III`; `act_three` starts on `act_two_complete` as
  well as on `ball_started` while `act` is `III` and `matrix_complete` is 0.
- **From the act select:** `AVAILABLE_ACTS` is now `("I", "II", "III")`.
- **The intro** (clip `mobil_avenue`, card "ACT III / REVOLUTIONS") plays
  once per player, 8 s late when Act III starts on Act II's last ball so it
  does not play over the Sentinels clip.
- Nothing carries over from Act II except score. Any Act II multiball still
  queued is forfeited.

## 2. Always-on features

The base mode is unchanged.

## 3. Chapters

Started as in Acts I and II, in film order, with Act III's own counter
`a3_chapter_next`; after Chapter 4 the scoop replays the first chapter not
completed, and once the Machine City is lit it starts that instead.

### Chapter 1: Mobil Avenue (film: the station between worlds)

Single ball, two timed stages, built like Act I's Trinity's Escape (build).

1. **The tunnel** (30 s): Neo runs the tunnel and comes out on the same
   platform. 25 spinner spins, any spinners: 2,000 a spin, 150,000 at 25.
2. **The train** (20 s hurry-up): the Trainman's train is leaving. The Real
   World Ramp boards it for 300,000 plus 25,000 per second left.

- Either running out of time ends the chapter, played but not completed.
- Boarding adds **SATI**, who is at the station, to the DEFENDERS.

### Chapter 2: Club Hel (film: the club, the ceiling fight, the standoff)

Single ball, three timed rounds, built like Act I's Construct: a round lost
on time still moves on (build).

1. **The lobby** (30 s): the Merovingian's guards. All three Agents down
   (they are raised when the chapter starts). 150,000.
2. **The ceiling** (30 s): the fight upside down. All three Real World
   standups on the upper playfield. 200,000.
3. **The standoff** (20 s): every gun in the room. Both Sentinel entrance
   targets and both boss targets, any order. 300,000.

- Winning the standoff completes the chapter and adds **LOCK** (gameplay
  pairing only).

### Chapter 3: The Siege of Zion (film: the dock)

The chapter is a multiball, started straight from the Mission scoop (build).
Because it is a multiball it counts as the one multiball that may run: a
lock completed during it waits in the queue.

| Stage | Balls | Goal | Score |
| --- | --- | --- | --- |
| The dock | 3 | The APUs hold the dock: ten hits across the Sentinel entrance and boss targets | 75,000 a hit |
| The gate | 4 (add a ball) | The Kid opens the gate for the Hammer: all three three-bank drops (reset at the start of the stage) | 250,000 |
| Mifune's last stand | 5 (add a ball) | The Sentinel ramp | 1,000,000 |

- 20 s ball save, 10 s on each added ball.
- The last stand adds **MIFUNE** to the DEFENDERS. The chapter ends when the
  multiball does.

### Chapter 4: The Hammer (film: the tunnels and the EMP)

Single ball, two timed stages (build).

1. **The tunnels** (40 s): Niobe flies the service tunnels. The four ramps
   in order, left to right: Trinity, Deja Vu, Real World, Sentinel (an MPF
   `sequences:` logic block). A ramp out of order does not count. 100,000
   per ramp in order.
2. **The EMP** (15 s): the Deja Vu VUK fires it. 750,000.

- Either running out of time ends the chapter, played but not completed.
- The EMP adds **ROLAND**, the Hammer's captain, to the DEFENDERS.

## 4. The two standalone multiballs, re-skinned again

Same hardware and mechanics as Acts I and II; new names, callouts, clips and
roster names. They run on every Act III ball except while the Machine City
runs.

| Act I / Act II | Act III | The one change (build) | Defender |
| --- | --- | --- | --- |
| Trinity / Logos lock and multiball | **APU Corps**: three locks on the Trinity Ramp, 3 balls, jackpots on the Trinity Ramp | Each jackpot is worth 50,000 more than the last: 150,000, 200,000, 250,000 | **ZEE** at three jackpots |
| Sentinel gate and multiball / Sentinel Hunt | **Sentinel Swarm**: the Sentinel VUK starts it once the gate is open; 3 balls plus the add-a-ball; jackpots on the Sentinel ramp and boss targets, 150,000 | The gate needs six hits, not four | The **KID** at three jackpots |

Pairings: Zee fights in the dock; the Kid is at the dock. Both are film
links, but which multiball each goes with is a gameplay choice.

## 5. DEFENDERS roster

| Name | Player variable | Added by |
| --- | --- | --- |
| SATI | `defenders_sati` | Chapter 1 |
| LOCK | `defenders_lock` | Chapter 2 |
| MIFUNE | `defenders_mifune` | Chapter 3 |
| ROLAND | `defenders_roland` | Chapter 4 |
| ZEE | `defenders_zee` | APU Corps |
| KID | `defenders_kid` | Sentinel Swarm |

- Each name pays 250,000 once and adds one to `defenders_count`. The event
  is `defender_joined` with the argument `defender`.
- **The Machine City lights at 4 names** (500,000). The operator setting
  `machine_city_threshold` takes 4, 5 or 6.
- The HUD's DEFENDERS panel replaces ALLIES while `act` is `III`
  (`act_panel.gd`; FREED is Act I, ALLIES Act II).

## 6. The Machine City (Act III wizard)

Starts from the Mission scoop once lit. While it runs, chapters, the APU
lock and the Sentinel Swarm gate are off. It runs until Smith is beaten,
survives ball end (`machine_city_stage`, `machine_city_progress`) and resumes
on the player's next ball with that stage's balls served again. Stage logic
is in `modes/the_machine_city/code/the_machine_city.py` (build throughout).

| Stage | Balls | Goal | Score |
| --- | --- | --- | --- |
| 1. Above the clouds | 2 | Trinity flies the Logos up through the clouds: 3 ramps, any | 250,000 each |
| 2. The Machine City | 4 | Neo's offer: each of the four EMP standups once, which opens the Sentinel gate; then the Sentinel VUK jacks Neo in | 300,000 each, 1,000,000 to jack in |
| 3. The rain | 6 | Smith copies: the Agents rise again 1 s after they drop; ten of them | 400,000 each |
| 4. The last Smith | any | The Deja Vu VUK | 10,000,000 |

- Ball saves: 15 s on stages 1 and 2, 20 s on stage 3.
- A resumed stage 2 keeps the targets already hit, and reopens the gate if
  all four were.
- **The end.** The last shot posts `machine_city_peace`, which ends Act III:
  `matrix_complete` is set to 1, `act` stays `III`, and `act_three_complete`
  plays the finale in `base` (clip `peace_sunrise`, card "ACT III COMPLETE /
  THE WAR IS OVER / THE MATRIX COMPLETE"). The remaining balls, and every
  later ball of that player's game, play under the base mode only, as a
  Terminator 2 player does after Judgment Day.
- Trinity's death in the crash is not a stage: it is the transition between
  stages 1 and 2 in the film, and a clip can carry it.

## 7. Display

- Stage widgets are the existing ones: `countdown` (with `value_base` and
  `value_step` for the train), `chapter_card`, `mode_banner`. No new widget.
- Callouts for anything that ends a mode are played by `act_three` (defender
  cards, "The train leaves without you", "The Merovingian walks away", "The
  Hammer is late", the Hammer's EMP clip) or `base` (the finale).

### Film clips

Listed in `gmc/video/manifest.txt`; every entry has an `expire`.

| Clip | Used for |
| --- | --- |
| `mobil_avenue` | Act III intro |
| `trainman` | Chapter 1, the train |
| `club_hel` | Chapter 2 start |
| `siege_dock` | Chapter 3 start |
| `hammer_tunnels` | Chapter 4 start |
| `hammer_emp` | Chapter 4, the EMP |
| `apu_corps` | APU Corps start |
| `sentinel_swarm` | Sentinel Swarm start |
| `above_the_clouds` | The Machine City start |
| `deus_ex_machina` | The Machine City, the offer made |
| `smith_rain` | The Machine City, stage 3 |
| `peace_sunrise` | The end |

## 8. Implementation

| Mode | Priority | Starts on | Logic |
| --- | --- | --- | --- |
| `act_three` | 200 | `act_two_complete`, and every ball while `act` is `III` and the Matrix is not complete | `code/act_three.py` |
| `apu_lock`, `swarm_gate` | 250 | `act_three_features_start` | YAML |
| `a3_ch1_mobil_ave`, `a3_ch2_club_hel`, `a3_ch4_hammer` | 300 | `start_a3_ch1`, `start_a3_ch2`, `start_a3_ch4` from `act_three` | YAML |
| `a3_ch3_siege_mb` | 310 | `start_a3_ch3` from `act_three` | YAML |
| `apu_mb`, `swarm_mb` | 320 | `start_apu_mb`, `start_swarm_mb` | YAML |
| `the_machine_city` | 400 | `start_machine_city_mb` | `code/the_machine_city.py` |

- `ActThree` is the shared controller (`ActOne`) with Act III's tables, as
  `ActTwo` is. The Siege is listed both as chapter 3 and as the multiball
  `siege`, which is what makes it count as the running multiball.
  `CHAPTER_PHASES` is empty.
- `ActOne._act_complete` now leaves `act` alone when `NEXT_ACT` is `None`;
  `ActThree` uses that and sets `matrix_complete` instead.
- New player variables: `a3_chapter_next`, `a3_intro_played`,
  `defenders_*`, `defenders_count`, `machine_city_lit`,
  `machine_city_stage`, `machine_city_progress`, `apu_jackpot_value`,
  `matrix_complete`. New setting: `machine_city_threshold`.

## 9. Testing

    python -m unittest discover -s tests -t .

183 tests at the time of writing, all passing on MPF 0.80.0 and the
smart_virtual platform. `tests/test_act_three.py` covers both ways into Act
III, every chapter's win and time-out paths, the Siege holding a lock in the
queue, both re-skinned multiballs (the rising jackpot values and the
six-hit gate), the roster threshold and setting, and the Machine City's
every stage, the resume after a drain, the Matrix complete and playing on in
the base mode. `tests/test_display.py` checks the intro card, that a
defender card outlives its chapter, and the finale.

## 10. Still to verify

- **The display on the cabinet**, as for Act II: the DEFENDERS panel loads
  and binds in Godot 4.7.2 headless but has not been rendered with the real
  fonts.
- **Film accuracy** of every scene reference and on-screen line.
- **Scoring balance**, including the 10,000,000 final shot against the
  earlier wizards' 5,000,000.
