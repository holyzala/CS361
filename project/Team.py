import unittest
from abc import ABC, abstractmethod
from GameMaker import UserABC


class TeamI(ABC):
    @abstractmethod
    def login(self, username, password):
        pass

    @abstractmethod
    def answer_question(self, answer):
        pass

    @abstractmethod
    def get_status(self):
        pass

    @abstractmethod
    def add_penalty(self, penalty):
        pass

    @property
    @abstractmethod
    def points(self):
        pass

    @points.setter
    @abstractmethod
    def points(self, points):
        pass

    @property
    @abstractmethod
    def password(self):
        pass

    @password.setter
    @abstractmethod
    def password(self, password):
        pass


class TeamFactory:
    def get_team(self, username, password):
        return self.Team(username, password)

    class Team(TeamI, UserABC):
        def __init__(self, username, password):
            self.username = username
            self.__password = password
            self.__points = 0
            self.current_landmark = 0
            self.penalty_count = 0
            self.time_log = []
            self.clue_time = None

        def __eq__(self, other):
            return self.username == other.username

        def login(self, username, password):
            if username != self.username or password != self.__password:
                return None
            return self

        def answer_question(self, answer):
            return ""

        def get_status(self):
            return ""

        @property
        def points(self):
            return self.__points

        @points.setter
        def points(self, points):
            self.__points = max(0, points)

        def add_penalty(self, penalty=1):
            try:
                if penalty <= 0:
                    return False
                self.penalty_count += penalty
                return True
            except ValueError:
                return False

        def is_admin(self):
            return False

        @property
        def password(self):
            return None

        @password.setter
        def password(self, password):
            self.__password = password


class TestInit(unittest.TestCase):
    def test_init(self):
        # pylint: disable=protected-access,no-member
        team = TeamFactory().get_team("TeamA", "2123")
        self.assertEqual("TeamA", team.username, "username value improperly set")
        self.assertEqual("2123", team._Team__password, "password value improperly set")


class TestPassword(unittest.TestCase):
    def setUp(self):
        self.team = TeamFactory().get_team("Team1", "1234")

    def test_get_password(self):
        self.assertIsNone(self.team.password, "Got some password")

    def test_set_password(self):
        # pylint: disable=protected-access,no-member
        self.team.password = "2132"
        self.assertEqual("2132", self.team._Team__password, "Password not set properly")


class TestPoints(unittest.TestCase):
    # pylint: disable=protected-access,invalid-name,attribute-defined-outside-init
    def setUp(self):
        self.team = TeamFactory().get_team("Team 1", "1234")

    def test_get_points(self):
        self.team._Team__points = 32
        self.assertEqual(32, self.team.points, "Failed to read 32 points properly")

    def test_add_once_positive(self):
        self.team.points = 100
        self.assertEqual(100, self.team._Team__points, "Failed to set 100 points properly")

    def test_add_cumulative_positive(self):
        self.team.points = 100
        self.assertEqual(100, self.team._Team__points, "Failed to set 100 points properly")
        self.team.points = 15
        self.assertEqual(15, self.team._Team__points, "Failed to set 15 points properly")

    def test_add_once_negative(self):
        self.team.points = -15
        self.assertEqual(0, self.team._Team__points, "Cannot drop below the 0 threshold")

    def test_add_cumulative_posandneg(self):
        self.team.points = 100
        self.assertEqual(100, self.team._Team__points, "Failed to set 100 points properly")
        self.team.points = -15
        self.assertEqual(0, self.team._Team__points, "Failed to set 15 points properly")


class TestTeamLogin(unittest.TestCase):
    def setUp(self):
        self.team = TeamFactory().get_team("team1", "password123")

    def test_team_login_success(self):
        user = self.team.login("team1", "password123")
        self.assertEqual(self.team, user, "Different user returned")
        self.assertEqual(self.team.username, user.username)
        self.assertFalse(user.is_admin())

    def test_team_login_fail(self):
        user = self.team.login("team1", "wrong password")
        self.assertEqual(None, user, "Invalid user returned")


class TestAddCurrentPenalty(unittest.TestCase):
    def setUp(self):
        self.team = TeamFactory().get_team("Team2", "password123")

    def test_add_pos_points(self):
        self.assertTrue(self.team.add_penalty(1), "Incorrect Penalty Value")

    def test_add_neg_points(self):
        self.assertFalse(self.team.add_penalty(-1), "Penalty points are being given neg values")


if __name__ == "__main__":
    SUITE = unittest.TestSuite()
    SUITE.addTest(unittest.makeSuite(TestInit))
    SUITE.addTest(unittest.makeSuite(TestTeamLogin))
    SUITE.addTest(unittest.makeSuite(TestPoints))
    SUITE.addTest(unittest.makeSuite(TestAddCurrentPenalty))
    SUITE.addTest(unittest.makeSuite(TestPassword))
    RUNNER = unittest.TextTestRunner()
    RES = RUNNER.run(SUITE)
    print(RES)
    print("*" * 20)
    for i in RES.failures:
        print(i[1])
