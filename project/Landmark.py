import unittest
from abc import ABC, abstractmethod


class LandmarkI(ABC):
    @abstractmethod
    def submit_answer(self, answer):
        pass

    @abstractmethod
    def get_location(self):
        pass

    @abstractmethod
    def get_clue(self):
        pass

    @abstractmethod
    def get_answer(self):
        pass


class LandmarkFactory:
    def get_landmark(self, location, clue, answer):
        return self.Landmark(location, clue, answer)

    class Landmark(LandmarkI):
        def __init__(self, location, clue, answer):
            self.location = location
            self.clue = clue
            self.answer = answer
            self.pointValue = 100

        def submit_answer(self, answer):
            pass

        def get_location(self):
            return self.location

        def get_clue(self):
            return self.clue

        def get_answer(self):
            return self.answer

        def __eq__(self, other):
            return self.location == other.location


class TestInit(unittest.TestCase):
    def test_init(self):
        self.landmark = LandmarkFactory().get_landmark("New York", "Gift given by the French", "Statue of Liberty")
        self.assertEqual("New York", self.landmark.location, "Failed to set location properly")
        self.assertEqual("Gift given by the French", self.landmark.clue, "Failed to set clue properly")
        self.assertEqual("Statue of Liberty", self.landmark.answer, "Failed to answer location properly")


class TestGetters(unittest.TestCase):
    def setUp(self):
        self.location = "New York"
        self.clue = "Gift given by the French"
        self.answer = "Statue of Liberty"
        self.landmark = LandmarkFactory().get_landmark(self.location, self.clue, self.answer)

    def test_get_location(self):
        self.assertEqual(self.location, self.landmark.get_location(), "Wrong location returned returned")

    def test_get_clue(self):
        self.assertEqual(self.clue, self.landmark.get_clue(), "Wrong clue returned")

    def test_get_answer(self):
        self.assertEqual(self.answer, self.landmark.get_answer(), "Wrong answer returned")


if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestInit))
    suite.addTest(unittest.makeSuite(TestGetters))
    runner = unittest.TextTestRunner()
    res = runner.run(suite)
    print(res)
    print("*" * 20)
    for i in res.failures: print(i[1])
