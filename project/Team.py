import unittest
from abc import ABC
from GameMaker import UserABC

class TeamI(ABC):
    def login(self, password):
        return "", False

    def changeName(self, name):
        self.username = name;

    def changePassword(self, password):
        self.password = password;

    def answer_question(self, answer):
        return ""

    def get_status(self):
        return ""

    def get_clue(self):
        return ""

    def set_username(self, username):
        pass

    def set_pass(self, password):
        pass

    def get_username(self):
        pass

class TeamFactory:
    def getTeam(self, username, password):
        return self.Team(username, password)

    class Team(TeamI, UserABC):
        def __init__(self, username, password):
            self.username = username
            self.password = password

        def login(self, username, password):
            if username == self.username and password == self.password:
                return self.username, False
            return "", False

        def answer_question(self, answer):
            return ""

        def get_status(self):
            return ""

        def get_clue(self):
            return ""

        def get_username(self):
            return self.username


class TestInit(unittest.TestCase):
    def test_init(self):
        self.team = TeamFactory().getTeam("TeamA", "2123")
        self.assertEqual("TeamA", self.team.username, "username value improperly set")
        self.assertEqual("2123", self.team.password, "password value improperly set")


class TestGetAnswer(unittest.TestCase):
    def test_get_answer(self):
        self.team = TeamFactory().getTeam("TeamA", "2123")
        self.assertEqual("TeamA", self.team.get_username(), "getter does not work")

class TestTeam(unittest.TestCase):
    def setUp(self):
        self.team = TeamFactory().getTeam("team1", "password123")

    def test_team_login_success(self):
        username, isadmin = self.team.login("team1", "password123")

        self.assertEquals(self.team.username, username)
        self.assertFalse(isadmin)

    def test_team_login_fail(self):
        username, isadmin = self.team.login("team1", "wrongpassword")
        self.assertEquals("", username)
        self.assertFalse(isadmin)

    def test_change_name(self):
        self.team.changeName("team2")
        username, isadmin = self.team.login("team2", "password123")

        self.assertEquals(self.team.username, username)
        self.assertFalse(isadmin)

    def test_change_password(self):
        self.team.changePassword("random")

        username, isadmin = self.team.login("team1", "random")
        self.assertEquals(self.team.username, username)
        self.assertFalse(isadmin)

if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestInit))
    suite.addTest(unittest.makeSuite(TestGetAnswer))
    suite.addTest(unittest.makeSuite(TestTeam))
    runner = unittest.TextTestRunner()
    res = runner.run(suite)
    print(res)
    print("*" * 20)
    for i in res.failures: print(i[1])
