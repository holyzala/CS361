from datetime import timedelta

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models, IntegrityError
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.utils import timezone

from .Errors import Errors
from .StringConst import no_game_running


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

    def get_team_question(self, team):
        if not self.started or self.ended:
            return no_game_running
        try:
            return team.current_landmark.question
        except AttributeError:
            return "No more landmarks"

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
        first_landmark = self.landmarks.first()
        for team in self.teams.all():
            team.current_landmark = first_landmark
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
        next_landmark = None
        try:
            next_landmark = team.current_landmark.get_next_in_order()
        except Landmark.DoesNotExist:
            pass
        except AttributeError:
            return Errors.LANDMARK_INDEX
        temp = None
        try:
            temp = LandmarkStat.objects.create(time_delta=now - team.clue_time, team=team,
                                               landmark=team.current_landmark, quit=True)
            temp.full_clean()
            temp.save()
        except ValidationError:
            temp.delete()
            temp = LandmarkStat.objects.create(time_delta=timedelta(0), team=team, landmark=team.current_landmark,
                                               quit=True)
            temp.full_clean()
            temp.save()
        team.clue_time = now
        team.penalty_count = 0
        team.current_landmark = next_landmark
        team.full_clean()
        team.save()
        if not team.current_landmark:
            return Errors.FINAL_ANSWER
        return Errors.NO_ERROR

    def answer_question(self, now, team, answer):
        if not self.started or self.ended:
            return Errors.NO_GAME
        try:
            if not team.current_landmark.check_answer(answer):
                team.penalty_count += self.penalty_value
                team.full_clean()
                team.save()
                return Errors.WRONG_ANSWER
        except AttributeError:
            return Errors.LANDMARK_INDEX
        temp = None
        if self.timer:
            team.penalty_count += int(((now - team.clue_time) / self.timer)) * self.penalty_time
        points = max(0, self.landmark_points - team.penalty_count)
        try:
            temp = LandmarkStat.objects.create(time_delta=now - team.clue_time, team=team,
                                               landmark=team.current_landmark, points=points, quit=False)
            temp.full_clean()
            temp.save()
        except ValidationError:
            temp.delete()
            temp = LandmarkStat.objects.create(time_delta=timedelta(0), team=team, landmark=team.current_landmark,
                                               points=points, quit=False)
            temp.full_clean()
            temp.save()
        team.points += points
        team.clue_time = now
        team.penalty_count = 0
        team.full_clean()
        team.save()
        try:
            team.current_landmark = team.current_landmark.get_next_in_order()
        except Landmark.DoesNotExist:
            team.current_landmark = None
            team.save()
            return Errors.FINAL_ANSWER
        team.save()
        return Errors.NO_ERROR

    def get_status(self, now, username):
        current_team = self.teams.get(username=username)
        current_time_calc = max(timedelta(0), now - current_team.clue_time)
        total_time = current_team.history.aggregate(total=Coalesce(Sum("time_delta"), 0))['total']
        place = self.teams.filter(points__gt=current_team.points).count() + 1
        try:
            lm_place = list(self.get_landmark_order()).index(current_team.current_landmark.id) + 1
        except AttributeError:
            lm_place = self.landmarks.all().count()
        if current_team.current_landmark:
            stat_str = ('You are in place {} of {} teams\n'
                        'Points:{}\n'
                        'You are on Landmark:{} of {}\n'
                        'Current Landmark Elapsed Time:{}\n'
                        'Total Time Taken:{}')
            return stat_str.format(place, self.teams.all().count(), current_team.points,
                                   lm_place, self.landmarks.all().count(),
                                   str(current_time_calc).split(".")[0],
                                   str(total_time + current_time_calc).split(".")[0])
        return (f'You are in place {place} of {self.teams.all().count()} teams\n'
                f'Total Time Taken: {str(total_time).split(".")[0]}\n'
                f'Final Points: {current_team.points}')

    def get_snapshot(self):
        if not self.started or self.ended:
            return Errors.NO_GAME, None
        stringList = []

        for current_team in self.teams.all():
            total_time = current_team.history.aggregate(test=Coalesce(Sum("time_delta"), 0))['test']
            if current_team.current_landmark:
                lm_place = list(self.get_landmark_order()).index(current_team.current_landmark.id) + 1
                stat_str = "Team: {}\nYou Are On Landmark {}\nTime Taken For Landmarks: {}\nTotal Points: {}\n"
                stringList.append(stat_str.format(current_team.username, lm_place,
                                                  str(total_time).split(".")[0], current_team.points))
            else:  # on last landmark
                stat_str = "Team: {}\nYou Are On Landmark {}\nTime Taken For Landmarks: {}\nTotal Points: {}\n"
                stringList.append(stat_str.format(current_team.username, self.landmarks.all().count(),
                                                  str(total_time).split(".")[0], current_team.points))

        return Errors.NO_ERROR, ''.join(stringList)


class Landmark(models.Model):
    name = models.TextField(unique=True)
    clue = models.TextField()
    question = models.TextField()
    answer = models.TextField()
    game = models.ForeignKey(Game, on_delete=models.CASCADE, null=True, related_name='landmarks')

    class Meta:
        order_with_respect_to = 'game'

    def check_answer(self, answer):
        return self.answer.lower() == answer.lower()


class Team(models.Model):
    username = models.TextField(unique=True)
    password = models.TextField()
    points = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])
    current_landmark = models.ForeignKey(Landmark, on_delete=models.CASCADE, blank=True, null=True)
    penalty_count = models.IntegerField(default=0)
    clue_time = models.DateTimeField(default=timezone.now)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, blank=True, null=True, related_name='teams')

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


class LandmarkStat(models.Model):
    time_delta = models.DurationField(default=timedelta(0), validators=[MinValueValidator(timedelta(0))])
    team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True, related_name='history')
    landmark = models.ForeignKey(Landmark, on_delete=models.CASCADE, related_name='stats')
    points = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])
    quit = models.BooleanField()


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
