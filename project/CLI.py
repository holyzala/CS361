
import unittest
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
    
    
    def test_team_edit_name(self):
        self.assertEqual("Login successful", self.cli.command("login gamemaker 1234"), "Invalid parameters")
        self.assertEqual("Game created", self.cli.command("Create Game"), "Invalid parameters")
        self.assertEqual("Team added", self.cli.command("Add teamName teamPassword")
        self.assertEqual("Team name changed", self.cli.command("Edit teamName name newName")

    def test_team_edit_password(self):
        self.assertEqual("Login successful", self.cli.command("login gamemaker 1234"), "Invalid parameters")
        self.assertEqual("Game created", self.cli.command("Create Game"), "Invalid parameters")
        self.assertEqual("Team added", self.cli.command("Add teamName teamPassword")
        self.assertEqual("Team password changed", self.cli.command("Edit teamName password newPassword")
             

if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestLogin))
    runner = unittest.TextTestRunner()
    res = runner.run(suite)
    print(res)
    print("*" * 20)
    for i in res.failures: print(i[1])
