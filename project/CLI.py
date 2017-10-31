import unittest


class CLI():
    def __init__(self):
        self.gm = None

    def command(self, args):
        return ''


class TestLogin(unittest.TestCase):
    def setUp(self):
        self.cli = CLI()

    def test_login_success(self):
        self.assertEqual("Login successful", self.cli.command("login gamemaker 1234"), "Login return message not correct")

    def test_login_bad_password(self):
        self.assertEqual("Login failed", self.cli.command("login gamemaker 4321"), "Login return message not correct")

    def test_login_bad_username(self):
        self.assertEqual("Login failed", self.cli.command("login ___ 1234"), "Login return message not correct")


if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestLogin))
    runner = unittest.TextTestRunner()
    res = runner.run(suite)
    print(res)
    print("*" * 20)
    for i in res.failures: print(i[1])
