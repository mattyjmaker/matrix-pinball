"""The One: the Act I wizard mode.

Four stages, stored per player so the mode picks up where it left off on the
player's next ball. It runs until the EMP is fired; it does not end when the
multiball drops to one ball. See docs/11-rules-act-1.md, section 8.

1. Subway (2 balls): hit Agents SUBWAY_HITS times to beat Smith.
2. The Chase (4, then 6 balls): a lit "phone" moves between the ramps. Reach
   PHONES_NEEDED of them before the Sentinel timer runs out.
3. Room 303 (6 balls): the magnet takes a ball and every shot goes dark
   ("Neo dies") with a ball save covering all drains. Then every ramp is a
   super jackpot. SUPER_JACKPOTS of them light the EMP.
4. EMP: the Sentinel VUK fires it and Act I is complete.
"""
from mpf.core.mode import Mode

SUBWAY_HITS = 6
PHONES = ("trinity_ramp", "dejavu_ramp", "real_world_ramp", "sentinel_ramp")
PHONES_NEEDED = 4
# The Chase starts at 4 balls and goes to 6 after this many phones.
PHONES_FOR_SIX_BALLS = 2
CHASE_SECONDS = 60
PHONE_MOVE_MS = 5000
DARK_MS = 5000
AGENT_RAISE_MS = 1000
SUPER_JACKPOTS = 3

PHONE_NAMES = {
    "trinity_ramp": "TRINITY RAMP",
    "dejavu_ramp": "DEJA VU RAMP",
    "real_world_ramp": "REAL WORLD RAMP",
    "sentinel_ramp": "SENTINEL RAMP",
}

OBJECTIVES = {
    1: "SUBWAY: BEAT SMITH, HIT THE AGENTS",
    2: "THE CHASE: REACH THE LIT PHONE",
    3: "ROOM 303: EVERY RAMP IS A SUPER JACKPOT",
    4: "FIRE THE EMP: SENTINEL VUK",
}


class TheOne(Mode):

    """Stage machine for the Act I wizard."""

    __slots__ = ["_dark"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._dark = False

    def mode_start(self, **kwargs):
        self._dark = False
        for number in (1, 2, 3):
            self.add_mode_event_handler("drop_target_agent_{}_down".format(number), self._agent_down,
                                        number=number)
        for phone in PHONES:
            self.add_mode_event_handler("{}_hit".format(phone), self._phone_hit, phone=phone)
        self.add_mode_event_handler("ramp_hit", self._ramp_hit)
        self.add_mode_event_handler("balldevice_bd_sentinel_vuk_ball_entered", self._sentinel_vuk)

        stage = self.player["the_one_stage"]
        if not stage:
            self.player["the_one_stage"] = 1
            self.player["the_one_progress"] = 0
            self.machine.events.post("the_one_started")
            stage = 1
        else:
            self.machine.events.post("the_one_resumed", stage=stage)
        self._enter_stage(stage)

    def mode_stop(self, **kwargs):
        # Leave the_one_stage alone: it is how the mode resumes next ball.
        self.player["the_one_phone"] = ""

    def _set_stage(self, stage):
        self.player["the_one_stage"] = stage
        self.player["the_one_progress"] = 0
        self.machine.events.post("the_one_stage_{}_started".format(stage))
        self._enter_stage(stage)

    def _enter_stage(self, stage):
        """Set up a stage, either fresh or resumed on a new ball."""
        self.delay.clear()
        self.player["objective"] = OBJECTIVES[stage]
        progress = self.player["the_one_progress"]

        if stage == 1:
            self.machine.events.post("agents_raise")
            self.machine.events.post("the_one_mb_subway")
        elif stage == 2:
            if progress >= PHONES_FOR_SIX_BALLS:
                self.machine.events.post("the_one_mb_chase_full")
            else:
                self.machine.events.post("the_one_mb_chase")
            self.player["the_one_timer"] = CHASE_SECONDS
            self._move_phone()
            self.delay.add(ms=1000, callback=self._chase_tick, name="chase_tick")
        elif stage == 3:
            self._room_303()
        elif stage == 4:
            self.machine.events.post("sentinel_gate_open")

    # --- stage 1: Subway -------------------------------------------------

    def _agent_down(self, number, **kwargs):
        del kwargs
        if self.player["the_one_stage"] != 1:
            return
        self.machine.events.post("the_one_agent_hit")
        self.player["the_one_progress"] += 1
        if self.player["the_one_progress"] >= SUBWAY_HITS:
            self._set_stage(2)
            return
        self.delay.add(ms=AGENT_RAISE_MS, callback=self.machine.events.post,
                       event="agent_{}_raise".format(number))

    # --- stage 2: The Chase ----------------------------------------------

    def _move_phone(self):
        current = self.player["the_one_phone"]
        index = PHONES.index(current) + 1 if current in PHONES else 0
        phone = PHONES[index % len(PHONES)]
        self.player["the_one_phone"] = phone
        self.player["objective"] = "THE CHASE: THE PHONE IS ON THE " + PHONE_NAMES[phone]
        self.machine.events.post("the_one_phone_moved", phone=phone)
        self.delay.add(ms=PHONE_MOVE_MS, callback=self._move_phone, name="phone")

    def _chase_tick(self):
        self.player["the_one_timer"] -= 1
        if self.player["the_one_timer"] <= 0:
            self.machine.events.post("the_one_chase_timeout")
            self._set_stage(3)
            return
        self.delay.add(ms=1000, callback=self._chase_tick, name="chase_tick")

    def _phone_hit(self, phone, **kwargs):
        del kwargs
        if self.player["the_one_stage"] != 2 or self.player["the_one_phone"] != phone:
            return
        self.machine.events.post("the_one_phone_reached")
        self.player["the_one_progress"] += 1
        progress = self.player["the_one_progress"]
        if progress >= PHONES_NEEDED:
            self._set_stage(3)
            return
        if progress == PHONES_FOR_SIX_BALLS:
            self.machine.events.post("the_one_mb_chase_full")
        self.delay.remove("phone")
        self._move_phone()

    # --- stage 3: Room 303 -----------------------------------------------

    def _room_303(self):
        self._dark = True
        self.player["the_one_phone"] = ""
        self.machine.events.post("the_one_dark")
        self.machine.events.post("sentinel_magnet_grab")
        self.delay.add(ms=DARK_MS, callback=self._resurrect)

    def _resurrect(self):
        self._dark = False
        self.machine.events.post("sentinel_magnet_release")
        self.machine.events.post("the_one_resurrected")
        self.machine.events.post("the_one_mb_room_303")

    def _ramp_hit(self, **kwargs):
        del kwargs
        if self.player["the_one_stage"] != 3 or self._dark:
            return
        self.machine.events.post("the_one_super_jackpot")
        self.player["the_one_progress"] += 1
        if self.player["the_one_progress"] >= SUPER_JACKPOTS:
            self._set_stage(4)

    # --- stage 4: EMP ----------------------------------------------------

    def _sentinel_vuk(self, **kwargs):
        del kwargs
        if self.player["the_one_stage"] != 4:
            return
        self.machine.events.post("sentinel_gate_close")
        self.machine.events.post("the_one_emp")
