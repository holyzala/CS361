import unittest
from abc import ABC


class LandmarkI(ABC):
    def submit_answer(self, answer):
        return False

    def get_location(self):
        return ""

    def get_clue(self):
        return ""

    def get_answer(self):
        return ""


class LandmarkFactory:
    def getLandmark(self, location, clue, answer):
        return self.Landmark(location, clue, answer)

    class Landmark(LandmarkI):
        def __init__(self, location, clue, answer):
            self.location = location
            self.clue = clue
            self.answer = answer

        def submit_answer(self, answer):
            return False

        def get_location(self):
            return self.location

        def get_clue(self):
            return self.clue

        def get_answer(self):
            return self.answer


class TestInit(unittest.TestCase):
    def test_init(self):
        self.landmark = LandmarkFactory().getLandmark("New York", "Gift given by the French", "Statue of Liberty")
        self.assertEqual("New York", self.landmark.location, "Failed to set location properly")
        self.assertEqual("Gift given by the French", self.landmark.clue, "Failed to set clue properly")
        self.assertEqual("Statue of Liberty", self.landmark.answer, "Failed to answer location properly")


if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestInit))
    runner = unittest.TextTestRunner()
    res = runner.run(suite)
    print(res)
    print("*" * 20)
    for i in res.failures: print(i[1])

