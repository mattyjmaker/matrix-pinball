"""The Machine City: the Act III wizard mode, and the end of the Matrix.

Four stages, stored per player so the mode picks up where it left off on the
player's next ball. It runs until Smith is beaten; it does not end when the
multiball drops to one ball. See docs/15-rules-act-3.md, section 6.

1. Above the clouds (2 balls): Trinity flies the Logos up through the
   clouds. CLOUD_RAMPS ramp shots, any ramps.
2. The Machine City (4 balls): Neo makes his offer. Each of the four EMP
   standups (the pop area targets) once; that opens the Sentinel gate, and
   the Sentinel VUK (the platform VUK) jacks Neo in.
3. The rain (6 balls): Smith copies everywhere. The three pop-ups (the
   Agents) rise again SMITH_RAISE_MS after they drop; SMITHS_NEEDED of them.
4. The last Smith: the Deja Vu VUK (the middle loop VUK). The machines purge
   Smith, the war ends and the Matrix is complete.
"""
from mpf.core.mode import Mode

CLOUD_RAMPS = 3
OFFER_TARGETS = 4
SMITHS_NEEDED = 10
SMITH_RAISE_MS = 1000

OBJECTIVES = {
    1: "ABOVE THE CLOUDS: 3 RAMPS",
    2: "THE MACHINE CITY: HIT THE FOUR EMP TARGETS",
    3: "THE RAIN: HIT THE SMITHS",
    4: "THE LAST SMITH: SHOOT THE DEJA VU VUK",
}


class TheMachineCity(Mode):

    """Stage machine for the Act III wizard."""

    __slots__ = []

    def mode_start(self, **kwargs):
        self.add_mode_event_handler("ramp_hit", self._ramp_hit)
        for number in range(1, OFFER_TARGETS + 1):
            self.add_mode_event_handler("pop_target_{}_hit".format(number), self._offer_hit, number=number)
        self.add_mode_event_handler("balldevice_bd_platform_vuk_ball_entered", self._jack_in)
        for number in (1, 2, 3):
            self.add_mode_event_handler("drop_target_popup_{}_down".format(number), self._smith_down,
                                        number=number)
        self.add_mode_event_handler("balldevice_bd_middle_loop_vuk_ball_entered", self._last_smith)

        stage = self.player["machine_city_stage"]
        if not stage:
            self.player["machine_city_stage"] = 1
            self.player["machine_city_progress"] = 0
            self.machine.events.post("machine_city_started")
            stage = 1
        else:
            self.machine.events.post("machine_city_resumed", stage=stage)
        self._enter_stage(stage)

    def _stage(self):
        return self.player["machine_city_stage"]

    def _set_stage(self, stage):
        self.player["machine_city_stage"] = stage
        self.player["machine_city_progress"] = 0
        self._enter_stage(stage)

    def _enter_stage(self, stage):
        """Set up a stage, either fresh or resumed on a new ball."""
        self.delay.clear()
        self.player["objective"] = OBJECTIVES[stage]
        # Posted on a fresh stage and on resuming it next ball, so the display
        # shows the stage card either way.
        self.machine.events.post("machine_city_stage_{}_started".format(stage),
                                 progress=self.player["machine_city_progress"])

        if stage == 1:
            self.machine.events.post("machine_city_mb_clouds")
        elif stage == 2:
            self.machine.events.post("machine_city_mb_city")
            if self._offer_made():
                self.machine.events.post("platform_gate_open")
        elif stage == 3:
            self.machine.events.post("machine_city_mb_rain")
            self.machine.events.post("popups_raise")

    # --- stage 1: above the clouds ---------------------------------------

    def _ramp_hit(self, **kwargs):
        del kwargs
        if self._stage() != 1:
            return
        self.machine.events.post("machine_city_cloud")
        self.player["machine_city_progress"] += 1
        if self.player["machine_city_progress"] >= CLOUD_RAMPS:
            self._set_stage(2)

    # --- stage 2: the Machine City ---------------------------------------

    def _offer_made(self):
        return self.player["machine_city_progress"] == (1 << OFFER_TARGETS) - 1

    def _offer_hit(self, number, **kwargs):
        del kwargs
        bit = 1 << (number - 1)
        if self._stage() != 2 or self.player["machine_city_progress"] & bit:
            return
        self.player["machine_city_progress"] |= bit
        self.machine.events.post("machine_city_offer")
        if self._offer_made():
            self.player["objective"] = "THE MACHINE CITY: JACK IN AT THE SENTINEL VUK"
            self.machine.events.post("platform_gate_open")
            self.machine.events.post("machine_city_offer_made")

    def _jack_in(self, **kwargs):
        del kwargs
        if self._stage() != 2 or not self._offer_made():
            return
        self.machine.events.post("platform_gate_close")
        self.machine.events.post("machine_city_jacked_in")
        self._set_stage(3)

    # --- stage 3: the rain -----------------------------------------------

    def _smith_down(self, number, **kwargs):
        del kwargs
        if self._stage() != 3:
            return
        self.machine.events.post("machine_city_smith")
        self.player["machine_city_progress"] += 1
        if self.player["machine_city_progress"] >= SMITHS_NEEDED:
            self._set_stage(4)
            return
        self.delay.add(ms=SMITH_RAISE_MS, callback=self.machine.events.post,
                       event="popup_{}_raise".format(number))

    # --- stage 4: the last Smith -----------------------------------------

    def _last_smith(self, **kwargs):
        del kwargs
        if self._stage() != 4:
            return
        self.machine.events.post("machine_city_peace")
