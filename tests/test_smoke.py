from tests.matrix_test_case import MatrixTestCase


class TestSmoke(MatrixTestCase):

    def test_game_starts_with_the_game_select(self):
        self.fill_troughs()
        self.start_game()
        self.advance_time_and_run(.1)
        self.assertModeRunning("game_select")
        self.assertModeNotRunning("base")

    def test_matrix_game_starts(self):
        self.start_matrix_game()
        self.assertModeRunning("base")
        self.assertModeRunning("act_one")
        self.assertModeNotRunning("t2_main")

    def test_t2_game_starts(self):
        self.start_t2_game()
        self.assertModeRunning("base")
        self.assertModeRunning("t2_main")
        self.assertModeNotRunning("act_one")
