"""Spot checks that the scores match docs/11-rules-act-1.md."""
from tests.test_act_one import ActOneTestCase


class TestScoring(ActOneTestCase):

    def gained(self, action):
        before = self.player().score
        action()
        return self.player().score - before

    def test_mission_drop_and_empty_scoop(self):
        self.start()
        self.assertEqual(5000, self.gained(self.open_mission))
        self.player()["mode_ready"] = 0
        self.assertEqual(10000, self.gained(self.shoot_mission))

    def test_chapter_one_jumps(self):
        self.start()
        self.start_chapter(1)
        self.assertEqual(50000, self.gained(lambda: self.ramp("left_lock")))

    def test_roster_name_and_the_one_lit(self):
        self.start()
        for event in ("ch1_completed", "ch2_completed", "ch3_completed"):
            self.assertEqual(250000, self.gained(lambda e=event: self.post_event(e, .1)))
        self.assertEqual(250000 + 500000, self.gained(lambda: self.post_event("ch4_completed", .1)))

    def test_trinity_lock(self):
        self.start()
        self.assertEqual(10000, self.gained(lambda: self.enter_device("s_left_lock_1", 3)))

    def test_platform_gate_opens(self):
        self.start()

        def four_hits():
            for _ in range(4):
                self.hit_and_release_switch("s_platform_gate_left")
            self.advance_time_and_run(.5)
        self.assertEqual(100000, self.gained(four_hits))

    def test_gate_and_count_reset_at_ball_end(self):
        self.start()
        for _ in range(4):
            self.hit_and_release_switch("s_platform_gate_left")
        self.advance_time_and_run(.5)
        self.assertTrue(self.machine.diverters["platform_gate"].active)
        self.drain_all_balls()
        self.advance_time_and_run(5)
        self.assertBallNumber(2)
        self.assertFalse(self.machine.diverters["platform_gate"].active)
        self.enter_device("s_platform_vuk")
        self.assertModeNotRunning("sentinel_mb")
