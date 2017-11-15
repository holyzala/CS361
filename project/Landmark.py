import unittest
from abc import ABC, abstractmethod


class LandmarkI(ABC):
    @abstractmethod
    def check_answer(self, answer):
        pass

    @property
    @abstractmethod
    def answer(self):
        pass

    @answer.setter
    @abstractmethod
    def answer(self, answer):
        pass


class LandmarkFactory:
    def get_landmark(self, clue, question, answer):
        return self.Landmark(clue, question, answer)

    class Landmark(LandmarkI):
        def __init__(self, clue, question, answer):
            self.question = question
            self.clue = clue
            self.__answer = answer

        @property
        def answer(self):
            return None

        @answer.setter
        def answer(self, answer):
            self.__answer = answer

        def check_answer(self, answer):
            return self.__answer.lower() == answer.lower()

        def __eq__(self, other):
            return self.clue == other.clue


class TestInit(unittest.TestCase):
    CLUE = "Gift given by the French in New York?"
    QUESTION = "What does the plaque say?"
    ANSWER = "Give me your tired, your poor, your huddled masses yearning to breathe free"

    def test_init(self):
        # pylint: disable=protected-access
        landmark = LandmarkFactory().get_landmark(self.CLUE, self.QUESTION, self.ANSWER)
        self.assertEqual(self.CLUE, landmark.clue, "Failed to set clue properly")
        self.assertEqual(self.QUESTION, landmark.question, "Failed to set question properly")
        self.assertEqual(self.ANSWER, landmark._Landmark__answer, "Failed to answer properly")


class TestEquivalence(unittest.TestCase):
    CLUE = "Gift given by the French in New York?"
    QUESTION = "What does the plaque say?"
    ANSWER = "Give me your tired, your poor, your huddled masses yearning to breathe free"

    def setUp(self):
        self.landmark = LandmarkFactory().get_landmark(self.CLUE, self.QUESTION, self.ANSWER)

    def test_equal(self):
        landmark = LandmarkFactory().get_landmark(self.CLUE, "q1", "a1")
        self.assertEqual(landmark, self.landmark, "Didn't come out equal")


class TestCheckAnswer(unittest.TestCase):
    CLUE = "Gift given by the French in New York?"
    QUESTION = "What does the plaque say?"
    ANSWER = "Give me your tired, your poor, your huddled masses yearning to breathe free"

    def setUp(self):
        self.landmark = LandmarkFactory().get_landmark(self.CLUE, self.QUESTION, self.ANSWER)

    def test_correct(self):
        self.assertTrue(self.landmark.check_answer(self.ANSWER), "Incorrectly returned False")

    def test_incorrect(self):
        self.assertFalse(self.landmark.check_answer("This is wrong"), "Incorrectly returned True")


if __name__ == "__main__":
    SUITE = unittest.TestSuite()
    SUITE.addTest(unittest.makeSuite(TestInit))
    SUITE.addTest(unittest.makeSuite(TestCheckAnswer))
    SUITE.addTest(unittest.makeSuite(TestEquivalence))
    RUNNER = unittest.TextTestRunner()
    RES = RUNNER.run(SUITE)
    print(RES)
    print("*" * 20)
    for i in RES.failures:
        print(i[1])
