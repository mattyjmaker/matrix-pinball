from unittest.mock import patch

from tests.matrix_test_case import MatrixTestCase

ACTS = "modes.act_select.code.act_select.AVAILABLE_ACTS"


class TestActSelect(MatrixTestCase):

    def begin(self):
        self.fill_troughs()
        self.hit_and_release_switch("s_start")
        self.advance_time_and_run(1)

    def test_skipped_with_one_act(self):
        self.mock_event("ball_started")
        self.begin()
        self.assertEventCalled("ball_started")
        self.assertModeNotRunning("act_select")
        self.assertModeRunning("act_one")

    def test_choose_act_two(self):
        with patch(ACTS, ("I", "II")):
            self.mock_event("ball_started")
            self.begin()
            self.assertModeRunning("act_select")
            # The ball waits for the choice.
            self.assertEventNotCalled("ball_started")
            self.assertPlayerVarEqual("I", "act_choice")
            self.hit_and_release_switch("s_right_flipper")
            self.advance_time_and_run(.1)
            self.assertPlayerVarEqual("II", "act_choice")
            self.hit_and_release_switch("s_start")
            self.advance_time_and_run(2)
            self.assertModeNotRunning("act_select")
            self.assertEventCalled("ball_started")
            self.assertPlayerVarEqual("II", "act")
            self.assertModeNotRunning("act_one")
            # Start confirmed the act; it did not add a player.
            self.assertPlayerCount(1)

    def test_timeout_starts_act_one(self):
        with patch(ACTS, ("I", "II")):
            self.begin()
            # The choice moved to II, but nobody confirmed it.
            self.hit_and_release_switch("s_right_flipper")
            self.advance_time_and_run(27)
            self.assertModeRunning("act_select")
            self.advance_time_and_run(4)
            self.assertModeNotRunning("act_select")
            self.assertPlayerVarEqual("I", "act")
            self.assertModeRunning("act_one")
