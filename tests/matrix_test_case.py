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
        """Fill the trough, start a game and put the first ball on the playfield."""
        self.fill_troughs()
        self.start_game()
        self.advance_time_and_run(1)
        self.confirm_playfield()

    def confirm_playfield(self):
        """Hit a playfield switch so ejected balls count as on the playfield."""
        self.advance_time_and_run(1)
        self.hit_and_release_switch("s_emp_trigger")
        self.advance_time_and_run(1)

    def enter_device(self, switch, settle=2):
        """Roll a ball from the playfield into a ball device via its switch."""
        self.hit_switch_and_run(switch, settle)
