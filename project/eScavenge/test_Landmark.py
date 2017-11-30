from django.test import TestCase
from .Landmark import LandmarkFactory, Landmark


class TestInit(TestCase):
    NAME = "lm1"
    CLUE = "Gift given by the French in New York?"
    QUESTION = "What does the plaque say?"
    ANSWER = "Give me your tired, your poor, your huddled masses yearning to breathe free"

    def test_init(self):
        # pylint: disable=protected-access,no-member
        landmark = LandmarkFactory.get_landmark(self.NAME, self.CLUE, self.QUESTION, self.ANSWER)
        self.assertEqual(self.NAME, landmark.name, "Failed to set name properly")
        self.assertEqual(self.CLUE, landmark.clue, "Failed to set clue properly")
        self.assertEqual(self.QUESTION, landmark.question, "Failed to set question properly")
        self.assertEqual(self.ANSWER, landmark._Landmark__answer, "Failed to answer properly")


class TestSettersToDatabase(TestCase):
    def setUp(self):
        self.landmark = LandmarkFactory.get_landmark("landmark1", "C1", "Q1", "A1")

    def test_name(self):
        self.landmark.name = "blah"
        self.landmark.full_clean()
        self.landmark.save()
        self.landmark = Landmark.objects.get(name=self.landmark.name)
        self.assertEqual("blah", self.landmark.clue, "name not set properly")

    def test_clue(self):
        self.landmark.clue = "c1"
        self.landmark.save()
        self.landmark = Landmark.objects.get(name=self.landmark.name)
        self.assertEqual("c1", self.landmark.clue, "Clue not set properly")

    def test_question(self):
        self.landmark.question = "q1"
        self.landmark.save()
        self.landmark = Landmark.objects.get(name=self.landmark.name)
        self.assertEqual("q1", self.landmark.clue, "question not set properly")

    def test_answer(self):
        self.landmark.answer = "a1"
        self.landmark.save()
        self.landmark = Landmark.objects.get(name=self.landmark.name)
        self.assertEqual("a1", self.landmark.clue, "answer not set properly")


class TestCheckAnswer(TestCase):
    NAME = "lm1"
    CLUE = "Gift given by the French in New York?"
    QUESTION = "What does the plaque say?"
    ANSWER = "Give me your tired, your poor, your huddled masses yearning to breathe free"

    def setUp(self):
        self.landmark = LandmarkFactory.get_landmark(self.NAME, self.CLUE, self.QUESTION, self.ANSWER)

    def test_correct(self):
        self.assertTrue(self.landmark.check_answer(self.ANSWER), "Incorrectly returned False")

    def test_incorrect(self):
        self.assertFalse(self.landmark.check_answer("This is wrong"), "Incorrectly returned True")
