# Act I Rules: The Matrix (1999)

Design for the first act of the game. Act I is the first film. This is a
rules design, not an implementation: nothing here is in `config/` or
`modes/` yet.

Status (2026-09-24):

- Agreed with the user: Act I is movie 1; the four VPX prototype multiballs
  stay; the new chapter modes are mashed up with them; the machine may be
  filled with as many balls as the design needs.
- Agreed with the user (second round): chapters play in film order, with an
  act select before play starts so a player can skip straight to a later act
  (section 5); The One lights at 4 FREED names; The One runs until the EMP is
  hit; Sentinel Multiball is 3 balls plus an add-a-ball.
- Everything else is a proposal, marked where it matters. Shot names are
  logical names. The ramps, wireforms and upper playfield are not built yet
  (see 08-this-machine.md), so which physical switch each shot uses is
  decided when the ball paths are final.
- Scoring values are left out on purpose. They get balanced once the modes
  run. Where a value is quoted it is the VPX prototype's, for scale.

Sources: the VPX v1.7 rules summary in 10-dropbox-design-files.md
(user-provided), the feature list in 09-parts-inventory.md (user-provided),
MPF 0.80 behaviour from 04-game-logic-and-mechs.md (official docs,
summarised). Film scene references are from recall of the film and have not
been checked against a script; check any quoted line against the clip before
it goes on screen.

## 1. Structure at a glance

```
  Act select (before the first ball): Act I, or skip straight to a later act
                                        |
            always on: Agents, Ammo Lock drain save, Deja Vu, Oracle, kickback
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

The five modes from the planning discussion map onto this as four chapters
plus the wizard. Of the four VPX multiballs, two stay as standalone features
and two are merged into chapters:

| VPX multiball | In Act I |
| --- | --- |
| Trinity Multiball | Standalone, as in the VPX |
| Sentinel Multiball | Standalone, as in the VPX |
| Human Pod "Unplugged" | Merged into Chapter 2, Red Pill |
| Morpheus Rescue | Merged into Chapter 4, Rescue Morpheus |

Why merge those two: the Human Pod and Morpheus Rescue locks were subways in
the VPX (`HumanPodSubway`, `LeftSubwayCatch`), and neither subway appears in
the physical feature list in 09-parts-inventory.md. The chapters give them a
start condition that does not need a subway.

## 2. Ball count

- The trough is the 8-ball PBL-100-0016-00, so 8 is the physical ceiling.
- Only 7 can be counted until the trough 1 opto is fitted. Deduction, not
  tested: an 8th ball would sit in an unswitched position, MPF would count one
  ball missing, and it would ball-search. So **load 7 now, 8 once the trough 1
  opto is in**.
- The design needs at most **6 balls in play** (The One, final stage). That is
  the VPX's ceiling too. The rest are the spare for a physically held lock
  plus margin.
- All locks use MPF's `virtual_only` counting, which the docs call "usually the
  best option for modern machines": a lock counts per player whatever is
  physically in the device, so one player cannot steal another's lock.
- Raising `balls_installed` and the virtual trough seed in
  `config/config.yaml` is a separate change, made together, when multiball
  implementation starts.

| Feature | Balls in play |
| --- | --- |
| Chapters 1 and 3 | 1 |
| Trinity Multiball | 3 |
| Red Pill: Unplugged Multiball | 3 |
| Sentinel Multiball | 3, rising to 4 with its add-a-ball |
| Rescue Morpheus | 3, rising to 5 |
| The One | 2, rising to 6 |

### Stacking rule

**One multiball at a time.** A lock completed during another multiball stays
lit and starts when the running one ends. The Mission Drop scoop does not
start a chapter during a multiball. This extends the VPX rule that Human Pod
multiball cannot start during Trinity or Sentinel multiball, keeps the ball
count predictable, and keeps to the one-video-at-a-time rule in the README.

## 3. Always-on features (base mode)

| Feature | Rule | Source |
| --- | --- | --- |
| Agents (3 pop-ups) | Hit a raised Agent: "Agent Kill". All three down: "Agents Down". | VPX |
| Agents Coming scoop (Cypher) | Re-raises the Agents when all three are down ("Agents are Coming"), otherwise a small award. | VPX |
| Ammo Lock | Holds one ball as a drain save. The next hit, or a drain with no other ball in play, releases it. | VPX |
| Deja Vu VUK and ramp | "Deja vu" award and re-kick. Used as a lead-in in Chapter 4. | VPX |
| Oracle | Mystery award (proposed): completing the EMP standups lights it, and the Deja Vu VUK collects it. | Proposed |
| Kickback | Left outlane save, relit by the kickback target. | Hardware (auto-fire assembly, `s_kickback_target`) |

## 4. Chapters

### Starting a chapter

- The **Mission Drop** area (1-bank smart drop, standup, open-back scoop)
  starts chapters. Knocking the smart drop down lights "Mission Ready", and
  the scoop starts the next chapter.
  - Assumption, not confirmed: the drop sits in front of the scoop and blocks
    it. If it does not, the drop lights the scoop instead.
- Chapters run in **film order** (agreed). Act I is a story, so the order is
  the point, and it keeps the clip sequence and the rules simple. The way to
  skip content is the act select (section 5), not chapter choice.
- A chapter is **played** when it ends. It is **completed** when its goal was
  met. Only completion lights a roster name. An unfinished chapter can be
  replayed from the Mission Drop after Chapter 4, including after The One is
  lit.
- Each chapter sets `objective` on the HUD to its current goal.

### Chapter 1: Trinity's Escape (film: opening, room 303 to the phone booth)

Single-ball hurry-up. The truck is the clock.

1. **Rooftops:** three ramp shots, one per jump between buildings. Any ramp
   counts.
2. **The phone:** the Deja Vu VUK lights as the ringing phone. Its value counts
   down from the moment the third jump lands. Reach it before it runs out.
- Timer expires: the truck hits and the chapter ends, played but not
  completed.
- Completion lights **TRINITY**.
- Fits the hardware already on the board: the timer and hurry-up are pure
  logic, so this is the easiest chapter to prove out on the virtual platform
  first.

### Chapter 2: Red Pill (film: the pills, waking in the pod, unplugged)

Choice, then multiball. Merges the VPX Human Pod "Unplugged" multiball.

1. **The choice:** the scoop holds the ball (`ball_holds:`, so the ball is
   still in play) while Morpheus offers the pills. Left flipper: blue. Right
   flipper: red. No input in 10 s means red.
   - **Blue:** "The story ends." A small award and the chapter ends, played
     but not completed.
   - **Red:** the pod clip, then **Unplugged Multiball**.
2. **Unplugged Multiball**, 3 balls (VPX Human Pod count), with a ball save.
   - Jackpots: the Real World ramp (the ship pulls Neo out of the water).
   - Super jackpot: all three Real World standups on the upper mini-playfield.
- Completion (super jackpot collected) lights **APOC**.

### Chapter 3: The Construct (film: the Construct, the dojo, the jump)

Single-ball skill mode in three timed rounds. Tank loads each program.

1. **"I know kung fu":** all five Matrix Team drop targets down inside the
   time.
2. **Sparring:** combos. Alternate left-side and right-side shots
   (Morpheus's attack from each side). A set number of combos wins the round.
3. **The jump program:** the Real World ramp to the mini-playfield. Hit a
   standup with the mini flipper to make the jump.
   - Miss: "Everybody falls the first time." The round still counts, at a
     lower award.
- Bonus: **the Woman in the Red Dress.** One random lit shot walks across the
  playfield during rounds 2 and 3. Following her raises an Agent. Hitting that
  Agent before the round ends pays a bonus.
- Completion (rounds 1 and 2 won) lights **MOUSE**, who wrote the Woman in the
  Red Dress program.

### Chapter 4: Rescue Morpheus (film: deja vu to the helicopter)

Lock, then a three-stage multiball. Merges the VPX Morpheus Rescue lock.

1. **Deja vu (lead-in):** the Deja Vu VUK plays the black cat and Cypher's
   betrayal as the intro, and lights the Ammo Lock for locking.
2. **"Guns. Lots of guns.":** lock three balls in the Ammo Lock (VPX Morpheus
   Rescue: "Two balls left!", "One more ball!"). `virtual_only` counting.
   Only one ball is held physically, as in the VPX.
3. **Multiball**, three stages:

| Stage | Balls | Goal | Film |
| --- | --- | --- | --- |
| Lobby | 3 | Hit the guards: every EMP standup and Agent, each a jackpot | Lobby shootout |
| Rooftop | 4 (add a ball) | "Dodge this": hit a raised Agent inside the time after a Trinity Ramp shot | Rooftop and bullet-dodge |
| Helicopter | 5 (add a ball) | The Sentinel magnet catches a ball (Neo catches Morpheus) for the super jackpot | Helicopter rescue |

- Completion (the Helicopter super jackpot) lights **TANK**, who loads the
  weapons program in the film.

## 5. Act select

Agreed with the user: acts play in order, but a player can skip ahead before
play starts.

- **When:** on each player's first ball, before the ball is served. The
  player picks with the flippers and confirms with start. No input in 10 s
  (proposed) means Act I. Per player rather than per game, so players of
  different skill can share a game.
- **Choices:** only acts that have rules. Until Act II exists the select is
  skipped entirely, so the game starts in Act I with no screen in the way.
- **Skipping an act:** the player starts at the chosen act with `act` set to
  match. Everything in the skipped acts is forfeited: its chapters, its
  multiballs, its FREED names and its wizard. No compensation award is
  proposed; skipping is for players who want the later content, and handing
  out the skipped points would make it the best scoring choice.
- **MPF (to verify when implementing):** a mode started on `ball_starting`
  for ball 1 with `use_wait_queue: true` holds the ball start until the choice
  is made. The docs name `use_wait_queue` as the way a mode holds a queue
  event; using it on `ball_starting` with a ball-number condition has not
  been tried here. `queue_relay_player` on `ball_starting` is the documented
  fallback.

## 6. The two standalone multiballs

### Trinity Multiball (VPX, unchanged in principle)

- The Trinity Ramp lock (Stern ball lock assembly) locks three balls. The
  third starts a 3-ball multiball. "Trinity Bonus" jackpots on the Trinity
  Ramp.
- Completion (a set number of jackpots, to be tuned) lights **SWITCH**.
- The HUD's power station cells (`balls_locked`) show this lock's count.

### Sentinel Multiball (VPX, unchanged in principle)

- Four hits across the Sentinel entrance targets open the gate and raise the
  Sentinel ("Hit the Sentinel!"). A ball into the Sentinel VUK starts the
  multiball. **3 balls** (agreed).
- **Add-a-ball** (agreed; placement proposed): during the multiball, hit all
  three Sentinel Boss standups (the rectangular one and the two squares) to
  light it, then shoot the Sentinel VUK to collect it. Once per multiball, so
  it peaks at 4 balls. The standups and VUK are already part of the Sentinel
  Boss hardware in 09-parts-inventory.md, so it needs no extra parts.
- Balls release via the Deja Vu VUK, as in the VPX. The Sentinel closes when
  the multiball ends.
- Completion lights **DOZER**.

The roster pairings for SWITCH, APOC and DOZER are for gameplay only and have
no link to the film. TRINITY, MOUSE and TANK follow the film.

## 7. FREED roster

The six names already on the base HUD, and what lights each:

| Name | Player variable | Lit by |
| --- | --- | --- |
| TRINITY | `freed_trinity` | Chapter 1 |
| APOC | `freed_apoc` | Chapter 2 |
| MOUSE | `freed_mouse` | Chapter 3 |
| TANK | `freed_tank` | Chapter 4 |
| SWITCH | `freed_switch` | Trinity Multiball |
| DOZER | `freed_dozer` | Sentinel Multiball |

In MPF each name is an achievement, and its completion sets the matching
`freed_*` variable, which the HUD's `roster_entry.gd` already reads. A
counter of completions against the threshold below lights The One. An
`achievement_group`'s all-complete event (the TAF Mansion Awards pattern)
would only cover a threshold of 6.

**Wizard threshold: 4 names** (agreed). Kept as an operator setting from 4
to 6, so it can be raised for experienced players without a code change.

## 8. The One (Act I wizard)

Lit when the roster threshold is met. Starts at the Mission Drop scoop.

| Stage | Balls | Goal | Film |
| --- | --- | --- | --- |
| 1. Subway | 2 | Beat Smith: every Agent hit a set number of times | Subway fight |
| 2. The Chase | 4, then 6 | A lit "phone" shot moves around the playfield. Each one reached is a jackpot. A Sentinel timer runs on the trace readout while the sub and shaker build up. | City chase and the Sentinel breach |
| 3. Room 303 | 6 | Timer expiry or the last phone ends the chase. The magnet takes a ball and every shot goes dark for about 5 s ("Neo dies"), with a ball save covering every drain. Then all shots relight at super jackpot value. | Neo is killed and comes back |
| 4. EMP | any | The Sentinel VUK fires the EMP: collect the total, then the flashers and the EMP area light show | The EMP is fired |

- Neo dies without the flippers going dead. Disabling the flippers in
  multiball throws balls away and feels like a fault, not a story beat.
- **The One runs until the EMP is hit** (agreed). It does not end when the
  multiball drops to one ball; play carries on single-ball with the current
  stage's shots still lit.
- It also survives ball end (interpretation of the agreed rule, to confirm):
  the stage and its progress are stored per player and resume on that
  player's next ball, so the mode is `stop_on_ball_end: true` with its state
  in player variables. The stage's extra balls are served again when it
  resumes. If the game ends first, Act I stays incomplete.
- While The One runs, chapters and the standalone multiballs are off, so the
  one-multiball rule in section 2 holds.
- The EMP sets `act` to `II` and Act II starts.
- The sub build-ups here are what the audio plan in 08-this-machine.md was
  sized for. The shaker needs its driver wired and checked first.

## 9. HUD variables used

| Variable | Set by |
| --- | --- |
| `act` | `I` at game start, `II` after the EMP |
| `objective` | Each chapter, multiball and wizard stage |
| `balls_locked` | Trinity Ramp lock count |
| `freed_*` | Section 7 |

The trace readout (`trace_readout.gd`) suits the hurry-up clocks: Chapter 1's
phone, and The Chase's Sentinel timer.

## 10. Film clips (proposed names)

These are not added to `gmc/video/manifest.txt` yet, because
`tools/check_video.py` exits non-zero for every listed clip that is missing.
Add each clip to the manifest when it is cut.

| Clip | Used for |
| --- | --- |
| `trinity_room_303` | Chapter 1 intro |
| `phone_booth_truck` | Chapter 1 complete or failed |
| `pills_choice` | Chapter 2 choice |
| `pod_wake` | Unplugged Multiball start |
| `kung_fu_load` | Chapter 3 intro |
| `jump_program` | Chapter 3 round 3 |
| `deja_vu_cat` | Chapter 4 lead-in |
| `lots_of_guns` | Chapter 4 lock lit |
| `lobby_shootout` | Chapter 4 multiball start |
| `helicopter_catch` | Chapter 4 complete |
| `trinity_mb_intro` | Trinity Multiball start |
| `sentinel_attack` | Sentinel Multiball start |
| `subway_smith` | The One, stage 1 |
| `neo_resurrects` | The One, stage 3 |
| `emp_fire` | The One, stage 4 |

Keep them short and inset during play, full screen only for intros, as the
README's clip rules say.

## 11. Suggested build order

Only the lower third, the EMP targets, the Ammo target and the kickback
target have switch numbers today. So build what the virtual platform can
exercise first, with the keyboard standing in for unwired switches:

1. Base mode: shots under logical names, the Agents and Ammo Lock logic, the
   roster achievement group, `act` and `objective`.
2. The Mission Drop chapter framework, then Chapter 1 (single ball, timer
   only).
3. Chapter 3 (single ball).
4. Raise the ball count, then Trinity Multiball, Chapter 2, Sentinel
   Multiball and Chapter 4.
5. The One.
6. The act select, once Act II has rules to select.

## 12. Open decisions

- Whether The One resuming on a later ball matches what was meant by "until
  the EMP is hit" (section 8).
- The act select timeout and whether it defaults to Act I or to the player's
  last choice (section 5).
- Whether the Mission Drop sits in front of its scoop (section 4).
