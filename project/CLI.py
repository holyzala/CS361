import unittest
import shlex

from Game import GameFactory
from GameMaker import GMFactory


def need_admin(func):
    def wrapper(*args):
        if not args[0].current_user or not args[0].current_user.is_admin():
            return "Permission denied"
        return func(*args)

    return wrapper


class CLI:
    def __init__(self):
        self.gm = GMFactory().get_gm()
        self.current_user = None
        self.game = None

    def __login(self, args):
        if self.current_user:
            return "Already logged in"
        try:
            self.current_user = self.gm.login(args[1], args[2])
            if self.current_user:
                return "Login successful"
            if self.game:
                for team in self.game.teams:
                    self.current_user = team.login(args[1], args[2])
                    if self.current_user:
                        return "Login successful"
        except IndexError:
            return "Invalid parameters"
        return "Login failed"

    def __logout(self, _):
        if not self.current_user:
            return "No user logged in"
        self.current_user = None
        return "Logged out"

    @need_admin
    def __addteam(self, args):
        try:
            added = self.game.add_team(args[1], args[2])
        except IndexError:
            return "Invalid parameters"
        if added:
            return "Team added"
        return "Failed to add team"

    @need_admin
    def __removeteam(self, args):
        try:
            removed = self.game.remove_team(args[1])
        except IndexError:
            return "Invalid parameters"
        if removed:
            return "Removed Team"
        return "Remove Team Failed"

    @need_admin
    def __addlandmark(self, args):
        try:
            added = self.game.add_landmark(args[1],args[2],args[3])
        except IndexError:
            return "Invalid parameters"
        if added:
            return "Added landmark"
        return "Failed to add landmark"

    @need_admin
    def __start(self, _):
        try:
            started = self.game.start()
        except IndexError:
            return "Invalid parameters"
        if started:
            return "Started Game"
        return "Failed to start Game"

    @need_admin
    def __create(self, args):
        try:
            self.game = GameFactory().getGame()
        except IndexError:
            return "Invalid Parameters"
        if self.game:
            return "Game Created"
        return "Game Failed"

    def command(self, args):
        commands = {"login": self.__login, "addteam": self.__addteam, "addlandmark": self.__addlandmark,
                    "removeteam": self.__removeteam, "start": self.__start, "create": self.__create,
                    "logout": self.__logout}
        inp = shlex.split(args)
        try:
            return commands[inp[0].lower()](inp)
        except (KeyError, IndexError):
            return "Invalid command"


class TestGMLogin(unittest.TestCase):
    def setUp(self):
        self.cli = CLI()

    def test_login_success(self):
        self.assertEqual("Login successful", self.cli.command("login gamemaker 1234"), "Login message not correct")

    def test_login_bad_password(self):
        self.assertEqual("Login failed", self.cli.command("login gamemaker 4321"), "Login return message not correct")

    def test_login_bad_username(self):
        self.assertEqual("Login failed", self.cli.command("login ___ 1234"), "Login return message not correct")

    def test_login_bad_args(self):
        self.assertEqual("Invalid parameters", self.cli.command("login gamemaker"), "Invalid parameters")


class TestTeamExistsLogin(unittest.TestCase):
    def setUp(self):
        self.cli = CLI()
        self.assertEqual("Login successful", self.cli.command("login gamemaker 1234"), "Valid login failed")
        self.assertEqual("Game Created", self.cli.command("create game"), "Failed to create game")
        self.assertEqual("Team added", self.cli.command("addteam teamName teamPassword"), "Failed to add Team")
        self.assertEqual("Logged out", self.cli.command("logout"), "Failed to log out")

    def test_login_success(self):
        self.assertEqual("Login successful", self.cli.command("login teamName teamPassword"), "Valid login failed")

    def test_login_bad_password(self):
        self.assertEqual("Login failed", self.cli.command("login teamName 1234"), "Invalid login succeeded")

    def test_login_bad_username(self):
        self.assertEqual("Login failed", self.cli.command("login ___ teamPassword"), "Invalid login succeeded")


class TestTeamNotExistsLogin(unittest.TestCase):
    def setUp(self):
        self.cli = CLI()
        self.assertEqual("Login successful", self.cli.command("login gamemaker 1234"), "Valid login failed")
        self.assertEqual("Game Created", self.cli.command("create game"), "Failed to create game")
        self.assertEqual("Logged out", self.cli.command("logout"), "Failed to log out")

    def test_login(self):
        self.assertEqual("Login failed", self.cli.command("login teamName teamPassword"), "Invalid login failed")


class TestEditTeams(unittest.TestCase):
    def setUp(self):
        self.cli = CLI()
        self.assertEqual("Login successful", self.cli.command("login gamemaker 1234"), "Login message not correct")
        self.assertEqual("Game Created", self.cli.command("create game"), "Failed to create game")
        self.assertEqual("Team added", self.cli.command("Addteam teamName teamPassword"))

    def test_team_edit_name(self):
        self.assertEqual("Team name changed", self.cli.command("Edit teamName name newName"))

    def test_team_edit_password(self):
        self.assertEqual("Team password changed", self.cli.command("Edit TeamName password newPassword"))


class TestAddTeam(unittest.TestCase):
    def setUp(self):
        self.cli = CLI()
        self.assertEqual("Login successful", self.cli.command("login gamemaker 1234"), "Login message not correct")
        self.assertEqual("Game Created", self.cli.command("create game"), "Failed to create game")

    def test_add_team_is_gm(self):
        self.assertEqual("Team added", self.cli.command("addTeam Team1 1234"), "Failed to add team")

    def test_add_team_not_gm(self):
        self.assertEqual("Logged out", self.cli.command("logout"), "Failed to logout")
        self.assertEqual("Permission denied", self.cli.command("addTeam Team1 1234"), "Only game maker can add teams")

    def test_add_team_duplicate(self):
        self.assertEqual("Team added", self.cli.command("addTeam Team1 1234"), "Failed to add team")
        self.assertEqual("Failed to add team", self.cli.command("addTeam Team1 1234"),
                         "can not have duplicate teams")

    def test_add_team_bad_args(self):
        self.assertEqual("Invalid parameters", self.cli.command("addTeam"), "Invalid parameters")


class TestRemoveTeam(unittest.TestCase):
    def setUp(self):
        self.cli = CLI()
        self.assertEqual("Login successful", self.cli.command("login gamemaker 1234"), "Login message not correct")
        self.assertEqual("Game Created", self.cli.command("create game"), "Failed to create game")
        self.assertEqual("Team added", self.cli.command("addTeam Team1 1526"), "setup failed")
        self.assertEqual("Team added", self.cli.command("addTeam Team2 02ka"), "setup failed")
        self.assertEqual("Team added", self.cli.command("addTeam Team3 192j"), "setup failed")

    def test_remove_team_is_gm(self):
        self.assertEqual("Removed Team", self.cli.command("remove Team1"), "Failed to remove team")

    def test_remove_team_is_not_gm(self):
        self.assertEqual("Logged out", self.cli.command("logout"), "Failed to logout")
        self.assertEqual("Remove Team Failed", self.cli.command("remove Team1"), "only game maker can remove")

    def test_remove_team_does_not_exist(self):
        self.cli.game.teams.pop()
        self.assertEqual("Remove Team Failed", self.cli.command("remove Team3"), "team does not exist")

    def test_remove_team_from_empty_team_list(self):
        self.cli.game.teams.clear()
        self.assertEqual("Remove Team Failed", self.cli.command("remove Team1"), "list of teams empty")

    def test_remove_team_bad_args(self):
        self.cli.is_gm = True
        self.assertEqual("Invalid parameters", self.cli.command("remove"), "Invalid parameters")


class TestStartGame(unittest.TestCase):
    def setUp(self):
        self.cli = CLI()
        self.assertEqual("Login successful", self.cli.command("login gamemaker 1234"), "Login message not correct")
        self.assertEqual("Game Created", self.cli.command("create game"), "Failed to create game")
        self.assertEqual("Team added", self.cli.command("addTeam Team1 1526"), "setup failed")
        self.assertEqual("Team added", self.cli.command("addTeam Team2 02ka"), "setup failed")
        self.assertEqual("Added landmark",
                         self.cli.command('addlandmark "New York" "Gift given by the French" "Statue of Liberty"'),
                         "Failed to add landmark")

    def test_start_game_is_gm(self):
        self.assertEqual("Started Game", self.cli.command("start"), "Failed to start game")

    def test_start_game_is_not_gm(self):
        self.assertEqual("Logged out", self.cli.command("logout"), "Failed to logout")
        self.assertEqual("Permission denied", self.cli.command("start"), "Only admin can not start a Game")

    def test_start_team_bad_args(self):
        self.assertEqual("Invalid parameters", self.cli.command(""), "Invalid parameters")


class TestCreate(unittest.TestCase):
    def setUp(self):
        self.cli = CLI()
        self.assertEqual("Login successful", self.cli.command("login gamemaker 1234"), "Login message not correct")

    def test_create_is_gm(self):
        self.assertEqual(None, self.game)
        self.assertEqual("Game Created". self.cli.command("create"), "Failed to Create Game")

    def test_create_not_gm(self):
        self.assertEqual("Logged out", self.cli.command("logout"), "Failed to logout")
        self.assertEqual("Permission denied", self.cli.command("create"), "Only admin can Create a new Game")


class TestAddLandmark(unittest.TestCase):
    def setUp(self):
        self.cli = CLI()
        self.assertEqual("Login successful", self.cli.command("login gamemaker 1234"), "Login message not correct")
        self.assertEqual("Game Created", self.cli.command("create"), "Failed to Create Game")

    def test_add_landmark_is_gm(self):
        self.assertEqual("Added landmark",
                         self.cli.command('addlandmark "New York" "Gift given by the French" "Statue of Liberty"'),
                         "Failed to add landmark")

    def test_add_landmark_not_gm(self):
        self.assertEqual("Logged out", self.cli.command("logout"), "Failed to logout")
        self.assertEqual("Permission denied",
                         self.cli.command('addlandmark "New York" "Gift given by the French" "Statue of Liberty"'),
                         "Only admin can add landmarks")

    def test_add_landmark_duplicate(self):
        self.assertEqual("Added landmark",
                         self.cli.command('addlandmark "New York" "Gift given by the French" "Statue of Liberty"'),
                         "Failed to add landmark")
        self.assertEqual("Failed to add landmark",
                         self.cli.command('addlandmark "New York" "Gift given by the French" "Statue of Liberty"'),
                         "no duplicate landmarks")

    def test_add_landmark_bad_args(self):
        self.assertEqual("Invalid parameters", self.cli.command("addlandmark"), "Invalid parameters")


if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestGMLogin))
    suite.addTest(unittest.makeSuite(TestTeamExistsLogin))
    suite.addTest(unittest.makeSuite(TestTeamNotExistsLogin))
    suite.addTest(unittest.makeSuite(TestEditTeams))
    suite.addTest(unittest.makeSuite(TestAddTeam))
    suite.addTest(unittest.makeSuite(TestRemoveTeam))
    suite.addTest(unittest.makeSuite(TestStartGame))
    suite.addTest(unittest.makeSuite(TestAddLandmark))
    runner = unittest.TextTestRunner()
    res = runner.run(suite)
    print(res)
    print("*" * 20)
    for i in res.failures: print(i[1])
