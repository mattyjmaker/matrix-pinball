"""Act III rules: docs/15-rules-act-3.md."""
from tests.test_act_two import ActTwoTestCase


class ActThreeTestCase(ActTwoTestCase):

    def start(self):
        self.start_matrix_game(act="III")

    def start_chapter(self, number):
        self.player()["a3_chapter_next"] = number
        self.open_mission()
        self.shoot_mission()
        self.assertModeRunning(
            {1: "a3_ch1_mobil_ave", 2: "a3_ch2_club_hel", 3: "a3_ch3_siege_mb", 4: "a3_ch4_hammer"}[number])

    def spin(self, count):
        for _ in range(count):
            self.tap("s_left_lock_spinner", .05)


class TestStart(ActThreeTestCase):

    def test_act_select_starts_act_three(self):
        self.mock_event("act_three_intro")
        self.start()
        self.assertPlayerVarEqual("III", "act")
        self.assertModeRunning("act_three")
        self.assertModeNotRunning("act_two")
        self.assertModeNotRunning("act_one")
        self.assertModeRunning("apu_lock")
        self.assertModeRunning("swarm_gate")
        self.assertModeNotRunning("logos_lock")
        self.assertModeNotRunning("hunt_gate")
        self.assertEventCalled("act_three_intro")
        self.assertPlayerVarEqual("KNOCK DOWN THE MISSION DROP: MOBIL AVENUE", "objective")

    def test_start_mid_ball_after_the_architect(self):
        self.start_matrix_game(act="II")
        self.player()["architect_stage"] = 5
        self.player()["mb_pending"] = "logos"
        self.mock_event("act_three_intro")
        self.post_event("architect_sentinels_stopped")
        self.advance_time_and_run(1)
        self.assertPlayerVarEqual("III", "act")
        self.assertModeNotRunning("act_two")
        self.assertModeRunning("act_three")
        self.assertPlayerVarEqual("", "mb_pending")
        self.assertBallNumber(1)
        # The intro waits for Act II's finale.
        self.assertEventNotCalled("act_three_intro")
        self.advance_time_and_run(8)
        self.assertEventCalled("act_three_intro")


class TestMobilAvenue(ActThreeTestCase):

    def test_complete(self):
        self.start()
        self.start_chapter(1)
        self.spin(24)
        self.assertPlayerVarEqual("THE TUNNEL: 25 SPINNER SPINS", "objective")
        self.spin(1)
        self.assertPlayerVarEqual("THE TRAIN: BOARD IT ON THE REAL WORLD RAMP", "objective")
        before = self.player().score
        self.advance_time_and_run(5)
        self.ramp("right_loop")
        self.advance_time_and_run(.5)
        # 300k plus 25k per second left (about 15), the defender award on top.
        gained = self.player().score - before
        self.assertGreaterEqual(gained, 300000 + 14 * 25000 + 250000)
        self.assertLessEqual(gained, 300000 + 16 * 25000 + 250000 + 1000)
        self.assertModeNotRunning("a3_ch1_mobil_ave")
        self.assertPlayerVarEqual(1, "defenders_sati")
        self.assertPlayerVarEqual(2, "a3_chapter_next")
        self.assertPlayerVarEqual("KNOCK DOWN THE MISSION DROP: CLUB HEL", "objective")

    def test_ramp_before_the_train_does_not_board(self):
        self.start()
        self.start_chapter(1)
        self.ramp("right_loop")
        self.assertModeRunning("a3_ch1_mobil_ave")
        self.assertPlayerVarEqual(0, "defenders_sati")

    def test_tunnel_times_out(self):
        self.start()
        self.start_chapter(1)
        self.mock_event("a3_ch1_failed")
        self.advance_time_and_run(31)
        self.assertEventCalled("a3_ch1_failed")
        self.assertModeNotRunning("a3_ch1_mobil_ave")
        self.assertPlayerVarEqual(0, "defenders_sati")
        self.assertPlayerVarEqual(2, "a3_chapter_next")

    def test_train_leaves(self):
        self.start()
        self.start_chapter(1)
        self.spin(25)
        self.advance_time_and_run(21)
        self.assertModeNotRunning("a3_ch1_mobil_ave")
        self.assertPlayerVarEqual(0, "defenders_sati")


class TestClubHel(ActThreeTestCase):

    def agents_down(self):
        for n in (1, 2, 3):
            self.knock_down_popup(n)
        self.advance_time_and_run(.5)

    def test_all_three_rounds(self):
        self.start()
        self.start_chapter(2)
        self.agents_down()
        self.assertPlayerVarEqual("THE CEILING: ALL THREE REAL WORLD TARGETS", "objective")
        for n in (1, 2, 3):
            self.tap("s_upper_target_{}".format(n))
        self.assertPlayerVarEqual("THE STANDOFF: BOTH ENTRANCE AND BOTH BOSS TARGETS", "objective")
        for switch in ("s_platform_gate_left", "s_platform_gate_right", "s_platform_target_1"):
            self.tap(switch)
        self.assertPlayerVarEqual(0, "defenders_lock")
        self.tap("s_platform_target_2")
        self.advance_time_and_run(1)
        self.assertModeNotRunning("a3_ch2_club_hel")
        self.assertPlayerVarEqual(1, "defenders_lock")
        self.assertPlayerVarEqual(3, "a3_chapter_next")

    def test_lost_rounds_move_on_and_the_standoff_has_a_clock(self):
        self.start()
        self.start_chapter(2)
        self.advance_time_and_run(31)
        self.assertPlayerVarEqual("THE CEILING: ALL THREE REAL WORLD TARGETS", "objective")
        self.advance_time_and_run(31)
        self.assertPlayerVarEqual("THE STANDOFF: BOTH ENTRANCE AND BOTH BOSS TARGETS", "objective")
        self.mock_event("a3_ch2_standoff_lost")
        self.advance_time_and_run(21)
        self.assertEventCalled("a3_ch2_standoff_lost")
        self.assertModeNotRunning("a3_ch2_club_hel")
        self.assertPlayerVarEqual(0, "defenders_lock")
        self.assertPlayerVarEqual(3, "a3_chapter_next")


class TestSiege(ActThreeTestCase):

    def test_three_stages(self):
        self.start()
        self.start_chapter(3)
        self.confirm_playfield()
        self.assertBallsInPlay(3)
        # The chapter is the multiball: the scoop starts nothing else.
        self.assertModeRunning("a3_ch3_siege_mb")
        for i in range(10):
            self.tap(("s_platform_gate_left", "s_platform_target_1")[i % 2])
        self.assertPlayerVarEqual("THE GATE: ALL THREE THREE-BANK TARGETS", "objective")
        self.confirm_playfield()
        self.assertBallsInPlay(4)
        self.drop_bank("three_bank", 3)
        self.advance_time_and_run(.5)
        self.assertPlayerVarEqual("MIFUNE'S LAST STAND: SENTINEL RAMP", "objective")
        self.confirm_playfield()
        self.assertBallsInPlay(5)
        self.ramp("backboard")
        self.assertPlayerVarEqual(1, "defenders_mifune")

    def test_chapter_ends_with_the_multiball(self):
        self.start()
        self.start_chapter(3)
        self.confirm_playfield()
        self.advance_time_and_run(22)
        while self.machine.game.balls_in_play > 1:
            self.drain_one_ball()
            self.advance_time_and_run(2)
        self.advance_time_and_run(1)
        self.assertModeNotRunning("a3_ch3_siege_mb")
        self.assertPlayerVarEqual(4, "a3_chapter_next")
        self.assertBallNumber(1)

    def test_a_lock_during_the_siege_waits(self):
        self.start()
        self.start_chapter(3)
        self.confirm_playfield()
        self.post_event("request_apu_mb", .5)
        self.assertModeNotRunning("apu_mb")
        self.assertPlayerVarEqual("apu", "mb_pending")


class TestTheHammer(ActThreeTestCase):

    def test_complete(self):
        self.start()
        self.start_chapter(4)
        # Out of order does not count.
        self.ramp("middle_loop")
        self.ramp("left_lock")
        self.ramp("right_loop")
        self.assertPlayerVarEqual("THE TUNNELS: TRINITY, DEJA VU, REAL WORLD, SENTINEL RAMPS IN ORDER",
                                  "objective")
        for ramp in ("middle_loop", "right_loop", "backboard"):
            self.ramp(ramp)
        self.assertPlayerVarEqual("THE EMP: SHOOT THE DEJA VU VUK", "objective")
        self.enter_device("s_middle_loop_vuk")
        self.assertModeNotRunning("a3_ch4_hammer")
        self.assertPlayerVarEqual(1, "defenders_roland")
        self.assertPlayerVarEqual(5, "a3_chapter_next")

    def test_emp_times_out(self):
        self.start()
        self.start_chapter(4)
        for ramp in ("left_lock", "middle_loop", "right_loop", "backboard"):
            self.ramp(ramp)
        self.mock_event("a3_ch4_failed")
        self.advance_time_and_run(16)
        self.assertEventCalled("a3_ch4_failed")
        self.assertModeNotRunning("a3_ch4_hammer")
        self.assertPlayerVarEqual(0, "defenders_roland")


class TestApuCorps(ActThreeTestCase):

    def lock(self):
        for n in (1, 2, 3):
            name = "s_left_lock_{}".format(n)
            if not self.machine.switch_controller.is_active(self.machine.switches[name]):
                self.enter_device(name, 3)
                break
        self.confirm_playfield()

    def test_rising_jackpots(self):
        self.start()
        for _ in range(3):
            self.lock()
        self.assertModeRunning("apu_mb")
        self.assertModeNotRunning("logos_mb")
        self.confirm_playfield()
        self.assertBallsInPlay(3)
        gains = []
        for _ in range(3):
            before = self.player().score
            self.ramp("left_lock")
            self.advance_time_and_run(.1)
            gains.append(self.player().score - before)
        # 150k, 200k, 250k; the third also adds ZEE (250k).
        self.assertEqual(150000, gains[0])
        self.assertEqual(200000, gains[1])
        self.assertEqual(250000 + 250000, gains[2])
        self.assertPlayerVarEqual(1, "defenders_zee")


class TestSentinelSwarm(ActThreeTestCase):

    def test_gate_needs_six_hits(self):
        self.start()
        for side in ("left", "right", "left", "right"):
            self.tap("s_platform_gate_{}".format(side))
        self.enter_device("s_platform_vuk")
        self.assertModeNotRunning("swarm_mb")
        self.tap("s_platform_gate_left")
        self.tap("s_platform_gate_right")
        self.assertTrue(self.machine.diverters["platform_gate"].active)
        self.enter_device("s_platform_vuk")
        self.assertModeRunning("swarm_mb")
        self.confirm_playfield()
        self.assertBallsInPlay(3)
        for _ in range(3):
            self.ramp("backboard")
        self.assertPlayerVarEqual(1, "defenders_kid")


class TestDefenders(ActThreeTestCase):

    EVENTS = {"sati": "a3_ch1_completed", "lock": "a3_ch2_completed", "mifune": "a3_ch3_completed",
              "roland": "a3_ch4_completed", "zee": "apu_mb_completed", "kid": "swarm_mb_completed"}

    def defend(self, *names):
        for name in names:
            self.post_event(self.EVENTS[name])
        self.advance_time_and_run(.1)

    def test_threshold_is_four(self):
        self.start()
        self.mock_event("defender_joined")
        self.defend("sati", "lock", "mifune")
        self.assertPlayerVarEqual(0, "machine_city_lit")
        self.defend("kid")
        self.assertEventCalledWith("defender_joined", defender="kid")
        self.assertPlayerVarEqual(1, "machine_city_lit")
        self.assertPlayerVarEqual("KNOCK DOWN THE MISSION DROP: THE MACHINE CITY", "objective")

    def test_threshold_setting(self):
        self.machine.settings.set_setting_value("machine_city_threshold", 5)
        self.start()
        self.defend("sati", "lock", "mifune", "roland")
        self.assertPlayerVarEqual(0, "machine_city_lit")
        self.defend("zee")
        self.assertPlayerVarEqual(1, "machine_city_lit")

    def test_act_two_roster_plays_no_part(self):
        self.start()
        self.player()["allies_count"] = 6
        self.defend("sati")
        self.assertPlayerVarEqual(0, "machine_city_lit")


class TestTheMachineCity(ActThreeTestCase):

    def start_machine_city(self):
        for name in ("a3_ch1_completed", "a3_ch2_completed", "a3_ch3_completed", "apu_mb_completed"):
            self.post_event(name)
        self.advance_time_and_run(.1)
        self.open_mission()
        self.shoot_mission()
        self.assertModeRunning("the_machine_city")
        self.confirm_playfield()

    def rain(self, count):
        for i in range(count):
            self.knock_down_popup(i % 3 + 1, .2)
            self.raise_popup_switch(i % 3 + 1, 1.2)

    def test_all_stages_to_the_end(self):
        self.start()
        self.start_machine_city()
        self.assertModeNotRunning("apu_lock")
        self.assertModeNotRunning("swarm_gate")
        self.assertBallsInPlay(2)
        for ramp in ("left_lock", "right_loop", "backboard"):
            self.ramp(ramp)
        self.assertPlayerVarEqual(2, "machine_city_stage")
        self.confirm_playfield()
        self.assertBallsInPlay(4)

        # No jacking in before the offer is made.
        self.enter_device("s_platform_vuk")
        self.assertPlayerVarEqual(2, "machine_city_stage")
        # A playfield switch confirms that eject before the next entry.
        self.confirm_playfield()
        for n in (1, 2, 3, 4):
            self.tap("s_pop_target_{}".format(n))
        self.assertTrue(self.machine.diverters["platform_gate"].active)
        self.enter_device("s_platform_vuk")
        self.assertPlayerVarEqual(3, "machine_city_stage")
        self.assertFalse(self.machine.diverters["platform_gate"].active)
        self.confirm_playfield()
        self.assertBallsInPlay(6)

        self.rain(10)
        self.assertPlayerVarEqual(4, "machine_city_stage")
        self.mock_event("act_three_complete")
        self.enter_device("s_middle_loop_vuk")
        self.assertEventCalled("act_three_complete")
        self.assertPlayerVarEqual(1, "matrix_complete")
        self.assertPlayerVarEqual("III", "act")
        self.assertModeNotRunning("the_machine_city")
        self.assertModeNotRunning("act_three")
        self.assertModeRunning("base")

    def test_complete_matrix_plays_on_in_base(self):
        self.start()
        self.player()["machine_city_stage"] = 4
        self.player()["machine_city_lit"] = 1
        self.drain_all_balls()
        self.advance_time_and_run(5)
        self.assertModeRunning("the_machine_city")
        self.confirm_playfield()
        self.enter_device("s_middle_loop_vuk")
        self.assertPlayerVarEqual(1, "matrix_complete")
        self.drain_all_balls()
        self.advance_time_and_run(5)
        self.assertBallNumber(3)
        self.assertModeRunning("base")
        self.assertModeNotRunning("act_three")
        self.assertModeNotRunning("act_one")

    def test_resumes_on_next_ball(self):
        self.start()
        self.start_machine_city()
        for ramp in ("left_lock", "right_loop", "backboard"):
            self.ramp(ramp)
        self.tap("s_pop_target_1")
        self.assertPlayerVarEqual(2, "machine_city_stage")
        self.advance_time_and_run(20)
        self.confirm_playfield()
        self.drain_all_balls()
        self.advance_time_and_run(5)
        self.assertBallNumber(2)
        self.assertModeRunning("the_machine_city")
        self.assertPlayerVarEqual(2, "machine_city_stage")
        self.assertPlayerVarEqual(1, "machine_city_progress")
        self.confirm_playfield()
        self.assertBallsInPlay(4)
