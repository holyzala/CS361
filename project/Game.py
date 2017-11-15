import unittest
import datetime
from abc import ABC, abstractmethod

from Landmark import LandmarkFactory
from Team import TeamFactory


class GameInterface(ABC):
    @abstractmethod
    def add_team(self, name, password):
        pass

    @abstractmethod
    def remove_team(self, name):
        pass

    @abstractmethod
    def modify_team(self, oldname, newname=None, newpassword=None):
        pass

    @abstractmethod
    def add_landmark(self, clue, question, answer):
        pass

    @abstractmethod
    def remove_landmark(self, clue):
        pass

    @abstractmethod
    def modify_landmark(self, oldclue, clue, question, answer):
        pass

    @abstractmethod
    def set_point_penalty(self, points):
        pass

    @abstractmethod
    def set_time_penalty(self, penalty):
        pass

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def end(self):
        pass

    @abstractmethod
    def get_status(self, now, username):
        pass

    @abstractmethod
    def answer_question(self, now, username, answer):
        pass

    @abstractmethod
    def quit_question(self, now, username, password):
        pass


class Game(GameInterface):
    def __init__(self):
        self.teams = {}
        self.landmarks = []
        self.started = False
        self.ended = False
        self.penaltyValue = 0
        self.penaltyTime = 0
        self.timer = None
        self.landmarkPoints = 0

    def add_team(self, name, password):
        if not self.started:
            if name in self.teams:
                return False
            self.teams[name] = TeamFactory().get_team(name, password)
            return True
        return False

    def remove_team(self, name):
        if not self.started:
            try:
                del self.teams[name]
            except KeyError:
                return False
            else:
                return True
        return False

    def modify_team(self, oldname, newname=None, newpassword=None):
        try:
            if newname in self.teams:
                return False
            if newpassword:
                self.teams[oldname].password = newpassword
            if newname:
                self.teams[oldname].username = newname
                self.teams[newname] = self.teams.pop(oldname)
            return True
        except KeyError:
            return False

    def add_landmark(self, clue, question, answer):
        if not self.started:
            landmarkToBeAdded = LandmarkFactory().get_landmark(clue, question, answer)
            if landmarkToBeAdded in self.landmarks:
                return False
            self.landmarks.append(landmarkToBeAdded)
            return True
        return False

    def remove_landmark(self, clue):
        if not self.started:
            for landmark in self.landmarks:
                if landmark.clue == clue:
                    self.landmarks.remove(landmark)
                    return True
        return False

    def modify_landmark(self, oldclue, clue=None, question=None, answer=None):
        try:
            for x in self.landmarks:
                if x.clue == oldclue:
                    if question:
                        x.question = question
                    if answer:
                        x.answer = answer
                    if clue:
                        x.clue = clue
            return True

        except KeyError:
            return False

    def set_point_penalty(self, points):
        if self.started:
            return False
        try:
            if int(points) <= 0:
                return False
            self.penaltyValue = int(points)
            return True
        except ValueError:
            return False

    def set_time_penalty(self, penalty):
        if self.started:
            return False
        try:
            if int(penalty) <= 0:
                return False
            self.penaltyValue = int(penalty)
            return True
        except ValueError:
            return False

    def start(self):
        dt = datetime.datetime.now()
        now = datetime.timedelta(days=dt.day, hours=dt.hour,
                                 minutes=dt.minute, seconds=dt.second)
        for team in self.teams:
            self.teams[team].clue_time = now
        self.started = True

    def end(self):
        self.ended = True

    def quit_question(self, now, username, password):
        if not self.started:
            return False
        current_team = self.teams[username]
        if current_team.login(username, password):
            current_team.current_landmark += 1
            if now < current_team.clue_time:
                current_team.time_log.append(datetime.timedelta(days=0, hours=0, minutes=0, seconds=0))
            else:
                current_team.time_log.append(now - current_team.clue_time)
                current_team.clue_time = now
                current_team.penalty_count = 0
            return True
        return False

    def answer_question(self, now, username, answer):
        if not self.started:
            return False
        current_team = self.teams[username]
        try:
            lm = self.landmarks[current_team.current_landmark]
        except IndexError:
            return False
        if lm.answer.lower() != answer.lower():
            current_team.penalty_count += self.penaltyValue
            return False
        else:
            if now < current_team.clue_time:
                current_team.time_log.append(datetime.timedelta(days=0, hours=0, minutes=0, seconds=0))
            else:
                current_team.time_log.append(now - current_team.clue_time)
                current_team.current_landmark += 1
                if self.timer:
                    current_team.penalty_count += int(((now - current_team.clue_time) / self.timer)) * self.penaltyTime
            if current_team.penalty_count <= self.landmarkPoints:
                current_team.points += (self.landmarkPoints - current_team.penalty_count)
            current_team.clue_time = now
            current_team.penalty_count = 0
            return True

    def get_status(self, now, username):
        current_team = self.teams[username]
        current_time_calc = (now - current_team.clue_time)
        total_time = datetime.timedelta(days=0, hours=0, minutes=0, seconds=0)
        for t in current_team.time_log:
            total_time += t
        if current_team.current_landmark <= len(self.landmarks):
            stat_str = 'Points:{};You Are On Landmark:{};Current Landmark Elapsed Time:{};Time Taken For Landmarks:{}'
            return stat_str.format(current_team.points, current_team.current_landmark + 1, current_time_calc, total_time)
        return 'Final Points: {}'.format(current_team.points)

    def get_clue(self, team):
        if not self.started:
            return "Game not started yet"
        return self.landmarks[team.current_landmark].clue


def make_game(*args, **kwargs):
    """This function should only ever return classes that implement GameInterface"""
    return Game()


class GameFactory:
    def __init__(self, maker):
        self.maker = maker

    def create_game(self, *args, **kwargs):
        return self.maker(*args, **kwargs)


TEST_FACTORY = GameFactory(make_game).create_game


class TestSetPenaltyValue(unittest.TestCase):
    def setUp(self):
        self.game = TEST_FACTORY()
        self.game.started = False

    def test_set_penalty_positive(self):
        pointValue = 10
        self.assertTrue(self.game.set_point_penalty(pointValue), "Point value not setting correctly")
        self.assertEqual(10, self.game.penaltyValue, "Penalty Value not setting correctly")

    def test_set_penalty_negative(self):
        pointValue = -10
        self.assertFalse(self.game.set_point_penalty(pointValue), "Set Point allowing negative values")

    def test_set_penalty_nonNumber(self):
        pointValue = "ABC"
        self.assertFalse(self.game.set_point_penalty(pointValue), "Set Point allowing string values")

    def test_set_penalty_during_game(self):
        pointValue = 10
        self.game.started = True
        self.assertFalse(self.game.set_point_penalty(pointValue), "Allowing setting penalty during game")


class TestSetPenaltyTime(unittest.TestCase):
    def setUp(self):
        self.game = TEST_FACTORY()
        self.game.started = False

    def test_set_penalty_time_positive(self):
        pointValue = 10
        self.assertTrue(self.game.set_time_penalty(pointValue), "Time value not setting correctly")
        self.assertEqual(pointValue, self.game.penaltyValue, "Time value not setting correctly")

    def test_set_penalty_time_negative(self):
        self.assertFalse(self.game.set_time_penalty(-10), "Set Time allowing negative values")

    def test_set_penalty_time_nonNumber(self):
        pointValue = "ABC"
        self.assertFalse(self.game.set_time_penalty(pointValue), "Set Time allowing string values")

    def test_set_penalty_game_started(self):
        pointValue = 10
        self.game.started = True
        self.assertFalse(self.game.set_time_penalty(pointValue), "Allowing time penalty setting during game")


class TestAddTeam(unittest.TestCase):
    def setUp(self):
        self.game = TEST_FACTORY()
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
        self.game = TEST_FACTORY()
        self.game.started = False
        self.game.teams["Team1"] = TeamFactory().get_team("Team1", "1232")

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
        self.game = TEST_FACTORY()
        self.game.started = False

    def test_start_game(self):
        self.game.start()
        self.assertTrue(self.game.started, "game in progress value not set")


class TestAddLandmark(unittest.TestCase):
    def setUp(self):
        self.game = TEST_FACTORY()
        self.game.started = False

    def test_add_landmark(self):
        self.assertTrue(self.game.add_landmark("New York", "Gift given by the French", "statue of liberty")
                        , "Failed to add landmark")

    def test_add_landmark_game_in_progress(self):
        self.game.started = True
        self.assertFalse(self.game.add_landmark("New York", "Gift given by the French", "statue of liberty")
                         , "Cannot add landmark once game has started")

    def test_add_landmark_duplicates(self):
        ld = LandmarkFactory().get_landmark("New York", "Gift given by the French", "statue of liberty")
        self.game.landmarks.append(ld)
        self.assertFalse(self.game.add_landmark("New York", "Gift given by the French", "statue of liberty"),
                         "Cannot add duplicate landmarks")


class TestModifyLandmark(unittest.TestCase):
    def setUp(self):
        self.game = TEST_FACTORY()
        self.game.landmarks.append(LandmarkFactory().get_landmark("Chicago", "Where the Bears play", "Soldier Field"))

    def test_edit_question(self):
        self.assertTrue(self.game.modify_landmark("Chicago", question="Where the UFC fights are"),
                        "Landmark question was not modified")

    def test_edit_answer(self):
        self.assertTrue(self.game.modify_landmark("Chicago", answer="The United Center"),
                        "Landmark answer was not modified")

    def test_edit_clue(self):
        self.assertTrue(self.game.modify_landmark("Chicago", clue="Chiccago"), "Landmark clue was not modified")

    def test_edit_question_and_answer(self):
        self.assertTrue(self.game.modify_landmark("Chicago", question="Tallest Building", answer="Sears Tower"),
                        "Landmark question and answer not modified")

    def test_edit_question_and_clue(self):
        self.assertTrue(self.game.modify_landmark("Chicago", question="Tallest Building", clue="Chicaago"),
                        "Landmark question and clue not modified")

    def test_edit_clue_and_answer(self):
        self.assertTrue(self.game.modify_landmark("Chicago", clue="CChicago", answer="Sears Tower"),
                        "Landmark question and clue not modified")


class TestModifyTeam(unittest.TestCase):
    def setUp(self):
        self.game = TEST_FACTORY()
        self.game.teams["Team1"] = TeamFactory().get_team("Team1", "1234")

    def test_modify_team_name(self):
        self.assertTrue(self.game.modify_team("Team1", newname="Team2", newpassword=None), "Team name was not modified")
        self.assertIn("Team2", self.game.teams, "Key was not updated")

    def test_modify_team_password(self):
        self.assertTrue(self.game.modify_team("Team1", newname=None, newpassword="5678"), "password was not modified")
        self.assertIn("Team1", self.game.teams, "Key should not be updated")

    def test_modify_team_name_and_password(self):
        self.assertTrue(self.game.modify_team("Team1", newname="Team103", newpassword="5678"),
                        "name and password was not modified")
        self.assertIn("Team103", self.game.teams, "Key was not updated")

    def test_modify_team_does_not_exist(self):
        self.game.teams.clear()
        self.assertFalse(self.game.modify_team("Team1", newname="Team2", newpassword="5678"), "Team does not exist")


class TestEndGame(unittest.TestCase):
    def setUp(self):
        self.game = TEST_FACTORY()
        self.game.started = True

    def test_end_game_command(self):
        self.assertTrue(self.game.started, "Game in progress")
        self.game.end()
        self.assertTrue(self.game.ended, "Game Has Ended")


class TestDeleteLandmarks(unittest.TestCase):
    def setUp(self):
        self.game = TEST_FACTORY()
        self.game.started = False

    def test_delete_landmark(self):
        landmark1 = LandmarkFactory().get_landmark("ABC", "DEF", "GHI")
        self.game.landmarks.append(landmark1)
        self.game.remove_landmark("ABC")
        self.assertNotIn(landmark1, self.game.landmarks, "Failed to remove landmark")

    def test_delete_multi_landmarks(self):
        landmark1 = LandmarkFactory().get_landmark("ABC", "DEF", "GHI")
        landmark2 = LandmarkFactory().get_landmark("JKL", "MNO", "PQR")
        self.game.landmarks.append(landmark1)
        self.game.landmarks.append(landmark2)
        self.game.remove_landmark("ABC")
        self.assertNotIn(landmark1, self.game.landmarks, "Failed to remove Landmark1")
        self.game.remove_landmark("JKL")
        self.assertNotIn(landmark1, self.game.landmarks, "Failed to remove Landmark2")

    def test_delete_landmark_does_not_exist(self):
        self.assertFalse(self.game.remove_landmark("ABC"), "landmark does not exist")

    def test_delete_landmark_from_empty_landmark_list(self):
        landmark1 = LandmarkFactory().get_landmark("ABC", "DEF", "GHI")
        landmark2 = LandmarkFactory().get_landmark("JKL", "MNO", "PQR")
        self.game.landmarks.append(landmark1)
        self.game.landmarks.append(landmark2)
        self.game.landmarks.clear()
        self.assertFalse(self.game.remove_team("ABC"), "Failed to remove team, list of teams empty")

    def test_remove_landmark_game_started(self):
        self.game.started = True
        landmark1 = LandmarkFactory().get_landmark("ABC", "DEF", "GHI")
        self.game.landmarks.append(landmark1)
        self.assertFalse(self.game.remove_team("ABC"), "should not remove teams once game starts")


class TestAddLandmark2(unittest.TestCase):
    def setUp(self):
        self.game = TEST_FACTORY()

    def test_add_landmark(self):
        landmark1 = LandmarkFactory().get_landmark("ABC", "DEF", "GHI")
        self.assertNotIn(landmark1, self.game.landmarks, "Landmark already Exists")
        self.game.add_landmark(landmark1.clue, landmark1.question, landmark1.answer)
        self.assertIn(landmark1, self.game.landmarks, "Landmark was not successfully added")

    def test_add_landmark2(self):
        landmark1 = LandmarkFactory().get_landmark("ABC", "DEF", "GHI")
        landmark2 = LandmarkFactory().get_landmark("JKL", "MNO", "PQR")
        self.assertNotIn(landmark1, self.game.landmarks, "Landmark already Exists")
        self.game.add_landmark(landmark1.clue, landmark1.question, landmark1.answer)
        self.assertIn(landmark1, self.game.landmarks, "Landmark1 was not successfully added")
        self.game.add_landmark(landmark2.clue, landmark2.question, landmark2.answer)
        self.assertIn(landmark2, self.game.landmarks, "Landmark2 was not sucessfully added")
        self.assertEqual((self.game.landmarks[0], self.game.landmarks[1]), (landmark1, landmark2),
                         "Adding not indexing properly")


class landmarkDummy:
    def __init__(self):
        self.clue = "The Place we drink coffee and read books"
        self.question = "What is the name of the statue out front?"
        self.answer = "three disks"
        self.location = "uwm library"


class teamDummy:
    def __init__(self):
        self.points = 100
        self.current_landmark = 1
        self.time_log = [datetime.timedelta(hours=0, minutes=20, seconds=15),
                        datetime.timedelta(hours=0, minutes=35, seconds=25)]
        self.clue_time = datetime.timedelta(hours=0, minutes=0, seconds=0)
        self.password = "password"
        self.penalty_count = 0
        self.username = "Dummy"

    def login(self, username, password):
        return self.username == username and self.password == password


class Test_Game_Team(unittest.TestCase):
    def setUp(self):
        self.team = teamDummy()
        self.game = GameFactory(make_game).create_game()
        l1 = landmarkDummy()
        l2 = landmarkDummy()
        l3 = landmarkDummy()
        self.game.landmarks = [l1, l2, l3]
        self.game.penaltyTime = 20
        self.game.penaltyValue = 10
        self.game.timer = datetime.timedelta(hours=0, minutes=0, seconds=15)
        self.game.landmarkPoints = 150
        self.game.teams[self.team.username] = self.team

    def test_get_status(self):
        self.team.clue_time = datetime.timedelta(hours=5, minutes=30, seconds=50)
        now = datetime.timedelta(hours=6, minutes=35, seconds=15)
        self.game.started = True
        self.assertEqual(self.game.get_status(now, self.team.username), 'Points:100;You Are On Landmark:2;' +
                         'Current Landmark Elapsed Time:1:04:25;Time Taken For Landmarks:0:55:40',
                         'get_status did not print the proper stats!')

    def test_quit_question_incorrectpass(self):
        self.team.clue_time = self.team.clue_time = datetime.timedelta(days=15, hours=12, minutes=30, seconds=15)
        now = datetime.timedelta(days=16, hours=7, minutes=25, seconds=8)
        self.assertFalse(self.game.quit_question(now, self.team.username, "incorrectpasswerd"),
                         "Quit Question Returned True After Incorrect Password!")
        self.assertEqual(self.team.points, 100, "Points Changed after Failing Give Up!")
        self.assertEqual(self.team.current_landmark, 1, "Landmark Index Increased after Failed Password")
        self.assertEqual(len(self.team.time_log), 2, "Time log logged a new entry after failied password")
        self.assertNotEqual(self.team.clue_time, now, "Clue Time Updated After Incorrect Password!")

    def test_quit_question(self):
        self.team.clue_time = datetime.timedelta(days=15, hours=12, minutes=30, seconds=15)
        now = datetime.timedelta(days=16, hours=7, minutes=25, seconds=8)
        self.game.started = True
        self.assertTrue(self.game.quit_question(now, self.team.username, "password"),
                        "Quit Question Returned False After Correct Password!")
        self.assertEqual(self.team.points, 100, "Points Changed after Giving Up!")
        self.assertEqual(self.team.current_landmark, 2, "Landmark Index Did Not Properly Incriment")
        self.assertEqual(len(self.team.time_log), 3, "Time log did not recieve new entry")
        self.assertEqual(self.team.time_log[2], datetime.timedelta(days=0, hours=18, minutes=54, seconds=53),
                         "Time Log Did Not Recieve The Correct Time")  # this may not work correctly
        self.assertEqual(self.team.clue_time, now, "Clue Time Did Not Update!")

    def test_answer_question_correct_no_time(self):
        self.team.clue_time = datetime.timedelta(days=20, hours=9, minutes=24, seconds=10)
        now = datetime.timedelta(days=20, hours=9, minutes=24, seconds=20)
        self.game.started = True
        self.assertTrue(self.game.answer_question(now, self.team.username, "three disks"),
                        "Correct Answer Returned False!")
        self.assertEqual(self.team.points, 250, "Points did not increment correctly")
        self.assertEqual(self.team.current_landmark, 2, "Landmark Index Did not Properly increment")
        self.assertEqual(len(self.team.time_log), 3, "Time Log Did Not recieve a new entry")
        self.assertEqual(self.team.time_log[2], datetime.timedelta(days=0, hours=0, minutes=0, seconds=10),
                         "Time Log Did Not Save The Correct Time")
        self.assertEqual(self.team.clue_time, now, "Clue Time Did Not Update!")

    def test_answer_question_incorrect_no_time(self):
        self.team.clue_time = datetime.timedelta(days=20, hours=9, minutes=24, seconds=10)
        now = datetime.timedelta(days=20, hours=9, minutes=24, seconds=20)
        self.game.started = True
        self.assertFalse(self.game.answer_question(now, self.team.username, "trash fire"),
                         "Incorrect Answer Returned True!")
        self.assertEqual(self.team.points, 100, "Points did not increment correctly")
        self.assertEqual(self.team.current_landmark, 1, "Landmark Index Did not Properly increment")
        self.assertEqual(len(self.team.time_log), 2, "Time Log Did Not recieve a new entry")
        self.assertNotEqual(self.team.clue_time, now, "Clue Time Updated After Incorrect Answer!")
        # Attempt 2
        self.assertTrue(self.game.answer_question(now, self.team.username, "three disks"),
                        " Correct Answer Returned False After Incorrect Guess!")
        self.assertEqual(self.team.points, 240, "Points did not increment correctly")
        self.assertEqual(self.team.current_landmark, 2, "Landmark Index Did not Properly increment")
        self.assertEqual(len(self.team.time_log), 3, "Time Log Did Not recieve a new entry")
        self.assertEqual(self.team.time_log[2], datetime.timedelta(days=0, hours=0, minutes=0, seconds=10),
                         "Time Log Did Not Save The Correct Time")
        self.assertEqual(self.team.clue_time, now, "Clue Time Did Not Update!")

    def test_answer_question_time_penalty(self):
        self.team.clue_time = datetime.timedelta(days=20, hours=9, minutes=24, seconds=10)
        now = datetime.timedelta(days=20, hours=9, minutes=24, seconds=26)
        self.game.started = True
        self.assertTrue(self.game.answer_question(now, self.team.username, "three disks"),
                        "Returned False after Correct Answer!")
        self.assertEqual(self.team.points, 230, "Points did not increment correctly")
        self.assertEqual(self.team.current_landmark, 2, "Landmark Index Did not Properly increment")
        self.assertEqual(len(self.team.time_log), 3, "Time Log Did Not recieve a new entry")
        self.assertEqual(self.team.time_log[2], datetime.timedelta(hours=0, minutes=00, seconds=16),
                         "Time Log Did Not Save The Correct Time")
        self.assertEqual(self.team.clue_time, now, "Clue Time Did Not Update!")

    def test_answer_question_time_penalty2(self):
        self.team.clue_time = datetime.timedelta(days=20, hours=9, minutes=24, seconds=10)
        now = datetime.timedelta(days=20, hours=9, minutes=25, seconds=26)
        self.game.started = True
        self.assertTrue(self.game.answer_question(now, self.team.username, "three disks"),
                        "Returned False After Correct Answer!")
        self.assertEqual(self.team.points, 150, "Points did not increment correctly")
        self.assertEqual(self.team.current_landmark, 2, "Landmark Index Did not Properly increment")
        self.assertEqual(len(self.team.time_log), 3, "Time Log Did Not recieve a new entry")
        self.assertEqual(self.team.time_log[2], datetime.timedelta(hours=0, minutes=1, seconds=16),
                         "Time Log Did Not Save The Correct Time")
        self.assertEqual(self.team.clue_time, now, "Clue Time Did Not Update!")

    def test_answer_question_time_complex(self):
        self.team.clue_time = datetime.timedelta(days=20, hours=9, minutes=24, seconds=10)
        now = datetime.timedelta(days=20, hours=9, minutes=25, seconds=26)
        self.game.started = True
        self.assertFalse(self.game.answer_question(now, self.team.username, "two disks"),
                         "Returned True after Incorrect Answer!")
        self.assertEqual(self.team.points, 100, "Points did not increment correctly")
        self.assertEqual(self.team.current_landmark, 1, "Landmark Index Did not Properly increment")
        self.assertEqual(len(self.team.time_log), 2, "Time Log Did Not recieve a new entry")
        self.assertNotEqual(self.team.clue_time, now, "Clue Time Updated After Incorrect Answer!")
        self.assertTrue(self.game.answer_question(now, self.team.username, "three disks"),
                        "Correct Answer Retruned False After Incorrect Answer and Wait!")
        self.assertEqual(self.team.points, 140, "Points did not increment correctly")
        self.assertEqual(self.team.current_landmark, 2, "Landmark Index Did not Properly increment")
        self.assertEqual(len(self.team.time_log), 3, "Time Log Did Not recieve a new entry")
        self.assertEqual(self.team.time_log[2], datetime.timedelta(hours=0, minutes=1, seconds=16),
                         "Time Log Did Not Save The Correct Time")  # This may not work properly
        self.assertEqual(self.team.clue_time, now, "Clue Time Did Not Update!")

    def test_answer_question_time_max(self):
        self.team.clue_time = datetime.timedelta(days=3, hours=12, minutes=30, seconds=0)
        now = datetime.timedelta(days=5, hours=20, minutes=30, seconds=15)
        self.game.started = True
        self.assertTrue(self.game.answer_question(now, self.team.username, "three disks"),
                        "Returned False after Correct Answer!")
        self.assertEqual(self.team.points, 100, "Team Earned Negative Points, Thats not fair!")
        self.assertEqual(self.team.current_landmark, 2, "Landmark Index Did not Properly increment")
        self.assertEqual(len(self.team.time_log), 3, "Time Log Did Not recieve a new entry")
        self.assertEqual(self.team.time_log[2], datetime.timedelta(days=2, hours=8, minutes=0, seconds=15),
                         "Time Log did not Save The Correct Time")
        self.assertEqual(self.team.clue_time, now, "Clue Time Did Not Update!")

    def test_answer_question_incorrect_max(self):
        self.team.clue_time = datetime.timedelta(days=3, hours=12, minutes=30, seconds=0)
        now = datetime.timedelta(days=3, hours=12, minutes=30, seconds=0)
        self.game.started = True
        for _ in range(0, 16):
            self.assertFalse(self.game.answer_question(now, self.team.username, "two disks"),
                             "Returned True after Incorrect Answer!")
        self.assertTrue(self.game.answer_question(now, self.team.username, "three disks"),
                        "Returned False After Correct Answer!")
        self.assertEqual(self.team.points, 100, "Team Earned Negative Points, Thats not fair!")
        self.assertEqual(self.team.current_landmark, 2, "Landmark Index Did not Properly increment")
        self.assertEqual(len(self.team.time_log), 3, "Time Log Did Not recieve a new entry")
        self.assertEqual(self.team.time_log[2], datetime.timedelta(days=0, hours=0, minutes=0, seconds=0),
                         "Time Log did not Save The Correct Time")
        self.assertEqual(self.team.clue_time, now, "Clue Time Did Not Update!")

    def test_answer_question_incorrect_max_complex(self):
        self.team.clue_time = datetime.timedelta(days=3, hours=12, minutes=30, seconds=0)
        now = datetime.timedelta(days=3, hours=12, minutes=31, seconds=45)
        self.game.started = True
        for _ in range(0, 11):
            self.assertFalse(self.game.answer_question(now, self.team.username, "two disks"),
                             "Returned True after Incorrect Answer!")
        before_time = self.team.clue_time
        self.assertTrue(self.game.answer_question(now, self.team.username, "three disks"),
                        "Returned False After Correct Answer!")
        self.assertEqual(self.team.points, 100, "Team Earned Negative Points, Thats not fair!")
        self.assertEqual(self.team.current_landmark, 2, "Landmark Index Did not Properly increment")
        self.assertEqual(len(self.team.time_log), 3, "Time Log Did Not recieve a new entry")
        self.assertEqual(self.team.time_log[2], datetime.timedelta(days=0, hours=0, minutes=1, seconds=45),
                         "Time Log did not Save The Correct Time")
        self.assertEqual(self.team.clue_time, now, "Clue Time Did Not Update!")
        self.assertEqual(self.team.time_log[2], now - before_time,
                         "Time Log Did Not Save The Correct Time")  # This may not work properly


class TestGetClue(unittest.TestCase):
    def setUp(self):
        self.game = TEST_FACTORY()
        self.game.teams['abc'] = TeamFactory().get_team('abc', 'def')
        self.game.teams['ghi'] = TeamFactory().get_team('ghi', 'jkl')
        self.game.landmarks.append(LandmarkFactory().get_landmark('clue1', 'question1', 'answer1'))
        self.game.landmarks.append(LandmarkFactory().get_landmark('clue2', 'question2', 'answer2'))
        self.game.landmarks.append(LandmarkFactory().get_landmark('clue3', 'question3', 'answer3'))

    def test_game_not_started(self):
        self.assertEqual("Game not started yet", self.game.get_clue(self.game.teams['abc']),
                         "Got clue before game started")
        self.assertEqual(0, self.game.teams['abc'].points, "Points assigned")
        self.assertEqual(0, self.game.teams['abc'].current_landmark, "Current landmark changed")

    def test_game_ready(self):
        self.game.started = True
        self.assertEqual("clue1", self.game.get_clue(self.game.teams['abc']), "Got the wrong clue")
        self.assertEqual(0, self.game.teams['abc'].points, "Points assigned")
        self.assertEqual(0, self.game.teams['abc'].current_landmark, "Current landmark changed")

    def test_different_landmark(self):
        self.game.started = True
        self.game.teams['abc'].current_landmark = 1
        self.game.teams['abc'].points = 100
        self.assertEqual("clue2", self.game.get_clue(self.game.teams['abc']), "Got the wrong clue")
        self.assertEqual(100, self.game.teams['abc'].points, "Pooints assigned")
        self.assertEqual(1, self.game.teams['abc'].current_landmark, "Current landmark changed")

    def get_status_negative_time(self):
        self.game.teams['abc'].clue_time = datetime.timedelta(days=2, hours=5, minutes=30, seconds=50)
        now = datetime.timedelta(days=1, hours=0, minutes=35, seconds=15)
        self.assertEqual(self.game.get_status(now, self.game.teams['abc'].username),
                         'Points:100;You Are On Landmark:1;Current Time:0:00:00;Time Taken For Landmarks:0:55:40',
                         'get_status did not print the proper stats!')

    def answer_question_negative_time(self):
        self.game.teams['abc'].clue_time = datetime.timedelta(days=2, hours=5, minutes=30, seconds=50)
        now = datetime.timedelta(days=1, hours=0, minutes=35, seconds=15)
        self.game.answer_question(now, self.game.teams['abc'].username, "three disks")
        self.assertEqual(self.game.teams['abc'].time_log[2], datetime.timedelta(days=0, hours=0, minutes=0, seconds=0),
                         "Time Log did not Save The Correct Time")
        self.assertEqual(self.game.teams['abc'].clue_time, now, "Clue Time Did Not Update!")

    def quit_question_negative_time(self):
        self.game.teams['abc'].clue_time = datetime.timedelta(days=2, hours=5, minutes=30, seconds=50)
        now = datetime.timedelta(days=1, hours=0, minutes=35, seconds=15)
        self.game.quit_question(now, self.game.teams['abc'].username, "password")
        self.assertEqual(self.game.teams['abc'].time_log[2], datetime.timedelta(days=0, hours=0, minutes=0, seconds=0),
                         "Time Log did not Save The Correct Time")
        self.assertEqual(self.game.teams['abc'].clue_time, now, "Clue Time Did Not Update!")


if __name__ == "__main__":
    SUITE = unittest.TestSuite()
    SUITE.addTest(unittest.makeSuite(TestSetPenaltyValue))
    SUITE.addTest(unittest.makeSuite(TestSetPenaltyTime))
    SUITE.addTest(unittest.makeSuite(TestDeleteLandmarks))
    SUITE.addTest(unittest.makeSuite(TestModifyTeam))
    SUITE.addTest(unittest.makeSuite(TestAddTeam))
    SUITE.addTest(unittest.makeSuite(TestRemoveTeam))
    SUITE.addTest(unittest.makeSuite(TestStartGame))
    SUITE.addTest(unittest.makeSuite(TestAddLandmark))
    SUITE.addTest(unittest.makeSuite(TestAddLandmark2))
    SUITE.addTest(unittest.makeSuite(TestModifyLandmark))
    SUITE.addTest(unittest.makeSuite(TestEndGame))
    SUITE.addTest(unittest.makeSuite(TestGetClue))
    SUITE.addTest(unittest.makeSuite(Test_Game_Team))
    RUNNER = unittest.TextTestRunner()
    RES = RUNNER.run(SUITE)
    print(RES)
    print("*" * 20)
    for i in RES.failures:
        print(i[1])
