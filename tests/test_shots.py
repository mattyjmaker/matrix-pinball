"""The physical switch events and the Matrix names modes/matrix_shots gives them."""
from tests.matrix_test_case import MatrixTestCase

# switch: (physical events it posts, Matrix events matrix_shots re-posts)
SHOTS = {
    "s_trinity_ramp": (("ramp_1_hit", "ramp_hit", "left_shot_hit"), ("trinity_ramp_hit",)),
    "s_dejavu_ramp": (("ramp_2_hit", "ramp_hit", "left_shot_hit"), ("dejavu_ramp_hit",)),
    "s_real_world_ramp": (("ramp_3_hit", "ramp_hit", "right_shot_hit"), ("real_world_ramp_hit",)),
    "s_sentinel_ramp": (("ramp_4_hit", "ramp_hit", "right_shot_hit"), ("sentinel_ramp_hit",)),
    "s_real_world_1": (("upper_target_1_hit", "upper_target_hit"), ("real_world_1_hit", "real_world_target_hit")),
    "s_real_world_2": (("upper_target_2_hit", "upper_target_hit"), ("real_world_2_hit", "real_world_target_hit")),
    "s_real_world_3": (("upper_target_3_hit", "upper_target_hit"), ("real_world_3_hit", "real_world_target_hit")),
    "s_sentinel_left": (("gate_left_target_hit", "gate_entrance_hit"), ("sentinel_left_hit", "sentinel_entrance_hit")),
    "s_sentinel_right": (("gate_right_target_hit", "gate_entrance_hit"), ("sentinel_right_hit", "sentinel_entrance_hit")),
    "s_sentinel_boss": (("gate_main_target_hit",), ("sentinel_boss_hit",)),
    "s_sentinel_magnet": (("magnet_hit",), ("sentinel_magnet_hit",)),
    "s_emp_target_1": (("pop_target_1_hit", "pop_target_hit"), ("emp_target_1_hit", "emp_target_hit")),
    "s_emp_target_2": (("pop_target_2_hit", "pop_target_hit"), ("emp_target_2_hit", "emp_target_hit")),
    "s_emp_target_3": (("pop_target_3_hit", "pop_target_hit"), ("emp_target_3_hit", "emp_target_hit")),
    "s_emp_target_4": (("pop_target_4_hit", "pop_target_hit"), ("emp_target_4_hit", "emp_target_hit")),
    "s_ammo_target": (("lock_2_target_hit",), ("ammo_target_hit",)),
}

MATRIX_EVENTS = sorted({event for _, matrix in SHOTS.values() for event in matrix})


class TestShots(MatrixTestCase):

    def test_switches_post_physical_events(self):
        for switch, (physical, _) in SHOTS.items():
            self.assertEqual(list(physical), self.machine.switches[switch].config["events_when_activated"],
                             switch)

    def test_no_switch_posts_a_matrix_name(self):
        for switch in self.machine.switches.values():
            for event in switch.config["events_when_activated"]:
                self.assertNotIn(event, MATRIX_EVENTS, "{} posts the themed event {}".format(switch.name, event))

    def test_matrix_shots_runs_with_the_game(self):
        self.start_matrix_game()
        self.assertModeRunning("matrix_shots")

    def test_every_switch_reaches_its_matrix_event(self):
        self.start_matrix_game()
        for switch, (_, matrix) in SHOTS.items():
            for event in matrix:
                self.mock_event(event)
            self.hit_and_release_switch(switch)
            self.advance_time_and_run(.1)
            for event in matrix:
                self.assertEventCalled(event, 1)
