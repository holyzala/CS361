import unittest
from abc import ABC, abstractmethod


class LandmarkI(ABC):
    @abstractmethod
    def submit_answer(self, answer):
        pass


class LandmarkFactory:
    def get_landmark(self, clue, question, answer):
        return self.Landmark(clue, question, answer)

    class Landmark(LandmarkI):
        def __init__(self, clue, question, answer):
            self.question = question
            self.clue = clue
            self.answer = answer
            self.point_value = 100

        def submit_answer(self, answer):
            pass

        def __eq__(self, other):
            return self.clue == other.clue


class TestInit(unittest.TestCase):
    def test_init(self):
        self.landmark = LandmarkFactory().get_landmark("What does the plaque say?", "Gift given by the French in New York?",
                                                       "Give me your tired, your poor, your huddled masses yearing to breathe free")
        self.assertEqual("Gift given by the French in New York?", self.landmark.question, "Failed to set question properly")
        self.assertEqual("What does the plaque say?", self.landmark.clue, "Failed to set clue properly")
        self.assertEqual("Give me your tired, your poor, your huddled masses yearing to breathe free",
                         self.landmark.answer, "Failed to answer properly")


if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestInit))
    suite.addTest(unittest.makeSuite(TestGetters))
    suite.addTest(unittest.makeSuite(TestSetters))
    runner = unittest.TextTestRunner()
    res = runner.run(suite)
    print(res)
    print("*" * 20)
    for i in res.failures: print(i[1])
