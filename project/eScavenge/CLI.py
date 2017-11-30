import shlex
from django.db import IntegrityError
from django.utils import timezone

from .StringConst import *
from .Errors import Errors
from .Game import GameFactory, make_game
from .GameMaker import GMFactory
from .Team import Team


def need_admin(func):
    def wrapper(*args):
        if not args[0].current_user or not args[0].current_user.is_admin():
            return permission_denied
        return func(*args)

    return wrapper


def need_self(func):
    def wrapper(*args):
        try:
            if not args[0].current_user:
                return permission_denied
            if not args[0].current_user.is_admin() and not args[0].current_user.username == args[1][1]:
                return permission_denied
        except IndexError:
            return invalid_param
        return func(*args)

    return wrapper


def login(self, args):
    if self.current_user:
        return existing_login
    try:
        self.current_user = self.game_maker.login(args[1], args[2])
        if self.current_user:
            return login_success
        if self.game:
            self.current_user = self.game.login(args[1], args[2])
            if self.current_user:
                return login_success
    except IndexError:
        return invalid_param
    except KeyError:
        return login_fail
    return login_fail


@need_admin
def add_team(self, args):
    try:
        if self.game is None:
            return team_add_fail
        if args[1] == self.game_maker.username:
            return team_add_fail
        added = self.game.add_team(args[1], args[2])
    except IndexError:
        return invalid_param
    except IntegrityError:
        return "Team already exists"
    if added:
        return team_add
    return team_add_fail


@need_admin
def remove_team(self, args):
    try:
        removed = self.game.remove_team(args[1])
    except IndexError:
        return invalid_param
    if removed:
        return team_remove
    return team_remove_fail


@need_admin
def add_landmark(self, args):
    try:
        if self.game is None:
            return landmark_add_fail
        added = self.game.add_landmark(args[1], args[2], args[3])
    except IndexError:
        return invalid_param
    if added:
        return landmark_add
    return landmark_add_fail


@need_admin
def remove_landmark(self, args):
    try:
        removed = self.game.remove_landmark(args[1])
    except IndexError:
        return invalid_param
    if removed:
        return landmark_remove
    return landmark_remove_fail


@need_admin
def start(self, _):
    self.game.start()
    if self.game.started:
        return game_started
    return "Failed to start Game"


@need_admin
def end(self, _):
    self.game.end()
    if self.game.ended:
        return game_ended
    return "Failed to end game"


@need_admin
def create(self, _):
    if not self.game or not self.game.started or self.game.ended:
        self.game = GameFactory(make_game).create_game()
        return "Game Created"
    return "Game Failed"


@need_admin
def edit_landmark_order(self, args):
    try:
        index1 = int(args[1])
        index2 = int(args[2])
        value = self.game.edit_landmark_order(index1, index2)
    except (IndexError, ValueError):
        return invalid_param
    if value == Errors.NO_ERROR:
        return edit_landmark_order_success
    return edit_landmark_order_fail


@need_admin
def edit_landmark(self, args):
    oldclue_index = args[1]
    clue_index = None
    question_index = None
    answer_index = None
    try:
        clue_index = args.index('clue', 2)
    except ValueError:
        pass
    try:
        question_index = args.index('question', 2)
    except ValueError:
        pass
    try:
        answer_index = args.index('answer', 2)
    except ValueError:
        pass

    try:
        clue = args[clue_index + 1] if clue_index else None
        question = args[question_index + 1] if question_index else None
        answer = args[answer_index + 1] if answer_index else None
        if self.game.modify_landmark(oldclue=oldclue_index, clue=clue, question=question, answer=answer):
            return edit_landmark_success
    except IndexError:
        return invalid_param


@need_self
def edit_team(self, args):
    name_index = None
    pass_index = None
    try:
        name_index = args.index('name', 2)
    except ValueError:
        pass

    try:
        pass_index = args.index('password', 2)
    except ValueError:
        pass

    try:
        if name_index:
            name = args[name_index + 1]
            password = None
            if pass_index:
                password = args[pass_index + 1]
            if self.game.modify_team(oldname=args[1], newname=name, newpassword=password):
                return "Team changed"
            return "Team new name already exists"
        if pass_index:
            if self.game.modify_team(oldname=args[1], newpassword=args[pass_index + 1]):
                return "Team changed"
        return "No Changes"
    except IndexError:
        return invalid_param


def get_clue(self, _):
    if not self.current_user or self.current_user.is_admin():
        return permission_denied
    return self.game.get_team_landmark(self.current_user).clue


def quit_question(self, args):
    if len(args) < 3:
        return "Proper Format giveup <username> <password>"
    if not self.current_user or args[1] != self.current_user.username:
        return permission_denied
    if self.current_user.is_admin():
        return "You're Not Playing!"
    rtn = self.game.quit_question(timezone.now(), self.current_user, args[2])
    if rtn == Errors.INVALID_LOGIN:
        return permission_denied
    elif rtn == Errors.NO_GAME:
        return no_game_running
    return "Question Quit, Your Next Question: \n{}".format(self.game.get_team_landmark(self.current_user).question)


def get_stats(self, args):
    if not self.game.started or self.game.ended:
        return no_game_running
    if self.current_user is None:
        return permission_denied
    if len(args) < 1:
        return "Proper Format get_stats <username>"
    if self.current_user.username == args[1] or self.current_user.is_admin():
        return self.game.get_status(timezone.now(), args[1])
    return "You cannot see another users stats"


@need_admin
def get_snapshot(self, _):
    err, rtn = self.game.get_snapshot(timezone.now())
    if err == Errors.NO_GAME:
        return no_game_running
    if err == Errors.NO_ERROR:
        return rtn


def answer_question(self, args):
    if not self.current_user:
        return permission_denied
    if self.current_user.is_admin():
        return "You're Not Playing!"
    correct_answer = self.game.answer_question(timezone.now(), self.current_user, args[1])
    if correct_answer == Errors.NO_ERROR:
        return "That is Correct! The Next Question is: \n{}".format(
            self.game.get_team_landmark(self.current_user).question)
    elif correct_answer == Errors.NO_GAME:
        return no_game_running
    elif correct_answer == Errors.FINAL_ANSWER:
        return "That is Correct! There are no more landmarks!"
    elif correct_answer == Errors.LANDMARK_INDEX:
        return "There are no more landmarks!"
    return "Incorrect Answer! The Question Was: \n{}".format(self.game.get_team_landmark(self.current_user).question)


@need_admin
def edit_penalty_value(self, args):
    try:
        penalty_value = self.game.set_point_penalty(int(args[1]))
    except (ValueError, IndexError):
        return "Proper Format editpenaltyvalue <amount>"
    if penalty_value:
        return penalty_value_changed
    return penalty_value_failed


@need_admin
def edit_penalty_time(self, args):
    try:
        penalty_time = self.game.set_time_penalty(int(args[1]))
    except (ValueError, IndexError):
        return "Proper Format editpenaltytime <amount>"
    if penalty_time:
        return penalty_time_changed
    return penalty_time_failed


COMMANDS = {"login": login, "addteam": add_team, "addlandmark": add_landmark, "removeteam": remove_team, "start": start,
            "end": end, "create": create, "editteam": edit_team, "removelandmark": remove_landmark, "getclue": get_clue,
            "editlandmark": edit_landmark, "answer": answer_question, "giveup": quit_question, "getstats": get_stats,
            "editlandmarkorder": edit_landmark_order, "editpenaltyvalue" : edit_penalty_value,
            "editpenaltytime": edit_penalty_time, "snapshot": get_snapshot}


class CLI:
    def __init__(self, command_dict):
        self.game_maker = GMFactory().get_gm()
        self.commands = command_dict
        self.current_user = None
        self.game = None

    def command(self, inp, name):
        if name == self.game_maker.username:
            self.current_user = self.game_maker
        else:
            self.current_user = Team.objects.get(username=name)
        inp = shlex.split(inp)
        try:
            return self.commands[inp[0].lower()](self, inp)
        except KeyError:
            return "Invalid command"
        except IndexError:
            return invalid_param
