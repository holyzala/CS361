from datetime import timedelta

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models, IntegrityError
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.utils import timezone

from .Errors import Errors


class Game(models.Model):
    name = models.TextField(primary_key=True)
    started = models.BooleanField(default=False)
    ended = models.BooleanField(default=False)
    penalty_value = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])
    penalty_time = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])
    timer = models.DurationField(blank=True, null=True)
    landmark_points = models.PositiveIntegerField(default=100, validators=[MinValueValidator(0)])

    def login(self, username, password):
        try:
            return self.teams.get(username=username).login(username, password)
        except Team.DoesNotExist:
            return None

    def get_team(self, username):
        try:
            return self.teams.get(username=username)
        except Team.DoesNotExist:
            return None

    def get_team_landmark(self, team):
        return self.landmarks.all()[team.current_landmark]

    def get_team_question(self, team):
        return self.landmarks.all()[team.current_landmark].question

    def add_team(self, name, password):
        if self.started:
            return False
        try:
            TeamFactory.get_team(name, password, self)
        except IntegrityError:
            return False
        return True

    def remove_team(self, name):
        if self.started:
            return False
        try:
            self.teams.get(username=name).delete()
        except Team.DoesNotExist:
            return False
        return True

    def modify_team(self, oldname, newname=None, newpassword=None):
        try:
            self.teams.get(username=newname)
        except Team.DoesNotExist:
            pass
        else:
            return False
        try:
            team = self.teams.get(username=oldname)
            if newpassword:
                team.password = newpassword
            if newname:
                team.delete()
                team.username = newname
            team.full_clean()
            team.save()
        except Team.DoesNotExist:
            return False
        return True

    def add_landmark(self, name, clue, question, answer):
        if self.started:
            return False
        try:
            LandmarkFactory.get_landmark(name, clue, question, answer, self)
        except IntegrityError:
            return False
        return True

    def remove_landmark(self, name):
        if self.started:
            return False
        try:
            self.landmarks.get(name=name).delete()
        except Landmark.DoesNotExist:
            return False
        return True

    def get_landmarks_index(self):
        landmarks = ""
        for i, landmark in enumerate(self.landmarks.all()):
            landmarks += f"{i}: {landmark.name}\n"
        return landmarks

    def modify_landmark(self, oldname, name=None, clue=None, question=None, answer=None):
        try:
            landmark = self.landmarks.get(name=oldname)
            if question:
                landmark.question = question
            if answer:
                landmark.answer = answer
            if clue:
                landmark.clue = clue
            if name:
                landmark.delete()
                landmark.name = name
            landmark.full_clean()
            landmark.save()
            return True
        except Landmark.DoesNotExist:
            return False

    def edit_landmark_order(self, oldindex, newindex):
        if self.started or self.ended:
            return Errors.CAN_ONLY_EDIT_ORDER_WHEN_GAME_IS_NEW
        try:
            order = list(self.get_landmark_order())
            order.insert(newindex, order.pop(oldindex))
            self.set_landmark_order(order)
        except IndexError:
            return Errors.LANDMARK_INDEX
        return Errors.NO_ERROR

    def set_point_penalty(self, points):
        if self.started:
            return False
        if points < 0:
            return False
        self.penalty_value = points
        self.full_clean()
        self.save()
        return True

    def set_time_penalty(self, penalty):
        if self.started:
            return False
        if penalty < 0:
            return False
        self.penalty_time = penalty
        self.full_clean()
        self.save()
        return True

    def start(self):
        if self.started:
            return Errors.ALREADY_STARTED
        now = timezone.now()
        for team in self.teams.all():
            team.clue_time = now
            team.full_clean()
            team.save()
        self.started = True
        self.full_clean()
        self.save()
        return Errors.NO_ERROR

    def end(self):
        self.ended = True
        self.full_clean()
        self.save()

    def quit_question(self, now, team, password):
        if not self.started or self.ended:
            return Errors.NO_GAME
        if not team.login(team.username, password):
            return Errors.INVALID_LOGIN
        team.current_landmark += 1
        temp = None
        try:
            temp = TimeDelta.objects.create(time_delta=now - team.clue_time, team=team)
            temp.full_clean()
            temp.save()
        except ValidationError:
            temp.delete()
            temp = TimeDelta.objects.create(time_delta=timedelta(0), team=team)
            temp.full_clean()
            temp.save()
        team.clue_time = now
        team.penalty_count = 0
        team.full_clean()
        team.save()
        return Errors.NO_ERROR

    def answer_question(self, now, team, answer):
        if not self.started or self.ended:
            return Errors.NO_GAME
        try:
            lm = self.landmarks.all()[team.current_landmark]
        except IndexError:
            return Errors.LANDMARK_INDEX
        if not lm.check_answer(answer):
            team.penalty_count += self.penalty_value
            return Errors.WRONG_ANSWER
        else:
            temp = None
            try:
                temp = TimeDelta.objects.create(time_delta=now-team.clue_time, team=team)
                temp.full_clean()
                temp.save()
            except ValidationError:
                temp.delete()
                temp = TimeDelta.objects.create(time_delta=timedelta(0), team=team)
                temp.full_clean()
                temp.save()
            team.current_landmark += 1
            if self.timer:
                team.penalty_count += int(((now - team.clue_time) / self.timer)) * self.penalty_time
            team.points += max(0, self.landmark_points - team.penalty_count)
            team.clue_time = now
            team.penalty_count = 0
            team.full_clean()
            team.save()
            if self.landmarks.all().count() == team.current_landmark:
                return Errors.FINAL_ANSWER
            return Errors.NO_ERROR

    def get_status(self, now, username):
        current_team = self.teams.get(username=username)
        current_time_calc = max(timedelta(0), now - current_team.clue_time)
        total_time = current_team.time_log.aggregate(total=Coalesce(Sum("time_delta"), 0))['total']
        place = self.teams.filter(points__gt=current_team.points).count() + 1
        if current_team.current_landmark <= self.landmarks.all().count():
            stat_str = ('You are in place {} of {} teams\n'
                        'Points:{}\n'
                        'You are on Landmark:{} of {}\n'
                        'Current Landmark Elapsed Time:{}\n'
                        'Total Time Taken:{}')
            return stat_str.format(place, self.teams.all().count(), current_team.points,
                                   current_team.current_landmark+1, self.landmarks.all().count(),
                                   str(current_time_calc).split(".")[0],
                                   str(total_time + current_time_calc).split(".")[0])
        return f'Final Points: {current_team.points}'

    def get_snapshot(self):
        if not self.started or self.ended:
            return Errors.NO_GAME, None
        stringList = []

        for current_team in self.teams.all():
            total_time = current_team.time_log.aggregate(test=Coalesce(Sum("time_delta"), 0))['test']
            if current_team.current_landmark < self.landmarks.all().count():
                stat_str = "Team: {}\nYou Are On Landmark {}\nTime Taken For Landmarks: {}\nTotal Points: {}\n"
                stringList.append(stat_str.format(current_team.username, current_team.current_landmark + 1,
                                                  str(total_time).split(".")[0], current_team.points))
            else:  # on last landmark
                stat_str = "Team: {}\nYou Are On Landmark {}\nTime Taken For Landmarks: {}\nTotal Points: {}\n"
                stringList.append(stat_str.format(current_team.username, current_team.current_landmark,
                                                  str(total_time).split(".")[0], current_team.points))

        return Errors.NO_ERROR, ''.join(stringList)


class Team(models.Model):
    username = models.TextField(primary_key=True)
    password = models.TextField()
    points = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])
    current_landmark = models.IntegerField(default=0)
    penalty_count = models.IntegerField(default=0)
    clue_time = models.DateTimeField(default=timezone.now)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, blank=True, null=True, related_name='teams')

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
    time_delta = models.DurationField(default=timedelta(0), validators=[MinValueValidator(timedelta(0))])
    team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True, related_name='time_log')


class Landmark(models.Model):
    name = models.TextField(primary_key=True)
    clue = models.TextField()
    question = models.TextField()
    answer = models.TextField()
    game = models.ForeignKey(Game, on_delete=models.CASCADE, null=True, related_name='landmarks')

    class Meta:
        order_with_respect_to = 'game'

    def check_answer(self, answer):
        return self.answer.lower() == answer.lower()

    def __eq__(self, other):
        return self.name == other.name


class TeamFactory:
    @staticmethod
    def get_team(username, password, game):
        return Team.objects.create(username=username, password=password, game=game)


class GMFactory:
    def get_gm(self):
        return self.GameMaker()

    class GameMaker:
        def __init__(self):
            self.username = "gamemaker"
            self.__password = "1234"
            self.game = None

        def login(self, username, password):
            if self.username == username and self.__password == password:
                return self
            return None

        @staticmethod
        def is_admin():
            return True


class LandmarkFactory:
    @staticmethod
    def get_landmark(name, clue, question, answer, game):
        return Landmark.objects.create(name=name, clue=clue, question=question, answer=answer, game=game)


def make_game(name):
    return Game.objects.create(name=name)


class GameFactory:
    def __init__(self, maker):
        self.maker = maker

    def create_game(self, args):
        game = self.maker(args[1])
        game.save()
        return game
