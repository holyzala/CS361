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
        if landmark not in self.game.landmarks:
            self.game.landmarks.append(landmark)

    def remove_landmark(self, landmark):
        if landmark in self.game.landmarks:
            self.game.landmarks.remove(landmark)

    def modify_landmark(self, oldlandmark, newlandmark):
        self.landmarks = [x.replace(oldlandmark, newlandmark) for x in self.landmarks]

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

class TestDeleteLandmarks(unittest.TestCase):
    def setUp(self):
        self.game = Game()

    def test_delete_landmark(self):
        landmark1 = "ABC"
        self.game.add_landmark(landmark1)
        self.assertIn(landmark1, self.game.landmarks)
        self.game.remove_landmark(landmark1)
        self.assertNotIn(landmark1, self.game.landmarks, "Failed to remove landmark")

    def test_delete_multi_landmarks(self):
        landmark1 = "ABC"
        landmark2 = "DEF"
        self.game.add_landmark(landmark1)
        self.game.add_landmark(landmark2)
        self.assertIn(landmark1, self.game.landmarks)
        self.assertIn(landmark1, self.game.landmarks)
        self.game.remove_landmark(landmark1)
        self.assertNotIn(landmark1, self.game.landmarks, "Failed to remove Landmark1")
        self.assertEqual(landmark2, self.game.landmarks[0], "List not properly reindexing")
        self.game.remove_landmark(landmark2)
        self.assertNotIn(landmark1, self.game.landmarks, "Failed to remove Landmark2")

class TestAddLandmark(unittest.testcase):
    def setUp(self):
        self.game = Game()

    def test_add_landmark(self):
        landmark1 = "ABC"
        self.assertNotIn(landmark1, self.game.landmarks, "Landmark already Exists")
        self.game.add_landmark(landmark1)
        self.assertIn(landmark1, self.game.landmarks, "Landmark was not successfully added")

    def test_add_landmark(self):
        landmark1 = "ABC"
        landmark2 = "DEF"
        self.assertNotIn(landmark1, self.game.landmarks, "Landmark already Exists")
        self.game.add_landmark(landmark1)
        self.assertIn(landmark1, self.game.landmarks, "Landmark1 was not successfully added")
        self.game.add_landmark(landmark2)
        self.assertIn(landmark2, self.game.landmarks, "Landmark2 was not sucessfully added")
        self.assertEqual((self.game.landmark[0], self.game.landmarks[1]), (landmark1, landmark2), "Adding not indexing properly")

    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestLogin))
    runner = unittest.TextTestRunner()
    res = runner.run(suite)
    print(res)
    print("*" * 20)
    for i in res.failures: print(i[1])