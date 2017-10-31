import unittest
import datetime
import time

class Team:
    def __init__(self):
        self.username = ""
        self.password = ""
        self.points = 0
        self.clueTime = datetime.time(0,0,0)
        self.currentLandmark = 0
        self.timelog = []

    def login(self, password):
        return "", False

    def get_clue(self): #THIS PROBABLY SHOULDN'T BE HERE
        return ""


class TestTeam(unittest.TestCase):
    def setUp(self):
        self.team = Team()
