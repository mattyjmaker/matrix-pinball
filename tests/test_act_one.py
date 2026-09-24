from tests.matrix_test_case import MatrixTestCase


class ActOneTestCase(MatrixTestCase):

    def start(self):
        self.start_matrix_game()

    def player(self):
        return self.machine.game.player

    def open_mission(self):
        self.hit_switch_and_run("s_mission_drop", .5)

    def shoot_mission(self, settle=3):
        self.enter_device("s_mission_scoop", settle)

    def start_chapter(self, number):
        self.player()["chapter_next"] = number
        self.open_mission()
        self.shoot_mission()
        self.assertModeRunning(
            {1: "ch1_trinity_escape", 2: "ch2_red_pill", 3: "ch3_construct", 4: "ch4_rescue_lock"}[number])

    def ramp(self, name):
        self.hit_and_release_switch("s_{}_ramp".format(name))
        self.advance_time_and_run(.1)


class TestController(ActOneTestCase):

    def test_act_one_and_features_start(self):
        self.start()
        self.assertModeRunning("act_one")
        self.assertModeRunning("trinity_lock")
        self.assertModeRunning("sentinel_gate")
        self.assertPlayerVarEqual("I", "act")
        self.assertPlayerVarEqual("KNOCK DOWN THE MISSION DROP: TRINITY'S ESCAPE", "objective")

    def test_mission_drop_lights_scoop(self):
        self.start()
        self.open_mission()
        self.assertPlayerVarEqual(1, "mission_ready")
        self.assertPlayerVarEqual("SHOOT THE MISSION SCOOP: TRINITY'S ESCAPE", "objective")

    def test_scoop_without_drop_down_only_awards(self):
        self.start()
        self.mock_event("mission_scoop_award")
        self.shoot_mission()
        self.assertEventCalled("mission_scoop_award")
        self.assertModeNotRunning("ch1_trinity_escape")
        self.assertEqual(0, self.machine.ball_devices["bd_mission_scoop"].balls)

    def test_scoop_starts_chapter_one_and_resets_drop(self):
        self.start()
        self.mock_event("mission_drop_reset")
        self.open_mission()
        self.shoot_mission()
        self.assertModeRunning("ch1_trinity_escape")
        self.assertEventCalled("mission_drop_reset")
        self.assertPlayerVarEqual(0, "mission_ready")
        # The ball is released after the intro.
        self.assertEqual(0, self.machine.ball_devices["bd_mission_scoop"].balls)


class TestChapterOne(ActOneTestCase):

    def test_complete(self):
        self.start()
        self.start_chapter(1)
        for ramp in ("trinity", "dejavu", "real_world"):
            self.ramp(ramp)
        self.assertPlayerVarEqual("THE PHONE: SHOOT THE DEJA VU VUK", "objective")
        self.enter_device("s_dejavu_vuk")
        self.assertModeNotRunning("ch1_trinity_escape")
        self.assertPlayerVarEqual(1, "freed_trinity")
        self.assertPlayerVarEqual(1, "freed_count")
        self.assertPlayerVarEqual(2, "chapter_next")
        self.assertPlayerVarEqual("KNOCK DOWN THE MISSION DROP: RED PILL", "objective")

    def test_truck_wins_when_rooftops_run_out(self):
        self.start()
        self.start_chapter(1)
        self.ramp("trinity")
        self.advance_time_and_run(41)
        self.assertModeNotRunning("ch1_trinity_escape")
        self.assertPlayerVarEqual(0, "freed_trinity")
        # Played, so the story moves on.
        self.assertPlayerVarEqual(2, "chapter_next")

    def test_phone_value_counts_down(self):
        self.start()
        self.start_chapter(1)
        for ramp in ("trinity", "dejavu", "real_world"):
            self.ramp(ramp)
        before = self.player().score
        self.advance_time_and_run(10)
        self.enter_device("s_dejavu_vuk")
        gained = self.player().score - before
        # 250k base plus 25k per second left; the VUK's own 2,570 and the
        # crew award ride on top. About 10 s remain.
        self.assertGreater(gained, 250000 + 8 * 25000)
        self.assertLess(gained, 250000 + 12 * 25000 + 2570 + 250000 + 1)

    def test_ball_drain_ends_chapter_as_played(self):
        self.start()
        self.start_chapter(1)
        self.drain_all_balls()
        self.advance_time_and_run(5)
        self.assertModeNotRunning("ch1_trinity_escape")
        self.assertPlayerVarEqual(2, "chapter_next")


class TestChapterTwo(ActOneTestCase):

    def test_ball_held_through_choice(self):
        self.start()
        self.start_chapter(2)
        self.advance_time_and_run(5)
        self.assertEqual(1, self.machine.ball_devices["bd_mission_scoop"].balls)

    def test_blue_pill_ends_chapter(self):
        self.start()
        self.start_chapter(2)
        self.hit_and_release_switch("s_left_flipper")
        self.advance_time_and_run(3)
        self.assertModeNotRunning("ch2_red_pill")
        self.assertModeNotRunning("ch2_unplugged")
        self.assertEqual(0, self.machine.ball_devices["bd_mission_scoop"].balls)
        self.assertPlayerVarEqual(0, "freed_apoc")
        self.assertPlayerVarEqual(3, "chapter_next")

    def test_no_choice_means_red(self):
        self.start()
        self.start_chapter(2)
        self.advance_time_and_run(11)
        self.assertModeRunning("ch2_unplugged")

    def test_red_pill_unplugged_multiball_and_super_jackpot(self):
        self.start()
        self.start_chapter(2)
        self.hit_and_release_switch("s_right_flipper")
        self.advance_time_and_run(3)
        self.assertModeNotRunning("ch2_red_pill")
        self.assertModeRunning("ch2_unplugged")
        self.confirm_playfield()
        self.assertBallsInPlay(3)
        for n in (1, 2, 3):
            self.hit_and_release_switch("s_real_world_{}".format(n))
        self.advance_time_and_run(.5)
        self.assertPlayerVarEqual(1, "freed_apoc")
        # Chapter 2 ends when the multiball does.
        self.advance_time_and_run(25)
        self.drain_one_ball()
        self.drain_one_ball()
        self.advance_time_and_run(3)
        self.assertModeNotRunning("ch2_unplugged")
        self.assertPlayerVarEqual(3, "chapter_next")
        self.assertBallNumber(1)


class TestChapterThree(ActOneTestCase):

    def drop_team(self):
        for n in range(1, 6):
            self.hit_switch_and_run("s_team_{}".format(n), .1)

    def spar(self, combos):
        sides = ["trinity", "real_world"]
        for i in range(combos + 1):
            self.ramp(sides[i % 2])

    def test_win_rounds_one_and_two(self):
        self.start()
        self.start_chapter(3)
        self.drop_team()
        self.assertPlayerVarEqual(1, "ch3_won_kung_fu")
        self.assertPlayerVarEqual("SPARRING: ALTERNATE LEFT AND RIGHT SHOTS", "objective")
        self.spar(4)
        self.assertPlayerVarEqual(1, "ch3_won_sparring")
        self.assertPlayerVarEqual("JUMP PROGRAM: REAL WORLD RAMP, THEN A STANDUP", "objective")
        self.ramp("real_world")
        self.mock_event("ch3_jump_made")
        self.hit_and_release_switch("s_real_world_1")
        self.advance_time_and_run(1)
        self.assertEventCalled("ch3_jump_made")
        self.assertModeNotRunning("ch3_construct")
        self.assertPlayerVarEqual(1, "freed_mouse")
        self.assertPlayerVarEqual(4, "chapter_next")

    def test_missed_jump_still_counts(self):
        self.start()
        self.start_chapter(3)
        self.drop_team()
        self.spar(4)
        self.mock_event("ch3_jump_missed")
        self.advance_time_and_run(21)
        self.assertEventCalled("ch3_jump_missed")
        self.assertModeNotRunning("ch3_construct")
        self.assertPlayerVarEqual(1, "freed_mouse")

    def test_losing_kung_fu_means_no_mouse(self):
        self.start()
        self.start_chapter(3)
        self.advance_time_and_run(31)
        self.assertPlayerVarEqual("SPARRING: ALTERNATE LEFT AND RIGHT SHOTS", "objective")
        self.spar(4)
        self.advance_time_and_run(21)
        self.assertModeNotRunning("ch3_construct")
        self.assertPlayerVarEqual(0, "freed_mouse")
        self.assertPlayerVarEqual(4, "chapter_next")

    def test_same_side_is_not_a_combo(self):
        self.start()
        self.start_chapter(3)
        self.drop_team()
        for _ in range(6):
            self.ramp("trinity")
        self.assertPlayerVarEqual(0, "ch3_won_sparring")

    def test_woman_in_the_red_dress(self):
        self.start()
        self.start_chapter(3)
        self.drop_team()
        # She starts on the Trinity Ramp.
        self.mock_event("ch3_woman_bonus")
        self.ramp("trinity")
        self.assertPlayerVarEqual(1, "ch3_agent_armed")
        self.hit_switch_and_run("s_agent_2", .5)
        self.assertEventCalled("ch3_woman_bonus")

    def test_woman_walks(self):
        self.start()
        self.start_chapter(3)
        self.drop_team()
        self.advance_time_and_run(3.5)
        # Moved on from the Trinity Ramp, so it no longer arms an Agent.
        self.ramp("trinity")
        self.assertPlayerVarEqual(0, "ch3_agent_armed")


class TestChapterFour(ActOneTestCase):

    def lock_three(self):
        for _ in range(3):
            self.enter_device("s_ammo_lock", 3)
            self.confirm_playfield()

    def test_full_rescue(self):
        self.start()
        self.start_chapter(4)
        self.assertPlayerVarEqual("DEJA VU: SHOOT THE DEJA VU VUK", "objective")
        # The Ammo Lock is Morpheus's lock now, not the drain save.
        self.assertFalse(self.machine.multiball_locks["ammo_save_lock"].enabled)
        self.enter_device("s_dejavu_vuk")
        self.assertPlayerVarEqual("GUNS. LOTS OF GUNS: LOCK 3 AT THE AMMO LOCK", "objective")
        self.lock_three()
        self.assertModeRunning("ch4_rescue_mb")
        self.assertModeNotRunning("ch4_rescue_lock")
        self.assertBallsInPlay(3)
        self.assertPlayerVarEqual("LOBBY: HIT EVERY GUARD", "objective")

        for n in (1, 2, 3, 4):
            self.hit_and_release_switch("s_emp_target_{}".format(n))
        for n in (1, 2, 3):
            self.hit_switch_and_run("s_agent_{}".format(n), .1)
        self.advance_time_and_run(1)
        self.assertPlayerVarEqual("ROOFTOP: TRINITY RAMP, THEN HIT AN AGENT", "objective")
        self.assertBallsInPlay(4)

        # Agents are raised for the rooftop. Release their switches.
        for n in (1, 2, 3):
            self.release_switch_and_run("s_agent_{}".format(n), .1)
        self.ramp("trinity")
        self.hit_switch_and_run("s_agent_1", .5)
        self.assertPlayerVarEqual("HELICOPTER: CATCH MORPHEUS AT THE SENTINEL MAGNET", "objective")
        self.assertBallsInPlay(5)

        self.hit_and_release_switch("s_sentinel_magnet")
        self.advance_time_and_run(1)
        self.assertPlayerVarEqual(1, "freed_tank")

    def test_agent_without_dodge_does_not_advance(self):
        self.start()
        self.start_chapter(4)
        self.enter_device("s_dejavu_vuk")
        self.lock_three()
        for n in (1, 2, 3, 4):
            self.hit_and_release_switch("s_emp_target_{}".format(n))
        for n in (1, 2, 3):
            self.hit_switch_and_run("s_agent_{}".format(n), .1)
        self.advance_time_and_run(1)
        for n in (1, 2, 3):
            self.release_switch_and_run("s_agent_{}".format(n), .1)
        self.hit_switch_and_run("s_agent_1", .5)
        self.assertPlayerVarEqual("ROOFTOP: TRINITY RAMP, THEN HIT AN AGENT", "objective")

    def test_lock_phase_drain_ends_chapter(self):
        self.start()
        self.start_chapter(4)
        self.enter_device("s_dejavu_vuk")
        self.drain_all_balls()
        self.advance_time_and_run(5)
        self.assertModeNotRunning("ch4_rescue_lock")
        self.assertPlayerVarEqual(5, "chapter_next")
        # The drain save lock is back for the next ball.
        self.assertTrue(self.machine.multiball_locks["ammo_save_lock"].enabled)


class TestTrinityMultiball(ActOneTestCase):

    def lock(self):
        # Balls stack in the lock: the new one lands on the next free switch.
        for n in (1, 2, 3):
            name = "s_trinity_lock_{}".format(n)
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
        self.assertModeRunning("trinity_mb")
        self.assertPlayerVarEqual(0, "balls_locked")
        self.confirm_playfield()
        self.assertBallsInPlay(3)
        for _ in range(3):
            self.ramp("trinity")
        self.assertPlayerVarEqual(1, "freed_switch")

    def test_chapter_blocked_during_multiball(self):
        self.start()
        for _ in range(3):
            self.lock()
        self.assertModeRunning("trinity_mb")
        self.open_mission()
        self.mock_event("mission_scoop_award")
        self.shoot_mission()
        self.assertEventCalled("mission_scoop_award")
        self.assertModeNotRunning("ch1_trinity_escape")

    def test_queued_behind_sentinel(self):
        self.start()
        for _ in range(4):
            self.hit_and_release_switch("s_sentinel_left")
        self.advance_time_and_run(.5)
        self.enter_device("s_sentinel_vuk")
        self.assertModeRunning("sentinel_mb")
        self.confirm_playfield()
        # Trinity lock fills during Sentinel Multiball: it waits.
        for _ in range(3):
            self.lock()
        self.assertModeNotRunning("trinity_mb")
        self.assertPlayerVarEqual("trinity", "mb_pending")
        # Sentinel Multiball ends; Trinity starts.
        self.advance_time_and_run(25)
        self.drain_one_ball()
        self.advance_time_and_run(2)
        self.drain_one_ball()
        self.advance_time_and_run(3)
        self.assertModeNotRunning("sentinel_mb")
        self.assertModeRunning("trinity_mb")
        self.assertPlayerVarEqual("", "mb_pending")


class TestSentinelMultiball(ActOneTestCase):

    def open_gate(self):
        for side in ("left", "right", "left", "right"):
            self.hit_and_release_switch("s_sentinel_{}".format(side))
        self.advance_time_and_run(.5)

    def test_gate_needs_four_hits(self):
        self.start()
        self.enter_device("s_sentinel_vuk")
        self.assertModeNotRunning("sentinel_mb")
        self.open_gate()
        self.assertTrue(self.machine.diverters["sentinel_gate"].active)
        self.enter_device("s_sentinel_vuk")
        self.assertModeRunning("sentinel_mb")

    def test_add_a_ball_once_and_completion(self):
        self.start()
        self.open_gate()
        self.enter_device("s_sentinel_vuk")
        self.confirm_playfield()
        self.assertBallsInPlay(3)
        for target in ("left", "right", "boss"):
            self.hit_and_release_switch("s_sentinel_{}".format(target))
        self.advance_time_and_run(.5)
        self.assertPlayerVarEqual(1, "sentinel_aab_lit")
        self.enter_device("s_sentinel_vuk")
        self.confirm_playfield()
        self.assertBallsInPlay(4)
        # Not again this multiball.
        for target in ("left", "right", "boss"):
            self.hit_and_release_switch("s_sentinel_{}".format(target))
        self.advance_time_and_run(.5)
        self.enter_device("s_sentinel_vuk")
        self.confirm_playfield()
        self.assertBallsInPlay(4)
        # The boss target is a jackpot: three have been scored with the ramp.
        self.ramp("sentinel")
        self.assertPlayerVarEqual(1, "freed_dozer")

    def test_gate_closes_when_multiball_ends(self):
        self.start()
        self.open_gate()
        self.enter_device("s_sentinel_vuk")
        self.confirm_playfield()
        self.advance_time_and_run(25)
        while self.machine.game.balls_in_play > 1:
            self.drain_one_ball()
            self.advance_time_and_run(2)
        self.advance_time_and_run(1)
        self.assertModeNotRunning("sentinel_mb")
        self.assertFalse(self.machine.diverters["sentinel_gate"].active)


class TestTheOne(ActOneTestCase):

    def free(self, *names):
        events = {"trinity": "ch1_completed", "apoc": "ch2_completed", "mouse": "ch3_completed",
                  "tank": "ch4_completed", "switch": "trinity_mb_completed", "dozer": "sentinel_mb_completed"}
        for name in names:
            self.post_event(events[name])
        self.advance_time_and_run(.1)

    def light_the_one(self):
        self.free("trinity", "apoc", "mouse", "switch")
        self.assertPlayerVarEqual(1, "the_one_lit")

    def start_the_one(self):
        self.light_the_one()
        self.open_mission()
        self.shoot_mission()
        self.assertModeRunning("the_one")

    def beat_smith(self):
        for _ in range(6):
            n = 1
            for n in (1, 2, 3):
                if not self.machine.switch_controller.is_active(self.machine.switches["s_agent_{}".format(n)]):
                    break
            self.hit_switch_and_run("s_agent_{}".format(n), .2)
            self.release_switch_and_run("s_agent_{}".format(n), 1.2)

    def reach_phones(self, count):
        for _ in range(count):
            phone = self.machine.game.player["the_one_phone"]
            self.ramp(phone[:-len("_ramp")])

    def test_threshold_is_four(self):
        self.start()
        self.free("trinity", "apoc", "mouse")
        self.assertPlayerVarEqual(0, "the_one_lit")
        self.free("dozer")
        self.assertPlayerVarEqual(1, "the_one_lit")
        self.assertPlayerVarEqual("KNOCK DOWN THE MISSION DROP: THE ONE", "objective")

    def test_threshold_setting(self):
        self.machine.settings.set_setting_value("the_one_threshold", 6)
        self.start()
        self.free("trinity", "apoc", "mouse", "switch", "dozer")
        self.assertPlayerVarEqual(0, "the_one_lit")
        self.free("tank")
        self.assertPlayerVarEqual(1, "the_one_lit")

    def test_same_name_counts_once(self):
        self.start()
        self.free("trinity", "trinity")
        self.assertPlayerVarEqual(1, "freed_count")

    def test_scoop_prefers_the_one_over_a_chapter(self):
        self.start()
        self.start_the_one()
        self.assertModeNotRunning("ch1_trinity_escape")
        # Chapters and the standalone multiballs stand down.
        self.assertModeNotRunning("trinity_lock")
        self.assertModeNotRunning("sentinel_gate")
        self.assertPlayerVarEqual(1, "the_one_stage")
        self.confirm_playfield()
        self.assertBallsInPlay(2)

    def test_all_stages_to_act_two(self):
        self.start()
        self.start_the_one()
        self.confirm_playfield()
        self.beat_smith()
        self.assertPlayerVarEqual(2, "the_one_stage")
        self.confirm_playfield()
        self.assertBallsInPlay(4)

        self.reach_phones(2)
        self.confirm_playfield()
        self.assertBallsInPlay(6)
        self.reach_phones(2)
        self.assertPlayerVarEqual(3, "the_one_stage")

        # Dark: ramps pay nothing.
        self.mock_event("the_one_super_jackpot")
        self.ramp("trinity")
        self.assertEventNotCalled("the_one_super_jackpot")
        self.advance_time_and_run(5)
        for _ in range(3):
            self.ramp("dejavu")
        self.assertEventCalled("the_one_super_jackpot", 3)
        self.assertPlayerVarEqual(4, "the_one_stage")
        self.assertTrue(self.machine.diverters["sentinel_gate"].active)

        self.enter_device("s_sentinel_vuk")
        self.assertPlayerVarEqual("II", "act")
        self.assertModeNotRunning("the_one")
        self.assertModeNotRunning("act_one")

    def test_chase_timer_moves_to_room_303(self):
        self.start()
        self.start_the_one()
        self.confirm_playfield()
        self.beat_smith()
        self.advance_time_and_run(61)
        self.assertPlayerVarEqual(3, "the_one_stage")

    def test_dark_ball_save(self):
        self.start()
        self.start_the_one()
        self.confirm_playfield()
        self.beat_smith()
        self.confirm_playfield()
        self.reach_phones(4)
        self.assertPlayerVarEqual(3, "the_one_stage")
        self.advance_time_and_run(1)
        balls = self.machine.game.balls_in_play
        self.drain_one_ball()
        self.advance_time_and_run(2)
        self.assertEqual(balls, self.machine.game.balls_in_play)

    def test_resumes_on_next_ball(self):
        self.start()
        self.start_the_one()
        self.confirm_playfield()
        self.beat_smith()
        self.assertPlayerVarEqual(2, "the_one_stage")
        self.reach_phones(1)
        # Lose every ball after the ball saves run out.
        self.advance_time_and_run(20)
        self.confirm_playfield()
        self.drain_all_balls()
        self.advance_time_and_run(5)
        self.assertBallNumber(2)
        self.assertModeRunning("the_one")
        self.assertPlayerVarEqual(2, "the_one_stage")
        self.assertPlayerVarEqual(1, "the_one_progress")
        self.assertModeNotRunning("trinity_lock")
        self.confirm_playfield()
        self.assertBallsInPlay(4)

    def test_gate_reopens_on_resume(self):
        self.start()
        self.start_the_one()
        self.player()["the_one_stage"] = 4
        self.advance_time_and_run(20)
        self.confirm_playfield()
        self.drain_all_balls()
        self.advance_time_and_run(5)
        self.assertBallNumber(2)
        self.assertModeRunning("the_one")
        self.assertTrue(self.machine.diverters["sentinel_gate"].active)
        self.enter_device("s_sentinel_vuk")
        self.assertPlayerVarEqual("II", "act")

    def test_act_two_has_no_act_one(self):
        self.start()
        self.player()["act"] = "II"
        self.drain_all_balls()
        self.advance_time_and_run(5)
        self.assertBallNumber(2)
        self.assertModeRunning("base")
        self.assertModeNotRunning("act_one")

