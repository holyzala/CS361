import unittest


class Game:
    def __init__(self):
        self.teams = []
        self.landmarks = []
        self.started = False
        self.ended = False
        self.penaltyValue = 0
        self.penaltyTime = 0

    def add_team(self, team):
        pass

    def remove_team(self, name):
        pass

    def modify_team(self, oldname, name=None, password=None):
        pass

    def add_landmark(self, landmark):
        pass

    def remove_landmark(self, landmark):
        pass

    def modify_landmark(self, oldlandmark, newlandmark):
        self.landmarks = [x.replace(oldlandmark, newlandmark) for x in self.landmarks]

    def reorder_landmarks(self, landmark, position):
        self.landmarks.insert(position, landmark)

    def set_point_penalty(self, points):
        pass

    def set_time_penalty(self, time):
        pass

    def start(self):
        pass

    def end(self):
        self.ended = True


class TestGame(unittest.TestCase):
    def setUp(self):
        self.game = Game()

class TestEditLandmarkClue(unittest.TestCase):
    def setUp(self):
        self.game = Game()

    def test_edit_clue(self):
        self.game.landmarks = ["Chicago", "Madison"]
        self.assertTrue(self.game.landmarks, "List is empty")
        self.game.modify_landmark("Chicago", "Vegas")
        self.assertIn("Vegas", self.game.landmarks, "Landmark edited incorrectly")

class TestEndGame(unittest.TestCase):
    def setUp(self):
       self.game = Game()

    def test_end_game_command(self):
        self.game.started = True
        self.assertTrue(self.game.started, "Game in progress")
        self.game.end()
        self.assertTrue(self.game.ended, "Game Has Ended")

    def test_completed_game(self):
        self.game.landmarks = "Final Clue solved"
        self.assertEqual(self.game.landmarks, "Final Clue solved", "Final clue has been solved, the game is over")
        self.game.end()
        self.assertTrue(self.game.ended, "Game Has Ended")

class TestReOrderLandmarks(unittest.TestCase):
    def setUp(self):
        self.game = Game()

    def test_change_order(self):
        self.game.landmarks = ["Chicago", "Vegas", "Dallas"]
        self.assertTrue(self.game.landmarks, "List is empty")
        self.game.reorder_landmarks("Dallas", 1)
        self.assertEqual("Dallas", self.game.landmarks[1], "Reorder did not move landmark to correct location")

if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestGame))
    suite.addTest(unittest.makeSuite(TestEditLandmarkClue))
    suite.addTest(unittest.makeSuite(TestEndGame))
    suite.addTest(unittest.makeSuite(TestReOrderLandmarks))
    runner = unittest.TextTestRunner()
    res = runner.run(suite)
    print(res)
    print("*" * 20)
    for i in res.failures: print(i[1])