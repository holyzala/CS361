from datetime import timedelta
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator


class Team(models.Model):
    username = models.TextField(primary_key=True)
    password = models.TextField()
    points = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])
    current_landmark = models.IntegerField(default=0)
    penalty_count = models.IntegerField(default=0)
    clue_time = models.DateTimeField(default=timezone.now)

    def __eq__(self, other):
        return self.username == other.username

    def login(self, username, password):
        if username != self.username or password != self.password:
            return None
        return self

    def add_penalty(self, penalty=1):
        if penalty <= 0:
            return False
        self.penalty_count += penalty
        self.full_clean()
        self.save()
        return True

    @staticmethod
    def is_admin():
        return False


class TimeDelta(models.Model):
    time_delta = models.DurationField(default=timedelta(0))
    team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True, related_name='time_log')


class TeamFactory:
    @staticmethod
    def get_team(username, password):
        return Team.objects.create(username=username, password=password)
