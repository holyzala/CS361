import unittest
from abc import ABC, abstractmethod
from GameMaker import UserABC


class TeamI(ABC):
    @abstractmethod
    def login(self, password):
        pass

    @abstractmethod
    def changeName(self, name):
        pass

    @abstractmethod
    def changePassword(self, password):
        pass

    @abstractmethod
    def answer_question(self, answer):
        pass

    @abstractmethod
    def get_status(self):
        pass

    @abstractmethod
    def get_username(self):
        pass


class TeamFactory:
    def getTeam(self, username, password):
        return self.Team(username, password)

    class Team(TeamI, UserABC):
        def __init__(self, username, password):
            self.username = username
            self.password = password

        def changeName(self, name):
            self.username = name

        def changePassword(self, password):
            self.password = password

        def login(self, username, password):
            if username == self.username and password == self.password:
                return self
            return None

        def answer_question(self, answer):
            return ""

        def get_status(self):
            return ""

        def get_username(self):
            return self.username

        def is_admin(self):
            return False

        def __eq__(self, other):
            return self.username == other.username


class TestGetters(unittest.TestCase):
    def setUp(self):
        self.username = "TeamA"
        self.password = "2123"
        self.team = TeamFactory().getTeam(self.username, self.password)

    def test_get_username(self):
        self.assertEqual(self.username, self.team.get_username(), "Returned username incorrect")


class TestInit(unittest.TestCase):
    def test_init(self):
        self.team = TeamFactory().getTeam("TeamA", "2123")
        self.assertEqual("TeamA", self.team.username, "username value improperly set")
        self.assertEqual("2123", self.team.password, "password value improperly set")


class TestTeamLogin(unittest.TestCase):
    def setUp(self):
        self.team = TeamFactory().getTeam("team1", "password123")

    def test_team_login_success(self):
        user = self.team.login("team1", "password123")
        self.assertEqual(self.team, user, "Different user returned")
        self.assertEquals(self.team.username, user.username)
        self.assertFalse(user.is_admin())

    def test_team_login_fail(self):
        user = self.team.login("team1", "wrong password")
        self.assertEqual(None, user, "Invalid user returned")


class TestEditTeam(unittest.TestCase):
    def setUp(self):
        self.team = TeamFactory().getTeam("team2", "password123")

    def test_change_name(self):
        self.team.changeName("team zebra")
        self.assertEqual(self.team.username, "team zebra", "username was not changed")

    def test_change_password(self):
        self.team.changePassword("random")
        self.assertEquals(self.team.password, "random", "password was not changed")


if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestInit))
    suite.addTest(unittest.makeSuite(TestGetters))
    suite.addTest(unittest.makeSuite(TestTeamLogin))
    suite.addTest(unittest.makeSuite(TestEditTeam))
    runner = unittest.TextTestRunner()
    res = runner.run(suite)
    print(res)
    print("*" * 20)
    for i in res.failures: print(i[1])
