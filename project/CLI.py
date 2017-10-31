import unittest
import shlex
from GameMaker import GMFactory


class CLI:
    def __init__(self):
        self.gm = GMFactory().getGM()
        self.current_user = ""
        self.is_gm = False
        self.game = None

    def __login(self, args):
        try:
            self.current_user, self.is_gm = self.gm.login(args[1], args[2])
        except IndexError:
            return "Invalid parameters"
        if self.current_user is "":
            return "Login failed"
        return "Login successful"

    def __create_game(self, args):
        try:
            self.gm = self.game.start(args[1])
        except IndexError:
            return "Invalid Parameters"
        if self.is_gm is False:
            return "Game Creation Failed"
        return "Game Creation Success"

    def command(self, args):
        commands = {"login": self.__login, "creategame" :self.__create_game}
        inp = shlex.split(args)
        try:
            return commands[inp[0].lower()](inp)
        except KeyError:
            return "Invalid command"


class TestGMLogin(unittest.TestCase):
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

class TestCreateGame(unittest.TestCase):
    def setUp(self):
        self.cli = CLI()

    def test_create_game_success(self):
        self.assertEquals("Game Creation Success", self.cli.command("creategame"), "GameCreate message not correct")

    def test_create_game_bad_args(self):
        self.assertEqual("Invalid Parameters", self.cli.command("create game"), "Invalid Parameters")

if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestGMLogin))
    runner = unittest.TextTestRunner()
    res = runner.run(suite)
    print(res)
    print("*" * 20)
    for i in res.failures: print(i[1])
