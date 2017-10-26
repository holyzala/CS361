import unittest


class GameMaster():
    def __init__(self):
        self.game = None
        self.username = ""
        self.password = ""

    def login(self):
        return "", False

    def create_game(self):
        return None


class TestGameMaster(unittest.TestCase):
    def setUp(self):
        self.gm = GameMaster()
