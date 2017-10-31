import unittest

from project.Game import GameFactory
from project.GameMaker import GMFactory


class CLI:
    def __init__(self):
        self.gm = GMFactory().getGM()
        self.current_user = ""
        self.is_gm = False
        self.game = GameFactory().getGame()

    def __login(self, args):
        try:
            self.current_user, self.is_gm = self.gm.login(args[1], args[2])
        except IndexError:
            return "Invalid parameters"
        if self.current_user is "":
            return "Login failed"
        return "Login successful"

    def __add_team(self, args):
        return ''

    def __remove_team(self, args):
        return ''

    def __add_landmark(self, args):
        return ''

    def __start(self, args):
        return ''

    def command(self, args):
        commands = {"login": self.__login}
        inp = args.split(" ")
        try:
            return commands[inp[0].lower()](inp)
        except KeyError:
            return "Invalid command"


class TestLogin(unittest.TestCase):
    def setUp(self):
        self.cli = CLI()

    def test_login_success(self):
        self.assertEqual("Login successful", self.cli.command("login gamemaker 1234"), "Login return message not correct")

    def test_login_bad_password(self):
        self.assertEqual("Login failed", self.cli.command("login gamemaker 4321"), "Login return message not correct")

    def test_login_bad_username(self):
        self.assertEqual("Login failed", self.cli.command("login ___ 1234"), "Login return message not correct")

    def test_login_bad_args(self):
        self.assertEqual("Invalid parameters", self.cli.command("login gamemaker"), "Invalid parameters")


class TestAddTeam(unittest.TestCase):
    def setUp(self):
        self.cli = CLI()

    def test_add_team_is_gm(self):
        self.cli.is_gm = True
        self.assertEqual("Added team", self.cli.command("addTeam Team1"), "Failed to add team")

    def test_add_team_not_gm(self):
        self.cli.is_gm = False
        self.assertEqual("Failed to add team", self.cli.command("addTeam Team1"), "Only game maker can add teams")

    def test_add_team_duplicate(self):
        self.cli.is_gm = True
        self.assertEqual("Added team", self.cli.command("addTeam Team1"), "Failed to add team")
        self.assertEqual("Failed to add team", self.cli.command("addTeam Team1"),
                         "can not have duplicate teams")

    def test_add_team_bad_args(self):
        self.cli.is_gm = True
        self.assertEqual("Invalid parameters", self.cli.command("addTeam"), "Invalid parameters")


class TestRemoveTeam(unittest.TestCase):
    def setUp(self):
        from project.Team import TeamFactory #is this allowed? I need it create dummy team objects
        self.cli = CLI()
        self.cli.game.teams.append(TeamFactory().getTeam("Team1", "1526"))
        self.cli.game.teams.append(TeamFactory().getTeam("Team2", "02ka"))
        self.cli.game.teams.append(TeamFactory().getTeam("Team3", "192j"))

    def test_remove_team_is_gm(self):
        self.cli.is_gm = True
        self.assertEqual("Removed Team", self.cli.command("remove Team1"), "Failed to remove team")

    def test_remove_team_is_not_gm(self):
        self.cli.is_gm = False
        self.assertEqual("Remove Team Failed", self.cli.command("remove Team1"), "only game maker can remove")

    def test_remove_team_does_not_exist(self):
        self.cli.is_gm = True
        self.cli.game.teams.pop()
        self.assertEqual("Removed Team Failed", self.cli.command("remove Team3"), "team does not exist")

    def test_remove_team_from_empty_team_list(self):
        self.cli.is_gm = True
        self.cli.game.teams.clear()
        self.assertEqual("Removed Team Failed", self.cli.command("remove Team1"), "list of teams empty")

    def test_remove_team_bad_args(self):
        self.cli.is_gm = True
        self.assertEqual("Invalid parameters", self.cli.command("remove"), "Invalid parameters")


class TestStartGame(unittest.TestCase):
    def setUp(self):
        self.cli = CLI()

    def test_start_game_is_gm(self):
        self.cli.is_gm = True
        self.assertEqual("Started Game", self.cli.command("start"), "Failed to start game")

    def test_start_game_is_not_gm(self):
        self.cli.is_gm = False
        self.assertEqual("Failed to start Game", self.cli.command("start"), "Only admin can not start a Game")

    def test_start_team_bad_args(self):
        self.cli.is_gm = True
        self.assertEqual("Invalid parameters", self.cli.command(""), "Invalid parameters")


# change format of string input, using commas for now.
class TestAddLandmark(unittest.TestCase):
    def setUp(self):
        self.cli = CLI()

    def test_add_landmark_is_gm(self):
        self.cli.is_gm = True
        self.assertEqual("Added landmark",
                         self.cli.command("addLandmark New York, Gift given by the French, Statue of Liberty"),
                         "Failed to add landmark")

    def test_add_landmark_not_gm(self):
        self.cli.is_gm = False
        self.assertEqual("Failed to add landmark",
                         self.cli.command("addLandmark New York, Gift given by the French, Statue of Liberty"),
                         "Only admin can add landmarks")

    def test_add_landmark_duplicate(self):
        from project.Landmark import LandmarkFactory #again is this allowed? Does this violate unit testing rules?
        self.cli.is_gm = True
        self.cli.game.landmarks.append(LandmarkFactory().getLandmark("New York", "Gift given by the French",
                                                                     "Statue of Liberty")) #used here
        self.assertEqual("Failed to add landmark",
                         self.cli.command("addLandmark New York, Gift given by the French, Statue of Liberty"),
                         "no duplicate landmarks")

    def test_add_landmark_bad_args(self):
        self.cli.is_gm = True
        self.assertEqual("Invalid parameters", self.cli.command("addLandmark"), "Invalid parameters")


if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestLogin))
    suite.addTest(unittest.makeSuite(TestAddTeam))
    suite.addTest(unittest.makeSuite(TestRemoveTeam))
    suite.addTest(unittest.makeSuite(TestStartGame))
    suite.addTest(unittest.makeSuite(TestAddLandmark))
    runner = unittest.TextTestRunner()
    res = runner.run(suite)
    print(res)
    print("*" * 20)
    for i in res.failures: print(i[1])
