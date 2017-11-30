from django.test import TestCase
from django.utils import timezone
from .CLI import CLI, COMMANDS
from .StringConst import *
import datetime
from .Team import Team

GM = "gamemaker"


class TestEditTeams(TestCase):
    def setUp(self):
        self.cli = CLI(COMMANDS)
        self.assertEqual(game_create, self.cli.command("create", GM), "Failed to create game")
        self.assertEqual(team_add, self.cli.command("addteam Team1 239103", GM))
        self.assertEqual(team_add, self.cli.command("addteam Team2 Rocks", GM))

    def test_team_edit_name_logged_in(self):
        self.assertEqual(team_change, self.cli.command("editteam name ILikeCheese", "Team1"),
                         "Failed to change username")

    def test_team_edit_password_logged_in(self):
        self.assertEqual(team_change, self.cli.command("editteam password ThisIsSecure", "Team1"),
                         "Failed to change pass")

    def test_team_edit_name_and_password_logged_in(self):
        self.assertEqual(team_change, self.cli.command("editteam name ILikeCheese password ThisIsSecure",
                                                       "Team1"),
                         "Failed to change pass")

    def test_team_edit_other_team_name(self):
        self.assertEqual(permission_denied, self.cli.command("editteam Team2 password ThisIsSecure", "Team1"),
                         "Only edit self")

    def test_team_edit_name_but_there_is_a_team_with_same_new_name(self):
        self.assertEqual(team_exist, self.cli.command("editteam Team1 name Team2", "Team1"),
                         "Name is already taken")

    def test_team_edit_name_but_there_is_a_team_with_same_new_name_v2(self):
        self.assertEqual(team_exist,
                         self.cli.command("editteam name Team2 password ThisIsSecure", "Team1"), "Only edit self")

    def test_gm_edit_team_name(self):
        self.assertEqual(team_change, self.cli.command("editteam Team1 name ILikeCheese", GM), "Failed to change name")

    def test_gm_edit_team_pass(self):
        self.assertEqual(team_change, self.cli.command("editteam Team1 password ThisIsSecure", GM),
                         "Failed to change pass")

    def test_team_edit_bad_args(self):
        self.assertEqual(team_no_change, self.cli.command("editteam Team1", "Team1"), "check for bad input")


class TestAddTeam(TestCase):
    def setUp(self):
        self.cli = CLI(COMMANDS)
        self.assertEqual(game_create, self.cli.command("create", GM), "Failed to create game")

    def test_add_team_is_gm(self):
        self.assertEqual(team_add, self.cli.command("addteam Team1 1234", GM), team_add_fail)

    def test_add_team_not_gm(self):
        self.assertEqual(team_add, self.cli.command("addteam Team1 1234", GM), team_add_fail)
        self.assertEqual(permission_denied, self.cli.command("addteam Team2 1234", "Team1"),
                         "Only game maker can add teams")

    def test_add_team_duplicate(self):
        self.assertEqual(team_add, self.cli.command("addteam Team1 1234", GM), team_add_fail)
        self.assertEqual(team_add_fail, self.cli.command("addteam Team1 1234", GM), "can not have duplicate teams")

    def test_add_team_before_game_created(self):
        self.cli.game = None
        self.assertEqual(team_add_fail, self.cli.command("addteam Team1 1234", GM),
                         "add team only after game is created")

    def test_add_team_bad_args(self):
        self.assertEqual(invalid_param, self.cli.command("addteam", GM), invalid_param)


class TestRemoveTeam(TestCase):
    def setUp(self):
        self.cli = CLI(COMMANDS)
        self.assertEqual(game_create, self.cli.command("create", GM), "Failed to create game")
        self.assertEqual(team_add, self.cli.command("addteam Team1 1526", GM), "setup failed")
        self.assertEqual(team_add, self.cli.command("addteam Team2 02ka", GM), "setup failed")
        self.assertEqual(team_add, self.cli.command("addteam Team3 192j", GM), "setup failed")

    def test_remove_team_is_gm(self):
        self.assertEqual(team_remove, self.cli.command("removeteam Team1", GM), "Failed to remove team")

    def test_remove_team_is_not_gm(self):
        self.assertEqual(permission_denied, self.cli.command("removeteam Team1", "Team1"), "only game maker can remove")

    def test_remove_team_does_not_exist(self):
        self.assertEqual(team_remove, self.cli.command("removeteam Team3", GM), "team does not exist")
        self.assertEqual(team_remove_fail, self.cli.command("removeteam Team3", GM), "team does not exist")

    def test_remove_team_from_empty_team_list(self):
        # pylint: disable=protected-access,no-member
        self.cli.game._Game__teams.clear()
        self.assertEqual(team_remove_fail, self.cli.command("removeteam Team1", GM), "list of teams empty")

    def test_remove_team_bad_args(self):
        self.assertEqual(invalid_param, self.cli.command("removeteam", GM), invalid_param)


class TestStartGame(TestCase):
    def setUp(self):
        self.cli = CLI(COMMANDS)
        self.assertEqual(game_create, self.cli.command("create", GM), "Failed to create game")
        self.assertEqual(team_add, self.cli.command("addteam Team1 1526", GM), "setup failed")
        self.assertEqual(team_add, self.cli.command("addteam Team2 02ka", GM), "setup failed")
        self.assertEqual(landmark_add,
                         self.cli.command('addlandmark "New York" "Gift given by the French" "Statue of Liberty"', GM),
                         landmark_add_fail)

    def test_start_game_is_gm(self):
        self.assertEqual(game_started, self.cli.command("start", GM), "Failed to start game")

    def test_start_game_is_not_gm(self):
        self.assertEqual(permission_denied, self.cli.command("start", "Team1"), "Only admin can not start a Game")

    def test_start_team_bad_args(self):
        self.assertEqual(invalid_param, self.cli.command("", GM), invalid_param)


class TestEndGame(TestCase):
    def setUp(self):
        self.cli = CLI(COMMANDS)
        self.assertEqual("Game Created", self.cli.command("create", GM), "Failed to create game")
        self.assertEqual(team_add, self.cli.command("addteam Team1 1526", GM), "setup failed")

    def test_end_game_is_gm(self):
        self.assertEqual(game_ended, self.cli.command("end", GM), "Failed to end game")

    def test_end_game_is_not_gm(self):
        self.assertEqual(permission_denied, self.cli.command("end", "Team1"), "Only game maker can end a game")

    def test_end_game_bad_args(self):
        self.assertEqual(invalid_param, self.cli.command("", GM), invalid_param)


class TestCreate(TestCase):
    def setUp(self):
        self.cli = CLI(COMMANDS)

    def test_create_is_gm(self):
        self.assertEqual(None, self.cli.game)
        self.assertEqual(game_create, self.cli.command("create", GM), "Failed to Create Game")

    def test_create_in_progress_game(self):
        self.assertEqual(game_create, self.cli.command("create", GM), "Failed to Create Game")
        self.assertEqual(game_started, self.cli.command("start", GM), "Failed to Start Game")
        self.assertEqual(game_failed, self.cli.command("create", GM), "Creation occurred with Game in Progress")

    def test_create_double_game(self):
        self.assertEqual(game_create, self.cli.command("create", GM), "Failed to Create Game")
        self.assertEqual(game_create, self.cli.command("create", GM), "Failed to Create Game")

    def test_create_after_end_game(self):
        self.assertEqual(game_create, self.cli.command("create", GM), "Failed to Create Game")
        self.assertEqual(game_started, self.cli.command("start", GM), "Failed to Start Game")
        self.assertEqual(game_ended, self.cli.command("end", GM), "Failed to End Game")
        self.assertEqual(game_create, self.cli.command("create", GM), "Failed to Create Game after Ending")


class TestAddLandmark(TestCase):
    def setUp(self):
        self.cli = CLI(COMMANDS)
        self.assertEqual(game_create, self.cli.command("create", GM), "Failed to Create Game")
        self.assertEqual(team_add, self.cli.command("addteam Team1 1526", GM), "setup failed")

    def test_add_landmark_is_gm(self):
        self.assertEqual(landmark_add,
                         self.cli.command('addlandmark "New York" "Gift given by the French" "Statue of Liberty"', GM),
                         landmark_add_fail)

    def test_add_landmark_not_gm(self):
        self.assertEqual(permission_denied,
                         self.cli.command('addlandmark "New York" "Gift given by the French" "Statue of Liberty"',
                                          "Team1"),
                         "Only admin can add landmarks")

    def test_add_landmark_duplicate(self):
        self.assertEqual(landmark_add,
                         self.cli.command('addlandmark "New York" "Gift given by the French" "Statue of Liberty"', GM),
                         landmark_add_fail)
        self.assertEqual(landmark_add_fail,
                         self.cli.command('addlandmark "New York" "Gift given by the French" "Statue of Liberty"', GM),
                         "no duplicate landmarks")

    def test_add_landmark_before_game_created(self):
        self.cli.game = None
        self.assertEqual(landmark_add_fail,
                         self.cli.command('addlandmark "New York" "Gift given by the French" "Statue of Liberty"', GM),
                         "add landmark only after game is created")

    def test_add_landmark_bad_args(self):
        self.assertEqual(invalid_param, self.cli.command("addlandmark", GM), invalid_param)


class TestRemoveLandmark(TestCase):
    # pylint: disable=protected-access,no-member
    def setUp(self):
        self.cli = CLI(COMMANDS)
        self.assertEqual(game_create, self.cli.command("create", GM), "Failed to create game")
        self.assertEqual(team_add, self.cli.command("addteam Team1 1526", GM), "setup failed")
        self.assertEqual(landmark_add,
                         self.cli.command('addlandmark "New York" "Gift given by the French" "Statue of Liberty"', GM),
                         landmark_add_fail)
        self.assertEqual(landmark_add,
                         self.cli.command('addlandmark "UWM" "Place we purchase coffee from" "Grind"', GM),
                         landmark_add_fail)

    def test_remove_landmark_is_gm(self):
        self.assertEqual(landmark_remove, self.cli.command("removelandmark UWM", GM), "Failed to remove landmark")

    def test_remove_landmark_is_not_gm(self):
        self.assertEqual(permission_denied, self.cli.command('removelandmark "New York"', "Team1"),
                         "only game maker can remove")

    def test_remove_landmark_does_not_exist(self):
        self.cli.game._Game__landmarks.pop()
        self.assertEqual(landmark_remove_fail, self.cli.command("removelandmark UWM", GM), "landmark does not exist")

    def test_remove_landmark_from_empty_landmark_list(self):
        self.cli.game._Game__landmarks.clear()
        self.assertEqual(landmark_remove_fail, self.cli.command("removelandmark UWM", GM), "list of teams empty")

    def test_remove_landmark_bad_args(self):
        self.assertEqual(invalid_param, self.cli.command("removelandmark", GM), invalid_param)


class TestEditLandmarkOrder(TestCase):
    def setUp(self):
        self.cli = CLI(COMMANDS)
        self.assertEqual(game_create, self.cli.command("create", GM), "Failed to create game")
        self.assertEqual(team_add, self.cli.command("addteam Team1 1526", GM), "setup failed")
        self.assertEqual(landmark_add,
                         self.cli.command('addlandmark "New York" "Gift given by the French" "Statue of Liberty"', GM),
                         landmark_add_fail)
        self.assertEqual(landmark_add,
                         self.cli.command('addlandmark "UWM" "Place we purchase coffee from" "Grind"', GM),
                         landmark_add_fail)
        self.assertEqual(landmark_add,
                         self.cli.command('addlandmark "Los Angeles" "Where the Lakers play" "Staples Center"', GM),
                         landmark_add_fail)
        self.assertEqual(landmark_add,
                         self.cli.command('addlandmark "Milwaukee" "Where the Brewers play" "Miller Park"', GM),
                         landmark_add_fail)

    def test_swap_landmark_is_gm(self):
        self.assertEqual(edit_landmark_order_success, self.cli.command("editlandmarkorder 0 3", GM),
                         "Failed to change landmark order")

    def test_swap_landmark_is_not_gm(self):
        self.assertEqual(permission_denied, self.cli.command("editlandmarkorder 0 3", "Team1"),
                         "only game maker can remove")

    def test_swap_landmark_invalid_index(self):
        self.assertEqual(edit_landmark_order_fail, self.cli.command("editlandmarkorder -10 3", GM),
                         "Failed to change landmark order")

    def test_swap_landmark_invalid_index_v2(self):
        self.assertEqual(edit_landmark_order_fail, self.cli.command("editlandmarkorder 10 2", GM),
                         "Failed to change landmark order")

    def test_swap_cannot_convert_to_int(self):
        self.assertEqual(invalid_param, self.cli.command("editlandmarkorder 3 blah", GM),
                         "input is not an integer")

    def test_swap_landmark_after_game_is_not_new(self):
        self.assertEqual(game_started, self.cli.command("start", GM), "Failed to start game.")
        self.assertEqual(game_ended, self.cli.command("end", GM), "Failed to end game.")
        self.assertEqual(edit_landmark_order_fail, self.cli.command("editlandmarkorder 2 3", GM),
                         "Failed to change landmark order")

    def test_swap_landmark_bad_args(self):
        self.assertEqual(invalid_param, self.cli.command("editlandmarkorder", GM), invalid_param)


class TestEditLandmark(TestCase):
    def setUp(self):
        self.cli = CLI(COMMANDS)
        self.assertEqual(game_create, self.cli.command("create", GM), "Failed to create game")
        self.assertEqual(team_add, self.cli.command("addteam Team1 1526", GM), "setup failed")
        self.assertEqual(landmark_add,
                         self.cli.command('addlandmark "New York" "Gift given by the French" "Statue of Liberty"', GM),
                         landmark_add_fail)
        self.assertEqual(landmark_add, self.cli.command('addlandmark "UWM" "Place we purchase coffee from" "Grind"',
                                                        GM),
                         landmark_add_fail)

    def test_edit_landmark_is_gm(self):
        self.assertEqual(edit_landmark_success,
                         self.cli.command('editlandmark "UWM" clue "New York" question "Where the Beastie Boys were ' +
                                          'going without sleep" answer "Brooklyn"', GM),
                         edit_landmark_fail)

    def test_edit_landmark_is_not_gm(self):
        self.assertEqual(permission_denied,
                         self.cli.command('editlandmark "UWM" clue "New York" question "Where the Beastie Boys were ' +
                                          'going without sleep" answer "Brooklyn"', "Team1"))

    def test_edit_landmark_clue_only(self):
        self.assertEqual(edit_landmark_success, self.cli.command('editlandmark "UWM" clue "New York"', GM),
                         edit_landmark_fail)

    def test_edit_landmark_question_only(self):
        self.assertEqual(edit_landmark_success, self.cli.command(
            'editlandmark "UWM" question "Where the Beastie Boys were going without sleep"', GM), edit_landmark_fail)

    def test_edit_landmark_answer_only(self):
        self.assertEqual(edit_landmark_success, self.cli.command('editlandmark "UWM" answer "Brooklyn"', GM),
                         edit_landmark_fail)

    def test_edit_landmark_clue_and_answer_only(self):
        self.assertEqual(edit_landmark_success,
                         self.cli.command('editlandmark "UWM" clue "New York" answer "Brooklyn"', GM),
                         edit_landmark_fail)

    def test_edit_landmark_clue_and_question_only(self):
        self.assertEqual(edit_landmark_success, self.cli.command(
            'editlandmark "UWM" clue "New York" question "Where the Beastie Boys were going without sleep"', GM),
                         edit_landmark_fail)

    def test_edit_landmark_question_and_answer_only(self):
        self.assertEqual(edit_landmark_success, self.cli.command(
            'editlandmark "UWM" question "Where the Beastie Boys were going without sleep" answer "Brooklyn"', GM),
                         edit_landmark_fail)

    def test_edit_landmark_bad_args(self):
        self.assertEqual(invalid_param, self.cli.command("editlandmark", GM), invalid_param)


class TestGetClue(TestCase):
    def setUp(self):
        self.cli = CLI(COMMANDS)
        self.assertEqual(game_create, self.cli.command("create", GM), "Failed to create game")
        self.assertEqual(team_add, self.cli.command("addteam Team1 1526", GM), "setup failed")
        self.assertEqual(landmark_add,
                         self.cli.command('addlandmark "New York" "Gift given by the French" "Statue of Liberty"', GM),
                         "Failed to add landmark")
        self.assertEqual(landmark_add,
                         self.cli.command('addlandmark "UWM" "Place we purchase coffee from" "Grind"', GM),
                         "Failed to add landmark")

    def test_admin(self):
        self.assertEqual(permission_denied, self.cli.command("getclue", GM), "Clue returned for admin")

    def test_correctly(self):
        self.assertEqual(game_started, self.cli.command("start", GM), "Failed to start game.")
        self.assertEqual("New York", self.cli.command("getclue", "Team1"), "Wrong clue returned")

    def test_after_answer(self):
        self.assertEqual(game_started, self.cli.command("start", GM), "Failed to start game.")
        self.assertEqual("That is Correct! The Next Question is: \nPlace we purchase coffee from",
                         self.cli.command("answer 'Statue of Liberty'", "Team1"), "Answer didn't work")
        self.assertEqual("UWM", self.cli.command("getclue", "Team1"), "Wrong clue returned")


class TestQuitQuestion(TestCase):
    def setUp(self):
        self.cli = CLI(COMMANDS)
        self.assertEqual(game_create, self.cli.command("create", GM), "Failed to create game")
        self.assertEqual(team_add, self.cli.command("addteam Team1 1526", GM), "setup failed")
        self.assertEqual(landmark_add,
                         self.cli.command('addlandmark "New York" "Gift given by the French" "Statue of Liberty"', GM),
                         landmark_add_fail)
        self.assertEqual(landmark_add, self.cli.command('addlandmark "UWM" "Place we purchase coffee from" "Grind"',
                                                        GM),
                         landmark_add_fail)
        self.assertEqual(game_started, self.cli.command("start", GM), "Failed to start game.")

    def test_game_ended(self):
        self.assertEqual(game_ended, self.cli.command("end", GM), "Incorrect Message when ending game")
        self.assertEqual(no_game_running, self.cli.command("giveup Team1 1526", "Team1"), "Allowed giveup with no game")

    def test_admin(self):
        self.assertEqual("You're Not Playing!", self.cli.command("giveup gamemaker 1234", GM),
                         "Gamemaker might have just given up, oh no")

    def test_incorrect_pass(self):
        self.assertEqual(permission_denied, self.cli.command("giveup Team1 15s6", "Team1"),
                         "Incorrect Message when giving up with wrong password")

    def test_incorrect_user(self):
        self.assertEqual(permission_denied, self.cli.command("giveup Teamp 1526", "Team1"),
                         "Incorrect Message when giving up with wrong password")

    def test_quit(self):
        # pylint: disable=protected-access,no-member
        self.cli.current_user = Team.objects.get(username="Team1")
        question = self.cli.game._Game__landmarks[self.cli.current_user.current_landmark+1].question
        self.assertEqual("Question Quit, Your Next Question: \n{}".format(question),
                         self.cli.command("giveup Team1 1526", "Team1"), "Could not quit question with proper login")

    def test_quit_bad_args(self):
        self.assertEqual("Proper Format giveup <username> <password>", self.cli.command("giveup teamp", "Team1"),
                         "Not enough args did not show correct message")


class TestGetStatus(TestCase):
    # pylint: disable=protected-access,no-member
    def setUp(self):
        self.cli = CLI(COMMANDS)
        self.assertEqual(game_create, self.cli.command("create", GM), "Failed to create game")
        self.assertEqual(team_add, self.cli.command("addteam Team1 1526", GM), "setup failed")
        self.assertEqual(team_add, self.cli.command("addteam Team2 1526", GM), "setup failed")
        self.assertEqual(landmark_add,
                         self.cli.command('addlandmark "New York" "Gift given by the French" "Statue of Liberty"', GM),
                         landmark_add_fail)
        self.assertEqual(landmark_add, self.cli.command('addlandmark "UWM" "Place we purchase coffee from" "Grind"',
                                                        GM),
                         landmark_add_fail)
        self.assertEqual(game_started, self.cli.command("start", GM), "Failed to start game.")

    def test_no_game(self):
        self.assertEqual(game_ended, self.cli.command("end", GM), "Incorrect Message when ending game")
        self.assertEqual(no_game_running, self.cli.command("getstats Team1", "Team1"),
                         "Get Stats wroked with noone logged in")

    def test_admin(self):
        tt = datetime.timedelta(days=0, hours=0, minutes=0, seconds=0)
        for t in self.cli.game._Game__teams["Team1"].time_log.all():
            tt += t
        currenttimecalc = (timezone.now() - self.cli.game._Game__teams["Team1"].clue_time)
        stat_str = 'Points:{};You Are On Landmark:{};Current Landmark Elapsed Time:{};Time Taken For Landmarks:{}'
        self.cli.current_user = Team.objects.get(username="Team1")
        self.assertEqual(stat_str.format(self.cli.current_user.points, self.cli.current_user.current_landmark+1,
                                         str(currenttimecalc).split(".")[0], tt),
                         self.cli.command("getstats Team1", "Team1"), "Admin Couldn't user get stats")

    def test_user(self):
        tt = datetime.timedelta(days=0, hours=0, minutes=0, seconds=0)
        for t in self.cli.game._Game__teams["Team1"].time_log.all():
            tt += t
        current_time_calc = (timezone.now() - self.cli.game._Game__teams["Team1"].clue_time)
        stat_str = 'Points:{};You Are On Landmark:{};Current Landmark Elapsed Time:{};Time Taken For Landmarks:{}'
        self.assertEqual(stat_str.format(self.cli.game.get_team("Team1").points,
                                         self.cli.game.get_team("Team1").current_landmark + 1,
                                         str(current_time_calc).split(".")[0], tt),
                         self.cli.command("getstats Team1", GM), "Admin Couldn't get user stats")

    def test_not_user(self):
        self.assertEqual("You cannot see another users stats", self.cli.command("getstats Team1", "Team2"),
                         "Get Stats wroked with noone logged in")

    def test_bad_args(self):
        self.assertEqual("Invalid parameters", self.cli.command("getstats", "Team1"), "CLI took improper args")


class TestAnswerQuestion(TestCase):
    # pylint: disable=protected-access,no-member
    def setUp(self):
        self.cli = CLI(COMMANDS)
        self.assertEqual(game_create, self.cli.command("create", GM), "Failed to create game")
        self.assertEqual(team_add, self.cli.command("addteam Team1 1526", GM), "setup failed")
        self.assertEqual(team_add, self.cli.command("addteam Team2 1526", GM), "setup failed")
        self.assertEqual(landmark_add, self.cli.command(
            'addlandmark "New York" "Gift given by the French" "Statue of Liberty"', GM), landmark_add_fail)
        self.assertEqual(landmark_add, self.cli.command('addlandmark "UWM" "Place we purchase coffee from" "Grind"',
                                                        GM),
                         landmark_add_fail)
        self.assertEqual(landmark_add, self.cli.command('addlandmark "Last Mark" "The Last Answer" "Last"', GM),
                         landmark_add_fail)
        self.assertEqual(game_started, self.cli.command("start", GM), "Failed to start game.")
        self.cli.current_user = Team.objects.get(username="Team1")

    def test_no_game(self):
        self.assertEqual(game_ended, self.cli.command("end", GM), "Incorrect Message when ending game")
        self.assertEqual(no_game_running, self.cli.command("answer 'Statue of Liberty'", "Team1"),
                         "allowed answer with no game running")

    def test_admin(self):
        self.assertEqual("You're Not Playing!", self.cli.command("answer 'Statue of Liberty'", GM),
                         "Gamemaker just answered his own question!")

    def test_bad_args(self):
        self.assertEqual("Invalid parameters", self.cli.command("answer", "Team1"), "CLI took improper args")

    def test_answer_incorrect(self):
        question = self.cli.game._Game__landmarks[self.cli.current_user.current_landmark].question
        self.assertEqual("Incorrect Answer! The Question Was: \n{}".format(question),
                         self.cli.command("answer 'this is so very wrong'", "Team1"),
                         "Incorrect answer did not print correct response")

    def test_answer_correct(self):
        question = self.cli.game._Game__landmarks[self.cli.current_user.current_landmark+1].question
        self.assertEqual("That is Correct! The Next Question is: \n{}".format(question),
                         self.cli.command("answer 'Statue of Liberty'", "Team1"),
                         "Correct answer did not print correct response")

    def test_answer_correcttwice(self):
        question = self.cli.game._Game__landmarks[self.cli.current_user.current_landmark+1].question
        self.assertEqual("That is Correct! The Next Question is: \n{}".format(question),
                         self.cli.command("answer 'Statue of Liberty'", "Team1"),
                         "Correct answer did not print correct response")
        question = self.cli.game._Game__landmarks[self.cli.current_user.current_landmark+1].question
        self.assertEqual("That is Correct! The Next Question is: \n{}".format(question),
                         self.cli.command("answer Grind", "Team1"), "Correct answer did not print correct response")

    def test_answer_last_question(self):
        question = self.cli.game._Game__landmarks[self.cli.current_user.current_landmark+1].question
        self.assertEqual("That is Correct! The Next Question is: \n{}".format(question),
                         self.cli.command("answer 'Statue of Liberty'", "Team1"),
                         "Correct answer did not print correct response")
        question = self.cli.game._Game__landmarks[self.cli.current_user.current_landmark+1].question
        self.assertEqual("That is Correct! The Next Question is: \n{}".format(question),
                         self.cli.command("answer Grind", "Team1"), "Correct answer did not print correct response")
        self.assertEqual("That is Correct! There are no more landmarks!", self.cli.command("answer 'Last'", "Team1"),
                         "Correct answer did not print correct response")

    def test_answer_pass_last_question(self):
        question = self.cli.game._Game__landmarks[self.cli.current_user.current_landmark+1].question
        self.assertEqual("That is Correct! The Next Question is: \n{}".format(question),
                         self.cli.command("answer 'Statue of Liberty'", "Team1"),
                         "Correct answer did not print correct response")
        question = self.cli.game._Game__landmarks[self.cli.current_user.current_landmark+1].question
        self.assertEqual("That is Correct! The Next Question is: \n{}".format(question),
                         self.cli.command("answer Grind", "Team1"), "Correct answer did not print correct response")
        self.assertEqual("That is Correct! There are no more landmarks!", self.cli.command("answer Last", "Team1"),
                         "Correct answer did not print correct response")
        self.assertEqual("There are no more landmarks!", self.cli.command("answer 'Last'", "Team1"),
                         "Correct answer did not print correct response")

    def test_answer_right_wrong_right(self):
        question = self.cli.game._Game__landmarks[self.cli.current_user.current_landmark+1].question
        self.assertEqual("That is Correct! The Next Question is: \n{}".format(question),
                         self.cli.command("answer 'Statue of Liberty'", "Team1"),
                         "Correct answer did not print correct response")
        question = self.cli.game._Game__landmarks[self.cli.current_user.current_landmark].question
        self.assertEqual("Incorrect Answer! The Question Was: \n{}".format(question),
                         self.cli.command("answer 'this is so very wrong'", "Team1"),
                         "Incorrect answer did not print correct response")
        question = self.cli.game._Game__landmarks[self.cli.current_user.current_landmark+1].question
        self.assertEqual("That is Correct! The Next Question is: \n{}".format(question),
                         self.cli.command("answer 'Grind'", "Team1"), "Correct answer did not print correct response")

    def test_answer_team1_team2(self):
        question = self.cli.game._Game__landmarks[self.cli.current_user.current_landmark+1].question
        self.assertEqual("That is Correct! The Next Question is: \n{}".format(question),
                         self.cli.command("answer 'Statue of Liberty'", "Team1"),
                         "Correct answer did not print correct response")
        self.cli.current_user = Team.objects.get(username="Team2")
        question = self.cli.game._Game__landmarks[self.cli.current_user.current_landmark+1].question
        self.assertEqual("That is Correct! The Next Question is: \n{}".format(question),
                         self.cli.command("answer 'Statue of Liberty'", "Team2"),
                         "Correct answer did not print correct response")

    def test_answer_correctteam1_incorrectteam2(self):
        question = self.cli.game._Game__landmarks[self.cli.current_user.current_landmark+1].question
        self.assertEqual("That is Correct! The Next Question is: \n{}".format(question),
                         self.cli.command("answer 'Statue of Liberty'", "Team1"),
                         "Correct answer did not print correct response")
        question = self.cli.game._Game__landmarks[self.cli.current_user.current_landmark+1].question
        self.assertEqual("That is Correct! The Next Question is: \n{}".format(question),
                         self.cli.command("answer 'Grind'", "Team1"), "Correct answer did not print correct response")
        self.cli.current_user = Team.objects.get(username="Team2")
        question = self.cli.game._Game__landmarks[self.cli.current_user.current_landmark].question
        self.assertEqual("Incorrect Answer! The Question Was: \n{}".format(question),
                         self.cli.command("answer 'this is so very wrong'", "Team2"),
                         "Incorrect answer did not print correct response")
        question = self.cli.game._Game__landmarks[self.cli.current_user.current_landmark+1].question
        self.assertEqual("That is Correct! The Next Question is: \n{}".format(question),
                         self.cli.command("answer 'Statue of Liberty'", "Team2"),
                         "Correct answer did not print correct response")


class TestSnapShot(TestCase):
    def setUp(self):
        self.cli = CLI(COMMANDS)
        self.assertEqual(game_create, self.cli.command("create", GM), "Failed to create game")
        self.assertEqual(team_add, self.cli.command("addteam Team1 1526", GM), "setup failed")
        self.assertEqual(team_add, self.cli.command("addteam Team2 1526", GM), "setup failed")
        self.assertEqual(landmark_add,
                         self.cli.command('addlandmark "New York" "Gift given by the French" "Statue of Liberty"', GM),
                         landmark_add_fail)
        self.assertEqual(landmark_add, self.cli.command('addlandmark "UWM" "Place we purchase coffee from" "Grind"',
                                                        GM),
                         landmark_add_fail)

    def test_snapshot_multiple_teams(self):
        self.assertEqual(game_started, self.cli.command("start", GM), "Failed to start game.")
        self.assertEqual("That is Correct! The Next Question is: \n{}".format("Place we purchase coffee from"),
                         self.cli.command("answer 'Statue of Liberty'", "Team1"),
                         "Correct answer did not print correct response")
        self.assertEqual("That is Correct! The Next Question is: \n{}".format("Place we purchase coffee from"),
                         self.cli.command("answer 'Statue of Liberty'", "Team2"),
                         "Correct answer did not print correct response")
        self.assertEqual("That is Correct! There are no more landmarks!", self.cli.command("answer 'Grind'", "Team2"),
                         "Correct answer did not print correct response")
        total_time_list = []
        team_points = []
        for username in self.cli.game._Game__teams:
            current_team = self.cli.game.get_team(username)
            total_time = datetime.timedelta(days=0, hours=0, minutes=0, seconds=0)
            for t in current_team.time_log.all():
                total_time += t.time_delta
            total_time_list.append(total_time)
            team_points.append(current_team.points)
        stat_str_team_1 = "Team: Team1\nYou Are On Landmark 2\nTime Taken For Landmarks: "\
                          + str(total_time_list[0]) +"\nTotal Points: "+str(team_points[0])+"\n"
        stat_str_team_2 = "Team: Team2\nYou Are On Landmark 2\nTime Taken For Landmarks: " \
                          + str(total_time_list[1]) + "\nTotal Points: " + str(team_points[1]) + "\n"
        final_stat_str = stat_str_team_1 + stat_str_team_2
        self.assertEqual(final_stat_str, self.cli.command("snapshot", GM), "Failed to get snapshot!!")

    def test_snapshot_no_game_running(self):
        self.assertEqual(no_game_running, self.cli.command("snapshot", GM), "Failed to get snapshot!!")

    def test_snapshot_not_gm(self):
        self.assertEqual(game_started, self.cli.command("start", GM), "Failed to start game.")
        self.assertEqual(permission_denied, self.cli.command("snapshot", "Team1"), "Not Game Maker!!")
