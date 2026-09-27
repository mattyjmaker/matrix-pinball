# Act II Rules: The Matrix Reloaded (2003)

Design for the second act of the game. Act II is the second film. This is a
rules design, not an implementation: nothing here is in `config/` or
`modes/` yet. Today an Act II player gets the base mode only
(docs/11-rules-act-1.md, section 5).

Status (2026-09-27):

- Agreed with the user: Act II is movie 2 and its chapters follow the film;
  Act I's two standalone multiballs stay on the same hardware, re-skinned for
  the second film; a new ALLIES roster qualifies the wizard; the wizard
  plays the Architect's two doors as a choice, both doors playable, with the
  Trinity door the film's path and the higher score.
- Everything else is a proposal, marked "(proposed)" where it first appears.
  In particular: which film beats become which chapter, every rule inside a
  chapter, the roster pairings, and every timer, count and score.
- Act I's framework is reused unchanged: the Mission Drop and scoop start
  chapters in film order, one multiball at a time with the `mb_pending`
  queue, `virtual_only` lock counting, at most 6 balls in play, a wizard that
  survives ball end. docs/11-rules-act-1.md sections 2 to 5 hold; this
  document states only what differs.
- No new hardware. Act II uses the three-bank, which neither game uses yet.
- Scores are placeholders at Act I's scale, for balancing once the machine
  is playable.

Sources: docs/11-rules-act-1.md and the Act I code (the framework reused
here), the feature list in 09-parts-inventory.md (user-provided), the
hardware vocabulary in 12-rules-terminator-2.md section 1. Film scene
references are from recall of the film and have not been checked against a
script or the film. No dialogue is quoted; check any line against the clip
before it goes on screen, as docs/11 asks for Act I.

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
          four names ALLIED -> The Architect (Act II wizard) -> Act III
```

### The film, in order, and where each part goes

"Follow the second movie" is read as: the chapters and the wizard together
cover the film from Zion to the cliffhanger, in the film's order.

| Film sequence (from recall) | In Act II |
| --- | --- |
| Trinity's motorcycle and the fall (the opening dream) | Act II intro clip |
| Zion: the dock, the Temple, the machines digging towards the city | Chapter 1, Zion |
| The Oracle: Seraph's test, the Oracle, then the Burly Brawl | Chapter 2, The Oracle |
| The Merovingian: the restaurant, the chateau fight, Persephone, the Keymaker | Chapter 3, The Merovingian |
| The garage and the freeway: the Twins, the Agents, the trucks, Neo arrives | Chapter 4, The Freeway |
| The power plant, the hallway of backdoors, the Architect, Trinity's fall | The Architect (wizard), stages 1 to 4 |
| Neo stops the Sentinels in the real world | The Architect, stage 5; sets Act III |

### Starting Act II

- **From the EMP (proposed):** Act II starts on the same ball. The EMP ends
  Act I and sets `act` to `II` (docs/11 section 8); `act_two` starts on
  `act_one_complete` as well as on `ball_started` while `act` is `II`, so the
  balls left in play after the EMP are already Act II balls. The Act II intro
  plays after the "Act I complete" card.
- **From the act select:** add `II` to `AVAILABLE_ACTS` in
  `modes/act_select/code/act_select.py`. The select then shows its screen for
  the first time. Skipping Act I forfeits everything in it, as docs/11
  section 5 already says.
- Nothing carries over from Act I except score. The `freed_*` variables keep
  their values but play no part in Act II; section 5 covers the HUD.

## 2. Always-on features

The base mode is unchanged: Agents, the Agents Coming scoop, the Ammo Lock
drain save, the Deja Vu VUK and the Oracle mystery. All of them fit the
second film as they are (the Agents return, upgraded; the Oracle is a
central character).

## 3. Chapters

Started as in Act I: the Mission Drop lights Mission Ready and the scoop
starts the next chapter in film order. After Chapter 4 has been played the
scoop replays the first chapter not completed; once the Architect is lit,
the scoop starts it instead. Played and completed mean what they mean in
Act I.

Act II needs its own chapter counter (`a2_chapter_next`, proposed), because
Act I's `chapter_next` is 5 by the time Act II starts.

### Chapter 1: Zion (film: the dock, the Temple, the digging)

Single ball, two timed stages (proposed).

1. **The dock** (30 s): bring the Nebuchadnezzar home. The Real World Ramp,
   the long way onto the upper playfield, then any Real World standup (the
   dock). 250,000.
2. **The Temple** (30 s frenzy): the gathering in the Temple. Every switch
   pays 5,000; each ramp shot raises that by 5,000 for the rest of the stage
   (the drums build). The four EMP standups (the drums) light a 500,000
   collect on the Deja Vu VUK.

- The dock timing out ends the chapter, played but not completed.
- Collecting the Temple award completes the chapter and allies **LINK**, the
  Nebuchadnezzar's new operator, who joins the crew in Zion.

### Chapter 2: The Oracle (film: Seraph, the Oracle, the Burly Brawl)

Built like Act I's Red Pill: a single-ball opening that always leads into a
multiball (proposed).

1. **Seraph's test** (single ball, 30 s): the Sentinel entrance targets are
   Seraph's guard. Hit them alternately, left, right, left, six times: each
   alternation 50,000, the sixth 250,000. Two hits on the same side do not
   count. The Oracle's door opens whether or not Seraph is beaten; beating
   him lights an extra ball save of 10 s on the Brawl (proposed).
2. **The Burly Brawl multiball** (3 balls, 20 s ball save): the three
   Agents are Smith copies. Each rises again 1 s after it drops, as in The
   One's Subway stage. 25,000 per Smith; the HUD counts them.
   - After 12 Smiths, the Sentinel ramp (up and away) is lit: Neo flies out.
     Super jackpot 1,000,000, once.
- The super jackpot allies **SERAPH**. The chapter ends when the multiball
  does.

### Chapter 3: The Merovingian (film: the restaurant to the Keymaker)

Single ball, three timed rounds, built like Act I's Construct: a round lost
on time still moves on (proposed).

1. **The chateau** (30 s): the weapons on the wall. All three three-bank
   drops, 150,000. The three-bank's first use.
2. **Persephone** (30 s): her price for the Keymaker. The Agents Coming scoop
   (her way through the chateau), 200,000.
3. **The Keymaker** (20 s): the Deja Vu VUK (his room), then any ramp (a
   backdoor out). 300,000.

- Winning round 3 completes the chapter and allies **PERSEPHONE**.

### Chapter 4: The Freeway (film: the garage to the trucks)

Built like Act I's Rescue Morpheus: a single-ball phase that leads into a
staged multiball (proposed).

1. **The garage** (single ball, 30 s): the Twins. Knock down the five Matrix
   Team drops, which reset 2 s after they fall (the Twins phase through). All
   five down at once reaches the car. Timing out ends the chapter, played.
2. **Freeway multiball** (3 balls, 20 s ball save):

| Stage | Balls | Goal | Score |
| --- | --- | --- | --- |
| The Twins | 3 | Every Twin hit: the five-bank, all five down again | 75,000 per drop |
| The Ducati | 4 (add a ball) | Trinity and the Keymaker against the traffic: three spinner ramps inside 20 s, any order | 250,000 per ramp |
| The trucks | 5 (add a ball) | Neo arrives before the trucks collide: the Sentinel ramp | 1,000,000 |

- The trucks stage allies **KEYMAKER**. The chapter ends when the multiball
  does.
- Chapter 4 uses no lock, so the Ammo Lock drain save stays on throughout
  (unlike Act I's Chapter 4).

## 4. The two standalone multiballs, re-skinned

Same hardware and mechanics as Act I's (docs/11 section 6); new names,
callouts, clips and roster names. They run whenever Act II's features are
on, which is every Act II ball except while the Architect runs.

| Act I | Act II (proposed) | Film link | Allies |
| --- | --- | --- | --- |
| Trinity lock, Trinity Multiball | **Logos lock, Logos Multiball**: Niobe's ship. Three locks on the Trinity Ramp, 3 balls, jackpots on the Trinity Ramp | Niobe captains the Logos | **NIOBE** at three jackpots |
| Sentinel gate, Sentinel Multiball | **Sentinel Hunt**: the machines searching the tunnels. Four gate hits open it, the Sentinel VUK starts it, 3 balls plus the add-a-ball, jackpots on the Sentinel ramp and boss targets | Gameplay pairing only | **GHOST** at three jackpots |

- One change to each, so they do not replay Act I exactly (proposed): the
  Logos jackpot moves between the Trinity Ramp and the Deja Vu Ramp after
  every jackpot, and the Sentinel Hunt needs four jackpots, not three.
- Act I's lock counts do not carry over: the Logos lock starts empty.

## 5. ALLIES roster

| Name | Player variable | Allied by |
| --- | --- | --- |
| LINK | `allies_link` | Chapter 1 |
| SERAPH | `allies_seraph` | Chapter 2 |
| PERSEPHONE | `allies_persephone` | Chapter 3 |
| KEYMAKER | `allies_keymaker` | Chapter 4 |
| NIOBE | `allies_niobe` | Logos Multiball |
| GHOST | `allies_ghost` | Sentinel Hunt |

- Each name pays 250,000 once and adds one to `allies_count`.
- **The Architect lights at 4 names** (500,000), as The One does. A new
  operator setting, `architect_threshold`, takes 4, 5 or 6 (proposed).
- The HUD's roster panel reads `prefix` and `key` per entry
  (`gmc/slides/base/roster_entry.gd`), so the ALLIES list is the same
  component with `prefix = "allies"`. It replaces the FREED list while `act`
  is `II` (proposed).

## 6. The Architect (Act II wizard)

Starts from the Mission scoop once lit. While it runs, chapters, the Logos
lock and the Sentinel Hunt gate are off. Like The One, it runs until its
last shot, survives ball end (`architect_stage`, `architect_progress`,
`architect_door`) and resumes on the player's next ball with that stage's
balls served again.

| Stage | Balls | Goal | Score |
| --- | --- | --- | --- |
| 1. The power plant | 2 | Niobe's crew cuts the power: the four EMP standups | 250,000 each |
| 2. The hallway | 4 | The backdoors: all three three-bank drops open doors; the Smiths close them again 5 s after each falls. All three down at once, then the Deja Vu VUK: the Keymaker's last door | 500,000 per door, 1,000,000 for the last |
| 3. The Architect | any | The choice. The **left door** is any left-side shot (Trinity Ramp, Deja Vu Ramp); the **right door** any right-side shot (Real World Ramp, Sentinel ramp). 15 s; no choice is the right door | |
| 4a. Left door: the Source | 6 (add to 6) | Reload Zion: every ramp is a super jackpot for 30 s, up to four | 750,000 per ramp |
| 4b. Right door: Trinity | any | Trinity falls: a hurry-up from 5,000,000 falling to 1,000,000 over 30 s, then holding. The Real World Ramp (Neo flies) then the Sentinel magnet catches a ball (Neo catches her) | The hurry-up value |
| 5. Something is different | any | Neo stops the Sentinels: the Sentinel VUK | 5,000,000 |

- **Why a shot, not the flippers, picks the door.** Act I's pill choice uses
  the flippers because it is single ball, with the ball held in the scoop.
  The Architect's choice comes mid-multiball, and holding the flippers for a
  menu would throw balls away (docs/11 section 8 says the same of Neo dying).
  The playfield's two sides are the two doors.
- **Both doors are playable.** The left door is shorter and pays at most
  3,000,000. The right door is the film's path, adds the magnet catch, and
  pays up to 5,000,000. Which door was taken is recorded in
  `architect_door` for the HUD and for Act III.
- Stage 5 sets `act` to `III`, ends Act II and leaves the remaining balls in
  play under the base mode, as the EMP does for Act I. Act III has no rules
  yet.
- The shaker is not wired yet, so the mode does not drive it.

## 7. Display

- `act` shows `II` on the HUD, which it already does after the EMP.
- `balls_locked` drives the power station cells for the Logos lock, as it
  does for the Trinity lock.
- The existing stage widgets cover every chapter: `countdown` for each timed
  stage and the hurry-up, `chapter_card` for starts, stages and allies,
  `mode_banner` for jackpots. One new widget, `doors_choice`, for the
  Architect's stage 3, laid out like `pill_choice` with the doors named by
  side rather than by flipper.
- As in Act I, a mode cannot show its own ending, so the callouts for
  anything that ends a mode are played by `act_two` or `base`.

### Film clips (proposed names)

| Clip | Used for |
| --- | --- |
| `trinity_dream` | Act II intro |
| `zion_dock` | Chapter 1 start |
| `zion_temple` | Chapter 1, the Temple |
| `seraph_test` | Chapter 2 start |
| `burly_brawl` | Burly Brawl multiball start |
| `merovingian` | Chapter 3 start |
| `keymaker` | Chapter 3 complete |
| `twins_garage` | Chapter 4 start |
| `freeway_trucks` | Freeway multiball start |
| `logos_mb_intro` | Logos Multiball start |
| `sentinel_hunt` | Sentinel Hunt start |
| `backdoor_hallway` | The Architect, stage 2 |
| `architect_doors` | The Architect, stage 3 |
| `trinity_falls` | The Architect, right door |
| `sentinels_stop` | The Architect, stage 5 |

## 8. Implementation plan

| Mode | Priority | Starts on | Logic |
| --- | --- | --- | --- |
| `act_two` | 200 | `act_one_complete`, and every ball while `act` is `II` | `code/act_two.py`, the shape of `act_one.py`: chapter order, Mission scoop, multiball queue, roster, Architect resume |
| `logos_lock`, `hunt_gate` | 250 | `act_two_features_start` | YAML |
| `a2_ch1_zion`, `a2_ch2_seraph`, `a2_ch3_merovingian`, `a2_ch4_garage` | 300 | `start_a2_ch1` to `start_a2_ch4` | YAML |
| `a2_ch2_brawl_mb`, `a2_ch4_freeway_mb` | 310 | `start_brawl_mb`, `start_freeway_mb` | YAML |
| `logos_mb`, `hunt_mb` | 320 | `start_logos_mb`, `start_hunt_mb` | YAML |
| `the_architect` | 400 | `start_architect_mb` | `code/the_architect.py` |

- `act_two.py` and `act_one.py` share most of their code. Proposed: move the
  shared sequencing (chapter order, scoop, queue, roster) into one base class
  the two controllers configure with their own tables, and leave
  `t2_main.py` alone for now. `mb_pending` is cleared when Act II starts so a
  queued Act I multiball cannot start in Act II.
- New player variables: `a2_chapter_next`, `allies_*`, `allies_count`,
  `architect_lit`, `architect_stage`, `architect_progress`,
  `architect_door`. New setting: `architect_threshold`.
- The three-bank needs keyboard keys for `mpf both -X` play.
- Tests in `tests/test_act_two.py`, to the same coverage as Act I: every
  chapter, both re-skinned multiballs, the queue, the roster threshold, both
  doors, the resume after a drain, and the move to Act III. Display checks in
  `tests/test_display.py`.
- Build order: the controller and the roster first, then the chapters in
  order, then the multiballs, then the Architect, then the HUD roster switch
  and `doors_choice`, then the act select.

## 9. Open questions

1. Does Act II start on the ball the EMP is fired (section 1), or on that
   player's next ball?
2. Chapter 1: is a frenzy right for the Temple, or should Zion be the
   machines digging towards the city, a defence mode on the platform toy?
3. The Architect's choice with no input: the right door (the film's choice),
   as proposed, or no default, so the stage waits for a shot?
4. The roster pairings: LINK, SERAPH, PERSEPHONE and KEYMAKER follow the
   film; NIOBE with the Logos is a film link; GHOST with the Sentinel Hunt is
   gameplay only. Any names to swap in (the Oracle, the Kid, Commander Lock)?
