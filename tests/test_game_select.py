"""The game select: one game per game of pinball, chosen on player 1's first ball."""
from tests.matrix_test_case import MatrixTestCase


class TestGameSelect(MatrixTestCase):

    def begin(self):
        self.fill_troughs()
        self.hit_and_release_switch("s_start")
        self.advance_time_and_run(1)

    def test_holds_the_ball_and_offers_the_matrix_first(self):
        self.mock_event("ball_started")
        self.begin()
        self.assertModeRunning("game_select")
        self.assertEventNotCalled("ball_started")
        self.assertPlayerVarEqual("MATRIX", "game_option")

    def test_flippers_step_and_wrap(self):
        self.begin()
        self.hit_and_release_switch("s_right_flipper")
        self.advance_time_and_run(.1)
        self.assertPlayerVarEqual("TERMINATOR 2", "game_option")
        self.hit_and_release_switch("s_right_flipper")
        self.advance_time_and_run(.1)
        self.assertPlayerVarEqual("MATRIX", "game_option")
        self.hit_and_release_switch("s_left_flipper")
        self.advance_time_and_run(.1)
        self.assertPlayerVarEqual("TERMINATOR 2", "game_option")

    def test_start_confirms_without_adding_a_player(self):
        self.mock_event("game_selected")
        self.begin()
        self.hit_and_release_switch("s_right_flipper")
        self.advance_time_and_run(.1)
        self.hit_and_release_switch("s_start")
        self.advance_time_and_run(1)
        self.assertEventCalledWith("game_selected", game="t2")
        self.assertEqual("t2", self.machine.variables.get_machine_var("game_choice"))
        self.assertPlayerVarEqual("t2", "game")
        self.assertPlayerCount(1)
        self.assertModeNotRunning("game_select")
        self.assertModeRunning("t2_main")
        self.assertModeNotRunning("act_select")

    def test_timeout_starts_the_matrix(self):
        self.begin()
        self.hit_and_release_switch("s_right_flipper")
        self.advance_time_and_run(13)
        self.assertModeRunning("game_select")
        self.advance_time_and_run(3)
        self.assertModeNotRunning("game_select")
        self.assertEqual("matrix", self.machine.variables.get_machine_var("game_choice"))
        self.assertModeRunning("act_one")

    def test_matrix_runs_the_act_select_before_the_ball(self):
        self.mock_event("start_act_select")
        self.begin()
        self.hit_and_release_switch("s_start")
        self.advance_time_and_run(1)
        self.assertEventCalled("start_act_select")
        self.assertModeRunning("act_one")

    def test_second_player_gets_the_same_game(self):
        self.start_t2_game()
        # Add a player once the ball is in play, then drain player 1.
        self.hit_and_release_switch("s_start")
        self.advance_time_and_run(1)
        self.assertPlayerCount(2)
        self.drain_all_balls()
        self.advance_time_and_run(3)
        self.assertEqual(2, self.machine.game.player.number)
        # No choice screen for player 2: straight into Terminator 2.
        self.assertModeNotRunning("game_select")
        self.assertModeRunning("t2_main")
        self.assertPlayerVarEqual("t2", "game")
