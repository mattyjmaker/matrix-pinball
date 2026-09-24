from tests.matrix_test_case import MatrixTestCase


class TestBase(MatrixTestCase):

    def start(self):
        self.start_matrix_game()

    def test_seven_balls_known(self):
        self.fill_troughs()
        self.assertNumBallsKnown(7)

    def test_agents_down_and_agents_coming(self):
        self.start()
        self.mock_event("agents_coming")
        for n in (1, 2, 3):
            self.hit_switch_and_run("s_agent_{}".format(n), .1)
        self.assertTrue(self.machine.drop_target_banks["agents"].complete)
        self.assertPlayerVarEqual(3 * 10000 + 50000, "score")
        # A ball into the Agents Coming scoop raises them again.
        self.hit_switch_and_run("s_cypher_scoop", 2)
        self.assertEventCalled("agents_coming")
        self.assertPlayerVarEqual(3 * 10000 + 50000 + 50000, "score")

    def test_cypher_scoop_small_award_when_agents_up(self):
        self.start()
        self.hit_switch_and_run("s_cypher_scoop", 2)
        self.assertPlayerVarEqual(5000, "score")

    def test_oracle_lit_and_collected(self):
        self.start()
        for n in (1, 2, 3, 4):
            self.hit_and_release_switch("s_emp_target_{}".format(n))
        self.advance_time_and_run(.1)
        self.assertPlayerVarEqual(1, "oracle_lit")
        self.mock_event("oracle_collect")
        self.hit_switch_and_run("s_dejavu_vuk", 2)
        self.assertEventCalled("oracle_collect")
        self.assertPlayerVarEqual(0, "oracle_lit")

    def test_ammo_lock_saves_last_ball(self):
        self.start()
        self.assertBallsInPlay(1)
        # The playfield ball goes into the Ammo Lock and is held.
        self.hit_switch_and_run("s_ammo_lock", 3)
        self.assertEqual(1, self.machine.ball_devices["bd_ammo_lock"].balls)
        # A new ball was served.
        self.confirm_playfield()
        self.assertEqual(1, self.machine.playfield.balls)
        # Drain it: the locked ball comes back instead of the ball ending.
        self.drain_one_ball()
        self.advance_time_and_run(5)
        self.assertBallNumber(1)
        self.assertEqual(0, self.machine.ball_devices["bd_ammo_lock"].balls)
        self.assertEqual(1, self.machine.playfield.balls)

    def test_ammo_target_releases_lock(self):
        self.start()
        self.hit_switch_and_run("s_ammo_lock", 3)
        self.confirm_playfield()
        self.hit_and_release_switch("s_ammo_target")
        self.advance_time_and_run(3)
        self.assertEqual(0, self.machine.ball_devices["bd_ammo_lock"].balls)
        self.assertBallsInPlay(2)
