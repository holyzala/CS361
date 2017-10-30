import unittest
from abc import ABC


class GMI(ABC):
    def login(self, username, password):
        pass

    def create_game(self):
        pass


class GMFactory:
    def getGM(self):
        return self.GameMaker()

    class GameMaker(GMI):
        def __init__(self):
            self.username = "gamemaker"
            self.password = "1234"

        def login(self, username, password):
            if self.username == username and self.password == password:
                return self.username, True
            return "", False

        def create_game(self):
            return None


class TestLogin(unittest.TestCase):
    def setUp(self):
        self.gm = GMFactory().getGM()

    def test_login_success(self):
        username, isadmin = self.gm.login("gamemaker", "1234")
        self.assertTrue(isadmin, "Admin flag not set")
        self.assertEqual("gamemaker", username, "Incorrect username returned")

    def test_login_bad_password(self):
        username, isadmin = self.gm.login("gamemaker", "4321")
        self.assertFalse(isadmin, "Admin flag incorrectly set")
        self.assertEqual("", username, "Username has value when it should be empty")

    def test_login_bad_username(self):
        username, isadmin = self.gm.login("___", "1234")
        self.assertFalse(isadmin, "Admin flag incorrectly set")
        self.assertEqual("", username, "Username has value when it should be empty")


if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestLogin))
    runner = unittest.TextTestRunner()
    res = runner.run(suite)
    print(res)
    print("*" * 20)
    for i in res.failures: print(i[1])
