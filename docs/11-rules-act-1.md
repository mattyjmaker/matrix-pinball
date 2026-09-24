# Act I Rules: The Matrix (1999)

Rules for the first act of the game. Act I is the first film. These rules are
implemented in `config/` and `modes/` and covered by the tests in `tests/`
(section 11). Every number below is the value in the code.

Status (2026-09-24):

- Agreed with the user: Act I is movie 1; the four VPX prototype multiballs
  stay, mashed up with the new chapter modes; the machine may be filled with
  as many balls as the design needs.
- Agreed with the user (second round): chapters play in film order, with an
  act select before play starts so a player can skip straight to a later act;
  The One lights at 4 FREED names; The One runs until the EMP is hit; Sentinel
  Multiball is 3 balls plus an add-a-ball.
- Agreed with the user (third round): The One resumes across ball end; the act
  select waits 30 s and then starts Act I; the Mission Drop smart drop sits in
  front of the scoop.
- Decided during the build, not yet reviewed by the user: every timer, count
  and score below, the jackpot counts that complete Trinity and Sentinel
  Multiball, and that a lit The One takes the Mission scoop ahead of a chapter
  replay. Each is marked "(build)" where it first appears.
- Scores are placeholders at the VPX prototype's scale, for balancing once the
  machine is playable.
- Shot names are logical. The ramps, wireforms and upper playfield are not
  built yet (see 08-this-machine.md), so the switches behind each shot are
  placeholders on the virtual platform (section 11).

Sources: the VPX v1.7 rules summary in 10-dropbox-design-files.md
(user-provided), the feature list in 09-parts-inventory.md (user-provided),
MPF 0.80 behaviour from 04-game-logic-and-mechs.md (official docs, summarised)
and the MPF 0.80.0 source. Film scene references are from recall of the film
and have not been checked against a script; check any quoted line against the
clip before it goes on screen.

## 1. Structure at a glance

```
  Act select (before the first ball): Act I, or skip straight to a later act
                                        |
            always on: Agents, Ammo Lock drain save, Deja Vu, Oracle
                                        |
  Mission Drop scoop starts the next chapter, in film order
     Ch1 Trinity's Escape -> Ch2 Red Pill -> Ch3 The Construct -> Ch4 Rescue Morpheus
                                        |
  Multiballs lit by their own features, any time no other multiball runs
     Trinity Multiball (Trinity Ramp lock)    Sentinel Multiball (Sentinel gate)
                                        |
  Each chapter and multiball completed lights one name in the FREED roster
                                        |
            four names FREED -> The One (Act I wizard) -> Act II
```

Of the four VPX multiballs, two stay as standalone features and two are merged
into chapters:

| VPX multiball | In Act I |
| --- | --- |
| Trinity Multiball | Standalone, as in the VPX |
| Sentinel Multiball | Standalone, as in the VPX |
| Human Pod "Unplugged" | Merged into Chapter 2, Red Pill |
| Morpheus Rescue | Merged into Chapter 4, Rescue Morpheus |

Why merge those two: the Human Pod and Morpheus Rescue locks were subways in
the VPX (`HumanPodSubway`, `LeftSubwayCatch`), and neither subway appears in
the physical feature list in 09-parts-inventory.md.

## 2. Ball count

- `balls_installed: 7`. The trough is the 8-ball PBL-100-0016-00, but only
  seven positions are switched until the trough 1 opto is fitted; an 8th ball
  would sit uncounted and MPF would ball-search for it. **The machine must
  physically hold 7 balls**, or attract mode searches constantly. Raise to 8
  with the opto.
- At most **6 balls in play** (The One).
- Locks use MPF's `virtual_only` counting (the docs call it "usually the best
  option for modern machines"): a lock counts per player whatever is
  physically in the device, so one player cannot steal another's lock. The
  Ammo drain save is the exception (section 3).

| Feature | Balls in play |
| --- | --- |
| Chapters 1 and 3 | 1 |
| Trinity Multiball | 3 |
| Red Pill: Unplugged Multiball | 3 |
| Sentinel Multiball | 3, rising to 4 with its add-a-ball |
| Rescue Morpheus | 3, rising to 5 |
| The One | 2, rising to 6 |

### Stacking rule

**One multiball at a time.** A multiball whose lock completes during another
one waits in the player's queue (`mb_pending`) and starts when the running one
ends. The Mission scoop does not start a chapter during a multiball. A queued
multiball survives ball end, except Rescue Morpheus, which ends with its
chapter.

## 3. Always-on features (base mode)

| Feature | Rule | Score |
| --- | --- | --- |
| Agents (3 pop-ups) | Hit a raised Agent: "Agent Kill". All three down: "Agents Down". Raised at the start of every ball. | 10,000 each, 50,000 all down |
| Agents Coming scoop (Cypher) | All three Agents down: raises them ("Agents are Coming"). Otherwise a small award. | 50,000 or 5,000 |
| Ammo Lock | Holds one ball as a drain save and serves a new one. The next Ammo target hit releases it as two-ball play; if the last ball on the playfield drains first, the held ball comes back instead of the ball ending. Physical counting, and emptied at ball end. Stands down during Chapter 4's lock phase. | 15,861 per lock |
| Deja Vu VUK | "Deja vu" award. | 2,570 |
| Oracle (build) | The four EMP standups, in any order, light it; the Deja Vu VUK collects a random award. | 25,000, 75,000 or 150,000 |
| Lanes and spinners | Inlanes and every spinner. | 100 |

Not yet modelled: the kickback and the Real World mini flipper. Both tie a FAST
switch to a coil through a hardware rule, and their coils are not wired yet
(`config/playfield_pending.yaml`, last comment).

## 4. Chapters

### Starting a chapter

- The Mission Drop smart drop sits in front of the Mission scoop. Knocking it
  down (5,000) lights "Mission Ready".
- Every ball into the scoop is held while the controller decides. With
  Mission Ready and no chapter or multiball running, it starts the next
  chapter, raises the drop again and releases the ball after 2 s (Chapter 2
  keeps it for the pill choice). Otherwise it pays 10,000 and releases the
  ball after 0.75 s.
- Chapters run in **film order**. A chapter is **played** when it ends,
  including by the ball draining; it is **completed** when its goal was met,
  and only completion frees a crew member.
- After Chapter 4 has been played, the scoop replays the first chapter not yet
  completed. Once The One is lit, the scoop starts The One instead (build).
- Each chapter sets `objective` on the HUD to its current goal. Between
  chapters the controller sets it to "KNOCK DOWN THE MISSION DROP: <next>" or
  "SHOOT THE MISSION SCOOP: <next>".

### Chapter 1: Trinity's Escape (film: opening, room 303 to the phone booth)

Single-ball hurry-up. The truck is the clock.

1. **Rooftops:** three ramp shots, any ramps, inside 40 s (build). 50,000 per
   jump.
2. **The phone:** the Deja Vu VUK, inside 20 s (build). Pays 250,000 plus
   25,000 per second left.

- Either timer running out: the truck wins, played but not completed.
- Completion frees **TRINITY**.

### Chapter 2: Red Pill (film: the pills, waking in the pod, unplugged)

1. **The choice:** the scoop keeps the ball. Left flipper: blue. Right flipper:
   red. No input in 10 s (build): red.
   - **Blue:** "The story ends." 5,000, and the chapter ends, played but not
     completed.
   - **Red:** Unplugged Multiball.
2. **Unplugged Multiball:** 3 balls, 20 s ball save (build).
   - Jackpot: the Real World ramp, 100,000.
   - Super jackpot: all three Real World standups, 500,000, once.
- The super jackpot frees **APOC**. The chapter ends when the multiball does.

### Chapter 3: The Construct (film: the Construct, the dojo, the jump)

Single-ball skill mode in three timed rounds (build: 30 s, 30 s, 20 s). A
round lost on time still moves to the next one.

1. **"I know kung fu":** all five Matrix Team drops. 150,000.
2. **Sparring:** 4 combos, 50,000 each and 200,000 for the round. A combo is a
   shot from the other side of the playfield to the last one; two shots from
   the same side do not count.
3. **The jump program:** the Real World ramp, then any Real World standup.
   300,000. Time out: "Everybody falls the first time", 100,000.

- **The Woman in the Red Dress** (rounds 2 and 3): she starts on the Trinity
  Ramp and moves to the next ramp every 3 s (build). Shooting the ramp she is
  on raises the middle Agent; hitting it before the round ends pays 200,000.
- Winning rounds 1 and 2 frees **MOUSE**, who wrote the Woman in the Red Dress
  program. The jump does not affect completion.

### Chapter 4: Rescue Morpheus (film: deja vu to the helicopter)

1. **Deja vu:** the Deja Vu VUK plays the black cat and lights the Ammo Lock.
2. **"Guns. Lots of guns.":** lock three balls at the Ammo Lock, 50,000 each
   ("Two balls left", "One more ball"). The lock holds one ball physically;
   the count is virtual.
3. **Multiball:** 3 balls, 20 s ball save, released from the Ammo Lock (build).

| Stage | Balls | Goal | Score |
| --- | --- | --- | --- |
| Lobby | 3 | Every guard: the four EMP standups and the three Agents (raised again whenever all three are down) | 75,000 per guard |
| Rooftop | 4 (add a ball) | Trinity Ramp lights "Dodge this" for 10 s; hit an Agent while it is lit | 250,000 |
| Helicopter | 5 (add a ball) | A ball over the Sentinel magnet is caught (Neo catches Morpheus); the magnet lets go after 2 s | 1,000,000 |

- The Helicopter catch frees **TANK**, who loads the weapons program in the
  film. The chapter ends when the multiball does.
- A drain during the lock phase ends the chapter, played.

## 5. Act select

Acts play in order, but a player can skip ahead before play starts.

- On each player's first ball, before the ball is served, the select holds
  `ball_starting`. Flippers step through the acts; start confirms. While it is
  up, start does not add a player. No confirmation in **30 s** starts Act I.
- Only acts with rules are offered (`AVAILABLE_ACTS` in
  `modes/act_select/code/act_select.py`). With one act the mode steps straight
  out, so today the game starts in Act I with no screen.
- Skipping an act forfeits everything in it: its chapters, multiballs, FREED
  names and wizard. No compensation award.
- An Act II player gets the base mode only until Act II has rules.

## 6. The two standalone multiballs

Both run whenever Act I's features are on, which is every Act I ball except
while The One runs.

### Trinity Multiball (VPX)

- The Trinity Ramp lock takes three balls, 10,000 each. The HUD's power
  station cells (`balls_locked`) show the count.
- The third lock requests a 3-ball multiball, 20 s ball save, released from
  the lock. "Trinity Bonus" jackpots on the Trinity Ramp, 150,000.
- Three jackpots (build) free **SWITCH**.

### Sentinel Multiball (VPX)

- Four hits across the two Sentinel entrance targets open the gate ("Hit the
  Sentinel!", 100,000). A ball into the Sentinel VUK while it is open requests
  the multiball: 3 balls, 20 s ball save.
- Jackpots on the Sentinel ramp and the boss target, 150,000. Three jackpots
  (build) free **DOZER**.
- **Add-a-ball**, once per multiball: hit the two entrance targets and the boss
  target to light it, then shoot the Sentinel VUK. 10 s save on the added ball.
  Peaks at 4 balls.
- The gate closes and the hit count resets when the multiball ends. Both also
  reset at ball end, so the four hits and the VUK shot must come on one ball.

The roster pairings for SWITCH, APOC and DOZER are for gameplay only and have
no link to the film. TRINITY, MOUSE and TANK follow the film.

## 7. FREED roster

| Name | Player variable | Freed by |
| --- | --- | --- |
| TRINITY | `freed_trinity` | Chapter 1 |
| APOC | `freed_apoc` | Chapter 2 |
| MOUSE | `freed_mouse` | Chapter 3 |
| TANK | `freed_tank` | Chapter 4 |
| SWITCH | `freed_switch` | Trinity Multiball |
| DOZER | `freed_dozer` | Sentinel Multiball |

- Each name pays 250,000 once and adds one to `freed_count`. The HUD's
  `roster_entry.gd` reads the `freed_*` variables.
- **The One lights at 4 names** (500,000). The operator setting
  `the_one_threshold` takes 4, 5 or 6.

## 8. The One (Act I wizard)

Starts from the Mission scoop once lit. While it runs, chapters, Trinity lock
and the Sentinel gate are off.

| Stage | Balls | Goal | Score |
| --- | --- | --- | --- |
| 1. Subway | 2 | Beat Smith: 6 Agent hits (build). Each Agent rises again 1 s after it drops. | 100,000 per hit |
| 2. The Chase | 4, then 6 after 2 phones | The phone rings on one ramp and moves to the next every 5 s; the HUD names the ramp. Reach 4 phones before the 60 s Sentinel timer runs out (build). The timer running out also moves on. | 500,000 per phone |
| 3. Room 303 | 6 | The magnet takes a ball and every shot goes dark for 5 s ("Neo dies"); an 8 s ball save covers every drain. Then 6 balls again, and every ramp is a super jackpot. 3 light the EMP (build). | 1,000,000 per super jackpot |
| 4. EMP | any | The Sentinel gate opens; the Sentinel VUK fires the EMP | 5,000,000 |

- **Runs until the EMP is hit.** It carries on single-ball when the multiball
  drops to one ball, and it survives ball end: the stage and its progress are
  stored per player (`the_one_stage`, `the_one_progress`) and resume on that
  player's next ball, with that stage's balls served again. A resumed Chase
  restarts its 60 s timer. If the game ends first, Act I stays incomplete.
- The flippers stay live when Neo dies. Disabling them in multiball throws
  balls away and feels like a fault, not a story beat.
- The EMP sets `act` to `II`, ends Act I and leaves the remaining balls in play
  under the base mode.
- The sub build-ups and shaker in 08-this-machine.md were sized for this
  mode. The shaker is not wired yet, so the mode drives neither.

## 9. HUD variables used

| Variable | Set by |
| --- | --- |
| `act` | `I` at game start (`player_vars:`), the act select, `II` after the EMP |
| `objective` | Each chapter, multiball, wizard stage, the act select and the controller between chapters |
| `balls_locked` | Trinity Ramp lock count |
| `freed_*` | Section 7 |

### Stage widgets

Modes draw on the HUD's empty centre stage with `widget_player`. The stage is
split into three zones so these widgets can share it:

| Widget | Zone (2560x1440 design) | Shows | Used for |
| --- | --- | --- | --- |
| `countdown` | Top, y 220 to 450 | Label, two-digit clock that churns and locks on every tick (the trace readout's number-lock), draining bar, optional hurry-up value | Chapter 1 rooftops then phone (with the phone's falling value), Chapter 3 rounds, Chapter 4 "Dodge this", The Chase |
| `chapter_card` | Middle, y 460 to 745 | Kicker, title, goal | Every chapter and multiball start, the stages of Rescue Morpheus and The One, each crew member freed, Act I complete |
| `mode_banner` | Bottom, y 760 to 980 | Title and detail | Jackpots and short callouts |
| `pill_choice` | Whole stage | Clock, blue and red pills with their flippers | Chapter 2's choice |
| `act_select` | Whole stage | Clock, the act on offer (player variable `act_choice`) | The act select |

- **Clocks** subscribe over BCP to the event named in their `event` token
  (`timer_<name>_tick` for MPF timers; `the_one_chase_tick` and
  `act_select_show` for the two code-driven clocks) and read the seconds from
  its `ticks` argument, or the argument named by `arg`. The shared part is
  `gmc/assets/parts/countdown_clock.tscn`.
- **A mode cannot show its own ending.** MPF clears every widget a mode played
  the moment the mode stops (MPF 0.80.0 source, `config_player.mode_stop`). So
  the callouts for events that end a mode are played by a mode that keeps
  running: crew cards, the truck clip, "The story ends" and "Everybody falls"
  by `act_one`; the EMP clip and "Act I complete" by `base`.
- **A live clock is switched with `action: update`**, not a second `play`: GMC
  ignores a play whose `key` is already on screen (`mpf_scene_base.gd`).
- **No placeholders in tokens.** MPF does not substitute event arguments into
  widget tokens, so anything that changes while on screen goes on the HUD's
  objective line or in a clock.
- **No event argument called `name`.** `widget_player` passes the triggering
  event's arguments on to BCP, where `name` collides with BCP's own and raises
  a `TypeError`. The tests caught this on `crew_freed`, which now uses `crew`.

## 10. Film clips

The modes play these through the `video_clip` widget. They are listed in
`gmc/video/manifest.txt`, so `tools/check_video.py` reports each one missing
until it is cut. Every clip entry has an `expire`, so a missing clip leaves the
stage after that time instead of blocking it.

| Clip | Used for |
| --- | --- |
| `trinity_room_303` | Chapter 1 start |
| `phone_booth_truck` | Chapter 1 failed |
| `pills_choice` | Chapter 2 choice |
| `pod_wake` | Unplugged Multiball start |
| `kung_fu_load` | Chapter 3 start |
| `jump_program` | Chapter 3 round 3 |
| `deja_vu_cat` | Chapter 4 start |
| `lots_of_guns` | Chapter 4 lock lit |
| `lobby_shootout` | Chapter 4 multiball start |
| `helicopter_catch` | Chapter 4 complete |
| `trinity_mb_intro` | Trinity Multiball start |
| `sentinel_attack` | Sentinel Multiball start |
| `subway_smith` | The One start |
| `neo_resurrects` | The One, Room 303 |
| `emp_fire` | The EMP |

## 11. Implementation

### Modes

| Mode | Priority | Starts on | Logic |
| --- | --- | --- | --- |
| `base` | 100 | every ball | YAML |
| `act_one` | 200 | every ball while `act` is `I` | `code/act_one.py`: chapter order, Mission scoop, multiball queue, roster, The One resume |
| `trinity_lock`, `sentinel_gate` | 250 | `act_one_features_start` | YAML |
| `ch1_trinity_escape`, `ch2_red_pill`, `ch3_construct`, `ch4_rescue_lock` | 300 | `start_ch1` to `start_ch4` from `act_one` | YAML |
| `ch2_unplugged`, `ch4_rescue_mb` | 310 | `start_unplugged_mb`, `start_rescue_mb` | YAML |
| `trinity_mb`, `sentinel_mb` | 320 | `start_trinity_mb`, `start_sentinel_mb` | YAML |
| `the_one` | 400 | `start_the_one_mb` | `code/the_one.py` |
| `act_select` | 1000 | `ball_starting` on ball 1 | `code/act_select.py` |

Multiballs never start themselves: a lock posts `request_<name>_mb` and
`act_one` posts `start_<name>_mb` when nothing else is running. Chapters post
`chN_completed` for the roster and `chN_ended` when played.

### Hardware layers

- **Logical events.** Every playfield switch posts a logical event through
  `events_when_activated` (for example `trinity_ramp_hit`, `ramp_hit`,
  `left_shot_hit`, `emp_target_1_hit`). The modes listen to those and to MPF's
  device events (`drop_target_…`, `balldevice_…_ball_entered`), never to raw
  switch names, so rewiring a feature changes no rules.
- **Pending hardware.** Everything not yet built or wired is in
  `config/playfield_pending.yaml`, on the `virtual` platform, which
  `hardware: platform: fast, virtual` loads alongside FAST. MPF configures every
  switch before any platform reports initial states, so the virtual platform
  never touches FAST switches (MPF 0.80.0 source,
  `core/switch_controller.py`). To bring a feature online, move its entries to
  `config/config.yaml`, give them FAST numbers and delete `platform: virtual`.
- Assumptions to check when each feature is built, all marked `TODO` in that
  file: the Trinity lock has three switched positions; the Ammo Lock holds one
  ball; the Sentinel gate is a held coil; which ramps count as left and right
  for the sparring combos (Trinity and Deja Vu left, Real World and Sentinel
  right).

### Testing

MPF's machine test framework runs the real config on the smart_virtual
platform with no hardware or Godot:

    python -m unittest discover -s tests -t .

66 tests at the time of writing. They cover every chapter, both standalone
multiballs, the multiball queue, the roster threshold, The One (including
resuming after a drain and the EMP) and the act select, plus spot checks of
the scores and timers in this document (`tests/test_scoring.py` and the
chapter tests). Not every score above has its own test.

`tests/test_display.py` checks what the rules send to the display through
MPF's mock BCP client: which widgets each mode plays and with which tokens,
that end-of-mode callouts survive their mode stopping, and that every widget
and clip the YAML names exists. They need MPF 0.80 installed (see the README).

For hands-on play, `mpf both -X` with the keyboard: section "Keyboard" in the
README lists the keys added for these rules.

## 12. Still to verify

- **Booting on the real FAST hardware** with the virtual platform alongside.
  Verified here only on smart_virtual (the tests, and `mpf game -X -b` booting
  to attract with no errors in the log). The FAST platform cannot start in this
  container.
- **The display on the cabinet.** Every stage widget was rendered in Godot
  4.7.2 (OpenGL, under Xvfb, with the real fonts) over the gameplay HUD at
  1280x720, including a clock driven through its tick handler and the longest
  texts the rules use. Not yet checked: the cabinet's own display, a live BCP
  connection to MPF, and how the full-screen film clips sit over these widgets
  once the clips exist.
- **Scoring balance**, once the machine is playable.
- The hardware assumptions in section 11.
