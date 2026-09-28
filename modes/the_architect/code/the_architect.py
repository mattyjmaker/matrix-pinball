"""The Architect: the Act II wizard mode.

Five stages, stored per player so the mode picks up where it left off on the
player's next ball. It runs until the Sentinels are stopped; it does not end
when the multiball drops to one ball. See docs/14-rules-act-2.md, section 6.

1. The power plant (2 balls): Niobe's crew cuts the power. Each of the four
   EMP standups (the pop area targets) once.
2. The hallway (4 balls): the backdoors. Each three-bank drop is a door; the
   Smiths close every door DOORS_CLOSE_MS after the first opens, unless all
   three are open. All three open lights the Keymaker's last door on the
   Deja Vu VUK (the middle loop VUK).
3. The Architect: the two doors. A left-side shot takes the left door (the
   Source), a right-side shot the right door (Trinity). No shot in
   CHOICE_SECONDS takes the right door, as Neo does.
4. The door taken (`architect_door`):
   - the Source (6 balls): every ramp is a super jackpot for SOURCE_SECONDS,
     up to SOURCE_JACKPOTS of them.
   - Trinity: a hurry-up falling from 5,000,000 to 1,000,000 over
     TRINITY_SECONDS, then holding. The Real World Ramp (Neo flies), then the
     Sentinel magnet catches a ball (Neo catches her) for the value.
5. Something is different: the Sentinel VUK (the platform VUK) stops the
   Sentinels, and Act II is complete.
"""
from mpf.core.mode import Mode

POWER_TARGETS = 4
DOORS_CLOSE_MS = 6000
CHOICE_SECONDS = 15
SOURCE_SECONDS = 30
SOURCE_JACKPOTS = 4
TRINITY_SECONDS = 40
TRINITY_FLOOR = 1000000
TRINITY_STEP = 100000
MAGNET_HOLD_MS = 2000

OBJECTIVES = {
    1: "THE POWER PLANT: HIT THE FOUR EMP TARGETS",
    2: "THE HALLWAY: OPEN ALL THREE DOORS",
    3: "THE ARCHITECT: SHOOT LEFT FOR THE SOURCE, RIGHT FOR TRINITY",
    5: "SOMETHING IS DIFFERENT: SENTINEL VUK",
}
DOOR_OBJECTIVES = {
    "source": "THE SOURCE: EVERY RAMP IS A SUPER JACKPOT",
    "trinity": "TRINITY FALLS: REAL WORLD RAMP, THEN THE SENTINEL MAGNET",
}


class TheArchitect(Mode):

    """Stage machine for the Act II wizard."""

    __slots__ = ["_seconds"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._seconds = 0

    def mode_start(self, **kwargs):
        for number in range(1, POWER_TARGETS + 1):
            self.add_mode_event_handler("pop_target_{}_hit".format(number), self._power_hit, number=number)
        for number in (1, 2, 3):
            self.add_mode_event_handler("drop_target_three_bank_{}_down".format(number), self._door_opened)
        self.add_mode_event_handler("drop_target_bank_three_bank_down", self._all_doors_open)
        self.add_mode_event_handler("balldevice_bd_middle_loop_vuk_ball_entered", self._last_door)
        self.add_mode_event_handler("left_shot_hit", self._door_chosen, door="source")
        self.add_mode_event_handler("right_shot_hit", self._door_chosen, door="trinity")
        self.add_mode_event_handler("ramp_hit", self._ramp_hit)
        self.add_mode_event_handler("right_loop_ramp_hit", self._fly)
        self.add_mode_event_handler("platform_magnet_hit", self._catch)
        self.add_mode_event_handler("balldevice_bd_platform_vuk_ball_entered", self._sentinel_vuk)

        stage = self.player["architect_stage"]
        if not stage:
            self.player["architect_stage"] = 1
            self.player["architect_progress"] = 0
            self.player["architect_door"] = ""
            self.machine.events.post("architect_started")
            stage = 1
        else:
            self.machine.events.post("architect_resumed", stage=stage)
        self._enter_stage(stage)

    def _stage(self):
        return self.player["architect_stage"]

    def _set_stage(self, stage):
        self.player["architect_stage"] = stage
        self.player["architect_progress"] = 0
        self._enter_stage(stage)

    def _enter_stage(self, stage):
        """Set up a stage, either fresh or resumed on a new ball."""
        self.delay.clear()
        door = self.player["architect_door"]
        self.player["objective"] = DOOR_OBJECTIVES[door] if stage == 4 else OBJECTIVES[stage]
        # Posted on a fresh stage and on resuming it next ball, so the display
        # shows the stage card and clock either way.
        self.machine.events.post("architect_stage_{}_started".format(stage),
                                 progress=self.player["architect_progress"], door=door)

        if stage == 1:
            self.machine.events.post("architect_mb_power")
        elif stage == 2:
            self.machine.events.post("architect_mb_hallway")
            if not self.player["architect_progress"]:
                self.machine.events.post("three_bank_reset")
        elif stage == 3:
            self._start_clock(CHOICE_SECONDS, "architect_choice_tick", self._choice_timeout)
        elif stage == 4 and door == "source":
            self.machine.events.post("architect_mb_source")
            self._start_clock(SOURCE_SECONDS, "architect_source_tick", self._source_timeout)
        elif stage == 4:
            self.player["architect_value"] = TRINITY_FLOOR + TRINITY_SECONDS * TRINITY_STEP
            self._start_clock(TRINITY_SECONDS, "architect_trinity_tick", None)
        elif stage == 5:
            self.machine.events.post("platform_gate_open")

    # --- clocks ----------------------------------------------------------

    def _start_clock(self, seconds, event, on_timeout):
        """Count down once a second, posting `event` with the seconds left."""
        self._seconds = seconds
        self.machine.events.post(event, ticks=seconds)
        self.delay.add(ms=1000, callback=self._clock_tick, name="clock", event=event, on_timeout=on_timeout)

    def _clock_tick(self, event, on_timeout):
        self._seconds -= 1
        if event == "architect_trinity_tick":
            self.player["architect_value"] = TRINITY_FLOOR + max(self._seconds, 0) * TRINITY_STEP
        self.machine.events.post(event, ticks=max(self._seconds, 0))
        if self._seconds <= 0:
            # The Trinity hurry-up holds at its floor rather than ending.
            if on_timeout:
                on_timeout()
            return
        self.delay.add(ms=1000, callback=self._clock_tick, name="clock", event=event, on_timeout=on_timeout)

    # --- stage 1: the power plant ----------------------------------------

    def _power_hit(self, number, **kwargs):
        del kwargs
        bit = 1 << (number - 1)
        if self._stage() != 1 or self.player["architect_progress"] & bit:
            return
        self.player["architect_progress"] |= bit
        self.machine.events.post("architect_power_cut")
        if self.player["architect_progress"] == (1 << POWER_TARGETS) - 1:
            self._set_stage(2)

    # --- stage 2: the hallway --------------------------------------------

    def _door_opened(self, **kwargs):
        del kwargs
        if self._stage() != 2 or self.player["architect_progress"]:
            return
        self.machine.events.post("architect_door_opened")
        # The first door of a round starts the Smiths' clock; later ones do not reset it.
        self.delay.add_if_doesnt_exist(ms=DOORS_CLOSE_MS, callback=self._smiths_close, name="smiths")

    def _smiths_close(self):
        if self._stage() == 2 and not self.player["architect_progress"]:
            self.machine.events.post("architect_doors_closed")
            self.machine.events.post("three_bank_reset")

    def _all_doors_open(self, **kwargs):
        del kwargs
        if self._stage() != 2 or self.player["architect_progress"]:
            return
        self.delay.remove("smiths")
        self.player["architect_progress"] = 1
        self.player["objective"] = "THE HALLWAY: THE KEYMAKER'S DOOR, DEJA VU VUK"
        self.machine.events.post("architect_last_door_lit")

    def _last_door(self, **kwargs):
        del kwargs
        if self._stage() != 2 or not self.player["architect_progress"]:
            return
        self.machine.events.post("architect_last_door")
        self._set_stage(3)

    # --- stage 3: the Architect ------------------------------------------

    def _door_chosen(self, door, **kwargs):
        del kwargs
        if self._stage() != 3:
            return
        self.player["architect_door"] = door
        self.machine.events.post("architect_door_chosen", door=door)
        self._set_stage(4)

    def _choice_timeout(self):
        self._door_chosen("trinity")

    # --- stage 4: the Source ---------------------------------------------

    def _ramp_hit(self, **kwargs):
        del kwargs
        if self._stage() != 4 or self.player["architect_door"] != "source":
            return
        self.machine.events.post("architect_super_jackpot")
        self.player["architect_progress"] += 1
        if self.player["architect_progress"] >= SOURCE_JACKPOTS:
            self._set_stage(5)

    def _source_timeout(self):
        self._set_stage(5)

    # --- stage 4: Trinity ------------------------------------------------

    def _fly(self, **kwargs):
        del kwargs
        if self._stage() != 4 or self.player["architect_door"] != "trinity" or self.player["architect_progress"]:
            return
        self.player["architect_progress"] = 1
        self.player["objective"] = "TRINITY FALLS: CATCH HER AT THE SENTINEL MAGNET"
        self.machine.events.post("architect_flying")

    def _catch(self, **kwargs):
        del kwargs
        if self._stage() != 4 or self.player["architect_door"] != "trinity" or not self.player["architect_progress"]:
            return
        self.delay.remove("clock")
        self.machine.events.post("platform_magnet_grab")
        self.machine.events.post("architect_trinity_caught")
        self.delay.add(ms=MAGNET_HOLD_MS, callback=self._release_trinity)

    def _release_trinity(self):
        self.machine.events.post("platform_magnet_release")
        self._set_stage(5)

    # --- stage 5: something is different ---------------------------------

    def _sentinel_vuk(self, **kwargs):
        del kwargs
        if self._stage() != 5:
            return
        self.machine.events.post("platform_gate_close")
        self.machine.events.post("architect_sentinels_stopped")
