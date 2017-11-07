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
    
    @abstractmethod
    def get_password(self):
        pass
    
    @abstractmethod
    def get_points(self):
        pass

    @abstractmethod
    def set_points(self, points):
        pass

    @abstractmethod
    def add_penalty(self):
        pass

    @abstractmethod
    def clear_penalty(self):
        pass


class TeamFactory:
    def getTeam(self, username, password):
        return self.Team(username, password)

    class Team(TeamI, UserABC):
        def __init__(self, username, password):
            self.username = username
            self.password = password
            self.points = 0
            self.current_landmark = 0
            self.penalty_count = 0

        def __eq__(self, other):
            return self.username == other.username

        def changeName(self, name):
            self.username = name

        def changePassword(self, password):
            self.password = password

        def login(self, username, password):
            if username != self.username or password != self.password:
                return None
            return self

        def answer_question(self, answer):
            return ""

        def get_status(self):
            return ""

        def get_username(self):
            return self.username

        def get_password(self):
            return self.password
        
        def get_points(self):
            return self.points

        def set_points(self, points):
            try:
                if(int(points) < 0):
                    self.points = 0
                self.points = int(points)
                return True
            except ValueError:
                return False
            return False

        def add_penalty(self):
            self.penalty_count += 1

        def clear_penalty(self):
            self.penalty_count = 0

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


class TestAddCurrentPenalty(unittest.TestCase):
    def setUp(self):
        self.team = TeamFactory().getTeam("Team2", "password123")

    def test_add_pos_points(self):
        penaltyValue = 1
        self.assertTrue(self.team.add_penalty(penaltyValue), "Incorrect Penalty Value")

    def test_add_neg_points(self):
        penaltyValue = -1
        self.assertFalse(self.team.add_penalty(penaltyValue), "Penalty points are being given neg values")

    def test_add_str_points(self):
        penaltyValue = "ABC"
        self.assertFalse(self.team.add_penalty(penaltyValue), "Penalty is allowing string input")


class TestClearTeamPenalty(unittest.TestCase):
    def setUp(self):
        self.team = TeamFactory().getTeam("Team2", "password123")

    def test_set_to_zero(self):
        self.team.penalty_count = 1
        self.assertNotEqual(0, self.team.penalty_count)
        self.team.clear_penalty()
        self.assertEqual(0, self.team.penalty_count, "Penalty not resetting to 0")


if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestInit))
    suite.addTest(unittest.makeSuite(TestGetters))
    suite.addTest(unittest.makeSuite(TestTeamLogin))
    suite.addTest(unittest.makeSuite(TestEditTeam))
    suite.addTest(unittest.makeSuite(TestSetPoints))
    suite.addTest(unittest.makeSuite(TestGetPoints))
    suite.addTest(unittest.makeSuite(TestAddCurrentPenalty))
    suite.addTest(unittest.makeSuite(TestClearTeamPenalty))
    runner = unittest.TextTestRunner()
    res = runner.run(suite)
    print(res)
    print("*" * 20)
    for i in res.failures: print(i[1])
