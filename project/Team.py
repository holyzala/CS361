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

    def get_username(self):
        pass

class TeamFactory:
    def getTeam(self, username, password):
        return self.Team(username, password)

    class Team(TeamI):
        def __init__(self, username, password):
            self.username = username
            self.password = password

        def login(self, password):
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

if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestInit))
    suite.addTest(unittest.makeSuite(TestGetAnswer))
    runner = unittest.TextTestRunner()
    res = runner.run(suite)
    print(res)
    print("*" * 20)
    for i in res.failures: print(i[1])

