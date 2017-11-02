import unittest
from abc import ABC
from GameMaker import UserABC


class TeamI(ABC):
    def login(self, password):
        pass

    def changeName(self, name):
        pass

    def changePassword(self, password):
        pass

    def answer_question(self, answer):
        pass

    def get_status(self):
        pass

    def get_clue(self):
        pass

    def get_username(self):
        pass

    def get_points(self):
        pass

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

        def get_clue(self):
            return ""

        def get_username(self):
            return self.username

        def get_points(self):
            return self.team.points

        def set_points(self, points):
            if self.team.points + points is 0:
                self.team.points = 0
            else:
                self.team.points += points


class TestInit(unittest.TestCase):
    def test_init(self):
        self.team = TeamFactory().getTeam("TeamA", "2123")
        self.assertEqual("TeamA", self.team.username, "username value improperly set")
        self.assertEqual("2123", self.team.password, "password value improperly set")

class TestGetPoints(unittest.TestCase):
    def setUp(self):
        self.team = TeamFactory().getTeam("Team 1", "1234")

    def test_get_points(self):
        self.points = 100
        self.assertEqual(100, self.team.get_points, "Points are not setting properly")

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
        self.team.set(-15)
        self.assertEquals(0, self.team.points, "Cannot drop below the 0 threshold")

    def test_add_cumulative_posandneg(self):
        self.team.set(100)
        self.assertEquals(100, self.team.points, "Failed to add 100 points properly")
        self.team.set(-15)
        self.assertEquals(85, self.team.points, "Failed to remove 15 points properly")

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
    suite.addTest(unittest.makeSuite(TestTeam))
    runner = unittest.TextTestRunner()
    res = runner.run(suite)
    print(res)
    print("*" * 20)
    for i in res.failures: print(i[1])
