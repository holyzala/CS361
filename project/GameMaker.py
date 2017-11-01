import unittest
from abc import ABC


class UserABC(ABC):
    def login(self, username, password):
        pass

    def is_admin(self):
        pass


class GMFactory:
    def get_gm(self):
        return self.GameMaker()

    class GameMaker(UserABC):
        def __init__(self):
            self.username = "gamemaker"
            self.password = "1234"

        def login(self, username, password):
            if self.username == username and self.password == password:
                return self
            return None

        def is_admin(self):
            return True


class TestLogin(unittest.TestCase):
    def setUp(self):
        self.gm = GMFactory().get_gm()

    def test_login_success(self):
        user = self.gm.login("gamemaker", "1234")
        self.assertEqual(self.gm, user, "Failed to return the same GameMaker object")
        self.assertEqual("gamemaker", user.username, "Username not correct")
        self.assertTrue(user.is_admin(), "Admin rights not correct")

    def test_login_bad_password(self):
        user = self.gm.login("gamemaker", "4321")
        self.assertEqual(None, user, "Bad password return the user object")

    def test_login_bad_username(self):
        user = self.gm.login("___", "1234")
        self.assertEqual(None, user, "Bad username returned the user object")


if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestLogin))
    runner = unittest.TextTestRunner()
    res = runner.run(suite)
    print(res)
    print("*" * 20)
    for i in res.failures: print(i[1])
