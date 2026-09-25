"""Shared base for this machine's MPF tests.

Runs the real machine config from the repo root on the smart_virtual platform,
without BCP, so the rules can be exercised without hardware or Godot.

    python -m unittest discover -s tests -t .
"""
import os

from mpf.tests.MpfGameTestCase import MpfGameTestCase

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))


class MatrixTestCase(MpfGameTestCase):

    def get_machine_path(self):
        return REPO_ROOT

    def get_absolute_machine_path(self):
        return REPO_ROOT

    def get_config_file(self):
        return "config.yaml"

    def get_platform(self):
        return "smart_virtual"

    def start_matrix_game(self):
        """Fill the trough, start a game as the Matrix and put the first ball on the playfield."""
        self.fill_troughs()
        self.start_game()
        self.choose_game(0)
        self.confirm_playfield()

    def start_t2_game(self):
        """Fill the trough, start a game as Terminator 2 and put the first ball on the playfield."""
        self.fill_troughs()
        self.start_game()
        self.choose_game(1)
        self.confirm_playfield()

    def choose_game(self, steps):
        """Step the game select `steps` times to the right and confirm."""
        self.advance_time_and_run(.1)
        self.assertModeRunning("game_select")
        for _ in range(steps):
            self.hit_and_release_switch("s_right_flipper")
            self.advance_time_and_run(.1)
        self.hit_and_release_switch("s_start")
        self.advance_time_and_run(1)

    def confirm_playfield(self):
        """Hit a playfield switch so ejected balls count as on the playfield."""
        self.advance_time_and_run(1)
        self.hit_and_release_switch("s_pop_trigger")
        self.advance_time_and_run(1)

    def enter_device(self, switch, settle=2):
        """Roll a ball from the playfield into a ball device via its switch."""
        self.hit_switch_and_run(switch, settle)
