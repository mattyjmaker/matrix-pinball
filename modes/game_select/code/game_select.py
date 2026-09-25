"""Game select: before the first ball, pick which game this is.

Holds `ball_starting` (the mode uses `use_wait_queue`) on every player's first
ball. On player 1's it offers the games: flippers step, start confirms, and
after TIMEOUT_SECONDS with no confirmation the Matrix starts. While the select
is up the start button does not add a player. The choice is one per game of
pinball: later players get the game player 1 chose.

Once a game is chosen the mode starts that game's own pre-ball select, if it
has one (`start_act_select` for the Matrix), and keeps the ball held until
that select stops. See docs/12-rules-terminator-2.md, section 2.
"""
from mpf.core.mode import Mode

# key: (label on screen, mode to start before the ball, or None)
GAMES = {
    "matrix": ("MATRIX", "act_select"),
    "t2": ("TERMINATOR 2", None),
}
ORDER = ("matrix", "t2")
TIMEOUT_SECONDS = 15


class GameSelect(Mode):

    """Machine-wide game choice, taken on player 1's first ball."""

    __slots__ = ["_index", "_remaining", "_chosen"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._index = 0
        self._remaining = TIMEOUT_SECONDS
        self._chosen = False

    def mode_start(self, **kwargs):
        self._chosen = False
        if self.player.number == 1:
            self._offer()
        else:
            self._enter(self.machine.variables.get_machine_var("game_choice"))

    def _offer(self):
        self._index = 0
        self._remaining = TIMEOUT_SECONDS
        self.add_mode_event_handler("s_left_flipper_active", self._step, direction=-1)
        self.add_mode_event_handler("s_right_flipper_active", self._step, direction=1)
        self.add_mode_event_handler("s_start_active", self._confirm)
        self.add_mode_event_handler("player_add_request", self._deny_player_add)
        self._show()
        self.delay.add(ms=1000, callback=self._tick, name="tick")

    def _show(self):
        game = ORDER[self._index]
        self.player["game_option"] = GAMES[game][0]
        self.player["objective"] = "SELECT YOUR GAME: {}   {}".format(GAMES[game][0], self._remaining)
        self.machine.events.post("game_select_show", game=game, seconds=self._remaining)

    def _step(self, direction, **kwargs):
        del kwargs
        if self._chosen:
            return
        self._index = (self._index + direction) % len(ORDER)
        self._show()

    def _tick(self):
        self._remaining -= 1
        if self._remaining <= 0:
            self._choose(ORDER[0])
            return
        self._show()
        self.delay.add(ms=1000, callback=self._tick, name="tick")

    def _confirm(self, **kwargs):
        del kwargs
        if not self._chosen:
            self._choose(ORDER[self._index])

    @staticmethod
    def _deny_player_add(**kwargs):
        del kwargs
        # Start confirms the game, and the same press must not also add a
        # player. The chosen game's own select, if any, keeps denying while
        # this mode holds the ball; adds work again once the ball is in play.
        return False

    def _choose(self, game):
        self._chosen = True
        self.delay.remove("tick")
        self.player["objective"] = ""
        self.machine.variables.set_machine_var("game_choice", game)
        self.machine.events.post("game_selected", game=game)
        self._enter(game)

    def _enter(self, game):
        """Hand over to the chosen game and release the ball when it is ready."""
        self.player["game"] = game
        pre_ball_mode = GAMES[game][1]
        if pre_ball_mode is None:
            # stop() is ignored while the mode is starting, so wait a tick.
            self.delay.add(ms=1, callback=self.stop)
            return
        self.add_mode_event_handler("mode_{}_stopped".format(pre_ball_mode), self._pre_ball_done)
        self.machine.events.post("start_{}".format(pre_ball_mode))

    def _pre_ball_done(self, **kwargs):
        del kwargs
        self.stop()
