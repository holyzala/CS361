import unittest


class Game:
    def __init__(self):
        self.teams = []
        self.landmarks = []
        self.started = False
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
        pass

    def set_point_penalty(self, points):
        pass

    def set_time_penalty(self, time):
        pass

    def start(self):
        pass

    def end(self):
        pass


class TestGame(unittest.TestCase):
    def setUp(self):
        self.game = Game()

class TestDeleteLandmarks(unittest.TestCase):
    def setUp(self):
        self.game = Game()

    def test_list_not_empty(self):
        self.assertFalse([], self.game.landmarks, "Landmark list is Empty, Cannot Remove")

    def test_list_contains_element(self):
        landmark1 = "ABC"
        self.assertIn(landmark1, self.game.landmarks, "Landmark does not exist in this list")

class TestAddLandmarks(unittest.TestCase):
    def setUp(self):
        self.game = Game()

    def test_list_contains_element(self):
        landmark1 = "ABC"
        self.assertNotIn(landmark1, self.game.landmarks, "Landmark already Exists in this list")