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

    def add_landmark(self, landmark):
        if landmark not in self.game.landmarks:
            self.game.landmarks.append(landmark)
            return "Landmark Added Sucesffuly"
        else:
            return "Could not Add Landmark"

    def remove_landmark(self, landmark):
        if landmark in self.game.landmarks:
            self.game.landmarks.remove(landmark)
            return "Landmark Removed Succesfully"
        else:
            return "Could not Remove Landmark"

    def modify_landmark(self, oldlandmark, newlandmark):
        self.landmarks = [x.replace(oldlandmark, newlandmark) for x in self.landmarks]

    def set_point_penalty(self, points):
        self.points = points

    def set_time_penalty(self, time):
        pass

    def start(self):
        return False

    def end(self):
        self.ended = True


class GameFactory:
    def getGame(self):
        return self.Game()

    class Game(GameInterface):
        def __init__(self):
            self.teams = []
            self.landmarks = []
            self.started = False
            self.ended = False
            self.penaltyValue = 0
            self.penaltyTime = 0

        def add_team(self, name, password):
            if not self.started:
                team = TeamFactory().getTeam(name, password)
                if team in self.teams:
                    return False
                self.teams.append(team)
                return True
            return False

        def remove_team(self, name):
            if not self.started:
                for team in self.teams:
                    if team.get_username() == name:
                        self.teams.remove(team)
                        return True
                return False
            return False

        def modify_team(self, oldname, name=None, password=None):
            pass

        def add_landmark(self, location, clue, answer):
            if not self.started:
                landmark = LandmarkFactory().getLandmark(location, clue, answer)
                if landmark in self.landmarks:
                    return False
                self.landmarks.append(landmark)
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
        self.assertTrue(self.game.add_landmark("New York", "Gift given by the French", "statue of liberty"),
                        "Failed to add landmark")

    def test_add_landmark_game_in_progress(self):
        self.game.started = True
        self.assertFalse(self.game.add_landmark("New York", "Gift given by the French", "statue of liberty"),
                         "Cannot add landmark once game has started")

    def test_add_landmark_duplicates(self):
        ld = LandmarkFactory().getLandmark("New York", "Gift given by the French", "statue of liberty")
        self.game.landmarks.append(ld)
        self.assertFalse(self.game.add_landmark("New York", "Gift given by the French", "statue of liberty"),
                         "Cannot add duplicate landmarks")

      
class TestEditLandmarkClue(unittest.TestCase):
    def setUp(self):
        self.game = GameFactory().getGame()

    def test_edit_clue(self):
        self.game.landmarks = ["Chicago", "Madison"]
        self.assertTrue(self.game.landmarks, "List is empty")
        self.game.modify_landmark("Chicago", "Vegas")
        self.assertIn("Vegas", self.game.landmarks, "Landmark edited incorrectly")

class TestModifyTeam(unittest.TestCase):
    def setUp(self):
        self.game = GameFactory().getGame()

    def test_modify_team_name(self):
        self.game.add_team("Team1", "1234")
        self.assertTrue(self.game.modify_team("Team1", name="Team2"), "Team was not modified")

    def test_modifiy_team_password(self):
        self.game.add_team("Team1", "21212")
        self.assertTrue(self.game.modify_team("Team1", password="5678"), "password was not modified")


class TestEndGame(unittest.TestCase):
    def setUp(self):
       self.game = GameFactory().getGame()

    def test_end_game_command(self):
        self.game.started = True
        self.assertTrue(self.game.started, "Game in progress")
        self.game.end()
        self.assertTrue(self.game.ended, "Game Has Ended")

    def test_completed_game(self):
        self.game.landmarks = "Final Clue solved"
        self.assertEqual(self.game.landmarks, "Final Clue solved", "Final clue has been solved, the game is over")
        self.game.end()
        self.assertTrue(self.game.ended, "Game Has Ended")

class TestDeleteLandmarks(unittest.TestCase):
    def setUp(self):
        self.game = Game()

    def test_delete_landmark(self):
        landmark1 = "ABC"
        self.game.landmark[0] = landmark1
        self.game.remove_landmark(landmark1)
        self.assertNotIn(landmark1, self.game.landmarks, "Failed to remove landmark")

    def test_delete_multi_landmarks(self):
        landmark1 = "ABC"
        landmark2 = "DEF"
        self.game.landmark[0] = landmark1
        self.game.landmark[1] = landmark2
        self.game.remove_landmark(landmark1)
        self.assertNotIn(landmark1, self.game.landmarks, "Failed to remove Landmark1")
        self.game.remove_landmark(landmark2)
        self.assertNotIn(landmark1, self.game.landmarks, "Failed to remove Landmark2")

class TestAddLandmark(unittest.testcase):
    def setUp(self):
        self.game = Game()

    def test_add_landmark(self):
        landmark1 = "ABC"
        self.assertNotIn(landmark1, self.game.landmarks, "Landmark already Exists")
        self.game.add_landmark(landmark1)
        self.assertIn(landmark1, self.game.landmarks, "Landmark was not successfully added")

    def test_add_landmark(self):
        landmark1 = "ABC"
        landmark2 = "DEF"
        self.assertNotIn(landmark1, self.game.landmarks, "Landmark already Exists")
        self.game.add_landmark(landmark1)
        self.assertIn(landmark1, self.game.landmarks, "Landmark1 was not successfully added")
        self.game.add_landmark(landmark2)
        self.assertIn(landmark2, self.game.landmarks, "Landmark2 was not sucessfully added")
        self.assertEqual((self.game.landmark[0], self.game.landmarks[1]), (landmark1, landmark2), "Adding not indexing properly")


if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestDeleteLandmarks))
    suite.addTest(unittest.makeSuite(TestModifyTeam))
    suite.addTest(unittest.makeSuite(TestAddTeam))
    suite.addTest(unittest.makeSuite(TestRemoveTeam))
    suite.addTest(unittest.makeSuite(TestStartGame))
    suite.addTest(unittest.makeSuite(TestAddLandmark))
    suite.addTest(unittest.makeSuite(TestEditLandmarkClue))
    suite.addTest(unittest.makeSuite(TestEndGame))
    runner = unittest.TextTestRunner()
    res = runner.run(suite)
    print(res)
    print("*" * 20)
    for i in res.failures: print(i[1])

