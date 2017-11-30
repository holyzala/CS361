from django.test import TestCase
from .Landmark import LandmarkFactory


class TestInit(TestCase):
    CLUE = "Gift given by the French in New York?"
    QUESTION = "What does the plaque say?"
    ANSWER = "Give me your tired, your poor, your huddled masses yearning to breathe free"

    def test_init(self):
        # pylint: disable=protected-access,no-member
        landmark = LandmarkFactory().get_landmark(self.CLUE, self.QUESTION, self.ANSWER)
        self.assertEqual(self.CLUE, landmark.clue, "Failed to set clue properly")
        self.assertEqual(self.QUESTION, landmark.question, "Failed to set question properly")
        self.assertEqual(self.ANSWER, landmark._Landmark__answer, "Failed to answer properly")


class TestEquivalence(TestCase):
    CLUE = "Gift given by the French in New York?"
    QUESTION = "What does the plaque say?"
    ANSWER = "Give me your tired, your poor, your huddled masses yearning to breathe free"

    def setUp(self):
        self.landmark = LandmarkFactory().get_landmark(self.CLUE, self.QUESTION, self.ANSWER)

    def test_equal(self):
        landmark = LandmarkFactory().get_landmark(self.CLUE, "q1", "a1")
        self.assertEqual(landmark, self.landmark, "Didn't come out equal")


class TestCheckAnswer(TestCase):
    CLUE = "Gift given by the French in New York?"
    QUESTION = "What does the plaque say?"
    ANSWER = "Give me your tired, your poor, your huddled masses yearning to breathe free"

    def setUp(self):
        self.landmark = LandmarkFactory().get_landmark(self.CLUE, self.QUESTION, self.ANSWER)

    def test_correct(self):
        self.assertTrue(self.landmark.check_answer(self.ANSWER), "Incorrectly returned False")

    def test_incorrect(self):
        self.assertFalse(self.landmark.check_answer("This is wrong"), "Incorrectly returned True")
