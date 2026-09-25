"""Judgment Day: the Terminator 2 wizard mode.

Four stages, stored per player so the mode picks up where it left off on the
player's next ball. It runs until Judgment Day is averted; it does not end
when the multiball drops to one ball. See docs/12-rules-terminator-2.md,
section 10. The shape is the_one.py's.

1. The Freeway (2 balls): the T-1000 Ramp (backboard ramp) FREEWAY_HITS times.
2. The Steel Mill (4 balls): a Semi Grille target (platform target) MILL_HITS
   times.
3. Molten Steel (6 balls): the magnet takes a ball and the T-1000 is down for
   DOWN_MS with a ball save covering all drains. Then every ramp is a super
   jackpot. SUPER_JACKPOTS of them light the launch sites.
4. Self-Sacrifice: the four Launch Site standups (pop area targets), in order
   1 to 4. The last one averts Judgment Day and T2 is complete.
"""
from mpf.core.mode import Mode

FREEWAY_HITS = 6
MILL_HITS = 4
DOWN_MS = 5000
SUPER_JACKPOTS = 3
LAUNCH_SITES = 4

OBJECTIVES = {
    1: "THE FREEWAY: SHOOT THE T-1000 RAMP",
    2: "THE STEEL MILL: HIT THE SEMI GRILLE",
    3: "MOLTEN STEEL: EVERY RAMP IS A SUPER JACKPOT",
    4: "SELF-SACRIFICE: LAUNCH SITE 1",
}


class JudgmentDay(Mode):

    """Stage machine for the Terminator 2 wizard."""

    __slots__ = ["_down"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._down = False

    def mode_start(self, **kwargs):
        self._down = False
        self.add_mode_event_handler("backboard_ramp_hit", self._freeway_hit)
        self.add_mode_event_handler("platform_target_hit", self._mill_hit)
        self.add_mode_event_handler("ramp_hit", self._ramp_hit)
        for number in range(1, LAUNCH_SITES + 1):
            self.add_mode_event_handler("pop_target_{}_hit".format(number), self._launch_site_hit,
                                        number=number)

        stage = self.player["judgment_day_stage"]
        if not stage:
            self.player["judgment_day_stage"] = 1
            self.player["judgment_day_progress"] = 0
            self.machine.events.post("judgment_day_started")
            stage = 1
        else:
            self.machine.events.post("judgment_day_resumed", stage=stage)
        self.player["chapter"] = "JUDGMENT DAY"
        self._enter_stage(stage)

    def mode_stop(self, **kwargs):
        # Leave judgment_day_stage alone: it is how the mode resumes next ball.
        pass

    def _set_stage(self, stage):
        self.player["judgment_day_stage"] = stage
        self.player["judgment_day_progress"] = 0
        self._enter_stage(stage)

    def _enter_stage(self, stage):
        """Set up a stage, either fresh or resumed on a new ball."""
        self.delay.clear()
        self.player["objective"] = OBJECTIVES[stage]
        progress = self.player["judgment_day_progress"]
        # Posted on a fresh stage and on resuming it next ball, so the display
        # shows the stage card either way.
        self.machine.events.post("judgment_day_stage_{}_started".format(stage), progress=progress)

        if stage == 1:
            self.machine.events.post("judgment_day_mb_freeway")
        elif stage == 2:
            self.machine.events.post("judgment_day_mb_mill")
        elif stage == 3:
            self._molten_steel()
        elif stage == 4:
            self.player["objective"] = "SELF-SACRIFICE: LAUNCH SITE {}".format(progress + 1)

    # --- stage 1: the Freeway ----------------------------------------------

    def _freeway_hit(self, **kwargs):
        del kwargs
        if self.player["judgment_day_stage"] != 1:
            return
        self.machine.events.post("judgment_day_freeway_hit")
        self.player["judgment_day_progress"] += 1
        if self.player["judgment_day_progress"] >= FREEWAY_HITS:
            self._set_stage(2)

    # --- stage 2: the Steel Mill -------------------------------------------

    def _mill_hit(self, **kwargs):
        del kwargs
        if self.player["judgment_day_stage"] != 2:
            return
        self.machine.events.post("judgment_day_mill_hit")
        self.player["judgment_day_progress"] += 1
        if self.player["judgment_day_progress"] >= MILL_HITS:
            self._set_stage(3)

    # --- stage 3: Molten Steel ---------------------------------------------

    def _molten_steel(self):
        self._down = True
        self.machine.events.post("judgment_day_down")
        self.machine.events.post("platform_magnet_grab")
        self.delay.add(ms=DOWN_MS, callback=self._reformed)

    def _reformed(self):
        self._down = False
        self.machine.events.post("platform_magnet_release")
        self.machine.events.post("judgment_day_reformed")
        self.machine.events.post("judgment_day_mb_molten")

    def _ramp_hit(self, **kwargs):
        del kwargs
        if self.player["judgment_day_stage"] != 3 or self._down:
            return
        self.machine.events.post("judgment_day_super_jackpot")
        self.player["judgment_day_progress"] += 1
        if self.player["judgment_day_progress"] >= SUPER_JACKPOTS:
            self._set_stage(4)

    # --- stage 4: Self-Sacrifice -------------------------------------------

    def _launch_site_hit(self, number, **kwargs):
        del kwargs
        if self.player["judgment_day_stage"] != 4:
            return
        if number != self.player["judgment_day_progress"] + 1:
            return
        self.player["judgment_day_progress"] = number
        if number >= LAUNCH_SITES:
            self.machine.events.post("judgment_day_averted")
            return
        self.player["objective"] = "SELF-SACRIFICE: LAUNCH SITE {}".format(number + 1)
        self.machine.events.post("judgment_day_sacrifice_step", site=number)
