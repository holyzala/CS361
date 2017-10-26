import unittest


class Team():
    def __init__(self):
        self.username = ""
        self.password = ""

    def login(self, password):
        return "", False

    def answer_question(self, answer):
        return ""


class TestTeam(unittest.TestCase):
    def setUp(self):
        self.team = Team()
