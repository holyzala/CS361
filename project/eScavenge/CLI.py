import datetime
import shlex
import unittest

from .StringConst import *
from .Errors import Errors
from .Game import GameFactory, make_game
from .GameMaker import GMFactory


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


def logout(self, _):
    if not self.current_user:
        return "No user logged in"
    self.current_user = None
    return logout


@need_admin
def add_team(self, args):
    try:
        if self.game is None:
            return team_add_fail
        added = self.game.add_team(args[1], args[2])
    except IndexError:
        return invalid_param
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
    try:
        self.game.start()
    except IndexError:
        return invalid_param
    if self.game.started:
        return game_started
    return "Failed to start Game"


@need_admin
def end(self, _):
    try:
        self.game.end()
    except IndexError:
        return invalid_param
    if self.game.ended:
        return game_ended
    return "Failed to end game"


@need_admin
def create(self, _):
    try:
        self.game = GameFactory(make_game).create_game()
    except IndexError:
        return invalid_param
    if self.game:
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
        if clue_index:
            clue = args[clue_index + 1]
            if question_index:
                question = args[question_index + 1]
                if answer_index:
                    answer = args[answer_index + 1]
                    if self.game.modify_landmark(oldclue=oldclue_index, clue=clue, question=question, answer=answer):
                        return edit_landmark_success
                if self.game.modify_landmark(oldclue=oldclue_index, clue=clue, question=question):
                    return edit_landmark_success
            if self.game.modify_landmark(oldclue=oldclue_index, clue=clue):
                return edit_landmark_success

        if question_index:
            question = args[question_index + 1]
            if answer_index:
                answer = args[answer_index + 1]
                if self.game.modify_landmark(oldclue=oldclue_index, question=question, answer=answer):
                    return edit_landmark_success
            if self.game.modify_landmark(oldclue=oldclue_index, question=question):
                return edit_landmark_success

        if answer_index:
            answer = args[answer_index + 1]
            if self.game.modify_landmark(oldclue=oldclue_index, answer=answer):
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
    time_now = datetime.datetime.now()
    now = datetime.timedelta(days=time_now.day, hours=time_now.hour, minutes=time_now.minute, seconds=time_now.second)
    rtn = self.game.quit_question(now, self.current_user, args[2])
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
    time_now = datetime.datetime.now()
    now = datetime.timedelta(days=time_now.day, hours=time_now.hour, minutes=time_now.minute, seconds=time_now.second)
    if self.current_user.username == args[1] or self.current_user.is_admin():
        return self.game.get_status(now, args[1])
    return "You cannot see another users stats"


def answer_question(self, args):
    if not self.current_user:
        return permission_denied
    if self.current_user.is_admin():
        return "You're Not Playing!"
    datetime_now = datetime.datetime.now()
    now = datetime.timedelta(days=datetime_now.day, hours=datetime_now.hour, minutes=datetime_now.minute,
                             seconds=datetime_now.second)
    correct_answer = self.game.answer_question(now, self.current_user, args[1])
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
            "end": end, "create": create, "logout": logout, "editteam": edit_team, "removelandmark": remove_landmark,
            "getclue": get_clue, "editlandmark": edit_landmark, "answer": answer_question, "giveup": quit_question,
            "getstats": get_stats, "editlandmarkorder": edit_landmark_order, "editpenaltyvalue" : edit_penalty_value,
            "editpenaltytime" : edit_penalty_time}


class CLI:
    def __init__(self, command_dict):
        self.game_maker = GMFactory().get_gm()
        self.commands = command_dict
        self.current_user = None
        self.game = None

    def command(self, args):
        inp = shlex.split(args)
        try:
            return self.commands[inp[0].lower()](self, inp)
        except KeyError:
            return "Invalid command"
        except IndexError:
            return invalid_param


class TestGMLogin(unittest.TestCase):
    def setUp(self):
        self.cli = CLI(COMMANDS)

    def test_login_success(self):
        self.assertEqual(login_success, self.cli.command("login gamemaker 1234"), "Login message not correct")

    def test_login_bad_password(self):
        self.assertEqual(login_fail, self.cli.command("login gamemaker 4321"), "Login return message not correct")

    def test_login_bad_username(self):
        self.assertEqual(login_fail, self.cli.command("login ___ 1234"), "Login return message not correct")

    def test_login_bad_args(self):
        self.assertEqual(invalid_param, self.cli.command("login gamemaker"), invalid_param)


class TestTeamExistsLogin(unittest.TestCase):
    def setUp(self):
        self.cli = CLI(COMMANDS)
        self.assertEqual(login_success, self.cli.command("login gamemaker 1234"), "Valid login failed")
        self.assertEqual(game_create, self.cli.command("create"), "Failed to create game")
        self.assertEqual(team_add, self.cli.command("addteam teamName teamPassword"), "Failed to add Team")
        self.assertEqual(logout, self.cli.command("logout"), "Failed to log out")

    def test_login_success(self):
        self.assertEqual(login_success, self.cli.command("login teamName teamPassword"), "Valid login failed")

    def test_login_bad_password(self):
        self.assertEqual(login_fail, self.cli.command("login teamName 1234"), "Invalid login succeeded")

    def test_login_bad_username(self):
        self.assertEqual(login_fail, self.cli.command("login ___ teamPassword"), "Invalid login succeeded")


class TestTeamNotExistsLogin(unittest.TestCase):
    def setUp(self):
        self.cli = CLI(COMMANDS)
        self.assertEqual(login_success, self.cli.command("login gamemaker 1234"), "Valid login failed")
        self.assertEqual(game_create, self.cli.command("create"), "Failed to create game")
        self.assertEqual(logout, self.cli.command("logout"), "Failed to log out")

    def test_login(self):
        self.assertEqual(login_fail, self.cli.command("login teamName teamPassword"), "Invalid login failed")


class TestEditTeams(unittest.TestCase):
    def setUp(self):
        self.cli = CLI(COMMANDS)
        self.assertEqual(login_success, self.cli.command("login gamemaker 1234"), "Login message not correct")
        self.assertEqual(game_create, self.cli.command("create"), "Failed to create game")
        self.assertEqual(team_add, self.cli.command("addteam Team1 239103"))
        self.assertEqual(team_add, self.cli.command("addteam Team2 Rocks"))
        self.assertEqual(logout, self.cli.command("logout"), "Failed to log out")

    def test_team_edit_name_logged_in(self):
        self.assertEqual(login_success, self.cli.command("login Team1 239103"), "Valid login failed")
        self.assertEqual(team_change, self.cli.command("editteam Team1 name ILikeCheese"),
                         "Failed to change username")

    def test_team_edit_password_logged_in(self):
        self.assertEqual(login_success, self.cli.command("login Team1 239103"), "Valid login failed")
        self.assertEqual(team_change, self.cli.command("editteam Team1 password ThisIsSecure"),
                         "Failed to change pass")

    def test_team_edit_name_and_password_logged_in(self):
        self.assertEqual(login_success, self.cli.command("login Team1 239103"), "Valid login failed")
        self.assertEqual(team_change, self.cli.command("editteam Team1 name ILikeCheese password ThisIsSecure"),
                         "Failed to change pass")

    def test_team_edit_name_not_logged_in(self):
        self.assertEqual(permission_denied, self.cli.command("editteam Team1 name ILikeCheese"),
                         "no team is logged in")

    def test_team_edit_password_not_logged_in(self):
        self.assertEqual(permission_denied, self.cli.command("editteam Team1 password ThisIsSecure"),
                         "no team is logged in")

    def test_team_edit_other_team_name(self):
        self.assertEqual(login_success, self.cli.command("login Team1 239103"), "Valid login failed")
        self.assertEqual(permission_denied, self.cli.command("editteam Team2 password ThisIsSecure"),
                         "Only edit self")

    def test_team_edit_name_but_there_is_a_team_with_same_new_name(self):
        self.assertEqual(login_success, self.cli.command("login Team1 239103"), "Valid login failed")
        self.assertEqual(team_exist, self.cli.command("editteam Team1 name Team2"),
                         "Name is already taken")

    def test_team_edit_name_but_there_is_a_team_with_same_new_name_v2(self):
        self.assertEqual(login_success, self.cli.command("login Team1 239103"), "Valid login failed")
        self.assertEqual(team_exist,
                         self.cli.command("editteam Team1 name Team2 password ThisIsSecure"), "Only edit self")

    def test_gm_edit_team_name(self):
        self.assertEqual(login_success, self.cli.command("login gamemaker 1234"), "Login message not correct")
        self.assertEqual(team_change, self.cli.command("editteam Team1 name ILikeCheese"), "Failed to change name")

    def test_gm_edit_team_pass(self):
        self.assertEqual(login_success, self.cli.command("login gamemaker 1234"), "Login message not correct")
        self.assertEqual(team_change, self.cli.command("editteam Team1 password ThisIsSecure"),
                         "Failed to change pass")

    def test_team_edit_bad_args(self):
        self.assertEqual(login_success, self.cli.command("login Team1 239103"), "Valid login failed")
        self.assertEqual(team_no_change, self.cli.command("editteam Team1"), "check for bad input")


class TestAddTeam(unittest.TestCase):
    def setUp(self):
        self.cli = CLI(COMMANDS)
        self.assertEqual(login_success, self.cli.command("login gamemaker 1234"), "Login message not correct")
        self.assertEqual(game_create, self.cli.command("create"), "Failed to create game")

    def test_add_team_is_gm(self):
        self.assertEqual(team_add, self.cli.command("addteam Team1 1234"), team_add_fail)

    def test_add_team_not_gm(self):
        self.assertEqual(logout, self.cli.command("logout"), "Failed to logout")
        self.assertEqual(permission_denied, self.cli.command("addteam Team1 1234"), "Only game maker can add teams")

    def test_add_team_duplicate(self):
        self.assertEqual(team_add, self.cli.command("addteam Team1 1234"), team_add_fail)
        self.assertEqual(team_add_fail, self.cli.command("addteam Team1 1234"), "can not have duplicate teams")

    def test_add_team_before_game_created(self):
        self.cli.game = None
        self.assertEqual(team_add_fail, self.cli.command("addteam Team1 1234"),
                         "add team only after game is created")

    def test_add_team_bad_args(self):
        self.assertEqual(invalid_param, self.cli.command("addteam"), invalid_param)


class TestRemoveTeam(unittest.TestCase):
    def setUp(self):
        self.cli = CLI(COMMANDS)
        self.assertEqual(login_success, self.cli.command("login gamemaker 1234"), "Login message not correct")
        self.assertEqual(game_create, self.cli.command("create"), "Failed to create game")
        self.assertEqual(team_add, self.cli.command("addteam Team1 1526"), "setup failed")
        self.assertEqual(team_add, self.cli.command("addteam Team2 02ka"), "setup failed")
        self.assertEqual(team_add, self.cli.command("addteam Team3 192j"), "setup failed")

    def test_remove_team_is_gm(self):
        self.assertEqual(team_remove, self.cli.command("removeteam Team1"), "Failed to remove team")

    def test_remove_team_is_not_gm(self):
        self.assertEqual(logout, self.cli.command("logout"), "Failed to logout")
        self.assertEqual(permission_denied, self.cli.command("removeteam Team1"), "only game maker can remove")

    def test_remove_team_does_not_exist(self):
        self.assertEqual(team_remove, self.cli.command("removeteam Team3"), "team does not exist")
        self.assertEqual(team_remove_fail, self.cli.command("removeteam Team3"), "team does not exist")

    def test_remove_team_from_empty_team_list(self):
        # pylint: disable=protected-access,no-member
        self.cli.game._Game__teams.clear()
        self.assertEqual(team_remove_fail, self.cli.command("removeteam Team1"), "list of teams empty")

    def test_remove_team_bad_args(self):
        self.assertEqual(invalid_param, self.cli.command("removeteam"), invalid_param)


class TestStartGame(unittest.TestCase):
    def setUp(self):
        self.cli = CLI(COMMANDS)
        self.assertEqual(login_success, self.cli.command("login gamemaker 1234"), "Login message not correct")
        self.assertEqual(game_create, self.cli.command("create"), "Failed to create game")
        self.assertEqual(team_add, self.cli.command("addteam Team1 1526"), "setup failed")
        self.assertEqual(team_add, self.cli.command("addteam Team2 02ka"), "setup failed")
        self.assertEqual(landmark_add,
                         self.cli.command('addlandmark "New York" "Gift given by the French" "Statue of Liberty"'),
                         landmark_add_fail)

    def test_start_game_is_gm(self):
        self.assertEqual(game_started, self.cli.command("start"), "Failed to start game")

    def test_start_game_is_not_gm(self):
        self.assertEqual(logout, self.cli.command("logout"), "Failed to logout")
        self.assertEqual(permission_denied, self.cli.command("start"), "Only admin can not start a Game")

    def test_start_team_bad_args(self):
        self.assertEqual(invalid_param, self.cli.command(""), invalid_param)


class TestEndGame(unittest.TestCase):
    def setUp(self):
        self.cli = CLI(COMMANDS)
        self.assertEqual(login_success, self.cli.command("login gamemaker 1234"), "Login message not correct")
        self.assertEqual("Game Created", self.cli.command("create"), "Failed to create game")

    def test_end_game_is_gm(self):
        self.assertEqual(game_ended, self.cli.command("end"), "Failed to end game")

    def test_end_game_is_not_gm(self):
        self.assertEqual(logout, self.cli.command("logout"), "Failed to logout")
        self.assertEqual(permission_denied, self.cli.command("end"), "Only game maker can end a game")

    def test_end_game_bad_args(self):
        self.assertEqual(invalid_param, self.cli.command(""), invalid_param)


class TestCreate(unittest.TestCase):
    def setUp(self):
        self.cli = CLI(COMMANDS)
        self.assertEqual(login_success, self.cli.command("login gamemaker 1234"), "Login message not correct")

    def test_create_is_gm(self):
        self.assertEqual(None, self.cli.game)
        self.assertEqual(game_create, self.cli.command("create"), "Failed to Create Game")

    def test_create_not_gm(self):
        self.assertEqual(logout, self.cli.command("logout"), "Failed to logout")
        self.assertEqual(permission_denied, self.cli.command("create"), "Only admin can Create a new Game")


class TestAddLandmark(unittest.TestCase):
    def setUp(self):
        self.cli = CLI(COMMANDS)
        self.assertEqual(login_success, self.cli.command("login gamemaker 1234"), "Login message not correct")
        self.assertEqual(game_create, self.cli.command("create"), "Failed to Create Game")

    def test_add_landmark_is_gm(self):
        self.assertEqual(landmark_add,
                         self.cli.command('addlandmark "New York" "Gift given by the French" "Statue of Liberty"'),
                         landmark_add_fail)

    def test_add_landmark_not_gm(self):
        self.assertEqual(logout, self.cli.command("logout"), "Failed to logout")
        self.assertEqual(permission_denied,
                         self.cli.command('addlandmark "New York" "Gift given by the French" "Statue of Liberty"'),
                         "Only admin can add landmarks")

    def test_add_landmark_duplicate(self):
        self.assertEqual(landmark_add,
                         self.cli.command('addlandmark "New York" "Gift given by the French" "Statue of Liberty"'),
                         landmark_add_fail)
        self.assertEqual(landmark_add_fail,
                         self.cli.command('addlandmark "New York" "Gift given by the French" "Statue of Liberty"'),
                         "no duplicate landmarks")

    def test_add_landmark_before_game_created(self):
        self.cli.game = None
        self.assertEqual(landmark_add_fail,
                         self.cli.command('addlandmark "New York" "Gift given by the French" "Statue of Liberty"'),
                         "add landmark only after game is created")

    def test_add_landmark_bad_args(self):
        self.assertEqual(invalid_param, self.cli.command("addlandmark"), invalid_param)


class TestRemoveLandmark(unittest.TestCase):
    # pylint: disable=protected-access,no-member
    def setUp(self):
        self.cli = CLI(COMMANDS)
        self.assertEqual(login_success, self.cli.command("login gamemaker 1234"), "Login message not correct")
        self.assertEqual(game_create, self.cli.command("create"), "Failed to create game")
        self.assertEqual(team_add, self.cli.command("addteam Team1 1526"), "setup failed")
        self.assertEqual(landmark_add,
                         self.cli.command('addlandmark "New York" "Gift given by the French" "Statue of Liberty"'),
                         landmark_add_fail)
        self.assertEqual(landmark_add,
                         self.cli.command('addlandmark "UWM" "Place we purchase coffee from" "Grind"'),
                         landmark_add_fail)

    def test_remove_landmark_is_gm(self):
        self.assertEqual(landmark_remove, self.cli.command("removelandmark UWM"), "Failed to remove landmark")

    def test_remove_landmark_is_not_gm(self):
        self.assertEqual(logout, self.cli.command("logout"), "Failed to logout")
        self.assertEqual(permission_denied, self.cli.command('removelandmark "New York"'),
                         "only game maker can remove")

    def test_remove_landmark_does_not_exist(self):
        self.cli.game._Game__landmarks.pop()
        self.assertEqual(landmark_remove_fail, self.cli.command("removelandmark UWM"), "landmark does not exist")

    def test_remove_landmark_from_empty_landmark_list(self):
        self.cli.game._Game__landmarks.clear()
        self.assertEqual(landmark_remove_fail, self.cli.command("removelandmark UWM"), "list of teams empty")

    def test_remove_landmark_bad_args(self):
        self.assertEqual(invalid_param, self.cli.command("removelandmark"), invalid_param)


class TestEditLandmarkOrder(unittest.TestCase):
    def setUp(self):
        self.cli = CLI(COMMANDS)
        self.assertEqual(login_success, self.cli.command("login gamemaker 1234"), "Login message not correct")
        self.assertEqual(game_create, self.cli.command("create"), "Failed to create game")
        self.assertEqual(team_add, self.cli.command("addteam Team1 1526"), "setup failed")
        self.assertEqual(landmark_add,
                         self.cli.command('addlandmark "New York" "Gift given by the French" "Statue of Liberty"'),
                         landmark_add_fail)
        self.assertEqual(landmark_add,
                         self.cli.command('addlandmark "UWM" "Place we purchase coffee from" "Grind"'),
                         landmark_add_fail)
        self.assertEqual(landmark_add,
                         self.cli.command('addlandmark "Los Angeles" "Where the Lakers play" "Staples Center"'),
                         landmark_add_fail)
        self.assertEqual(landmark_add,
                         self.cli.command('addlandmark "Milwaukee" "Where the Brewers play" "Miller Park"'),
                         landmark_add_fail)

    def test_swap_landmark_is_gm(self):
        self.assertEqual(edit_landmark_order_success, self.cli.command("editlandmarkorder 0 3"),
                         "Failed to change landmark order")

    def test_swap_landmark_is_not_gm(self):
        self.assertEqual(logout, self.cli.command("logout"), "Failed to logout")
        self.assertEqual(permission_denied, self.cli.command("editlandmarkorder 0 3"),
                         "only game maker can remove")

    def test_swap_landmark_invalid_index(self):
        self.assertEqual(edit_landmark_order_fail, self.cli.command("editlandmarkorder -10 3"),
                         "Failed to change landmark order")

    def test_swap_landmark_invalid_index_v2(self):
        self.assertEqual(edit_landmark_order_fail, self.cli.command("editlandmarkorder 10 2"),
                         "Failed to change landmark order")

    def test_swap_cannot_convert_to_int(self):
         self.assertEqual(invalid_param, self.cli.command("editlandmarkorder 3 blah"),
                          "input is not an integer")

    def test_swap_landmark_after_game_is_not_new(self):
        self.assertEqual(game_started, self.cli.command("start"), "Failed to start game.")
        self.assertEqual(game_ended, self.cli.command("end"), "Failed to end game.")
        self.assertEqual(edit_landmark_order_fail, self.cli.command("editlandmarkorder 2 3"),
                         "Failed to change landmark order")

    def test_swap_landmark_bad_args(self):
        self.assertEqual(invalid_param, self.cli.command("editlandmarkorder"), invalid_param)


class TestEditLandmark(unittest.TestCase):
    def setUp(self):
        self.cli = CLI(COMMANDS)
        self.assertEqual(login_success, self.cli.command("login gamemaker 1234"), "Login message not correct")
        self.assertEqual(game_create, self.cli.command("create"), "Failed to create game")
        self.assertEqual(team_add, self.cli.command("addteam Team1 1526"), "setup failed")
        self.assertEqual(landmark_add,
                         self.cli.command('addlandmark "New York" "Gift given by the French" "Statue of Liberty"'),
                         landmark_add_fail)
        self.assertEqual(landmark_add, self.cli.command('addlandmark "UWM" "Place we purchase coffee from" "Grind"'),
                         landmark_add_fail)

    def test_edit_landmark_is_gm(self):
        self.assertEqual(edit_landmark_success,
                         self.cli.command('editlandmark "UWM" clue "New York" question "Where the Beastie Boys were ' +
                                          'going without sleep" answer "Brooklyn"'),
                         edit_landmark_fail)

    def test_edit_landmark_is_not_gm(self):
        self.assertEqual(logout, self.cli.command("logout"), "Failed to logout")
        self.assertEqual(permission_denied,
                         self.cli.command('editlandmark "UWM" clue "New York" question "Where the Beastie Boys were ' +
                                          'going without sleep" answer "Brooklyn"'))

    def test_edit_landmark_clue_only(self):
        self.assertEqual(edit_landmark_success, self.cli.command('editlandmark "UWM" clue "New York"'),
                         edit_landmark_fail)

    def test_edit_landmark_question_only(self):
        self.assertEqual(edit_landmark_success, self.cli.command(
            'editlandmark "UWM" question "Where the Beastie Boys were going without sleep"'), edit_landmark_fail)

    def test_edit_landmark_answer_only(self):
        self.assertEqual(edit_landmark_success, self.cli.command('editlandmark "UWM" answer "Brooklyn"'),
                         edit_landmark_fail)

    def test_edit_landmark_clue_and_answer_only(self):
        self.assertEqual(edit_landmark_success,
                         self.cli.command('editlandmark "UWM" clue "New York" answer "Brooklyn"'),
                         edit_landmark_fail)

    def test_edit_landmark_clue_and_question_only(self):
        self.assertEqual(edit_landmark_success, self.cli.command(
            'editlandmark "UWM" clue "New York" question "Where the Beastie Boys were going without sleep"'),
                         edit_landmark_fail)

    def test_edit_landmark_question_and_answer_only(self):
        self.assertEqual(edit_landmark_success, self.cli.command(
            'editlandmark "UWM" question "Where the Beastie Boys were going without sleep" answer "Brooklyn"'),
                         edit_landmark_fail)

    def test_edit_landmark_bad_args(self):
        self.assertEqual(invalid_param, self.cli.command("editlandmark"), invalid_param)


class TestGetClue(unittest.TestCase):
    def setUp(self):
        self.cli = CLI(COMMANDS)
        self.cli = CLI(COMMANDS)
        self.assertEqual(login_success, self.cli.command("login gamemaker 1234"), "Login message not correct")
        self.assertEqual(game_create, self.cli.command("create"), "Failed to create game")
        self.assertEqual(team_add, self.cli.command("addteam Team1 1526"), "setup failed")
        self.assertEqual(landmark_add,
                         self.cli.command('addlandmark "New York" "Gift given by the French" "Statue of Liberty"'),
                         "Failed to add landmark")
        self.assertEqual(landmark_add,
                         self.cli.command('addlandmark "UWM" "Place we purchase coffee from" "Grind"'),
                         "Failed to add landmark")

    def test_admin(self):
        self.assertEqual(permission_denied, self.cli.command("getclue"), "Clue returned for admin")

    def test_no_login(self):
        self.assertEqual(logout, self.cli.command("logout"), "Failed to log out")
        self.assertEqual(permission_denied, self.cli.command("getclue"), "Clue returned for no one")

    def test_correctly(self):
        self.assertEqual(game_started, self.cli.command("start"), "Failed to start game.")
        self.assertEqual(logout, self.cli.command("logout"), "Failed to log out")
        self.assertEqual(login_success, self.cli.command("login Team1 1526"), "Failed to log in team")
        self.assertEqual("New York", self.cli.command("getclue"), "Wrong clue returned")

    def test_after_answer(self):
        self.assertEqual(game_started, self.cli.command("start"), "Failed to start game.")
        self.assertEqual(logout, self.cli.command("logout"), "Failed to log out")
        self.assertEqual(login_success, self.cli.command("login Team1 1526"), "Failed to log in team")
        self.assertEqual("That is Correct! The Next Question is: \nPlace we purchase coffee from",
                         self.cli.command("answer 'Statue of Liberty'"), "Answer didn't work")
        self.assertEqual("UWM", self.cli.command("getclue"), "Wrong clue returned")


class TestQuitQuestion(unittest.TestCase):
    def setUp(self):
        self.cli = CLI(COMMANDS)
        self.assertEqual(login_success, self.cli.command("login gamemaker 1234"), "Login message not correct")
        self.assertEqual(game_create, self.cli.command("create"), "Failed to create game")
        self.assertEqual(team_add, self.cli.command("addteam Team1 1526"), "setup failed")
        self.assertEqual(landmark_add,
                         self.cli.command('addlandmark "New York" "Gift given by the French" "Statue of Liberty"'),
                         landmark_add_fail)
        self.assertEqual(landmark_add, self.cli.command('addlandmark "UWM" "Place we purchase coffee from" "Grind"'),
                         landmark_add_fail)
        self.assertEqual(game_started, self.cli.command("start"), "Failed to start game.")
        self.assertEqual(logout, self.cli.command("logout"), "lougout message not correct")

    def test_game_ended(self):
        self.assertEqual(login_success, self.cli.command("login gamemaker 1234"), "Login message not correct")
        self.assertEqual(game_ended, self.cli.command("end"), "Incorrect Message when ending game")
        self.assertEqual(logout, self.cli.command("logout"), "lougout message not correct")
        self.assertEqual(login_success, self.cli.command("login Team1 1526"), "Login message not correct")
        self.assertEqual(no_game_running, self.cli.command("giveup Team1 1526"), "Allowed giveup with no game")

    def test_no_login(self):
        self.assertEqual(permission_denied, self.cli.command("giveup Team1 1526"),
                         "No error message when quitting with no login")

    def test_admin(self):
        self.assertEqual(login_success, self.cli.command("login gamemaker 1234"), "Login message not correct")
        self.assertEqual("You're Not Playing!", self.cli.command("giveup gamemaker 1234"),
                         "Gamemaker might have just given up, oh no")

    def test_incorrect_pass(self):
        self.assertEqual(login_success, self.cli.command("login Team1 1526"), "Login message not correct")
        self.assertEqual(permission_denied, self.cli.command("giveup Team1 15s6"),
                         "Incorrect Message when giving up with wrong password")

    def test_incorrect_user(self):
        self.assertEqual(login_success, self.cli.command("login Team1 1526"), "Login message not correct")
        self.assertEqual(permission_denied, self.cli.command("giveup Teamp 1526"),
                         "Incorrect Message when giving up with wrong password")

    def test_quit(self):
        # pylint: disable=protected-access,no-member
        self.assertEqual(login_success, self.cli.command("login Team1 1526"), "Login message not correct")
        question = self.cli.game._Game__landmarks[self.cli.current_user.current_landmark+1].question
        self.assertEqual("Question Quit, Your Next Question: \n{}".format(question),
                         self.cli.command("giveup Team1 1526"), "Could not quit question with proper login")

    def test_quit_bad_args(self):
        self.assertEqual(login_success, self.cli.command("login Team1 1526"), "Login message not correct")
        self.assertEqual("Proper Format giveup <username> <password>", self.cli.command("giveup teamp"),
                         "Not enough args did not show correct message")


class TestGetStatus(unittest.TestCase):
    # pylint: disable=protected-access,no-member
    def setUp(self):
        self.cli = CLI(COMMANDS)
        self.assertEqual(login_success, self.cli.command("login gamemaker 1234"), "Login message not correct")
        self.assertEqual(game_create, self.cli.command("create"), "Failed to create game")
        self.assertEqual(team_add, self.cli.command("addteam Team1 1526"), "setup failed")
        self.assertEqual(team_add, self.cli.command("addteam Team2 1526"), "setup failed")
        self.assertEqual(landmark_add,
                         self.cli.command('addlandmark "New York" "Gift given by the French" "Statue of Liberty"'),
                         landmark_add_fail)
        self.assertEqual(landmark_add, self.cli.command('addlandmark "UWM" "Place we purchase coffee from" "Grind"'),
                         landmark_add_fail)
        self.assertEqual(game_started, self.cli.command("start"), "Failed to start game.")
        self.assertEqual(logout, self.cli.command("logout"), "lougout message not correct")

    def test_no_login(self):
        self.assertEqual(permission_denied, self.cli.command("getstats Team1"),
                         "Get Stats wroked with noone logged in")

    def test_no_game(self):
        self.assertEqual(login_success, self.cli.command("login gamemaker 1234"), "Login message not correct")
        self.assertEqual(game_ended, self.cli.command("end"), "Incorrect Message when ending game")
        self.assertEqual(logout, self.cli.command("logout"), "lougout message not correct")
        self.assertEqual(login_success, self.cli.command("login Team1 1526"), "Login message not correct")
        self.assertEqual(no_game_running, self.cli.command("getstats Team1"),
                         "Get Stats wroked with noone logged in")

    def test_admin(self):
        tt = datetime.timedelta(days=0, hours=0, minutes=0, seconds=0)
        time_now = datetime.datetime.now()
        now = datetime.timedelta(days=time_now.day, hours=time_now.hour, minutes=time_now.minute,
                                 seconds=time_now.second)
        for t in self.cli.game._Game__teams["Team1"].time_log:
            tt += t
        currenttimecalc = (now - self.cli.game._Game__teams["Team1"].clue_time)
        self.assertEqual(login_success, self.cli.command("login Team1 1526"), "Login message not correct")
        stat_str = 'Points:{};You Are On Landmark:{};Current Landmark Elapsed Time:{};Time Taken For Landmarks:{}'
        self.assertEqual(stat_str.format(self.cli.current_user.points, self.cli.current_user.current_landmark+1,
                                         currenttimecalc, tt), self.cli.command("getstats Team1"),
                         "Admin Couldn't user get stats")

    def test_user(self):
        tt = datetime.timedelta(days=0, hours=0, minutes=0, seconds=0)
        time_now = datetime.datetime.now()
        now = datetime.timedelta(days=time_now.day, hours=time_now.hour, minutes=time_now.minute,
                                 seconds=time_now.second)
        for t in self.cli.game._Game__teams["Team1"].time_log:
            tt += t
        current_time_calc = (now - self.cli.game._Game__teams["Team1"].clue_time)
        self.assertEqual(login_success, self.cli.command("login gamemaker 1234"), "Login message not correct")
        stat_str = 'Points:{};You Are On Landmark:{};Current Landmark Elapsed Time:{};Time Taken For Landmarks:{}'
        self.assertEqual(stat_str.format(self.cli.game.get_team("Team1").points,
                                         self.cli.game.get_team("Team1").current_landmark + 1, current_time_calc, tt),
                         self.cli.command("getstats Team1"), "Admin Couldn't get user stats")

    def test_not_user(self):
        self.assertEqual(login_success, self.cli.command("login Team2 1526"), "Login message not correct")
        self.assertEqual("You cannot see another users stats", self.cli.command("getstats Team1"),
                         "Get Stats wroked with noone logged in")

    def test_bad_args(self):
        self.assertEqual(login_success, self.cli.command("login Team1 1526"), "Login message not correct")
        self.assertEqual("Invalid parameters", self.cli.command("getstats"), "CLI took improper args")


class TestAnswerQuestion(unittest.TestCase):
    # pylint: disable=protected-access,no-member
    def setUp(self):
        self.cli = CLI(COMMANDS)
        self.assertEqual(login_success, self.cli.command("login gamemaker 1234"), "Login message not correct")
        self.assertEqual(game_create, self.cli.command("create"), "Failed to create game")
        self.assertEqual(team_add, self.cli.command("addteam Team1 1526"), "setup failed")
        self.assertEqual(team_add, self.cli.command("addteam Team2 1526"), "setup failed")
        self.assertEqual(landmark_add, self.cli.command(
            'addlandmark "New York" "Gift given by the French" "Statue of Liberty"'), landmark_add_fail)
        self.assertEqual(landmark_add, self.cli.command('addlandmark "UWM" "Place we purchase coffee from" "Grind"'),
                         landmark_add_fail)
        self.assertEqual(landmark_add, self.cli.command('addlandmark "Last Mark" "The Last Answer" "Last"'),
                         landmark_add_fail)
        self.assertEqual(game_started, self.cli.command("start"), "Failed to start game.")
        self.assertEqual(logout, self.cli.command("logout"), "lougout message not correct")

    def test_no_game(self):
        self.assertEqual(login_success, self.cli.command("login gamemaker 1234"), "Login message not correct")
        self.assertEqual(game_ended, self.cli.command("end"), "Incorrect Message when ending game")
        self.assertEqual(logout, self.cli.command("logout"), "lougout message not correct")
        self.assertEqual(login_success, self.cli.command("login Team1 1526"), "Login message not correct")
        self.assertEqual(no_game_running, self.cli.command("answer 'Statue of Liberty'"),
                         "allowed answer with no game running")

    def test_no_login(self):
        self.assertEqual(permission_denied, self.cli.command("answer 'Statue of Liberty'"),
                         "allowed answer with no game running")

    def test_admin(self):
        self.assertEqual(login_success, self.cli.command("login gamemaker 1234"), "Login message not correct")
        self.assertEqual("You're Not Playing!", self.cli.command("answer 'Statue of Liberty'"),
                         "Gamemaker just answered his own question!")

    def test_bad_args(self):
        self.assertEqual(login_success, self.cli.command("login Team1 1526"), "Login message not correct")
        self.assertEqual("Invalid parameters", self.cli.command("answer"), "CLI took improper args")

    def test_answer_incorrect(self):
        self.assertEqual(login_success, self.cli.command("login Team1 1526"), "Login message not correct")
        question = self.cli.game._Game__landmarks[self.cli.current_user.current_landmark].question
        self.assertEqual("Incorrect Answer! The Question Was: \n{}".format(question),
                         self.cli.command("answer 'this is so very wrong'"),
                         "Incorrect answer did not print correct response")

    def test_answer_correct(self):
        self.assertEqual(login_success, self.cli.command("login Team1 1526"), "Login message not correct")
        question = self.cli.game._Game__landmarks[self.cli.current_user.current_landmark+1].question
        self.assertEqual("That is Correct! The Next Question is: \n{}".format(question),
                         self.cli.command("answer 'Statue of Liberty'"),
                         "Correct answer did not print correct response")

    def test_answer_correcttwice(self):
        self.assertEqual(login_success, self.cli.command("login Team1 1526"), "Login message not correct")
        question = self.cli.game._Game__landmarks[self.cli.current_user.current_landmark+1].question
        self.assertEqual("That is Correct! The Next Question is: \n{}".format(question),
                         self.cli.command("answer 'Statue of Liberty'"),
                         "Correct answer did not print correct response")
        question = self.cli.game._Game__landmarks[self.cli.current_user.current_landmark+1].question
        self.assertEqual("That is Correct! The Next Question is: \n{}".format(question),
                         self.cli.command("answer Grind"), "Correct answer did not print correct response")

    def test_answer_last_question(self):
        self.assertEqual(login_success, self.cli.command("login Team1 1526"), "Login message not correct")
        question = self.cli.game._Game__landmarks[self.cli.current_user.current_landmark+1].question
        self.assertEqual("That is Correct! The Next Question is: \n{}".format(question),
                         self.cli.command("answer 'Statue of Liberty'"),
                         "Correct answer did not print correct response")
        question = self.cli.game._Game__landmarks[self.cli.current_user.current_landmark+1].question
        self.assertEqual("That is Correct! The Next Question is: \n{}".format(question),
                         self.cli.command("answer Grind"), "Correct answer did not print correct response")
        self.assertEqual("That is Correct! There are no more landmarks!", self.cli.command("answer 'Last'"),
                         "Correct answer did not print correct response")

    def test_answer_pass_last_question(self):
        self.assertEqual(login_success, self.cli.command("login Team1 1526"), "Login message not correct")
        question = self.cli.game._Game__landmarks[self.cli.current_user.current_landmark+1].question
        self.assertEqual("That is Correct! The Next Question is: \n{}".format(question),
                         self.cli.command("answer 'Statue of Liberty'"),
                         "Correct answer did not print correct response")
        question = self.cli.game._Game__landmarks[self.cli.current_user.current_landmark+1].question
        self.assertEqual("That is Correct! The Next Question is: \n{}".format(question),
                         self.cli.command("answer Grind"), "Correct answer did not print correct response")
        self.assertEqual("That is Correct! There are no more landmarks!", self.cli.command("answer Last"),
                         "Correct answer did not print correct response")
        self.assertEqual("There are no more landmarks!", self.cli.command("answer 'Last'"),
                         "Correct answer did not print correct response")

    def test_answer_right_wrong_right(self):
        self.assertEqual(login_success, self.cli.command("login Team1 1526"), "Login message not correct")
        question = self.cli.game._Game__landmarks[self.cli.current_user.current_landmark+1].question
        self.assertEqual("That is Correct! The Next Question is: \n{}".format(question),
                         self.cli.command("answer 'Statue of Liberty'"),
                         "Correct answer did not print correct response")
        question = self.cli.game._Game__landmarks[self.cli.current_user.current_landmark].question
        self.assertEqual("Incorrect Answer! The Question Was: \n{}".format(question),
                         self.cli.command("answer 'this is so very wrong'"),
                         "Incorrect answer did not print correct response")
        question = self.cli.game._Game__landmarks[self.cli.current_user.current_landmark+1].question
        self.assertEqual("That is Correct! The Next Question is: \n{}".format(question),
                         self.cli.command("answer 'Grind'"), "Correct answer did not print correct response")

    def test_answer_team1_team2(self):
        self.assertEqual(login_success, self.cli.command("login Team1 1526"), "Login message not correct")
        question = self.cli.game._Game__landmarks[self.cli.current_user.current_landmark+1].question
        self.assertEqual("That is Correct! The Next Question is: \n{}".format(question),
                         self.cli.command("answer 'Statue of Liberty'"),
                         "Correct answer did not print correct response")
        self.assertEqual(logout, self.cli.command("logout"), "logout message not correct")
        self.assertEqual(login_success, self.cli.command("login Team2 1526"), "Login message not correct")
        question = self.cli.game._Game__landmarks[self.cli.current_user.current_landmark+1].question
        self.assertEqual("That is Correct! The Next Question is: \n{}".format(question),
                         self.cli.command("answer 'Statue of Liberty'"),
                         "Correct answer did not print correct response")

    def test_answer_correctteam1_incorrectteam2(self):
        self.assertEqual(login_success, self.cli.command("login Team1 1526"), "Login message not correct")
        question = self.cli.game._Game__landmarks[self.cli.current_user.current_landmark+1].question
        self.assertEqual("That is Correct! The Next Question is: \n{}".format(question),
                         self.cli.command("answer 'Statue of Liberty'"),
                         "Correct answer did not print correct response")
        question = self.cli.game._Game__landmarks[self.cli.current_user.current_landmark+1].question
        self.assertEqual("That is Correct! The Next Question is: \n{}".format(question),
                         self.cli.command("answer 'Grind'"), "Correct answer did not print correct response")
        self.assertEqual(logout, self.cli.command("logout"), "logout message not correct")
        self.assertEqual(login_success, self.cli.command("login Team2 1526"), "Login message not correct")
        question = self.cli.game._Game__landmarks[self.cli.current_user.current_landmark].question
        self.assertEqual("Incorrect Answer! The Question Was: \n{}".format(question),
                         self.cli.command("answer 'this is so very wrong'"),
                         "Incorrect answer did not print correct response")
        question = self.cli.game._Game__landmarks[self.cli.current_user.current_landmark+1].question
        self.assertEqual("That is Correct! The Next Question is: \n{}".format(question),
                         self.cli.command("answer 'Statue of Liberty'"),
                         "Correct answer did not print correct response")


if __name__ == "__main__":
    SUITE = unittest.TestSuite()
    SUITE.addTest(unittest.makeSuite(TestGMLogin))
    SUITE.addTest(unittest.makeSuite(TestTeamExistsLogin))
    SUITE.addTest(unittest.makeSuite(TestTeamNotExistsLogin))
    SUITE.addTest(unittest.makeSuite(TestEditTeams))
    SUITE.addTest(unittest.makeSuite(TestAddTeam))
    SUITE.addTest(unittest.makeSuite(TestRemoveTeam))
    SUITE.addTest(unittest.makeSuite(TestStartGame))
    SUITE.addTest(unittest.makeSuite(TestEndGame))
    SUITE.addTest(unittest.makeSuite(TestAddLandmark))
    SUITE.addTest(unittest.makeSuite(TestRemoveLandmark))
    SUITE.addTest(unittest.makeSuite(TestEditLandmark))
    SUITE.addTest(unittest.makeSuite(TestGetClue))
    SUITE.addTest(unittest.makeSuite(TestGetStatus))
    SUITE.addTest(unittest.makeSuite(TestQuitQuestion))
    SUITE.addTest(unittest.makeSuite(TestAnswerQuestion))
    RUNNER = unittest.TextTestRunner()
    RES = RUNNER.run(SUITE)
    print(RES)
    print("*" * 20)
    for i in RES.failures:
        print(i[1])
