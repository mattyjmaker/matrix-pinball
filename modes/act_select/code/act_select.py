"""Act select: before a player's first ball, pick which act to start in.

Started by game_select, which holds `ball_starting` until this mode stops.
Flippers step through the acts, start confirms, and after TIMEOUT_SECONDS
with no confirmation the game starts in Act I. While the select is up the
start button does not add a player.

Only acts with rules are offered. With one act the mode steps straight out,
so the game starts in Act I with no screen. Add "II" to AVAILABLE_ACTS when
Act II has rules. See docs/11-rules-act-1.md, section 5.
"""
from mpf.core.mode import Mode

AVAILABLE_ACTS = ("I",)
TIMEOUT_SECONDS = 30


class ActSelect(Mode):

    """Per-player act choice on ball 1."""

    __slots__ = ["_index", "_remaining"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._index = 0
        self._remaining = TIMEOUT_SECONDS

    def mode_start(self, **kwargs):
        if len(AVAILABLE_ACTS) < 2:
            # Nothing to choose. Stop on the next tick, which releases the
            # held ball_starting; stop() is ignored while the mode is starting.
            self.delay.add(ms=1, callback=self.stop)
            return

        self._index = 0
        self._remaining = TIMEOUT_SECONDS
        self.add_mode_event_handler("s_left_flipper_active", self._step, direction=-1)
        self.add_mode_event_handler("s_right_flipper_active", self._step, direction=1)
        self.add_mode_event_handler("s_start_active", self._confirm)
        self.add_mode_event_handler("player_add_request", self._deny_player_add)
        self._show()
        self.delay.add(ms=1000, callback=self._tick, name="tick")

    def _show(self):
        self.player["act_choice"] = AVAILABLE_ACTS[self._index]
        self.player["objective"] = "START IN ACT {}?   {}".format(AVAILABLE_ACTS[self._index], self._remaining)
        self.machine.events.post("act_select_show", act=AVAILABLE_ACTS[self._index],
                                 seconds=self._remaining)

    def _step(self, direction, **kwargs):
        del kwargs
        self._index = (self._index + direction) % len(AVAILABLE_ACTS)
        self._show()

    def _tick(self):
        self._remaining -= 1
        if self._remaining <= 0:
            self._choose(AVAILABLE_ACTS[0])
            return
        self._show()
        self.delay.add(ms=1000, callback=self._tick, name="tick")

    def _confirm(self, **kwargs):
        del kwargs
        self._choose(AVAILABLE_ACTS[self._index])

    @staticmethod
    def _deny_player_add(**kwargs):
        del kwargs
        return False

    def _choose(self, act):
        self.delay.remove("tick")
        self.player["act"] = act
        self.player["objective"] = ""
        self.machine.events.post("act_selected", act=act)
        self.stop()
