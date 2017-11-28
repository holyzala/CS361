import datetime
import unittest
from abc import ABC, abstractmethod

from .Landmark import LandmarkFactory
from .Team import Team
from .Errors import Errors


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
    def edit_landmark_order(self, oldindex, newindex):
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
    def answer_question(self, now, team, answer):
        pass

    @abstractmethod
    def quit_question(self, now, team, password):
        pass

    @abstractmethod
    def login(self, username, password):
        pass

    @abstractmethod
    def get_team(self, username):
        pass

    @abstractmethod
    def get_team_landmark(self, team):
        pass

    @abstractmethod
    def get_snapshot(self, now):
        pass


class Game(GameInterface):
    def __init__(self):
        self.__teams = {}
        self.__landmarks = []
        self.__started = False
        self.__running = False
        self.__ended = False
        self.__penalty_value = 0
        self.__penalty_time = 0
        self.timer = None
        self.landmark_points = 0

    @property
    def started(self):
        return self.__started

    @property
    def ended(self):
        return self.__ended

    def login(self, username, password):
        try:
            return self.__teams[username].login(username, password)
        except KeyError:
            return None

    def get_team(self, username):
        try:
            return self.__teams[username]
        except KeyError:
            return None

    def get_team_landmark(self, team):
        return self.__landmarks[team.current_landmark]

    def add_team(self, name, password):
        if not self.started:
            if name in self.__teams:
                return False
            temp = Team.objects.create(username=name, password=password)
            self.__teams[name] = temp
            temp.save()

            return True
        return False

    def remove_team(self, name):
        if not self.started:
            try:
                del self.__teams[name]
            except KeyError:
                return False
            else:
                return True
        return False

    def modify_team(self, oldname, newname=None, newpassword=None):
        try:
            if newname in self.__teams:
                return False
            if newpassword:
                self.__teams[oldname].password = newpassword
            if newname:
                self.__teams[oldname].username = newname
                self.__teams[newname] = self.__teams.pop(oldname)
            return True
        except KeyError:
            return False

    def add_landmark(self, clue, question, answer):
        if not self.started:
            landmark = LandmarkFactory().get_landmark(clue, question, answer)
            if landmark in self.__landmarks:
                return False
            self.__landmarks.append(landmark)
            return True
        return False

    def remove_landmark(self, clue):
        if not self.started:
            for landmark in self.__landmarks:
                if landmark.clue == clue:
                    self.__landmarks.remove(landmark)
                    return True
        return False

    def modify_landmark(self, oldclue, clue=None, question=None, answer=None):
        try:
            for x in self.__landmarks:
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

    def edit_landmark_order(self, index1, index2):
        if self.started or self.ended:
            return Errors.CAN_ONLY_EDIT_ORDER_WHEN_GAME_IS_NEW
        try:
            self.__landmarks.insert(index2, self.__landmarks.pop(index1))
        except IndexError:
            return Errors.LANDMARK_INDEX
        return Errors.NO_ERROR

    @property
    def penalty_value(self):
        return self.__penalty_value

    def set_point_penalty(self, points):
        if self.started:
            return False
        if points < 0:
            return False
        self.__penalty_value = points
        return True

    @property
    def penalty_time(self):
        return self.__penalty_time

    def set_time_penalty(self, penalty):
        if self.started:
            return False
        if penalty < 0:
            return False
        self.__penalty_time = penalty
        return True

    def start(self):
        dt = datetime.datetime.now()
        now = datetime.timedelta(days=dt.day, hours=dt.hour,
                                 minutes=dt.minute, seconds=dt.second)
        for team in self.__teams:
            self.__teams[team].clue_time = now
        self.__started = True

    def end(self):
        self.__ended = True

    def quit_question(self, now, team, password):
        if not self.started or self.ended:
            return Errors.NO_GAME
        if not team.login(team.username, password):
            return Errors.INVALID_LOGIN
        team.current_landmark += 1
        team.time_log.append(now - team.clue_time)
        team.clue_time = now
        team.penalty_count = 0
        return Errors.NO_ERROR

    def answer_question(self, now, team, answer):
        if not self.started or self.ended:
            return Errors.NO_GAME
        try:
            lm = self.__landmarks[team.current_landmark]
        except IndexError:
            return Errors.LANDMARK_INDEX
        if not lm.check_answer(answer):
            team.penalty_count += self.penalty_value
            return Errors.WRONG_ANSWER
        else:
            team.time_log.append(now - team.clue_time)
            team.current_landmark += 1
            if self.timer:
                team.penalty_count += int(((now - team.clue_time) / self.timer)) * self.penalty_time
            team.points += max(0, self.landmark_points - team.penalty_count)
            team.clue_time = now
            team.penalty_count = 0
            if len(self.__landmarks) == team.current_landmark:
                return Errors.FINAL_ANSWER
            return Errors.NO_ERROR

    def get_status(self, now, username):
        current_team = self.__teams[username]
        current_time_calc = (now - current_team.clue_time)
        total_time = datetime.timedelta(days=0, hours=0, minutes=0, seconds=0)
        for t in current_team.time_log:
            total_time += t
        if current_team.current_landmark <= len(self.__landmarks):
            stat_str = 'Points:{};You Are On Landmark:{};Current Landmark Elapsed Time:{};Time Taken For Landmarks:{}'
            return stat_str.format(current_team.points, current_team.current_landmark+1, current_time_calc, total_time)
        return 'Final Points: {}'.format(current_team.points)

    def get_snapshot(self, now):
        pass


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
    # pylint: disable=protected-access,no-member
    def setUp(self):
        self.game = TEST_FACTORY()
        self.game._Game__started = False

    def test_set_penalty_positive(self):
        point_value = 10
        self.assertTrue(self.game.set_point_penalty(point_value), "Point value not setting correctly")
        self.assertEqual(10, self.game._Game__penalty_value, "Penalty Value not setting correctly")

    def test_set_penalty_negative(self):
        point_value = -10
        self.assertFalse(self.game.set_point_penalty(point_value), "Set Point allowing negative values")

    def test_set_penalty_zero(self):
        point_value = 0
        self.assertTrue(self.game.set_point_penalty(point_value), "Time Penalty Value Correctly set to 0")
        self.assertEqual(point_value, self.game._Game__penalty_value, "Time Penalty Value not allowing 0")

    def test_set_penalty_during_game(self):
        point_value = 10
        self.game._Game__started = True
        self.assertFalse(self.game.set_point_penalty(point_value), "Allowing setting penalty during game")


class TestSetPenaltyTime(unittest.TestCase):
    # pylint: disable=protected-access,no-member
    def setUp(self):
        self.game = TEST_FACTORY()
        self.game._Game__started = False

    def test_set_penalty_time_positive(self):
        point_value = 10
        self.assertTrue(self.game.set_time_penalty(point_value), "Time value not setting correctly")
        self.assertEqual(point_value, self.game._Game__penalty_time, "Time value not setting correctly")

    def test_set_penalty_time_negative(self):
        self.assertFalse(self.game.set_time_penalty(-10), "Set Time allowing negative values")

    def test_set_penalty_game_started(self):
        point_value = 10
        self.game._Game__started = True
        self.assertFalse(self.game.set_time_penalty(point_value), "Allowing time penalty setting during game")

    def test_set_penalty_time_zero(self):
        point_value = 0
        self.assertTrue(self.game.set_time_penalty(point_value), "Time Penalty Value Correctly set to 0")
        self.assertEqual(point_value, self.game._Game__penalty_time, "Time Penalty Value not allowing 0")



class TestAddTeam(unittest.TestCase):
    # pylint: disable=protected-access,no-member
    def setUp(self):
        self.game = TEST_FACTORY()
        self.game._Game__started = False

    def test_add_team(self):
        self.assertTrue(self.game.add_team("Team1", "1232"), "Did not add team")

    def test_add_team_duplicates(self):
        self.assertTrue(self.game.add_team("Team1", "1232"), "Did not add team")
        self.assertFalse(self.game.add_team("Team1", "1232"), "duplicate teams!")

    def test_add_team_after_Game_started(self):
        self.game._Game__started = True
        self.assertFalse(self.game.add_team("Team1", "1232"), "should not add teams once Game starts")


class TestRemoveTeam(unittest.TestCase):
    # pylint: disable=protected-access,no-member
    def setUp(self):
        self.game = TEST_FACTORY()
        self.game._Game__started = False
        self.game._Game__teams["Team1"] = Team("Team1", "1232")

    def test_remove_team(self):
        self.assertTrue(self.game.remove_team("Team1"), "Failed to remove team")

    def test_remove_team_does_not_exist(self):
        self.assertTrue(self.game.remove_team("Team1"), "Failed to remove team")
        self.assertFalse(self.game.remove_team("Team1"), "Team does not exist")

    def test_remove_team_from_empty_team_list(self):
        self.game._Game__teams.clear()
        self.assertFalse(self.game.remove_team("Team1"), "Failed to remove team, list of teams empty")

    def test_remove_team_game_started(self):
        self.game._Game__started = True
        self.assertFalse(self.game.remove_team("Team1"), "should not remove teams once game starts")


class TestStartGame(unittest.TestCase):
    # pylint: disable=protected-access,no-member
    def setUp(self):
        self.game = TEST_FACTORY()
        self.game._Game__started = False

    def test_start_game(self):
        self.game.start()
        self.assertTrue(self.game._Game__started, "game in progress value not set")


class TestAddLandmark(unittest.TestCase):
    # pylint: disable=protected-access,no-member
    def setUp(self):
        self.game = TEST_FACTORY()
        self.game._Game__started = False

    def test_add_landmark(self):
        self.assertTrue(self.game.add_landmark("New York", "Gift given by the French", "statue of liberty")
                        , "Failed to add landmark")

    def test_add_landmark_game_in_progress(self):
        self.game._Game__started = True
        self.assertFalse(self.game.add_landmark("New York", "Gift given by the French", "statue of liberty")
                         , "Cannot add landmark once game has started")

    def test_add_landmark_duplicates(self):
        ld = LandmarkFactory().get_landmark("New York", "Gift given by the French", "statue of liberty")
        self.game._Game__landmarks.append(ld)
        self.assertFalse(self.game.add_landmark("New York", "Gift given by the French", "statue of liberty"),
                         "Cannot add duplicate landmarks")


class TestEditLandmarkOrder(unittest.TestCase):
    def setUp(self):
        self.game = TEST_FACTORY()
        self.game._Game__started = False
        self.game._Game__ended = False
        self.game._Game__landmarks.append(LandmarkFactory().get_landmark("Chicago", "Where the Bears play",
                                                                         "Soldier Field"))
        self.game._Game__landmarks.append(LandmarkFactory().get_landmark("GreenBay", "Where the Packers play",
                                                                         "Lambeau Field"))
        self.game._Game__landmarks.append(LandmarkFactory().get_landmark("Los Angeles", "Where the Lakers play",
                                                                         "Staples Center"))
        self.game._Game__landmarks.append(LandmarkFactory().get_landmark("Milwaukee", "Where the Brewers play",
                                                                         "Miller Park"))

    def test_swap_front_back(self):
        self.assertEqual(Errors.NO_ERROR, self.game.edit_landmark_order(0, 3), "should have succeeded swapping")
        self.assertEqual("GreenBay", self.game._Game__landmarks[0].clue, "Order changed")
        self.assertEqual("Chicago", self.game._Game__landmarks[3].clue, "Order changed")

    def test_swap_middle(self):
        self.assertEqual(Errors.NO_ERROR, self.game.edit_landmark_order(1, 2), "should have succeeded swapping")
        self.assertEqual("Los Angeles", self.game._Game__landmarks[1].clue, "Swapping failed")
        self.assertEqual("GreenBay", self.game._Game__landmarks[2].clue, "Swapping failed")

    def test_swap_double(self):
        self.assertEqual(Errors.NO_ERROR, self.game.edit_landmark_order(1, 2), "should have succeeded swapping")
        self.assertEqual(Errors.NO_ERROR, self.game.edit_landmark_order(1, 2), "should have succeeded swapping")
        self.assertEqual("GreenBay", self.game._Game__landmarks[1].clue,
                         "Swapping should have reverted back to original order")
        self.assertEqual("Los Angeles", self.game._Game__landmarks[2].clue,
                         "Swapping should have reverted back to original order")

    def test_swap_negative_index_with_positive(self):
        self.assertEqual(Errors.LANDMARK_INDEX, self.game.edit_landmark_order(-10, 3), "negative index!!")
        self.assertEqual("Milwaukee", self.game._Game__landmarks[3].clue, "Swapping should not have occurred")

    def test_swap_negative_index_with_negative(self):
        self.assertEqual(Errors.LANDMARK_INDEX, self.game.edit_landmark_order(-12, -1), "negative index!!")

    def test_swap_index_greater_than_length(self):
        self.assertEqual(Errors.LANDMARK_INDEX, self.game.edit_landmark_order(4, 3), "Index out of range")
        self.assertEqual("Milwaukee", self.game._Game__landmarks[3].clue, "Swapping should not have occurred")

    def test_swap_from_empty_list(self):
        self.game._Game__landmarks.clear()
        self.assertEqual(Errors.LANDMARK_INDEX, self.game.edit_landmark_order(4, 3), "negative index!!")

    def test_swap_after_game_started(self):
        self.game._Game__started = True
        self.assertEqual(Errors.CAN_ONLY_EDIT_ORDER_WHEN_GAME_IS_NEW, self.game.edit_landmark_order(1, 2), "can not change order after start of game")
        self.assertEqual("GreenBay", self.game._Game__landmarks[1].clue, "Swapping failed")
        self.assertEqual("Los Angeles", self.game._Game__landmarks[2].clue, "Swapping failed")


class TestModifyLandmark(unittest.TestCase):
    # pylint: disable=protected-access,no-member
    def setUp(self):
        self.game = TEST_FACTORY()
        self.game._Game__landmarks.append(LandmarkFactory().get_landmark("Chicago", "Where the Bears play",
                                                                         "Soldier Field"))

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
    # pylint: disable=protected-access,no-member
    def setUp(self):
        self.game = TEST_FACTORY()
        self.game._Game__teams["Team1"] = Team("Team1", "1234")

    def test_modify_team_name(self):
        self.assertTrue(self.game.modify_team("Team1", newname="Team2", newpassword=None), "Team name was not modified")
        self.assertIn("Team2", self.game._Game__teams, "Key was not updated")

    def test_modify_team_password(self):
        self.assertTrue(self.game.modify_team("Team1", newname=None, newpassword="5678"), "password was not modified")
        self.assertIn("Team1", self.game._Game__teams, "Key should not be updated")

    def test_modify_team_name_and_password(self):
        self.assertTrue(self.game.modify_team("Team1", newname="Team103", newpassword="5678"),
                        "name and password was not modified")
        self.assertIn("Team103", self.game._Game__teams, "Key was not updated")

    def test_modify_team_does_not_exist(self):
        self.game._Game__teams.clear()
        self.assertFalse(self.game.modify_team("Team1", newname="Team2", newpassword="5678"), "Team does not exist")


class TestEndGame(unittest.TestCase):
    # pylint: disable=protected-access,no-member
    def setUp(self):
        self.game = TEST_FACTORY()
        self.game._Game__started = True

    def test_end_game_command(self):
        self.assertTrue(self.game._Game__started, "Game in progress")
        self.game.end()
        self.assertTrue(self.game.ended, "Game Has Ended")


class TestDeleteLandmarks(unittest.TestCase):
    # pylint: disable=protected-access,no-member
    def setUp(self):
        self.game = TEST_FACTORY()
        self.game._Game__started = False

    def test_delete_landmark(self):
        landmark1 = LandmarkFactory().get_landmark("ABC", "DEF", "GHI")
        self.game._Game__landmarks.append(landmark1)
        self.game.remove_landmark("ABC")
        self.assertNotIn(landmark1, self.game._Game__landmarks, "Failed to remove landmark")

    def test_delete_multi_landmarks(self):
        landmark1 = LandmarkFactory().get_landmark("ABC", "DEF", "GHI")
        landmark2 = LandmarkFactory().get_landmark("JKL", "MNO", "PQR")
        self.game._Game__landmarks.append(landmark1)
        self.game._Game__landmarks.append(landmark2)
        self.game.remove_landmark("ABC")
        self.assertNotIn(landmark1, self.game._Game__landmarks, "Failed to remove Landmark1")
        self.game.remove_landmark("JKL")
        self.assertNotIn(landmark1, self.game._Game__landmarks, "Failed to remove Landmark2")

    def test_delete_landmark_does_not_exist(self):
        self.assertFalse(self.game.remove_landmark("ABC"), "landmark does not exist")

    def test_delete_landmark_from_empty_landmark_list(self):
        landmark1 = LandmarkFactory().get_landmark("ABC", "DEF", "GHI")
        landmark2 = LandmarkFactory().get_landmark("JKL", "MNO", "PQR")
        self.game._Game__landmarks.append(landmark1)
        self.game._Game__landmarks.append(landmark2)
        self.game._Game__landmarks.clear()
        self.assertFalse(self.game.remove_team("ABC"), "Failed to remove team, list of teams empty")

    def test_remove_landmark_game_started(self):
        self.game._Game__started = True
        landmark1 = LandmarkFactory().get_landmark("ABC", "DEF", "GHI")
        self.game._Game__landmarks.append(landmark1)
        self.assertFalse(self.game.remove_team("ABC"), "should not remove teams once game starts")


class TestAddLandmark2(unittest.TestCase):
    # pylint: disable=protected-access,no-member
    def setUp(self):
        self.game = TEST_FACTORY()

    def test_add_landmark(self):
        landmark1 = LandmarkFactory().get_landmark("ABC", "DEF", "GHI")
        self.assertNotIn(landmark1, self.game._Game__landmarks, "Landmark already Exists")
        self.game.add_landmark(landmark1.clue, landmark1.question, "GHI")
        self.assertIn(landmark1, self.game._Game__landmarks, "Landmark was not successfully added")

    def test_add_landmark2(self):
        landmark1 = LandmarkFactory().get_landmark("ABC", "DEF", "GHI")
        landmark2 = LandmarkFactory().get_landmark("JKL", "MNO", "PQR")
        self.assertNotIn(landmark1, self.game._Game__landmarks, "Landmark already Exists")
        self.game.add_landmark(landmark1.clue, landmark1.question, "GHI")
        self.assertIn(landmark1, self.game._Game__landmarks, "Landmark1 was not successfully added")
        self.game.add_landmark(landmark2.clue, landmark2.question, "PQR")
        self.assertIn(landmark2, self.game._Game__landmarks, "Landmark2 was not sucessfully added")
        self.assertEqual((self.game._Game__landmarks[0], self.game._Game__landmarks[1]), (landmark1, landmark2),
                         "Adding not indexing properly")


class TestGameTeam(unittest.TestCase):
    # pylint: disable=protected-access,no-member
    def setUp(self):
        self.team = Team("Dummy", "password")
        self.game = GameFactory(make_game).create_game()
        l1 = LandmarkFactory().get_landmark("The Place we drink coffee and read books",
                                            "What is the name of the statue out front?", "three disks")
        l2 = LandmarkFactory().get_landmark("The Place we drink coffee and read books",
                                            "What is the name of the statue out front?", "three disks")
        l3 = LandmarkFactory().get_landmark("The Place we drink coffee and read books",
                                            "What is the name of the statue out front?", "three disks")
        self.game._Game__landmarks = [l1, l2, l3]
        self.game._Game__penalty_time = 20
        self.game._Game__penalty_value = 10
        self.game.timer = datetime.timedelta(hours=0, minutes=0, seconds=15)
        self.game.landmark_points = 150
        self.game._Game__teams[self.team.username] = self.team

    def test_get_status(self):
        self.team.clue_time = datetime.timedelta(hours=5, minutes=30, seconds=50)
        now = datetime.timedelta(hours=6, minutes=35, seconds=15)
        self.game._Game__started = True
        self.assertEqual(self.game.get_status(now, self.team.username), 'Points:0;You Are On Landmark:1;' +
                         'Current Landmark Elapsed Time:1:04:25;Time Taken For Landmarks:0:00:00',
                         'get_status did not print the proper stats!')

    def test_quit_question_incorrectpass(self):
        self.game._Game__started = True
        self.team.clue_time = self.team.clue_time = datetime.timedelta(days=15, hours=12, minutes=30, seconds=15)
        now = datetime.timedelta(days=16, hours=7, minutes=25, seconds=8)
        self.assertEqual(Errors.INVALID_LOGIN, self.game.quit_question(now, self.team, "incorrectpasswerd"),
                         "Quit Question Returned True After Incorrect Password!")
        self.assertEqual(self.team.points, 0, "Points Changed after Failing Give Up!")
        self.assertEqual(self.team.current_landmark, 0, "Landmark Index Increased after Failed Password")
        self.assertEqual(len(self.team.time_log), 0, "Time log logged a new entry after failied password")
        self.assertNotEqual(self.team.clue_time, now, "Clue Time Updated After Incorrect Password!")

    def test_quit_question(self):
        self.team.clue_time = datetime.timedelta(days=15, hours=12, minutes=30, seconds=15)
        now = datetime.timedelta(days=16, hours=7, minutes=25, seconds=8)
        self.game._Game__started = True
        self.assertTrue(self.game.quit_question(now, self.team, "password"),
                        "Quit Question Returned False After Correct Password!")
        self.assertEqual(self.team.points, 0, "Points Changed after Giving Up!")
        self.assertEqual(self.team.current_landmark, 1, "Landmark Index Did Not Properly Incriment")
        self.assertEqual(len(self.team.time_log), 1, "Time log did not recieve new entry")
        self.assertEqual(self.team.time_log[0], datetime.timedelta(days=0, hours=18, minutes=54, seconds=53),
                         "Time Log Did Not Recieve The Correct Time")  # this may not work correctly
        self.assertEqual(self.team.clue_time, now, "Clue Time Did Not Update!")

    def test_answer_question_correct_no_time(self):
        self.team.clue_time = datetime.timedelta(days=20, hours=9, minutes=24, seconds=10)
        now = datetime.timedelta(days=20, hours=9, minutes=24, seconds=20)
        self.game._Game__started = True
        self.assertEqual(Errors.NO_ERROR, self.game.answer_question(now, self.team, "three disks"),
                         "Correct Answer Returned False!")
        self.assertEqual(self.team.points, 150, "Points did not increment correctly")
        self.assertEqual(self.team.current_landmark, 1, "Landmark Index Did not Properly increment")
        self.assertEqual(len(self.team.time_log), 1, "Time Log Did Not recieve a new entry")
        self.assertEqual(self.team.time_log[0], datetime.timedelta(days=0, hours=0, minutes=0, seconds=10),
                         "Time Log Did Not Save The Correct Time")
        self.assertEqual(self.team.clue_time, now, "Clue Time Did Not Update!")

    def test_answer_question_incorrect_no_time(self):
        self.team.clue_time = datetime.timedelta(days=20, hours=9, minutes=24, seconds=10)
        now = datetime.timedelta(days=20, hours=9, minutes=24, seconds=20)
        self.game._Game__started = True
        self.assertEqual(Errors.WRONG_ANSWER, self.game.answer_question(now, self.team, "trash fire"),
                         "Incorrect Answer Returned True!")
        self.assertEqual(self.team.points, 0, "Points did not increment correctly")
        self.assertEqual(self.team.current_landmark, 0, "Landmark Index Did not Properly increment")
        self.assertEqual(len(self.team.time_log), 0, "Time Log Did Not recieve a new entry")
        self.assertNotEqual(self.team.clue_time, now, "Clue Time Updated After Incorrect Answer!")
        # Attempt 2
        self.assertEqual(Errors.NO_ERROR, self.game.answer_question(now, self.team, "three disks"),
                         "Correct Answer Returned False After Incorrect Guess!")
        self.assertEqual(self.team.points, 140, "Points did not increment correctly")
        self.assertEqual(self.team.current_landmark, 1, "Landmark Index Did not Properly increment")
        self.assertEqual(len(self.team.time_log), 1, "Time Log Did Not recieve a new entry")
        self.assertEqual(self.team.time_log[0], datetime.timedelta(days=0, hours=0, minutes=0, seconds=10),
                         "Time Log Did Not Save The Correct Time")
        self.assertEqual(self.team.clue_time, now, "Clue Time Did Not Update!")

    def test_answer_question_time_penalty(self):
        self.team.clue_time = datetime.timedelta(days=20, hours=9, minutes=24, seconds=10)
        now = datetime.timedelta(days=20, hours=9, minutes=24, seconds=26)
        self.game._Game__started = True
        self.assertEqual(Errors.NO_ERROR, self.game.answer_question(now, self.team, "three disks"),
                         "Returned False after Correct Answer!")
        self.assertEqual(self.team.points, 130, "Points did not increment correctly")
        self.assertEqual(self.team.current_landmark, 1, "Landmark Index Did not Properly increment")
        self.assertEqual(len(self.team.time_log), 1, "Time Log Did Not recieve a new entry")
        self.assertEqual(self.team.time_log[0], datetime.timedelta(hours=0, minutes=00, seconds=16),
                         "Time Log Did Not Save The Correct Time")
        self.assertEqual(self.team.clue_time, now, "Clue Time Did Not Update!")

    def test_answer_question_time_penalty2(self):
        self.team.clue_time = datetime.timedelta(days=20, hours=9, minutes=24, seconds=10)
        now = datetime.timedelta(days=20, hours=9, minutes=25, seconds=26)
        self.game._Game__started = True
        self.assertEqual(Errors.NO_ERROR, self.game.answer_question(now, self.team, "three disks"),
                         "Returned False After Correct Answer!")
        self.assertEqual(self.team.points, 50, "Points did not increment correctly")
        self.assertEqual(self.team.current_landmark, 1, "Landmark Index Did not Properly increment")
        self.assertEqual(len(self.team.time_log), 1, "Time Log Did Not recieve a new entry")
        self.assertEqual(self.team.time_log[0], datetime.timedelta(hours=0, minutes=1, seconds=16),
                         "Time Log Did Not Save The Correct Time")
        self.assertEqual(self.team.clue_time, now, "Clue Time Did Not Update!")

    def test_answer_question_time_complex(self):
        self.team.clue_time = datetime.timedelta(days=20, hours=9, minutes=24, seconds=10)
        now = datetime.timedelta(days=20, hours=9, minutes=25, seconds=26)
        self.game._Game__started = True
        self.assertEqual(Errors.WRONG_ANSWER, self.game.answer_question(now, self.team, "two disks"),
                         "Returned True after Incorrect Answer!")
        self.assertEqual(self.team.points, 0, "Points did not increment correctly")
        self.assertEqual(self.team.current_landmark, 0, "Landmark Index Did not Properly increment")
        self.assertEqual(len(self.team.time_log), 0, "Time Log Did Not recieve a new entry")
        self.assertNotEqual(self.team.clue_time, now, "Clue Time Updated After Incorrect Answer!")
        self.assertEqual(Errors.NO_ERROR, self.game.answer_question(now, self.team, "three disks"),
                         "Correct Answer Returned False After Incorrect Answer and Wait!")
        self.assertEqual(self.team.points, 40, "Points did not increment correctly")
        self.assertEqual(self.team.current_landmark, 1, "Landmark Index Did not Properly increment")
        self.assertEqual(len(self.team.time_log), 1, "Time Log Did Not recieve a new entry")
        self.assertEqual(self.team.time_log[0], datetime.timedelta(hours=0, minutes=1, seconds=16),
                         "Time Log Did Not Save The Correct Time")  # This may not work properly
        self.assertEqual(self.team.clue_time, now, "Clue Time Did Not Update!")

    def test_answer_question_time_max(self):
        self.team.clue_time = datetime.timedelta(days=3, hours=12, minutes=30, seconds=0)
        now = datetime.timedelta(days=5, hours=20, minutes=30, seconds=15)
        self.game._Game__started = True
        self.assertTrue(self.game.answer_question(now, self.team, "three disks"),
                        "Returned False after Correct Answer!")
        self.assertEqual(self.team.points, 0, "Team Earned Negative Points, Thats not fair!")
        self.assertEqual(self.team.current_landmark, 1, "Landmark Index Did not Properly increment")
        self.assertEqual(len(self.team.time_log), 1, "Time Log Did Not recieve a new entry")
        self.assertEqual(self.team.time_log[0], datetime.timedelta(days=2, hours=8, minutes=0, seconds=15),
                         "Time Log did not Save The Correct Time")
        self.assertEqual(self.team.clue_time, now, "Clue Time Did Not Update!")

    def test_answer_question_incorrect_max(self):
        self.team.clue_time = datetime.timedelta(days=3, hours=12, minutes=30, seconds=0)
        now = datetime.timedelta(days=3, hours=12, minutes=30, seconds=0)
        self.game._Game__started = True
        for _ in range(0, 16):
            self.assertEqual(Errors.WRONG_ANSWER, self.game.answer_question(now, self.team, "two disks"),
                             "Returned True after Incorrect Answer!")
        self.assertEqual(Errors.NO_ERROR, self.game.answer_question(now, self.team, "three disks"),
                         "Returned False After Correct Answer!")
        self.assertEqual(self.team.points, 0, "Team Earned Negative Points, Thats not fair!")
        self.assertEqual(self.team.current_landmark, 1, "Landmark Index Did not Properly increment")
        self.assertEqual(len(self.team.time_log), 1, "Time Log Did Not recieve a new entry")
        self.assertEqual(self.team.time_log[0], datetime.timedelta(days=0, hours=0, minutes=0, seconds=0),
                         "Time Log did not Save The Correct Time")
        self.assertEqual(self.team.clue_time, now, "Clue Time Did Not Update!")

    def test_answer_question_incorrect_max_complex(self):
        self.team.clue_time = datetime.timedelta(days=3, hours=12, minutes=30, seconds=0)
        now = datetime.timedelta(days=3, hours=12, minutes=31, seconds=45)
        self.game._Game__started = True
        for _ in range(0, 11):
            self.assertEqual(Errors.WRONG_ANSWER, self.game.answer_question(now, self.team, "two disks"),
                             "Returned True after Incorrect Answer!")
        before_time = self.team.clue_time
        self.assertEqual(Errors.NO_ERROR, self.game.answer_question(now, self.team, "three disks"),
                         "Returned False After Correct Answer!")
        self.assertEqual(self.team.points, 0, "Team Earned Negative Points, Thats not fair!")
        self.assertEqual(self.team.current_landmark, 1, "Landmark Index Did not Properly increment")
        self.assertEqual(len(self.team.time_log), 1, "Time Log Did Not recieve a new entry")
        self.assertEqual(self.team.time_log[0], datetime.timedelta(days=0, hours=0, minutes=1, seconds=45),
                         "Time Log did not Save The Correct Time")
        self.assertEqual(self.team.clue_time, now, "Clue Time Did Not Update!")
        self.assertEqual(self.team.time_log[0], now - before_time,
                         "Time Log Did Not Save The Correct Time")  # This may not work properly


class TestAnswerQuit(unittest.TestCase):
    # pylint: disable=protected-access,no-member
    def setUp(self):
        self.game = TEST_FACTORY()
        self.game._Game__teams['abc'] = Team('abc', 'def')
        self.game._Game__teams['ghi'] = Team('ghi', 'jkl')
        self.game._Game__landmarks.append(LandmarkFactory().get_landmark('clue1', 'question1', 'answer1'))
        self.game._Game__landmarks.append(LandmarkFactory().get_landmark('clue2', 'question2', 'answer2'))
        self.game._Game__landmarks.append(LandmarkFactory().get_landmark('clue3', 'question3', 'answer3'))

    def get_status_negative_time(self):
        self.game._Game__teams['abc'].clue_time = datetime.timedelta(days=2, hours=5, minutes=30, seconds=50)
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
    SUITE.addTest(unittest.makeSuite(TestEditLandmarkOrder))
    SUITE.addTest(unittest.makeSuite(TestEndGame))
    SUITE.addTest(unittest.makeSuite(TestAnswerQuit))
    SUITE.addTest(unittest.makeSuite(TestGameTeam))
    RUNNER = unittest.TextTestRunner()
    RES = RUNNER.run(SUITE)
    print(RES)
    print("*" * 20)
    for i in RES.failures:
        print(i[1])
