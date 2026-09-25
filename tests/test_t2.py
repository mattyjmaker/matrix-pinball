"""Terminator 2 rules, played through on the smart_virtual platform.

Mirrors tests/test_act_one.py. See docs/12-rules-terminator-2.md.
"""
from tests.matrix_test_case import MatrixTestCase

CHAPTER_MODES = {1: "t2_ch1_arrival", 2: "t2_ch2_pescadero", 3: "t2_ch3_dyson", 4: "t2_ch4_raid_lock"}


class T2TestCase(MatrixTestCase):

    def start(self):
        self.start_t2_game()

    def player(self):
        return self.machine.game.player

    def open_drop(self):
        self.hit_switch_and_run("s_mode_drop", .5)

    def shoot_scoop(self, settle=3):
        self.enter_device("s_mode_scoop", settle)

    def start_chapter(self, number):
        self.player()["t2_chapter_next"] = number
        self.open_drop()
        self.shoot_scoop()
        self.assertModeRunning(CHAPTER_MODES[number])

    def ramp(self, name):
        self.hit_and_release_switch("s_{}_ramp".format(name))
        self.advance_time_and_run(.1)

    def hit_platform_targets(self, *names):
        for name in names:
            self.hit_and_release_switch("s_platform_{}".format(name))
        self.advance_time_and_run(.5)


class TestController(T2TestCase):

    def test_t2_and_features_start(self):
        self.start()
        self.assertModeRunning("t2_main")
        self.assertModeRunning("future_war_lock")
        self.assertModeRunning("t1000_gate")
        self.assertModeNotRunning("act_one")
        self.assertModeNotRunning("trinity_lock")
        self.assertPlayerVarEqual("CHAPTER 1", "chapter")
        self.assertPlayerVarEqual("KNOCK DOWN THE PERIMETER DROP: ARRIVAL", "objective")

    def test_drop_lights_scoop(self):
        self.start()
        self.open_drop()
        self.assertPlayerVarEqual(1, "mode_ready")
        self.assertPlayerVarEqual("SHOOT THE COMMAND SCOOP: ARRIVAL", "objective")

    def test_scoop_without_drop_down_only_awards(self):
        self.start()
        self.mock_event("t2_scoop_award")
        self.shoot_scoop()
        self.assertEventCalled("t2_scoop_award")
        self.assertModeNotRunning("t2_ch1_arrival")
        self.assertEqual(0, self.machine.ball_devices["bd_mode_scoop"].balls)

    def test_scoop_starts_chapter_one_and_resets_drop(self):
        self.start()
        self.mock_event("mode_drop_reset")
        self.open_drop()
        self.shoot_scoop()
        self.assertModeRunning("t2_ch1_arrival")
        self.assertEventCalled("mode_drop_reset")
        self.assertPlayerVarEqual(0, "mode_ready")
        self.assertEqual(0, self.machine.ball_devices["bd_mode_scoop"].balls)

    def test_matrix_modes_ignore_the_shared_hardware(self):
        self.start()
        # Four hits on the platform gate open the T-1000 gate, not the Sentinel's.
        self.hit_platform_targets("gate_left", "gate_right", "gate_left", "gate_right")
        self.assertPlayerVarEqual(1, "t1000_open")
        self.assertModeNotRunning("sentinel_gate")


class TestChapterOne(T2TestCase):

    def test_complete(self):
        self.start()
        self.start_chapter(1)
        for ramp in ("left_lock", "middle_loop", "backboard"):
            self.ramp(ramp)
        self.assertPlayerVarEqual("THE FLOOD CHANNEL: SHOOT THE DISPLACEMENT VUK", "objective")
        self.enter_device("s_middle_loop_vuk")
        self.assertModeNotRunning("t2_ch1_arrival")
        self.assertPlayerVarEqual(1, "saved_john")
        self.assertPlayerVarEqual(1, "saved_count")
        self.assertPlayerVarEqual(2, "t2_chapter_next")
        self.assertPlayerVarEqual("CHAPTER 2", "chapter")
        self.assertPlayerVarEqual("KNOCK DOWN THE PERIMETER DROP: PESCADERO BREAK-OUT", "objective")

    def test_t1000_wins_when_the_mall_runs_out(self):
        self.start()
        self.start_chapter(1)
        self.ramp("right_loop")
        self.advance_time_and_run(41)
        self.assertModeNotRunning("t2_ch1_arrival")
        self.assertPlayerVarEqual(0, "saved_john")
        self.assertPlayerVarEqual(2, "t2_chapter_next")

    def test_rescue_value_counts_down(self):
        self.start()
        self.start_chapter(1)
        for ramp in ("left_lock", "middle_loop", "right_loop"):
            self.ramp(ramp)
        before = self.player().score
        self.advance_time_and_run(10)
        self.enter_device("s_middle_loop_vuk")
        gained = self.player().score - before
        self.assertGreater(gained, 250000 + 8 * 25000)
        self.assertLess(gained, 250000 + 12 * 25000 + 2570 + 250000 + 1)

    def test_drain_ends_chapter_as_played(self):
        self.start()
        self.start_chapter(1)
        self.drain_all_balls()
        self.advance_time_and_run(5)
        self.assertModeNotRunning("t2_ch1_arrival")
        self.assertPlayerVarEqual(2, "t2_chapter_next")


class TestChapterTwo(T2TestCase):

    def get_inside(self):
        for n in (1, 2, 3):
            self.hit_and_release_switch("s_upper_target_{}".format(n))
        self.advance_time_and_run(.5)

    def test_ward_targets_start_the_multiball(self):
        self.start()
        self.start_chapter(2)
        self.assertEqual(0, self.machine.ball_devices["bd_mode_scoop"].balls)
        before = self.player().score
        self.get_inside()
        self.assertEqual(3 * 50000, self.player().score - before)
        self.assertModeNotRunning("t2_ch2_pescadero")
        self.assertModeRunning("t2_ch2_breakout_mb")
        self.confirm_playfield()
        self.assertBallsInPlay(3)

    def test_super_jackpot_saves_sarah_and_chapter_ends_with_multiball(self):
        self.start()
        self.start_chapter(2)
        self.get_inside()
        self.confirm_playfield()
        self.mock_event("t2_ch2_super_jackpot")
        self.ramp("right_loop")
        self.get_inside()
        self.assertEventCalled("t2_ch2_super_jackpot", 1)
        self.assertPlayerVarEqual(1, "saved_sarah")
        self.advance_time_and_run(25)
        self.drain_one_ball()
        self.drain_one_ball()
        self.advance_time_and_run(3)
        self.assertModeNotRunning("t2_ch2_breakout_mb")
        self.assertPlayerVarEqual(3, "t2_chapter_next")
        self.assertBallNumber(1)

    def test_drain_before_getting_in_ends_chapter(self):
        self.start()
        self.start_chapter(2)
        self.drain_all_balls()
        self.advance_time_and_run(5)
        self.assertModeNotRunning("t2_ch2_pescadero")
        self.assertPlayerVarEqual(3, "t2_chapter_next")
        self.assertPlayerVarEqual(0, "saved_sarah")


class TestChapterThree(T2TestCase):

    def drop_five_bank(self):
        for n in range(1, 6):
            self.hit_switch_and_run("s_five_bank_{}".format(n), .1)

    def test_ball_held_through_choice(self):
        self.start()
        self.start_chapter(3)
        self.advance_time_and_run(5)
        self.assertEqual(1, self.machine.ball_devices["bd_mode_scoop"].balls)

    def test_kill_ends_chapter(self):
        self.start()
        self.start_chapter(3)
        self.hit_and_release_switch("s_left_flipper")
        self.advance_time_and_run(3)
        self.assertModeNotRunning("t2_ch3_dyson")
        self.assertEqual(0, self.machine.ball_devices["bd_mode_scoop"].balls)
        self.assertPlayerVarEqual(0, "saved_dyson")
        self.assertPlayerVarEqual(4, "t2_chapter_next")

    def test_no_choice_means_spare(self):
        self.start()
        self.start_chapter(3)
        self.advance_time_and_run(11)
        self.assertModeRunning("t2_ch3_dyson")
        self.assertPlayerVarEqual("CYBERDYNE LAB BYPASS: ALL 5 LAB TARGETS", "objective")
        self.assertEqual(0, self.machine.ball_devices["bd_mode_scoop"].balls)

    def test_spare_and_bypass_saves_dyson(self):
        self.start()
        self.start_chapter(3)
        self.hit_and_release_switch("s_right_flipper")
        self.advance_time_and_run(3)
        self.drop_five_bank()
        self.advance_time_and_run(1)
        self.assertModeNotRunning("t2_ch3_dyson")
        self.assertPlayerVarEqual(1, "saved_dyson")
        self.assertPlayerVarEqual(4, "t2_chapter_next")

    def test_bypass_timeout_means_no_dyson(self):
        self.start()
        self.start_chapter(3)
        self.hit_and_release_switch("s_right_flipper")
        self.mock_event("t2_ch3_bypass_failed")
        self.advance_time_and_run(3)
        # Only four of the five: the bank is not down.
        for n in range(1, 5):
            self.hit_switch_and_run("s_five_bank_{}".format(n), .1)
        self.advance_time_and_run(31)
        self.assertEventCalled("t2_ch3_bypass_failed")
        self.assertModeNotRunning("t2_ch3_dyson")
        self.assertPlayerVarEqual(0, "saved_dyson")
        self.assertPlayerVarEqual(4, "t2_chapter_next")


class TestChapterFour(T2TestCase):

    def lock_three(self):
        for _ in range(3):
            self.enter_device("s_right_outlane_lock", 3)
            self.confirm_playfield()

    def clear_breakin(self):
        for n in (1, 2, 3, 4):
            self.hit_and_release_switch("s_pop_target_{}".format(n))
        for n in (1, 2, 3):
            self.hit_switch_and_run("s_popup_{}".format(n), .1)
        self.advance_time_and_run(1)
        for n in (1, 2, 3):
            self.release_switch_and_run("s_popup_{}".format(n), .1)

    def test_full_raid(self):
        self.start()
        self.start_chapter(4)
        self.assertPlayerVarEqual("DYSON'S ACCESS: SHOOT THE DISPLACEMENT VUK", "objective")
        self.assertFalse(self.machine.multiball_locks["outlane_save_lock"].enabled)
        self.enter_device("s_middle_loop_vuk")
        self.assertPlayerVarEqual("ARM UP: LOCK 3 AT THE ARSENAL LOCK", "objective")
        self.lock_three()
        self.assertModeRunning("t2_ch4_raid_mb")
        self.assertModeNotRunning("t2_ch4_raid_lock")
        self.assertBallsInPlay(3)
        self.assertPlayerVarEqual("BREAK-IN: HIT EVERY GUARD", "objective")

        self.clear_breakin()
        self.assertPlayerVarEqual("FIREFIGHT: FUTURE WAR RAMP, THEN HIT AN ENDOSKELETON", "objective")
        self.assertBallsInPlay(4)

        self.ramp("left_lock")
        self.hit_switch_and_run("s_popup_1", .5)
        self.assertPlayerVarEqual("ESCAPE: CATCH THE BALL AT THE T-1000 MAGNET", "objective")
        self.assertBallsInPlay(5)

        self.hit_and_release_switch("s_platform_magnet")
        self.advance_time_and_run(1)
        self.assertPlayerVarEqual(1, "saved_chip")

    def test_endoskeleton_without_hold_the_line_does_not_advance(self):
        self.start()
        self.start_chapter(4)
        self.enter_device("s_middle_loop_vuk")
        self.lock_three()
        self.clear_breakin()
        self.hit_switch_and_run("s_popup_1", .5)
        self.assertPlayerVarEqual("FIREFIGHT: FUTURE WAR RAMP, THEN HIT AN ENDOSKELETON", "objective")

    def test_lock_phase_drain_ends_chapter(self):
        self.start()
        self.start_chapter(4)
        self.enter_device("s_middle_loop_vuk")
        self.drain_all_balls()
        self.advance_time_and_run(5)
        self.assertModeNotRunning("t2_ch4_raid_lock")
        self.assertPlayerVarEqual(5, "t2_chapter_next")
        self.assertTrue(self.machine.multiball_locks["outlane_save_lock"].enabled)


class TestFutureWarMultiball(T2TestCase):

    def lock(self):
        for n in (1, 2, 3):
            name = "s_left_lock_{}".format(n)
            if not self.machine.switch_controller.is_active(self.machine.switches[name]):
                self.enter_device(name, 3)
                break
        self.confirm_playfield()

    def test_lock_and_multiball(self):
        self.start()
        self.lock()
        self.assertPlayerVarEqual(1, "balls_locked")
        self.lock()
        self.lock()
        self.assertModeRunning("future_war_mb")
        self.assertPlayerVarEqual(0, "balls_locked")
        self.confirm_playfield()
        self.assertBallsInPlay(3)
        for _ in range(3):
            self.ramp("left_lock")
        self.assertPlayerVarEqual(1, "saved_resistance")

    def test_chapter_blocked_during_multiball(self):
        self.start()
        for _ in range(3):
            self.lock()
        self.assertModeRunning("future_war_mb")
        self.open_drop()
        self.mock_event("t2_scoop_award")
        self.shoot_scoop()
        self.assertEventCalled("t2_scoop_award")
        self.assertModeNotRunning("t2_ch1_arrival")

    def test_queued_behind_t1000(self):
        self.start()
        self.hit_platform_targets("gate_left", "gate_right", "gate_left", "gate_right")
        self.enter_device("s_platform_vuk")
        self.assertModeRunning("t1000_mb")
        self.confirm_playfield()
        for _ in range(3):
            self.lock()
        self.assertModeNotRunning("future_war_mb")
        self.assertPlayerVarEqual("future_war", "mb_pending")
        self.advance_time_and_run(25)
        self.drain_one_ball()
        self.advance_time_and_run(2)
        self.drain_one_ball()
        self.advance_time_and_run(3)
        self.assertModeNotRunning("t1000_mb")
        self.assertModeRunning("future_war_mb")
        self.assertPlayerVarEqual("", "mb_pending")


class TestT1000Multiball(T2TestCase):

    def open_gate(self):
        self.hit_platform_targets("gate_left", "gate_right", "gate_left", "gate_right")

    def test_gate_needs_four_hits(self):
        self.start()
        self.enter_device("s_platform_vuk")
        self.assertModeNotRunning("t1000_mb")
        self.open_gate()
        self.assertTrue(self.machine.diverters["platform_gate"].active)
        self.enter_device("s_platform_vuk")
        self.assertModeRunning("t1000_mb")

    def test_add_a_ball_once_and_completion(self):
        self.start()
        self.open_gate()
        self.enter_device("s_platform_vuk")
        self.confirm_playfield()
        self.assertBallsInPlay(3)
        self.hit_platform_targets("gate_left", "gate_right", "target_2")
        self.assertPlayerVarEqual(1, "t1000_aab_lit")
        self.enter_device("s_platform_vuk")
        self.confirm_playfield()
        self.assertBallsInPlay(4)
        self.hit_platform_targets("gate_left", "gate_right", "target_1")
        self.enter_device("s_platform_vuk")
        self.confirm_playfield()
        self.assertBallsInPlay(4)
        # Two platform targets were jackpots; the ramp is the third.
        self.ramp("backboard")
        self.assertPlayerVarEqual(1, "saved_skynet")

    def test_gate_closes_when_multiball_ends(self):
        self.start()
        self.open_gate()
        self.enter_device("s_platform_vuk")
        self.confirm_playfield()
        self.advance_time_and_run(25)
        while self.machine.game.balls_in_play > 1:
            self.drain_one_ball()
            self.advance_time_and_run(2)
        self.advance_time_and_run(1)
        self.assertModeNotRunning("t1000_mb")
        self.assertFalse(self.machine.diverters["platform_gate"].active)


class TestJudgmentDay(T2TestCase):

    EVENTS = {"john": "t2_ch1_completed", "sarah": "t2_ch2_completed", "dyson": "t2_ch3_completed",
              "chip": "t2_ch4_completed", "resistance": "future_war_mb_completed",
              "skynet": "t1000_mb_completed"}

    def save(self, *names):
        for name in names:
            self.post_event(self.EVENTS[name])
        self.advance_time_and_run(.1)

    def light(self):
        self.save("john", "sarah", "dyson", "resistance")
        self.assertPlayerVarEqual(1, "judgment_day_lit")

    def start_judgment_day(self):
        self.light()
        self.open_drop()
        self.shoot_scoop()
        self.assertModeRunning("judgment_day")

    def freeway(self):
        for _ in range(6):
            self.ramp("backboard")

    def mill(self):
        for _ in range(4):
            self.hit_platform_targets("target_1")

    def test_threshold_is_four(self):
        self.start()
        self.save("john", "sarah", "dyson")
        self.assertPlayerVarEqual(0, "judgment_day_lit")
        self.save("skynet")
        self.assertPlayerVarEqual(1, "judgment_day_lit")
        self.assertPlayerVarEqual("JUDGMENT DAY", "chapter")
        self.assertPlayerVarEqual("KNOCK DOWN THE PERIMETER DROP: JUDGMENT DAY", "objective")

    def test_threshold_setting(self):
        self.machine.settings.set_setting_value("judgment_day_threshold", 6)
        self.start()
        self.save("john", "sarah", "dyson", "resistance", "skynet")
        self.assertPlayerVarEqual(0, "judgment_day_lit")
        self.save("chip")
        self.assertPlayerVarEqual(1, "judgment_day_lit")

    def test_same_name_counts_once(self):
        self.start()
        self.save("john", "john")
        self.assertPlayerVarEqual(1, "saved_count")

    def test_scoop_prefers_judgment_day_over_a_chapter(self):
        self.start()
        self.start_judgment_day()
        self.assertModeNotRunning("t2_ch1_arrival")
        self.assertModeNotRunning("future_war_lock")
        self.assertModeNotRunning("t1000_gate")
        self.assertPlayerVarEqual(1, "judgment_day_stage")
        self.confirm_playfield()
        self.assertBallsInPlay(2)

    def test_all_stages_to_t2_complete(self):
        self.start()
        self.start_judgment_day()
        self.confirm_playfield()
        self.freeway()
        self.assertPlayerVarEqual(2, "judgment_day_stage")
        self.confirm_playfield()
        self.assertBallsInPlay(4)

        self.mill()
        self.assertPlayerVarEqual(3, "judgment_day_stage")
        # Down: ramps pay nothing.
        self.mock_event("judgment_day_super_jackpot")
        self.ramp("left_lock")
        self.assertEventNotCalled("judgment_day_super_jackpot")
        self.advance_time_and_run(5)
        self.confirm_playfield()
        self.assertBallsInPlay(6)
        for _ in range(3):
            self.ramp("middle_loop")
        self.assertEventCalled("judgment_day_super_jackpot", 3)
        self.assertPlayerVarEqual(4, "judgment_day_stage")

        # Launch sites out of order do not count.
        self.hit_and_release_switch("s_pop_target_3")
        self.advance_time_and_run(.1)
        self.assertPlayerVarEqual(0, "judgment_day_progress")
        for n in (1, 2, 3):
            self.hit_and_release_switch("s_pop_target_{}".format(n))
            self.advance_time_and_run(.1)
        self.assertPlayerVarEqual(3, "judgment_day_progress")
        self.assertModeRunning("judgment_day")
        self.hit_and_release_switch("s_pop_target_4")
        self.advance_time_and_run(.5)
        self.assertPlayerVarEqual(1, "t2_complete")
        self.assertPlayerVarEqual("COMPLETE", "chapter")
        self.assertModeNotRunning("judgment_day")
        self.assertModeNotRunning("t2_main")

    def test_down_ball_save(self):
        self.start()
        self.start_judgment_day()
        self.confirm_playfield()
        self.freeway()
        self.confirm_playfield()
        self.mill()
        self.assertPlayerVarEqual(3, "judgment_day_stage")
        self.advance_time_and_run(1)
        balls = self.machine.game.balls_in_play
        self.drain_one_ball()
        self.advance_time_and_run(2)
        self.assertEqual(balls, self.machine.game.balls_in_play)

    def test_resumes_on_next_ball(self):
        self.start()
        self.start_judgment_day()
        self.confirm_playfield()
        self.freeway()
        self.assertPlayerVarEqual(2, "judgment_day_stage")
        self.hit_platform_targets("target_2")
        self.advance_time_and_run(20)
        self.confirm_playfield()
        self.drain_all_balls()
        self.advance_time_and_run(5)
        self.assertBallNumber(2)
        self.assertModeRunning("judgment_day")
        self.assertPlayerVarEqual(2, "judgment_day_stage")
        self.assertPlayerVarEqual(1, "judgment_day_progress")
        self.assertModeNotRunning("future_war_lock")
        self.confirm_playfield()
        self.assertBallsInPlay(4)

    def test_complete_player_has_no_t2_main(self):
        self.start()
        self.player()["t2_complete"] = 1
        self.drain_all_balls()
        self.advance_time_and_run(5)
        self.assertBallNumber(2)
        self.assertModeRunning("base")
        self.assertModeNotRunning("t2_main")
