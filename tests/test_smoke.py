from tests.matrix_test_case import MatrixTestCase


class TestSmoke(MatrixTestCase):

    def test_game_starts(self):
        self.fill_troughs()
        self.start_game()
        self.assertModeRunning("base")
