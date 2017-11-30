from abc import ABC, abstractmethod
from datetime import timedelta
from django.utils import timezone
from django.db import IntegrityError

from .Landmark import LandmarkFactory
from .Team import TeamFactory, Team, TimeDelta
from .Errors import Errors


class GameInterface(ABC):
    @abstractmethod
    def add_team(self, name, password):
        pass

    @abstractmethod
    def remove_team(self, name):
        pass

    @abstractmethod
    def modify_team(self, oldname, newname=None, newpassword=None):
        pass

    @abstractmethod
    def add_landmark(self, clue, question, answer):
        pass

    @abstractmethod
    def remove_landmark(self, clue):
        pass

    @abstractmethod
    def modify_landmark(self, oldclue, clue, question, answer):
        pass

    @abstractmethod
    def edit_landmark_order(self, oldindex, newindex):
        pass

    @abstractmethod
    def set_point_penalty(self, points):
        pass

    @abstractmethod
    def set_time_penalty(self, penalty):
        pass

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def end(self):
        pass

    @abstractmethod
    def get_status(self, now, username):
        pass

    @abstractmethod
    def answer_question(self, now, team, answer):
        pass

    @abstractmethod
    def quit_question(self, now, team, password):
        pass

    @abstractmethod
    def login(self, username, password):
        pass

    @abstractmethod
    def get_team(self, username):
        pass

    @abstractmethod
    def get_team_landmark(self, team):
        pass

    @abstractmethod
    def get_snapshot(self, now):
        pass


class Game(GameInterface):
    def __init__(self):
        self.__teams = {}
        self.__landmarks = []
        self.__started = False
        self.__running = False
        self.__ended = False
        self.__penalty_value = 0
        self.__penalty_time = 0
        self.timer = None
        self.landmark_points = 0

    @property
    def started(self):
        return self.__started

    @property
    def ended(self):
        return self.__ended

    def login(self, username, password):
        try:
            return self.__teams[username].login(username, password)
        except KeyError:
            return None

    def get_team(self, username):
        try:
            return self.__teams[username]
        except KeyError:
            return None

    def get_team_landmark(self, team):
        return self.__landmarks[team.current_landmark]

    def add_team(self, name, password):
        if not self.started:
            if name in self.__teams:
                return False
            temp = TeamFactory().get_team(name, password)
            self.__teams[name] = temp
            temp.save()

            return True
        return False

    def remove_team(self, name):
        if not self.started:
            try:
                del self.__teams[name]
            except KeyError:
                return False
            else:
                return True
        return False

    def modify_team(self, oldname, newname=None, newpassword=None):
        try:
            if newname in self.__teams:
                return False
            if newpassword:
                self.__teams[oldname].password = newpassword
            if newname:
                self.__teams[oldname].username = newname
                self.__teams[newname] = self.__teams.pop(oldname)
            return True
        except KeyError:
            return False

    def add_landmark(self, name, clue, question, answer):
        if not self.started:
            try:
                landmark = LandmarkFactory.get_landmark(name, clue, question, answer)
            except IntegrityError:
                return False
            if landmark in self.__landmarks:
                return False
            try:
                landmark.save()
            except IntegrityError:
                return False
            self.__landmarks.append(landmark)
            return True
        return False

    def remove_landmark(self, name):
        if not self.started:
            for landmark in self.__landmarks:
                if landmark.name == name:
                    self.__landmarks.remove(landmark)
                    return True
        return False

    def modify_landmark(self, oldname, name=None, clue=None, question=None, answer=None):
        try:
            for x in self.__landmarks:
                if x.name == oldname:
                    if question:
                        x.question = question
                    if answer:
                        x.answer = answer
                    if clue:
                        x.clue = clue
                    if name:
                        x.name = name
            return True

        except KeyError:
            return False

    def edit_landmark_order(self, index1, index2):
        if self.started or self.ended:
            return Errors.CAN_ONLY_EDIT_ORDER_WHEN_GAME_IS_NEW
        try:
            self.__landmarks.insert(index2, self.__landmarks.pop(index1))
        except IndexError:
            return Errors.LANDMARK_INDEX
        return Errors.NO_ERROR

    @property
    def penalty_value(self):
        return self.__penalty_value

    def set_point_penalty(self, points):
        if self.started:
            return False
        if points < 0:
            return False
        self.__penalty_value = points
        return True

    @property
    def penalty_time(self):
        return self.__penalty_time

    def set_time_penalty(self, penalty):
        if self.started:
            return False
        if penalty < 0:
            return False
        self.__penalty_time = penalty
        return True

    def start(self):
        now = timezone.now()
        for team in self.__teams:
            self.__teams[team].clue_time = now
        self.__started = True

    def end(self):
        self.__ended = True

    def quit_question(self, now, team, password):
        if not self.started or self.ended:
            return Errors.NO_GAME
        if not team.login(team.username, password):
            return Errors.INVALID_LOGIN
        team.current_landmark += 1
        TimeDelta.objects.create(time_delta=now-team.clue_time, team=team)
        team.clue_time = now
        team.penalty_count = 0
        return Errors.NO_ERROR

    def answer_question(self, now, team, answer):
        if not self.started or self.ended:
            return Errors.NO_GAME
        try:
            lm = self.__landmarks[team.current_landmark]
        except IndexError:
            return Errors.LANDMARK_INDEX
        if not lm.check_answer(answer):
            team.penalty_count += self.penalty_value
            return Errors.WRONG_ANSWER
        else:
            TimeDelta.objects.create(time_delta=now-team.clue_time, team=team)
            team.current_landmark += 1
            if self.timer:
                team.penalty_count += int(((now - team.clue_time) / self.timer)) * self.penalty_time
            team.points += max(0, self.landmark_points - team.penalty_count)
            team.clue_time = now
            team.penalty_count = 0
            team.full_clean()
            team.save()
            if len(self.__landmarks) == team.current_landmark:
                return Errors.FINAL_ANSWER
            return Errors.NO_ERROR

    def get_status(self, now, username):
        current_team = Team.objects.get(username=username)
        current_time_calc = (now - current_team.clue_time)
        total_time = timedelta(days=0, hours=0, minutes=0, seconds=0)
        for t in current_team.time_log.all():
            total_time += t.time_delta
        if current_team.current_landmark <= len(self.__landmarks):
            stat_str = 'Points:{};You Are On Landmark:{};Current Landmark Elapsed Time:{};Time Taken For Landmarks:{}'
            return stat_str.format(current_team.points, current_team.current_landmark+1,
                                   str(current_time_calc).split(".")[0], total_time)
        return 'Final Points: {}'.format(current_team.points)

    def get_snapshot(self, now):
        if not self.started or self.ended:
            return Errors.NO_GAME, None
        stringList = []
        for current_team in Team.objects.all():
            total_time = timedelta(days=0, hours=0, minutes=0, seconds=0)
            for t in current_team.time_log.all():
                total_time += t.time_delta
            if current_team.current_landmark < len(self.__landmarks):
                stat_str = "Team: {}\nYou Are On Landmark {}\nTime Taken For Landmarks: {}\nTotal Points: {}\n"
                stringList.append(stat_str.format(current_team.username, current_team.current_landmark + 1, total_time,
                                                  current_team.points))
            else:  # on last landmark
                stat_str = "Team: {}\nYou Are On Landmark {}\nTime Taken For Landmarks: {}\nTotal Points: {}\n"
                stringList.append(stat_str.format(current_team.username, current_team.current_landmark, total_time,
                                                  current_team.points))

        return Errors.NO_ERROR, ''.join(stringList)


def make_game(*args, **kwargs):
    """This function should only ever return classes that implement GameInterface"""
    return Game()


class GameFactory:
    def __init__(self, maker):
        self.maker = maker

    def create_game(self, *args, **kwargs):
        return self.maker(*args, **kwargs)
