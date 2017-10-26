import unittest


class Game():
    def __init__(self):
        self.teams = []
        self.landmarks = []


class TestGame(unittest.TestCase):
    def setUp(self):
        self.game = Game()
