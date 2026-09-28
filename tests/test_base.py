from tests.matrix_test_case import MatrixTestCase


class TestBase(MatrixTestCase):

    def start(self):
        self.start_matrix_game()

    def test_seven_balls_known(self):
        self.fill_troughs()
        self.assertNumBallsKnown(7)

    def test_popups_down_and_popup_scoop_reset(self):
        self.start()
        self.mock_event("popup_scoop_reset")
        for n in (1, 2, 3):
            self.knock_down_popup(n, .1)
        self.assertTrue(self.machine.drop_target_banks["popups"].complete)
        self.assertPlayerVarEqual(3 * 10000 + 50000, "score")
        # A ball into the pop-up scoop raises them again.
        self.hit_switch_and_run("s_popup_scoop", 2)
        self.assertEventCalled("popup_scoop_reset")
        self.assertPlayerVarEqual(3 * 10000 + 50000 + 50000, "score")

    def test_popups_down_and_unheld_in_attract(self):
        self.advance_time_and_run(1)
        for n in (1, 2, 3):
            self.assertTrue(self.popup_down(n))
            self.assertFalse(self.popup_held(n))

    def test_popups_raised_and_held_at_ball_start(self):
        self.start()
        for n in (1, 2, 3):
            self.assertFalse(self.popup_down(n))
            self.assertTrue(self.popup_held(n))

    def test_popup_hit_releases_only_its_hold(self):
        self.start()
        self.knock_down_popup(2)
        self.assertTrue(self.popup_down(2))
        self.assertTrue(self.popup_held(1))
        self.assertTrue(self.popup_held(3))
        self.assertPlayerVarEqual(10000, "score")

    def test_popups_raise_holds_again(self):
        self.start()
        for n in (1, 2, 3):
            self.knock_down_popup(n)
        self.post_event("popups_raise", 1)
        for n in (1, 2, 3):
            self.assertFalse(self.popup_down(n))
            self.assertTrue(self.popup_held(n))

    def test_popup_holds_released_at_game_end(self):
        self.start()
        self.stop_game()
        for n in (1, 2, 3):
            self.assertFalse(self.popup_held(n))

    def test_popup_hold_events_match_reset_events(self):
        # A pop-up raised without its hold falls straight back down, so every
        # event that resets a pop-up must also enable its hold.
        bank = set(self.machine.drop_target_banks["popups"].config["reset_events"])
        for n in (1, 2, 3):
            target = set(self.machine.drop_targets["popup_{}".format(n)].config["reset_events"])
            hold = set(self.machine.coils["c_popup_{}_hold".format(n)].config["enable_events"])
            self.assertEqual(bank | target, hold)

    def test_popup_scoop_small_award_when_popups_up(self):
        self.start()
        self.hit_switch_and_run("s_popup_scoop", 2)
        self.assertPlayerVarEqual(5000, "score")

    def test_mystery_lit_and_collected(self):
        self.start()
        for n in (1, 2, 3, 4):
            self.hit_and_release_switch("s_pop_target_{}".format(n))
        self.advance_time_and_run(.1)
        self.assertPlayerVarEqual(1, "mystery_lit")
        self.mock_event("mystery_collect")
        self.hit_switch_and_run("s_middle_loop_vuk", 2)
        self.assertEventCalled("mystery_collect")
        self.assertPlayerVarEqual(0, "mystery_lit")

    def test_outlane_lock_saves_last_ball(self):
        self.start()
        self.assertBallsInPlay(1)
        # The playfield ball goes into the Ammo Lock and is held.
        self.hit_switch_and_run("s_right_outlane_lock", 3)
        self.assertEqual(1, self.machine.ball_devices["bd_right_outlane_lock"].balls)
        # A new ball was served.
        self.confirm_playfield()
        self.assertEqual(1, self.machine.playfield.balls)
        # Drain it: the locked ball comes back instead of the ball ending.
        self.drain_one_ball()
        self.advance_time_and_run(5)
        self.assertBallNumber(1)
        self.assertEqual(0, self.machine.ball_devices["bd_right_outlane_lock"].balls)
        self.assertEqual(1, self.machine.playfield.balls)

    def test_outlane_lock_target_releases_lock(self):
        self.start()
        self.hit_switch_and_run("s_right_outlane_lock", 3)
        self.confirm_playfield()
        self.hit_and_release_switch("s_right_outlane_lock_target")
        self.advance_time_and_run(3)
        self.assertEqual(0, self.machine.ball_devices["bd_right_outlane_lock"].balls)
        self.assertBallsInPlay(2)
