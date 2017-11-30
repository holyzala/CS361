from django.db import models


class LandmarkFactory:
    @staticmethod
    def get_landmark(name, clue, question, answer):
        return Landmark.objects.create(name= name, clue=clue, question=question, answer=answer)


class Landmark(models.Model):
    name = models.TextField(primary_key=True)
    clue = models.TextField()
    question = models.TextField()
    answer = models.TextField()

    def check_answer(self, answer):
        return self.answer.lower() == answer.lower()

