import unittest


class Team:
    def __init__(self):
        self.username = ""
        self.password = ""

    def login(self, username, password):
        if username == self.username and password == self.password:
            return self.username, False
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


class TestTeam(unittest.TestCase):
    def setUp(self):
        self.team = Team()
        self.team.username = "team1"
        self.team.password = "password123"

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
    suite.addTest(unittest.makeSuite(TestTeam))
    runner = unittest.TextTestRunner()
    res = runner.run(suite)
    print(res)
    print("*" * 20)
    for i in res.failures: print(i[1])