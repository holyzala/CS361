import unittest
from abc import ABC, abstractmethod


class LandmarkI(ABC):
    @abstractmethod
    def submit_answer(self, answer):
        pass

    @abstractmethod
    def get_question(self):
        pass

    @abstractmethod
    def get_clue(self):
        pass

    @abstractmethod
    def get_answer(self):
        pass

    @abstractmethod
    def set_question(self):
        pass

    @abstractmethod
    def set_clue(self):
        pass

    @abstractmethod
    def set_answer(self):
        pass


class LandmarkFactory:
    def get_landmark(self, clue, question, answer):
        return self.Landmark(clue, question, answer)

    class Landmark(LandmarkI):
        def __init__(self, clue, question, answer):
            self.question = question
            self.clue = clue
            self.answer = answer
            self.pointValue = 100

        def submit_answer(self, answer):
            pass

        def get_clue(self):
            return self.clue

        def get_answer(self):
            return self.answer

        def get_question(self):
            return self.question

        def set_clue(self, clue):
            self.clue = clue

        def set_answer(self, answer):
            self.answer = answer

        def set_question(self, question):
            self.question = question

        def __eq__(self, other):
            return self.location == other.location


class TestInit(unittest.TestCase):
    def test_init(self):
        self.landmark = LandmarkFactory().get_landmark("What does the plaque say?", "Gift given by the French in New York?",
                                                       "Give me your tired, your poor, your huddled masses yearing to breathe free")
        self.assertEqual("Gift given by the French in New York?", self.landmark.question, "Failed to set question properly")
        self.assertEqual("What does the plaque say?", self.landmark.clue, "Failed to set clue properly")
        self.assertEqual("Give me your tired, your poor, your huddled masses yearing to breathe free",
                         self.landmark.answer, "Failed to answer properly")


class TestGetters(unittest.TestCase):
    def setUp(self):
        self.landmark = LandmarkFactory().get_landmark("What does the plaque say?",
                                                       "Gift given by the French in New York?",
                                                       "Give me your tired, your poor, your huddled masses yearing to breathe free")

    def test_get_question(self):
        self.assertEqual(self.landmark.question, self.landmark.get_question(), "Wrong question returned")

    def test_get_clue(self):
        self.assertEqual(self.landmark.clue, self.landmark.get_clue(), "Wrong clue returned")

    def test_get_answer(self):
        self.assertEqual(self.landmark.answer, self.landmark.get_answer(), "Wrong answer returned")


class TestSetters(unittest.TestCase):
    def setUp(self):
        self.landmark = LandmarkFactory().get_landmark("What does the plaque say?",
                                                       "Gift given by the French in New York?",
                                                       "Give me your tired, your poor, your huddled masses yearing to breathe free")

    def test_set_question(self):
        self.landmark.set_question("blah?")
        self.assertEqual("blah?", self.landmark.question, "question set improperly")

    def test_set_clue(self):
        self.landmark.set_clue("blah?")
        self.assertEqual("blah?", self.landmark.clue, "clue set improperly")

    def test_set_answer(self):
        self.landmark.set_answer("blah?")
        self.assertEqual("blah?", self.landmark.answer, "answer set improperly")



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
