"""The playfield's hardware names: every switch posts generic events, none posts a game's."""
from tests.matrix_test_case import MatrixTestCase

# switch: the events it posts
SHOTS = {
    "s_left_lock_ramp": ("left_lock_ramp_hit", "ramp_hit", "left_shot_hit"),
    "s_middle_loop_ramp": ("middle_loop_ramp_hit", "ramp_hit", "left_shot_hit"),
    "s_right_loop_ramp": ("right_loop_ramp_hit", "ramp_hit", "right_shot_hit"),
    "s_backboard_ramp": ("backboard_ramp_hit", "ramp_hit", "right_shot_hit"),
    "s_left_lock_spinner": ("spinner_hit",),
    "s_middle_loop_spinner": ("spinner_hit",),
    "s_right_loop_spinner": ("spinner_hit",),
    "s_upper_target_1": ("upper_target_1_hit", "upper_target_hit"),
    "s_upper_target_2": ("upper_target_2_hit", "upper_target_hit"),
    "s_upper_target_3": ("upper_target_3_hit", "upper_target_hit"),
    "s_platform_gate_left": ("platform_gate_left_hit", "platform_gate_hit"),
    "s_platform_gate_right": ("platform_gate_right_hit", "platform_gate_hit"),
    "s_platform_target_1": ("platform_target_1_hit", "platform_target_hit"),
    "s_platform_target_2": ("platform_target_2_hit", "platform_target_hit"),
    "s_platform_magnet": ("platform_magnet_hit",),
    "s_pop_target_1": ("pop_target_1_hit", "pop_target_hit"),
    "s_pop_target_2": ("pop_target_2_hit", "pop_target_hit"),
    "s_pop_target_3": ("pop_target_3_hit", "pop_target_hit"),
    "s_pop_target_4": ("pop_target_4_hit", "pop_target_hit"),
    "s_kickback_target": ("kickback_target_hit",),
    "s_right_outlane_lock_target": ("right_outlane_lock_target_hit",),
}

# Words from the Matrix design that must not appear in any hardware name.
MATRIX_WORDS = ("trinity", "dejavu", "deja_vu", "real_world", "sentinel", "agent", "cypher",
                "mission", "matrix", "team", "ammo", "emp_", "oracle", "morpheus", "neo")

DEVICE_SECTIONS = ("switches", "coils", "ball_devices", "drop_targets", "drop_target_banks",
                   "diverters", "magnets", "flippers", "autofire_coils")


class TestShots(MatrixTestCase):

    def test_switches_post_their_events(self):
        for switch, events in SHOTS.items():
            self.assertEqual(list(events), self.machine.switches[switch].config["events_when_activated"], switch)

    def test_no_hardware_name_is_a_matrix_name(self):
        names = []
        for section in DEVICE_SECTIONS:
            names.extend(self.machine.config.get(section, {}))
        for switch in self.machine.switches.values():
            names.extend(switch.config["events_when_activated"])
        for name in names:
            for word in MATRIX_WORDS:
                self.assertNotIn(word, name, "{} is named after the Matrix".format(name))

    def test_every_ramp_is_a_ramp_shot(self):
        self.start_matrix_game()
        self.mock_event("ramp_hit")
        for ramp in ("left_lock", "middle_loop", "right_loop", "backboard"):
            self.ramp(ramp)
        self.assertEventCalled("ramp_hit", 4)

    def ramp(self, name):
        self.hit_and_release_switch("s_{}_ramp".format(name))
        self.advance_time_and_run(.1)
