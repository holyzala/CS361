from django.db import models


class LandmarkFactory:
    def get_landmark(self, name, clue, question, answer):
        return Landmark.objects.create(name= name, clue=clue, question=question, answer=answer)


class Landmark(models.Model):
    name = models.CharField(max_length=20, primary_key=True)
    clue = models.CharField(max_length=120)
    question = models.CharField(max_length=120)
    answer = models.CharField(max_length=120)

    def check_answer(self, answer):
        return self.answer.lower() == answer.lower()

