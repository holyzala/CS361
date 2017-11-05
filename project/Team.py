import unittest
from abc import ABC, abstractmethod
from GameMaker import UserABC


class TeamI(ABC):
    @abstractmethod
    def login(self, username, password):
        pass

    @abstractmethod
    def changeName(self, name):
        pass

    @abstractmethod
    def changePassword(self, password):
        pass

    @abstractmethod
    def answer_question(self, answer, cur_time):
        pass

    @abstractmethod
    def get_status(self, cur_time):
        pass

    @abstractmethod
    def get_username(self):
        pass

    @abstractmethod
    def get_points(self):
        pass

    @abstractmethod
    def add_points(self, points):
        pass


class TeamFactory:
    def getTeam(self, username, password):
        return self.Team(username, password)

    class Team(TeamI, UserABC):
        def __init__(self, username, password):
            self.username = username
            self.password = password
            self.points = 0

        def __eq__(self, other):
            return self.username == other.username

        def changeName(self, name):
            self.username = name

        def changePassword(self, password):
            self.password = password

        def login(self, username, password):
            if username is not self.username or password is not self.password:
                return None
            return self

        def answer_question(self, answer, cur_time):
            return ""

        def get_status(self, cur_time):
            return ""

        def get_username(self):
            return self.username

        def get_points(self):
            return self.points

        def set_points(self, points):
            if self.points + points < 0:
                self.points = 0
            else:
                self.points += points

        def is_admin(self):
            return False

        def add_points(self, points):
            pass


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

class TestGetPoints(unittest.TestCase):
    def setUp(self):
        self.team = TeamFactory().getTeam("Team 1", "1234")

    def test_get_points(self):
        self.team.points = 100
        self.assertEqual(100, self.team.get_points(), "Points are not setting properly")

class TestSetPoints(unittest.TestCase):
    def setUp(self):
        self.team = TeamFactory().getTeam("Team 1", "1234")

    def test_add_once_positive(self):
        self.team.set_points(100)
        self.assertEquals(100, self.team.points, "Failed to add 100 points properly")

    def test_add_cumulative_positive(self):
        self.team.set_points(100)
        self.assertEquals(100, self.team.points, "Failed to add 100 points properly")
        self.team.set_points(15)
        self.assertEquals(115, self.team.points, "Failed to add 15 to 100 points properly")

    def test_add_once_negative(self):
        self.team.set_points(-15)
        self.assertEquals(0, self.team.points, "Cannot drop below the 0 threshold")

    def test_add_cumulative_posandneg(self):
        self.team.set_points(100)
        self.assertEquals(100, self.team.points, "Failed to add 100 points properly")
        self.team.set_points(-15)
        self.assertEquals(85, self.team.points, "Failed to remove 15 points properly")

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
