import unittest


class GameMaker():
    def __init__(self):
        self.game = None
        self.username = ""
        self.password = ""

    def login(self):
        return "", False

    def create_game(self):
        return None


class TestGameMaker(unittest.TestCase):
    def setUp(self):
        self.gm = GameMaker()
