import unittest


class Landmark:
    def __init__(self):
        self.location = ""
        self.clues = []
        self.answer = ""

    def submitAnswer(self, answer):
        return False


class TestLandmark(unittest.TestCase):
    def setUp(self):
        self.landmark = Landmark()
