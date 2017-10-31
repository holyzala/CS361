import unittest


class Team:
    def __init__(self):
        self.username = ""
        self.password = ""
        self.points
        self.currentLandmark
        self.timelog = []
    def login(self, password):
        return "", False

    def get_clue(self): #probably dont need this here anymore
        return ""


class TestTeam(unittest.TestCase):
    def setUp(self):
        self.team = Team()
