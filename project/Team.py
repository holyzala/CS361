import unittest
from abc import ABC


class TeamI(ABC):
    def login(self, password):
        return "", False

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

class TeamFactory:
    def getTeam(self, username, password):
        return self.Team(username, password)

    class Team(TeamI):
        def __init__(self, username, password):
            self.username = ""
            self.password = ""

        def login(self, password):
            return "", False

        def answer_question(self, answer):
            return ""

        def get_status(self):
            return ""

        def get_clue(self):
            return ""


class TestInit(unittest.TestCase):
    def test_init(self):
        self.team = TeamFactory().getTeam("TeamA", "2123")
        self.assertEqual("TeamA", self.team.username, "username value improperly set")
        self.assertEqual("2123", self.team.password, "password value improperly set")


if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestInit))
    runner = unittest.TextTestRunner()
    res = runner.run(suite)
    print(res)
    print("*" * 20)
    for i in res.failures: print(i[1])

