import unittest
from abc import ABC

from Landmark import LandmarkFactory
from Team import TeamFactory


class GameInterface(ABC):
    def add_team(self, name, password):
        return False

    def remove_team(self, name):
        return False

    def modify_team(self, oldname, name=None, password=None):
        pass

    def add_landmark(self, location, clue, answer):
        return False

    def remove_landmark(self, landmark):
        pass

    def modify_landmark(self, oldlandmark, newlandmark):
        pass

    def set_point_penalty(self, points):
        pass

    def set_time_penalty(self, time):
        pass

    def start(self):
        return False

    def end(self):
        pass


class GameFactory:
    def getGame(self):
        return self.Game()

    class Game(GameInterface):
        def __init__(self):
            self.teams = []
            self.landmarks = []
            self.started = False
            self.penaltyValue = 0
            self.penaltyTime = 0

        def add_team(self, name, password):
            if not self.started:
                teamToBeAdded = TeamFactory().getTeam(name, password)
                for team in self.teams:
                    if team.username == teamToBeAdded.username:
                        return False
                self.teams.append(teamToBeAdded)
                return True
            return False

        def remove_team(self, name):
            if not self.started:
                for team in self.teams:
                    if team.username == name:
                        self.teams.remove(team)
                        return True
            return False

        def modify_team(self, oldname, name=None, password=None):
            pass

        def add_landmark(self, location, clue, answer):
            if not self.started:
                landmarkToBeAdded = LandmarkFactory().getLandmark(location, clue, answer)
                for landmark in self.landmarks:
                    if landmark.location == landmarkToBeAdded.location:
                        return False
                self.landmarks.append(landmarkToBeAdded)
                return True
            return False

        def remove_landmark(self, landmark):
            pass

        def modify_landmark(self, oldlandmark, newlandmark):
            pass

        def set_point_penalty(self, points):
            pass

        def set_time_penalty(self, time):
            pass

        def start(self):
            self.started = True

        def end(self):
            pass


class TestAddTeam(unittest.TestCase):
    def setUp(self):
        self.game = GameFactory().getGame()
        self.game.started = False

    def test_add_team(self):
        self.assertTrue(self.game.add_team("Team1", "1232"), "Did not add team")

    def test_add_team_duplicates(self):
        self.assertTrue(self.game.add_team("Team1", "1232"), "Did not add team")
        self.assertFalse(self.game.add_team("Team1", "1232"), "duplicate teams!")

    def test_add_team_after_Game_started(self):
        self.game.started = True
        self.assertFalse(self.game.add_team("Team1", "1232"), "should not add teams once Game starts")


class TestRemoveTeam(unittest.TestCase):
    def setUp(self):
        self.game = GameFactory().getGame()
        self.game.started = False
        self.game.teams.append(TeamFactory().getTeam("Team1", "1232"))

    def test_remove_team(self):
        self.assertTrue(self.game.remove_team("Team1"), "Failed to remove team")

    def test_remove_team_does_not_exist(self):
        self.assertTrue(self.game.remove_team("Team1"), "Failed to remove team")
        self.assertFalse(self.game.remove_team("Team1"), "Team does not exist")

    def test_remove_team_from_empty_team_list(self):
        self.game.teams.clear()
        self.assertFalse(self.game.remove_team("Team1"), "Failed to remove team, list of teams empty")

    def test_remove_team_game_started(self):
        self.game.started = True
        self.assertFalse(self.game.remove_team("Team1"), "should not remove teams once game starts")


class TestStartGame(unittest.TestCase):
    def setUp(self):
        self.game = GameFactory().getGame()
        self.game.started = False

    def test_start_game(self):
        self.game.start()
        self.assertTrue(self.game.started, "game in progress value not set")


class TestAddLandmark(unittest.TestCase):
    def setUp(self):
        self.game = GameFactory().getGame()
        self.game.started = False

    def test_add_landmark(self):
        self.assertTrue(self.game.add_landmark("New York", "Gift given by the French", "statue of liberty")
                        , "Failed to add landmark")

    def test_add_landmark_game_in_progress(self):
        self.game.started = True
        self.assertFalse(self.game.add_landmark("New York", "Gift given by the French", "statue of liberty")
                        , "Cannot add landmark once game has started")

    def test_add_landmark_duplicates(self):
        ld = LandmarkFactory().getLandmark("New York", "Gift given by the French", "statue of liberty")
        self.game.landmarks.append(ld)
        self.assertFalse(self.game.add_landmark("New York", "Gift given by the French", "statue of liberty"),
                         "Cannot add duplicate landmarks")



if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestAddTeam))
    suite.addTest(unittest.makeSuite(TestRemoveTeam))
    suite.addTest(unittest.makeSuite(TestStartGame))
    suite.addTest(unittest.makeSuite(TestAddLandmark))
    runner = unittest.TextTestRunner()
    res = runner.run(suite)
    print(res)
    print("*" * 20)
    for i in res.failures: print(i[1])
