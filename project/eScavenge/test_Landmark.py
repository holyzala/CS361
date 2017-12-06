from django.test import TestCase

from .models import LandmarkFactory, Landmark


class TestInit(TestCase):
    NAME = "lm1"
    CLUE = "Gift given by the French in New York?"
    QUESTION = "What does the plaque say?"
    ANSWER = "Give me your tired, your poor, your huddled masses yearning to breathe free"

    def test_init(self):
        landmark = LandmarkFactory.get_landmark(self.NAME, self.CLUE, self.QUESTION, self.ANSWER, None)
        self.assertEqual(self.NAME, landmark.name, "Failed to set name properly")
        self.assertEqual(self.CLUE, landmark.clue, "Failed to set clue properly")
        self.assertEqual(self.QUESTION, landmark.question, "Failed to set question properly")
        self.assertEqual(self.ANSWER, landmark.answer, "Failed to answer properly")


class TestSettersToDatabase(TestCase):
    def setUp(self):
        self.landmark = LandmarkFactory.get_landmark("landmark1", "C1", "Q1", "A1", None)

    def test_name(self):
        self.landmark.name = "blah"
        self.landmark.save()
        self.landmark = Landmark.objects.get(name=self.landmark.name)
        self.assertEqual("blah", self.landmark.name, "name not set properly")

    def test_clue(self):
        self.landmark.clue = "c1"
        self.landmark.save()
        self.landmark = Landmark.objects.get(name=self.landmark.name)
        self.assertEqual("c1", self.landmark.clue, "Clue not set properly")

    def test_question(self):
        self.landmark.question = "q1"
        self.landmark.save()
        self.landmark = Landmark.objects.get(name=self.landmark.name)
        self.assertEqual("q1", self.landmark.question, "question not set properly")

    def test_answer(self):
        self.landmark.answer = "a1"
        self.landmark.save()
        self.landmark = Landmark.objects.get(name=self.landmark.name)
        self.assertEqual("a1", self.landmark.answer, "answer not set properly")


class TestCheckAnswer(TestCase):
    NAME = "lm1"
    CLUE = "Gift given by the French in New York?"
    QUESTION = "What does the plaque say?"
    ANSWER = "Give me your tired, your poor, your huddled masses yearning to breathe free"

    def setUp(self):
        self.landmark = LandmarkFactory.get_landmark(self.NAME, self.CLUE, self.QUESTION, self.ANSWER, None)

    def test_correct(self):
        self.assertTrue(self.landmark.check_answer(self.ANSWER), "Incorrectly returned False")

    def test_incorrect(self):
        self.assertFalse(self.landmark.check_answer("This is wrong"), "Incorrectly returned True")
