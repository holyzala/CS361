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


class TestGetAnswer(unittest.TestCase):
    def test_get_answer(self):
        self.team = TeamFactory().getTeam("TeamA", "2123")
        self.assertEqual("TeamA", self.team.get_username(), "getter does not work")


class TestTeam(unittest.TestCase):
    def setUp(self):
        self.team = TeamFactory().getTeam("team1", "password123")

    def test_team_login_success(self):
        user = self.team.login("team1", "password123")
        self.assertEqual(self.team, user, "Different user returned")
        self.assertEquals(self.team.username, user.username)
        self.assertFalse(user.is_admin())

    def test_team_login_fail(self):
        user = self.team.login("team1", "wrongpassword")
        self.assertEqual(None, user, "Invalid user returned")

    def test_change_name(self):
        self.team.changeName("team2")
        user = self.team.login("team2", "password123")
        self.assertEqual(self.team, user, "Wrong user returned")
        self.assertEquals(self.team.username, user.username, "Wrong username")
        self.assertFalse(user.is_admin(), "Invalid admin rights")

    def test_change_password(self):
        self.team.changePassword("random")
        user = self.team.login("team1", "random")
        self.assertEqual(self.team, user, "Wrong user returned")
        self.assertEquals(self.team.username, user.username, "Wrong username")
        self.assertFalse(user.is_admin(), "Invalid admin rights")


if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestInit))
    suite.addTest(unittest.makeSuite(TestGetAnswer))
    suite.addTest(unittest.makeSuite(TestGetters))
    suite.addTest(unittest.makeSuite(TestTeam))
    runner = unittest.TextTestRunner()
    res = runner.run(suite)
    print(res)
    print("*" * 20)
    for i in res.failures: print(i[1])
