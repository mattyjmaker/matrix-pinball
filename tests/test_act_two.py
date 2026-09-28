"""Act II rules: docs/14-rules-act-2.md."""
from tests.matrix_test_case import MatrixTestCase


class ActTwoTestCase(MatrixTestCase):

    def start(self):
        self.start_matrix_game(act="II")

    def player(self):
        return self.machine.game.player

    def open_mission(self):
        self.hit_switch_and_run("s_mode_drop", .5)

    def shoot_mission(self, settle=3):
        self.enter_device("s_mode_scoop", settle)

    def start_chapter(self, number):
        self.player()["a2_chapter_next"] = number
        self.open_mission()
        self.shoot_mission()
        self.assertModeRunning(
            {1: "a2_ch1_zion", 2: "a2_ch2_seraph", 3: "a2_ch3_merovingian", 4: "a2_ch4_garage"}[number])

    def ramp(self, name):
        self.hit_and_release_switch("s_{}_ramp".format(name))
        self.advance_time_and_run(.1)

    def tap(self, switch, settle=.1):
        self.hit_and_release_switch(switch)
        self.advance_time_and_run(settle)

    def drop(self, switch, settle=.1):
        """Knock a drop target down; it stays down until its bank or coil resets it."""
        self.hit_switch_and_run(switch, settle)

    def raise_drops(self, *switches):
        for switch in switches:
            self.release_switch_and_run(switch, 0)
        self.advance_time_and_run(.1)

    def drop_bank(self, bank, count):
        switches = ["s_{}_{}".format(bank, n) for n in range(1, count + 1)]
        self.raise_drops(*switches)
        for switch in switches:
            self.drop(switch)
        return switches


class TestStart(ActTwoTestCase):

    def test_act_select_starts_act_two(self):
        self.start()
        self.assertPlayerVarEqual("II", "act")
        self.assertModeRunning("act_two")
        self.assertModeNotRunning("act_one")
        self.assertModeRunning("logos_lock")
        self.assertModeRunning("hunt_gate")
        self.assertModeNotRunning("trinity_lock")
        self.assertModeNotRunning("sentinel_gate")
        self.assertPlayerVarEqual("KNOCK DOWN THE MISSION DROP: ZION", "objective")

    def test_start_mid_ball_after_the_emp(self):
        self.start_matrix_game()
        self.assertModeRunning("act_one")
        self.player()["the_one_stage"] = 4
        self.player()["mb_pending"] = "trinity"
        self.post_event("the_one_emp")
        self.advance_time_and_run(1)
        self.assertPlayerVarEqual("II", "act")
        self.assertModeNotRunning("act_one")
        self.assertModeRunning("act_two")
        self.assertModeRunning("logos_lock")
        # Act I's queue is forfeited with Act I.
        self.assertPlayerVarEqual("", "mb_pending")
        self.assertBallNumber(1)

    def test_intro_waits_for_the_emp_finale(self):
        self.start_matrix_game()
        self.player()["the_one_stage"] = 4
        self.mock_event("act_two_intro")
        self.post_event("the_one_emp")
        self.advance_time_and_run(5)
        self.assertEventNotCalled("act_two_intro")
        self.advance_time_and_run(4)
        self.assertEventCalled("act_two_intro")

    def test_intro_plays_once(self):
        self.mock_event("act_two_intro")
        self.start()
        self.assertEventCalled("act_two_intro", 1)
        self.drain_all_balls()
        self.advance_time_and_run(5)
        self.assertBallNumber(2)
        self.assertModeRunning("act_two")
        self.assertEventCalled("act_two_intro", 1)

    def test_scoop_starts_chapter_one(self):
        self.start()
        self.open_mission()
        self.assertPlayerVarEqual("SHOOT THE MISSION SCOOP: ZION", "objective")
        self.shoot_mission()
        self.assertModeRunning("a2_ch1_zion")
        self.assertEqual(0, self.machine.ball_devices["bd_mode_scoop"].balls)

    def test_scoop_without_drop_only_awards(self):
        self.start()
        self.mock_event("mode_scoop_award")
        self.shoot_mission()
        self.assertEventCalled("mode_scoop_award")
        self.assertModeNotRunning("a2_ch1_zion")


class TestZion(ActTwoTestCase):

    def dock(self):
        self.ramp("right_loop")
        self.tap("s_upper_target_1")

    def test_complete(self):
        self.start()
        self.start_chapter(1)
        # A standup without the ramp first does not dock.
        self.tap("s_upper_target_2")
        self.assertPlayerVarEqual("THE DOCK: REAL WORLD RAMP, THEN A STANDUP", "objective")
        self.dock()
        self.assertPlayerVarEqual("THE TEMPLE: EVERY SWITCH PAYS, RAMPS BUILD, HIT THE DRUMS", "objective")
        for n in (1, 2, 3, 4):
            self.tap("s_pop_target_{}".format(n))
        self.assertPlayerVarEqual("THE TEMPLE: COLLECT AT THE DEJA VU VUK", "objective")
        self.enter_device("s_middle_loop_vuk")
        self.assertModeNotRunning("a2_ch1_zion")
        self.assertPlayerVarEqual(1, "allies_link")
        self.assertPlayerVarEqual(1, "allies_count")
        self.assertPlayerVarEqual(2, "a2_chapter_next")
        self.assertPlayerVarEqual("KNOCK DOWN THE MISSION DROP: THE ORACLE", "objective")

    def test_frenzy_builds_with_ramps(self):
        self.start()
        self.start_chapter(1)
        self.dock()
        before = self.player().score
        self.tap("s_upper_target_3")
        self.assertEqual(5000, self.player().score - before)
        self.ramp("left_lock")
        self.ramp("middle_loop")
        before = self.player().score
        self.tap("s_upper_target_3")
        self.assertEqual(15000, self.player().score - before)

    def test_frenzy_only_in_the_temple(self):
        self.start()
        self.start_chapter(1)
        before = self.player().score
        self.tap("s_upper_target_3")
        self.assertEqual(0, self.player().score - before)

    def test_dock_times_out(self):
        self.start()
        self.start_chapter(1)
        self.mock_event("a2_ch1_failed")
        self.advance_time_and_run(31)
        self.assertEventCalled("a2_ch1_failed")
        self.assertModeNotRunning("a2_ch1_zion")
        self.assertPlayerVarEqual(0, "allies_link")
        self.assertPlayerVarEqual(2, "a2_chapter_next")

    def test_temple_times_out(self):
        self.start()
        self.start_chapter(1)
        self.dock()
        self.advance_time_and_run(31)
        self.assertModeNotRunning("a2_ch1_zion")
        self.assertPlayerVarEqual(0, "allies_link")
        self.assertPlayerVarEqual(2, "a2_chapter_next")


class TestTheOracle(ActTwoTestCase):

    def blows(self, count):
        for i in range(count):
            self.tap("s_platform_gate_{}".format(("left", "right")[i % 2]))

    def test_seraph_beaten_then_the_brawl(self):
        self.start()
        self.start_chapter(2)
        self.blows(6)
        self.assertPlayerVarEqual(1, "a2_seraph_won")
        self.advance_time_and_run(1)
        self.assertModeNotRunning("a2_ch2_seraph")
        self.assertModeRunning("a2_ch2_brawl_mb")
        self.confirm_playfield()
        self.assertBallsInPlay(3)
        # Beaten: every drain is saved for 30 s, not only the first 20 s.
        self.advance_time_and_run(22)
        self.drain_one_ball()
        self.advance_time_and_run(2)
        self.confirm_playfield()
        self.assertBallsInPlay(3)

    def test_same_side_does_not_count(self):
        self.start()
        self.start_chapter(2)
        for _ in range(8):
            self.tap("s_platform_gate_left")
        self.assertPlayerVarEqual(0, "a2_seraph_won")
        self.assertModeRunning("a2_ch2_seraph")

    def test_seraph_times_out_and_the_brawl_still_starts(self):
        self.start()
        self.start_chapter(2)
        self.blows(3)
        self.advance_time_and_run(31)
        self.assertPlayerVarEqual(0, "a2_seraph_won")
        self.assertModeRunning("a2_ch2_brawl_mb")
        self.confirm_playfield()
        # Not beaten: the ordinary 20 s save.
        self.advance_time_and_run(22)
        self.drain_one_ball()
        self.advance_time_and_run(2)
        self.assertBallsInPlay(2)

    def test_smiths_rise_again_and_neo_flies_out(self):
        self.start()
        self.start_chapter(2)
        self.blows(6)
        self.advance_time_and_run(1)
        self.confirm_playfield()
        self.mock_event("a2_brawl_super")
        # Before 12 Smiths the ramp pays nothing special.
        self.ramp("backboard")
        self.assertEventNotCalled("a2_brawl_super")
        for i in range(12):
            switch = "s_popup_{}".format(i % 3 + 1)
            self.hit_switch_and_run(switch, .2)
            self.release_switch_and_run(switch, 1.2)
            # The Smith is back up.
            self.assertFalse(self.machine.drop_targets["popup_{}".format(i % 3 + 1)].complete)
        self.assertPlayerVarEqual(1, "a2_brawl_fly")
        self.ramp("backboard")
        self.assertEventCalled("a2_brawl_super", 1)
        self.assertPlayerVarEqual(1, "allies_seraph")
        # Once only.
        self.ramp("backboard")
        self.assertEventCalled("a2_brawl_super", 1)

    def test_chapter_ends_with_the_brawl(self):
        self.start()
        self.start_chapter(2)
        self.blows(6)
        self.advance_time_and_run(1)
        self.confirm_playfield()
        self.advance_time_and_run(32)
        while self.machine.game.balls_in_play > 1:
            self.drain_one_ball()
            self.advance_time_and_run(2)
        self.advance_time_and_run(1)
        self.assertModeNotRunning("a2_ch2_brawl_mb")
        self.assertPlayerVarEqual(3, "a2_chapter_next")
        self.assertBallNumber(1)

    def test_drain_during_seraph_ends_the_chapter(self):
        self.start()
        self.start_chapter(2)
        self.drain_all_balls()
        self.advance_time_and_run(5)
        self.assertModeNotRunning("a2_ch2_seraph")
        self.assertModeNotRunning("a2_ch2_brawl_mb")
        self.assertPlayerVarEqual(3, "a2_chapter_next")

    def test_brawl_waits_behind_another_multiball_and_dies_with_the_ball(self):
        self.start()
        self.start_chapter(2)
        # The Sentinel Hunt starts during Seraph's test.
        for side in ("left", "right", "left", "right"):
            self.tap("s_platform_gate_{}".format(side))
        self.enter_device("s_platform_vuk")
        self.assertModeRunning("hunt_mb")
        self.confirm_playfield()
        self.advance_time_and_run(31)
        # Seraph's round is over; the Brawl waits.
        self.assertModeRunning("a2_ch2_seraph")
        self.assertModeNotRunning("a2_ch2_brawl_mb")
        self.assertPlayerVarEqual("brawl", "mb_pending")
        # Lose the ball with the Brawl still queued.
        self.drain_all_balls()
        self.advance_time_and_run(5)
        self.assertBallNumber(2)
        self.assertPlayerVarEqual("", "mb_pending")
        self.assertModeNotRunning("a2_ch2_brawl_mb")
        self.assertPlayerVarEqual(3, "a2_chapter_next")


class TestTheMerovingian(ActTwoTestCase):

    def test_all_three_rounds(self):
        self.start()
        self.start_chapter(3)
        for n in (1, 2, 3):
            self.drop("s_three_bank_{}".format(n))
        self.assertPlayerVarEqual("PERSEPHONE: SHOOT THE AGENTS COMING SCOOP", "objective")
        self.enter_device("s_popup_scoop")
        self.assertPlayerVarEqual("THE KEYMAKER: DEJA VU VUK, THEN ANY RAMP", "objective")
        # A ramp before his room does not find him.
        self.ramp("left_lock")
        self.assertPlayerVarEqual(0, "allies_persephone")
        self.enter_device("s_middle_loop_vuk")
        self.ramp("left_lock")
        self.advance_time_and_run(1)
        self.assertModeNotRunning("a2_ch3_merovingian")
        self.assertPlayerVarEqual(1, "allies_persephone")
        self.assertPlayerVarEqual(4, "a2_chapter_next")

    def test_lost_rounds_move_on(self):
        self.start()
        self.start_chapter(3)
        self.advance_time_and_run(31)
        self.assertPlayerVarEqual("PERSEPHONE: SHOOT THE AGENTS COMING SCOOP", "objective")
        self.advance_time_and_run(30)
        self.assertPlayerVarEqual("THE KEYMAKER: DEJA VU VUK, THEN ANY RAMP", "objective")
        self.enter_device("s_middle_loop_vuk")
        self.ramp("right_loop")
        self.assertPlayerVarEqual(1, "allies_persephone")

    def test_keymaker_lost_on_time(self):
        self.start()
        self.start_chapter(3)
        self.advance_time_and_run(61)
        self.mock_event("a2_ch3_keymaker_lost")
        self.advance_time_and_run(21)
        self.assertEventCalled("a2_ch3_keymaker_lost")
        self.assertModeNotRunning("a2_ch3_merovingian")
        self.assertPlayerVarEqual(0, "allies_persephone")
        self.assertPlayerVarEqual(4, "a2_chapter_next")


class TestTheFreeway(ActTwoTestCase):

    def escape_garage(self):
        self.drop_bank("five_bank", 5)
        self.advance_time_and_run(1)

    def test_twins_reset_the_bank(self):
        self.start()
        self.start_chapter(4)
        self.mock_event("five_bank_reset")
        self.advance_time_and_run(8.5)
        self.assertEventCalled("five_bank_reset", 1)
        self.advance_time_and_run(8)
        self.assertEventCalled("five_bank_reset", 2)

    def test_garage_times_out(self):
        self.start()
        self.start_chapter(4)
        self.mock_event("a2_ch4_failed")
        self.advance_time_and_run(31)
        self.assertEventCalled("a2_ch4_failed")
        self.assertModeNotRunning("a2_ch4_garage")
        self.assertModeNotRunning("a2_ch4_freeway_mb")
        self.assertPlayerVarEqual(0, "allies_keymaker")
        self.assertPlayerVarEqual(5, "a2_chapter_next")

    def test_full_freeway(self):
        self.start()
        self.start_chapter(4)
        # No lock in this chapter: the drain save stays on.
        self.assertTrue(self.machine.multiball_locks["outlane_save_lock"].enabled)
        self.escape_garage()
        self.assertModeNotRunning("a2_ch4_garage")
        self.assertModeRunning("a2_ch4_freeway_mb")
        self.confirm_playfield()
        self.assertBallsInPlay(3)
        self.assertPlayerVarEqual("THE TWINS: ALL 5 MATRIX TEAM TARGETS", "objective")

        self.drop_bank("five_bank", 5)
        self.advance_time_and_run(1)
        self.assertPlayerVarEqual("THE DUCATI: TRINITY, DEJA VU AND REAL WORLD RAMPS", "objective")
        self.confirm_playfield()
        self.assertBallsInPlay(4)

        for ramp in ("left_lock", "middle_loop", "right_loop"):
            self.ramp(ramp)
        self.assertPlayerVarEqual("THE TRUCKS: SENTINEL RAMP", "objective")
        self.confirm_playfield()
        self.assertBallsInPlay(5)

        self.ramp("backboard")
        self.assertPlayerVarEqual(1, "allies_keymaker")

    def test_ducati_clock_starts_the_ramps_again(self):
        self.start()
        self.start_chapter(4)
        self.escape_garage()
        self.confirm_playfield()
        self.drop_bank("five_bank", 5)
        self.advance_time_and_run(1)
        self.ramp("left_lock")
        self.ramp("middle_loop")
        self.advance_time_and_run(20)
        # Out of time: the two ramps no longer count.
        self.ramp("right_loop")
        self.assertPlayerVarEqual("THE DUCATI: TRINITY, DEJA VU AND REAL WORLD RAMPS", "objective")
        self.ramp("left_lock")
        self.ramp("middle_loop")
        self.assertPlayerVarEqual("THE TRUCKS: SENTINEL RAMP", "objective")


class TestLogosMultiball(ActTwoTestCase):

    def lock(self):
        for n in (1, 2, 3):
            name = "s_left_lock_{}".format(n)
            if not self.machine.switch_controller.is_active(self.machine.switches[name]):
                self.enter_device(name, 3)
                break
        self.confirm_playfield()

    def start_logos(self):
        for _ in range(3):
            self.lock()
        self.assertModeRunning("logos_mb")
        self.confirm_playfield()

    def test_lock_and_multiball(self):
        self.start()
        self.lock()
        self.assertPlayerVarEqual(1, "balls_locked")
        self.lock()
        self.lock()
        self.assertModeRunning("logos_mb")
        self.assertModeNotRunning("trinity_mb")
        self.assertPlayerVarEqual(0, "balls_locked")
        self.confirm_playfield()
        self.assertBallsInPlay(3)

    def test_jackpot_moves_between_the_left_ramps(self):
        self.start()
        self.start_logos()
        self.mock_event("logos_jackpot")
        self.ramp("left_lock")
        self.assertEventCalled("logos_jackpot", 1)
        # It has moved: the Trinity Ramp again pays nothing.
        self.ramp("left_lock")
        self.assertEventCalled("logos_jackpot", 1)
        self.ramp("middle_loop")
        self.assertEventCalled("logos_jackpot", 2)
        self.ramp("left_lock")
        self.assertEventCalled("logos_jackpot", 3)
        self.assertPlayerVarEqual(1, "allies_niobe")


class TestSentinelHunt(ActTwoTestCase):

    def open_gate(self):
        for side in ("left", "right", "left", "right"):
            self.tap("s_platform_gate_{}".format(side))
        self.advance_time_and_run(.5)

    def test_four_jackpots_and_add_a_ball(self):
        self.start()
        self.enter_device("s_platform_vuk")
        self.assertModeNotRunning("hunt_mb")
        self.open_gate()
        self.assertTrue(self.machine.diverters["platform_gate"].active)
        self.enter_device("s_platform_vuk")
        self.assertModeRunning("hunt_mb")
        self.assertModeNotRunning("sentinel_mb")
        self.confirm_playfield()
        self.assertBallsInPlay(3)
        for target in ("s_platform_gate_left", "s_platform_gate_right", "s_platform_target_1"):
            self.tap(target)
        self.enter_device("s_platform_vuk")
        self.confirm_playfield()
        self.assertBallsInPlay(4)
        # One jackpot so far, from the platform target.
        self.ramp("backboard")
        self.ramp("backboard")
        self.assertPlayerVarEqual(0, "allies_ghost")
        self.ramp("backboard")
        self.assertPlayerVarEqual(1, "allies_ghost")


class TestAllies(ActTwoTestCase):

    EVENTS = {"link": "a2_ch1_completed", "seraph": "a2_ch2_completed", "persephone": "a2_ch3_completed",
              "keymaker": "a2_ch4_completed", "niobe": "logos_mb_completed", "ghost": "hunt_mb_completed"}

    def ally(self, *names):
        for name in names:
            self.post_event(self.EVENTS[name])
        self.advance_time_and_run(.1)

    def test_threshold_is_four(self):
        self.start()
        self.ally("link", "seraph", "persephone")
        self.assertPlayerVarEqual(0, "architect_lit")
        self.ally("ghost")
        self.assertPlayerVarEqual(1, "architect_lit")
        self.assertPlayerVarEqual("KNOCK DOWN THE MISSION DROP: THE ARCHITECT", "objective")

    def test_threshold_setting(self):
        self.machine.settings.set_setting_value("architect_threshold", 6)
        self.start()
        self.ally("link", "seraph", "persephone", "keymaker", "niobe")
        self.assertPlayerVarEqual(0, "architect_lit")
        self.ally("ghost")
        self.assertPlayerVarEqual(1, "architect_lit")

    def test_same_name_counts_once(self):
        self.start()
        self.mock_event("ally_joined")
        self.ally("link", "link")
        self.assertPlayerVarEqual(1, "allies_count")
        self.assertEventCalledWith("ally_joined", ally="link")

    def test_replays_the_first_chapter_not_completed(self):
        self.start()
        self.ally("link")
        self.player()["a2_chapter_next"] = 5
        self.open_mission()
        self.shoot_mission()
        self.assertModeRunning("a2_ch2_seraph")

    def test_act_one_roster_plays_no_part(self):
        self.start()
        self.player()["freed_count"] = 6
        self.ally("link")
        self.assertPlayerVarEqual(0, "architect_lit")


class TestTheArchitect(ActTwoTestCase):

    def start_architect(self):
        for name in ("a2_ch1_completed", "a2_ch2_completed", "a2_ch3_completed", "logos_mb_completed"):
            self.post_event(name)
        self.advance_time_and_run(.1)
        self.assertPlayerVarEqual(1, "architect_lit")
        self.open_mission()
        self.shoot_mission()
        self.assertModeRunning("the_architect")
        self.confirm_playfield()

    def power_plant(self):
        for n in (1, 2, 3, 4):
            self.tap("s_pop_target_{}".format(n))

    def hallway(self):
        self.drop_bank("three_bank", 3)
        self.enter_device("s_middle_loop_vuk")

    def to_the_doors(self):
        self.start_architect()
        self.power_plant()
        self.confirm_playfield()
        self.hallway()
        self.assertPlayerVarEqual(3, "architect_stage")

    def test_features_stand_down(self):
        self.start()
        self.start_architect()
        self.assertModeNotRunning("logos_lock")
        self.assertModeNotRunning("hunt_gate")
        self.assertPlayerVarEqual(1, "architect_stage")
        self.assertBallsInPlay(2)

    def test_power_plant_needs_each_target(self):
        self.start()
        self.start_architect()
        for _ in range(4):
            self.tap("s_pop_target_1")
        self.assertPlayerVarEqual(1, "architect_stage")
        for n in (2, 3, 4):
            self.tap("s_pop_target_{}".format(n))
        self.assertPlayerVarEqual(2, "architect_stage")
        self.confirm_playfield()
        self.assertBallsInPlay(4)

    def test_smiths_close_the_doors(self):
        self.start()
        self.start_architect()
        self.power_plant()
        self.raise_drops("s_three_bank_1", "s_three_bank_2", "s_three_bank_3")
        self.mock_event("three_bank_reset")
        self.drop("s_three_bank_1")
        self.drop("s_three_bank_2")
        self.advance_time_and_run(6.5)
        self.assertEventCalled("three_bank_reset", 1)
        self.assertPlayerVarEqual(0, "architect_progress")
        # Deja Vu VUK does nothing until all three are open.
        self.enter_device("s_middle_loop_vuk")
        self.assertPlayerVarEqual(2, "architect_stage")

    def test_left_door_the_source(self):
        self.start()
        self.to_the_doors()
        self.ramp("middle_loop")
        self.assertPlayerVarEqual("source", "architect_door")
        self.assertPlayerVarEqual(4, "architect_stage")
        self.confirm_playfield()
        self.assertBallsInPlay(6)
        self.mock_event("architect_super_jackpot")
        for ramp in ("left_lock", "middle_loop", "right_loop", "backboard"):
            self.ramp(ramp)
        self.assertEventCalled("architect_super_jackpot", 4)
        self.assertPlayerVarEqual(5, "architect_stage")
        self.assertTrue(self.machine.diverters["platform_gate"].active)
        self.enter_device("s_platform_vuk")
        self.assertPlayerVarEqual("III", "act")
        self.assertModeNotRunning("the_architect")
        self.assertModeNotRunning("act_two")
        self.assertModeRunning("base")

    def test_source_times_out_to_the_last_stage(self):
        self.start()
        self.to_the_doors()
        self.ramp("left_lock")
        self.advance_time_and_run(31)
        self.assertPlayerVarEqual(5, "architect_stage")

    def test_right_door_trinity(self):
        self.start()
        self.to_the_doors()
        self.ramp("backboard")
        self.assertPlayerVarEqual("trinity", "architect_door")
        self.assertPlayerVarEqual(4, "architect_stage")
        # The magnet does nothing before Neo flies.
        self.tap("s_platform_magnet")
        self.assertPlayerVarEqual(4, "architect_stage")
        self.advance_time_and_run(10)
        self.ramp("right_loop")
        before = self.player().score
        self.tap("s_platform_magnet")
        self.advance_time_and_run(2.5)
        # About 30 s left of 40: close to 1,000,000 + 30 x 100,000.
        gained = self.player().score - before
        self.assertGreaterEqual(gained, 1000000 + 29 * 100000)
        self.assertLessEqual(gained, 1000000 + 31 * 100000)
        self.assertPlayerVarEqual(5, "architect_stage")
        self.enter_device("s_platform_vuk")
        self.assertPlayerVarEqual("III", "act")

    def test_trinity_value_holds_at_its_floor(self):
        self.start()
        self.to_the_doors()
        self.ramp("right_loop")
        self.advance_time_and_run(60)
        self.assertPlayerVarEqual(4, "architect_stage")
        self.assertPlayerVarEqual(1000000, "architect_value")
        self.ramp("right_loop")
        self.tap("s_platform_magnet")
        self.advance_time_and_run(2.5)
        self.assertPlayerVarEqual(5, "architect_stage")

    def test_no_choice_is_the_right_door(self):
        self.start()
        self.to_the_doors()
        self.advance_time_and_run(16)
        self.assertPlayerVarEqual("trinity", "architect_door")
        self.assertPlayerVarEqual(4, "architect_stage")

    def test_resumes_on_next_ball(self):
        self.start()
        self.start_architect()
        self.power_plant()
        self.assertPlayerVarEqual(2, "architect_stage")
        self.advance_time_and_run(20)
        self.confirm_playfield()
        self.drain_all_balls()
        self.advance_time_and_run(5)
        self.assertBallNumber(2)
        self.assertModeRunning("the_architect")
        self.assertModeNotRunning("logos_lock")
        self.assertPlayerVarEqual(2, "architect_stage")
        self.confirm_playfield()
        self.assertBallsInPlay(4)

    def test_resumed_door_keeps_its_choice(self):
        self.start()
        self.to_the_doors()
        self.ramp("left_lock")
        self.advance_time_and_run(35)
        self.player()["architect_stage"] = 4
        self.confirm_playfield()
        self.drain_all_balls()
        self.advance_time_and_run(5)
        self.assertBallNumber(2)
        self.assertPlayerVarEqual("source", "architect_door")
        self.confirm_playfield()
        self.assertBallsInPlay(6)
