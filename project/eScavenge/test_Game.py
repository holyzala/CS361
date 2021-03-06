import datetime

from django.test import TestCase
from django.utils import timezone

from .Errors import Errors
from .models import GameFactory, make_game
from .models import LandmarkFactory, Landmark
from .models import TeamFactory, LandmarkStat, Team


TEST_FACTORY = GameFactory(make_game).create_game


class TestSetPenaltyValue(TestCase):
    def setUp(self):
        self.game = TEST_FACTORY('test')
        self.game.started = False
        self.game.save()

    def test_set_penalty_positive(self):
        point_value = 10
        self.assertTrue(self.game.set_point_penalty(point_value), "Point value not setting correctly")
        self.assertEqual(10, self.game.penalty_value, "Penalty Value not setting correctly")

    def test_set_penalty_negative(self):
        point_value = -10
        self.assertFalse(self.game.set_point_penalty(point_value), "Set Point allowing negative values")

    def test_set_penalty_zero(self):
        point_value = 0
        self.assertTrue(self.game.set_point_penalty(point_value), "Time Penalty Value Correctly set to 0")
        self.assertEqual(point_value, self.game.penalty_value, "Time Penalty Value not allowing 0")

    def test_set_penalty_during_game(self):
        point_value = 10
        self.game.started = True
        self.assertFalse(self.game.set_point_penalty(point_value), "Allowing setting penalty during game")


class TestSetPenaltyTime(TestCase):
    def setUp(self):
        self.game = TEST_FACTORY('test')
        self.game.started = False
        self.game.save()

    def test_set_penalty_time_positive(self):
        point_value = 10
        self.assertTrue(self.game.set_time_penalty(point_value), "Time value not setting correctly")
        self.assertEqual(point_value, self.game.penalty_time, "Time value not setting correctly")

    def test_set_penalty_time_negative(self):
        self.assertFalse(self.game.set_time_penalty(-10), "Set Time allowing negative values")

    def test_set_penalty_game_started(self):
        point_value = 10
        self.game.started = True
        self.assertFalse(self.game.set_time_penalty(point_value), "Allowing time penalty setting during game")

    def test_set_penalty_time_zero(self):
        point_value = 0
        self.assertTrue(self.game.set_time_penalty(point_value), "Time Penalty Value Correctly set to 0")
        self.assertEqual(point_value, self.game.penalty_time, "Time Penalty Value not allowing 0")


class TestAddTeam(TestCase):
    def setUp(self):
        self.game = TEST_FACTORY('test')
        self.game.started = False
        self.game.save()

    def test_add_team(self):
        self.assertTrue(self.game.add_team("Team1", "1232"), "Did not add team")
        self.assertEqual("Team1", Team.objects.get(username="Team1").username, "Team not in DB")

    def test_add_team_duplicates(self):
        self.assertTrue(self.game.add_team("Team1", "1232"), "Did not add team")
        self.assertFalse(self.game.add_team("Team1", "1232"), "duplicate teams!")

    def test_add_team_after_Game_started(self):
        self.game.started = True
        self.game.save()
        self.assertFalse(self.game.add_team("Team1", "1232"), "should not add teams once Game starts")


class TestRemoveTeam(TestCase):
    def setUp(self):
        self.game = TEST_FACTORY('test')
        self.game.started = False
        self.game.save()
        TeamFactory.get_team("Team1", "1232", self.game)

    def test_remove_team(self):
        self.assertTrue(self.game.remove_team("Team1"), "Failed to remove team")
        with self.assertRaises(Team.DoesNotExist):
            Team.objects.get(username="Team1")

    def test_remove_team_does_not_exist(self):
        self.assertTrue(self.game.remove_team("Team1"), "Failed to remove team")
        self.assertFalse(self.game.remove_team("Team1"), "Team does not exist")

    def test_remove_team_from_empty_team_list(self):
        self.game.teams.clear()
        self.assertFalse(self.game.remove_team("Team1"), "Failed to remove team, list of teams empty")

    def test_remove_team_game_started(self):
        self.game.started = True
        self.assertFalse(self.game.remove_team("Team1"), "should not remove teams once game starts")


class TestStartGame(TestCase):
    def setUp(self):
        self.game = TEST_FACTORY('test')
        self.game.started = False

    def test_start_game(self):
        self.assertEqual(Errors.NO_ERROR, self.game.start(), "game already started")
        self.assertTrue(self.game.started, "game in progress value not set")

    def test_start_game_game_already_running(self):
        self.game.started = True
        self.assertEqual(Errors.ALREADY_STARTED, self.game.start(), "game already started")


class TestAddLandmark(TestCase):
    def setUp(self):
        self.game = TEST_FACTORY('test')
        self.game.started = False
        self.game.save()

    def test_add_landmark(self):
        self.assertTrue(self.game.add_landmark("lm1", "New York", "Gift given by the French", "statue of liberty"),
                        "Failed to add landmark")

    def test_add_landmark_game_in_progress(self):
        self.game.started = True
        self.game.save()
        self.assertFalse(self.game.add_landmark("lm1", "New York", "Gift given by the French", "statue of liberty"),
                         "Cannot add landmark once game has started")

    def test_add_landmark_duplicates(self):
        self.game.add_landmark("lm1", "New York", "Gift given by the French", "statue of liberty")
        self.assertFalse(self.game.add_landmark("lm1", "New York", "Gift given by the French", "statue of liberty"),
                         "Cannot add duplicate landmarks")


class TestEditLandmarkOrder(TestCase):
    def setUp(self):
        self.game = TEST_FACTORY('test')
        self.game.started = False
        self.game.ended = False
        self.game.save()
        LandmarkFactory().get_landmark("lm1", "Chicago", "Where the Bears play", "Soldier Field", self.game)
        LandmarkFactory().get_landmark("lm2", "GreenBay", "Where the Packers play", "Lambeau Field", self.game)
        LandmarkFactory().get_landmark("lm3", "Los Angeles", "Where the Lakers play", "Staples Center", self.game)
        LandmarkFactory().get_landmark("lm4", "Milwaukee", "Where the Brewers play", "Miller Park", self.game)

    def test_swap_front_back(self):
        self.assertEqual(Errors.NO_ERROR, self.game.edit_landmark_order(0, 3), "should have succeeded swapping")
        self.assertEqual("lm2", self.game.landmarks.all()[0].name, "Order changed")
        self.assertEqual("lm1", self.game.landmarks.all()[3].name, "Order changed")

    def test_swap_middle(self):
        self.assertEqual(Errors.NO_ERROR, self.game.edit_landmark_order(1, 2), "should have succeeded swapping")
        self.assertEqual("lm3", self.game.landmarks.all()[1].name, "Swapping failed")
        self.assertEqual("lm2", self.game.landmarks.all()[2].name, "Swapping failed")

    def test_swap_double(self):
        self.assertEqual(Errors.NO_ERROR, self.game.edit_landmark_order(1, 2), "should have succeeded swapping")
        self.assertEqual(Errors.NO_ERROR, self.game.edit_landmark_order(1, 2), "should have succeeded swapping")
        self.assertEqual("lm2", self.game.landmarks.all()[1].name,
                         "Swapping should have reverted back to original order")
        self.assertEqual("lm3", self.game.landmarks.all()[2].name,
                         "Swapping should have reverted back to original order")

    def test_swap_negative_index_with_positive(self):
        self.assertEqual(Errors.LANDMARK_INDEX, self.game.edit_landmark_order(-10, 3), "negative index!!")
        self.assertEqual("lm4", self.game.landmarks.all()[3].name,
                         "Swapping should not have occurred")

    def test_swap_negative_index_with_negative(self):
        self.assertEqual(Errors.LANDMARK_INDEX, self.game.edit_landmark_order(-12, -1), "negative index!!")

    def test_swap_index_greater_than_length(self):
        self.assertEqual(Errors.LANDMARK_INDEX, self.game.edit_landmark_order(4, 3), "Index out of range")
        self.assertEqual("lm4", self.game.landmarks.all()[3].name,
                         "Swapping should not have occurred")

    def test_swap_from_empty_list(self):
        self.game.landmarks.all().delete()
        self.assertEqual(Errors.LANDMARK_INDEX, self.game.edit_landmark_order(4, 3), "negative index!!")

    def test_swap_after_game_started(self):
        self.game.started = True
        self.game.save()
        self.assertEqual(Errors.CAN_ONLY_EDIT_ORDER_WHEN_GAME_IS_NEW, self.game.edit_landmark_order(1, 2),
                         "can not change order after start of game")
        self.assertEqual("lm2", self.game.landmarks.all()[1].name, "Swapping failed")
        self.assertEqual("lm3", self.game.landmarks.all()[2].name, "Swapping failed")


class TestModifyLandmark(TestCase):
    def setUp(self):
        self.game = TEST_FACTORY('test')
        self.game.save()
        LandmarkFactory().get_landmark("lm1", "Chicago", "Where the Bears play", "Soldier Field", self.game)

    def test_edit_name(self):
        self.assertTrue(self.game.modify_landmark("lm1", name="lmX"),
                        "Landmark name was not modified")
        self.assertEqual("lmX", Landmark.objects.get(name="lmX").name, "did not save in DB")

    def test_edit_question(self):
        self.assertTrue(self.game.modify_landmark("lm1", question="Where the UFC fights are"),
                        "Landmark question was not modified")

    def test_edit_answer(self):
        self.assertTrue(self.game.modify_landmark("lm1", answer="The United Center"),
                        "Landmark answer was not modified")

    def test_edit_clue(self):
        self.assertTrue(self.game.modify_landmark("lm1", clue="Chiccago"), "Landmark clue was not modified")

    def test_edit_question_and_answer(self):
        self.assertTrue(self.game.modify_landmark("lm1", question="Tallest Building", answer="Sears Tower"),
                        "Landmark question and answer not modified")

    def test_edit_question_and_clue(self):
        self.assertTrue(self.game.modify_landmark("lm1", question="Tallest Building", clue="Chicaago"),
                        "Landmark question and clue not modified")

    def test_edit_clue_and_answer(self):
        self.assertTrue(self.game.modify_landmark("lm1", clue="CChicago", answer="Sears Tower"),
                        "Landmark question and clue not modified")


class TestModifyTeam(TestCase):
    def setUp(self):
        self.game = TEST_FACTORY('test')
        self.game.save()
        TeamFactory.get_team("Team1", "1234", self.game)

    def test_modify_team_name(self):
        self.assertTrue(self.game.modify_team("Team1", newname="Team2", newpassword=None), "Team name was not modified")
        self.assertIn("Team2", [o.username for o in self.game.teams.all()], "Key was not updated")
        team = Team.objects.get(username="Team2")
        self.assertEqual("Team2", team.username, "Team name not udpated in DB")
        self.assertEqual("1234", team.password, "Team password got incorrectly updated in DB")
        with self.assertRaises(Team.DoesNotExist):
            Team.objects.get(username="Team1")

    def test_modify_team_password(self):
        self.assertTrue(self.game.modify_team("Team1", newname=None, newpassword="5678"), "password was not modified")
        self.assertIn("Team1", [o.username for o in self.game.teams.all()], "Key should not be updated")
        team = Team.objects.get(username="Team1")
        self.assertEqual("Team1", team.username, "Username changed in DB")
        self.assertEqual("5678", team.password, "Password not updated in DB")

    def test_modify_team_name_and_password(self):
        self.assertTrue(self.game.modify_team("Team1", newname="Team103", newpassword="5678"),
                        "name and password was not modified")
        self.assertIn("Team103", [o.username for o in self.game.teams.all()], "Key was not updated")
        with self.assertRaises(Team.DoesNotExist):
            Team.objects.get(username="Team1")
        team = Team.objects.get(username="Team103")
        self.assertEqual("Team103", team.username, "Team name not udpated in DB")
        self.assertEqual("5678", team.password, "Team password not updated in DB")

    def test_modify_team_does_not_exist(self):
        self.game.teams.all().delete()
        self.assertFalse(self.game.modify_team("Team1", newname="Team2", newpassword="5678"), "Team does not exist")


class TestEndGame(TestCase):
    def setUp(self):
        self.game = TEST_FACTORY('test')
        self.game.started = True

    def test_end_game_command(self):
        self.assertTrue(self.game.started, "Game in progress")
        self.game.end()
        self.assertTrue(self.game.ended, "Game Has Ended")


class TestDeleteLandmarks(TestCase):
    def setUp(self):
        self.game = TEST_FACTORY('test')
        self.game.started = False
        self.game.save()

    def test_delete_landmark(self):
        landmark1 = LandmarkFactory().get_landmark("lm1", "ABC", "DEF", "GHI", self.game)
        self.game.remove_landmark("lm1")
        self.assertNotIn(landmark1, self.game.landmarks.all(), "Failed to remove landmark")
        with self.assertRaises(Landmark.DoesNotExist):
            Landmark.objects.get(name="lm1")

    def test_delete_multi_landmarks(self):
        landmark2 = LandmarkFactory().get_landmark("lm2", "JKL", "MNO", "PQR", self.game)
        with self.assertRaises(Landmark.DoesNotExist):
            Landmark.objects.get(name="lm1")
        self.game.remove_landmark("lm2")
        self.assertNotIn(landmark2, self.game.landmarks.all(), "Failed to remove Landmark2")
        with self.assertRaises(Landmark.DoesNotExist):
            Landmark.objects.get(name="lm2")

    def test_delete_landmark_does_not_exist(self):
        self.assertFalse(self.game.remove_landmark("lm1"), "landmark does not exist")

    def test_delete_landmark_from_empty_landmark_list(self):
        self.assertFalse(self.game.remove_landmark("lm1"), "Failed to remove landmark, list of teams empty")
        with self.assertRaises(Landmark.DoesNotExist):
            Landmark.objects.get(name="lm2")

    def test_remove_landmark_game_started(self):
        landmark1 = LandmarkFactory().get_landmark("lm1", "ABC", "DEF", "GHI", self.game)
        self.game.started = True
        self.game.save()
        self.assertFalse(self.game.remove_landmark(landmark1.name), "should not remove landmark once game starts")
        self.assertEqual("lm1", Landmark.objects.get(name=landmark1.name).name,
                         "Landmark shouldnt have been delete from database")


class TestAddLandmark2(TestCase):
    def setUp(self):
        self.game = TEST_FACTORY('test')
        self.game.save()

    def test_add_landmark(self):
        self.assertTrue(self.game.add_landmark("lm1", "ABC", "DEF", "GHI"), "not added")
        landmark = Landmark.objects.get(name="lm1")
        self.assertIn(landmark, self.game.landmarks.all(), "Landmark was not successfully added")

    def test_add_multiple_landmarks2(self):
        self.assertTrue(self.game.add_landmark("lm1", "ABC", "DEF", "GHI"), "not added")
        self.assertTrue(self.game.add_landmark("lm2", "ABC", "DEF", "GHI"), "not added")
        landmark = Landmark.objects.get(name="lm1")
        landmark2 = Landmark.objects.get(name="lm2")
        self.assertIn(landmark, self.game.landmarks.all(), "Landmark was not successfully added")
        self.assertIn(landmark2, self.game.landmarks.all(), "Landmark was not successfully added")
        self.assertEqual((self.game.landmarks.all()[0],
                          self.game.landmarks.all()[1]), (landmark, landmark2),
                         "Adding not indexing properly")


class TestAnswerStatusLimitedDB(TestCase):
    def setUp(self):
        self.game = GameFactory(make_game).create_game('test')
        self.team = TeamFactory.get_team("Dummy", "password", self.game)
        self.team2 = TeamFactory.get_team("Dummy2", "password", self.game)
        self.team3 = TeamFactory.get_team("Dummy3", "passwird", self.game)
        LandmarkFactory().get_landmark("lm1", "The Place we drink coffee and read books",
                                       "What is the name of the statue out front?", "three disks", self.game)
        LandmarkFactory().get_landmark("lm2", "The Place we drink coffee and read books",
                                       "What is the name of the statue out front?", "three disks", self.game)
        LandmarkFactory().get_landmark("lm3", "The Place we drink coffee and read books",
                                       "What is the name of the statue out front?", "three disks", self.game)
        self.game.penalty_time = 20
        self.game.penalty_value = 10
        self.game.timer = datetime.timedelta(hours=0, minutes=0, seconds=15)
        self.game.landmark_points = 150

    def test_get_status(self):
        self.team.clue_time = timezone.now()
        now = self.team.clue_time + datetime.timedelta(hours=1, minutes=4, seconds=25)
        self.game.started = True
        stat_str = ('You are in place {} of {} teams\n'
                    'Total Time Taken: {}\n'
                    'Final Points: {}')
        self.assertEqual(stat_str.format(1, 3, "0:00:00", 0),
                         self.game.get_status(now, self.team.username))

    def test_get_landmarks_index(self):
        landmarks = "0: lm1\n"
        landmarks += "1: lm2\n"
        landmarks += "2: lm3\n"
        self.assertEqual(landmarks, self.game.get_landmarks_index(), "Landmarks aren't correctly returned")

    def test_team_question(self):
        self.game.started = True
        self.team.current_landmark = self.game.landmarks.first()
        self.assertEqual("What is the name of the statue out front?", self.game.get_team_question(self.team),
                         "Team question isn't correct")

    def test_quit_question_incorrectpass(self):
        self.game.started = True
        self.team.clue_time = timezone.now()
        self.team.current_landmark = self.game.landmarks.first()
        now = self.team.clue_time + datetime.timedelta(hours=18, minutes=54, seconds=53)
        self.assertEqual(Errors.INVALID_LOGIN, self.game.quit_question(now, self.team, "incorrectpasswerd"),
                         "Quit Question Returned True After Incorrect Password!")
        self.assertEqual(0, self.team.points, "Points Changed after Failing Give Up!")
        self.assertEqual(self.game.landmarks.first(), self.team.current_landmark,
                         "Landmark Index Increased after Failed Password")
        self.assertEqual(0, self.team.history.all().count(), "Time log logged a new entry after failied password")
        self.assertNotEqual(now, self.team.clue_time, "Clue Time Updated After Incorrect Password!")

    def test_quit_question(self):
        self.team.clue_time = timezone.now()
        self.team.current_landmark = self.game.landmarks.first()
        now = self.team.clue_time + datetime.timedelta(hours=18, minutes=54, seconds=53)
        self.game.started = True
        self.assertTrue(self.game.quit_question(now, self.team, "password"),
                        "Quit Question Returned False After Correct Password!")
        self.assertEqual(0, self.team.points, "Points Changed after Giving Up!")
        self.assertEqual(self.game.landmarks.all()[1], self.team.current_landmark,
                         "Landmark Index Did Not Properly Incriment")
        self.assertEqual(self.game.landmarks.all()[1], Team.objects.get(username="Dummy").current_landmark,
                         "Landmark index not updated in DB")
        self.assertEqual(1, self.team.history.all().count(), "Time log did not recieve new entry")
        temp = self.team.history.first()
        self.assertEqual(datetime.timedelta(hours=18, minutes=54, seconds=53), temp.time_delta,
                         "Time Log Did Not Recieve The Correct Time")
        self.assertEqual(0, temp.points, "History points not correct")
        self.assertTrue(temp.quit, "History quit field wrong")
        self.assertEqual(self.team.clue_time, now, "Clue Time Did Not Update!")

    def test_answer_question_correct_no_time(self):
        self.team.clue_time = timezone.now()
        self.team.current_landmark = self.game.landmarks.first()
        now = self.team.clue_time + datetime.timedelta(seconds=10)
        self.game.started = True
        self.assertEqual(Errors.NO_ERROR, self.game.answer_question(now, self.team, "three disks"),
                         "Correct Answer Returned False!")
        self.assertEqual(self.team.points, 150, "Points did not increment correctly")
        self.assertEqual(150, Team.objects.get(username="Dummy").points, "Points not saved in DB")
        self.assertEqual(self.team.current_landmark, self.game.landmarks.all()[1],
                         "Landmark Index Did not Properly increment")
        self.assertEqual(len(self.team.history.all()), 1, "Time Log Did Not recieve a new entry")
        temp = self.team.history.first()
        self.assertEqual(datetime.timedelta(seconds=10), temp.time_delta, "Time Log Did Not Save The Correct Time")
        self.assertEqual(150, temp.points, "History points not updated")
        self.assertFalse(temp.quit, "History quit field wrong")
        self.assertEqual(self.team.clue_time, now, "Clue Time Did Not Update!")

    def test_answer_question_incorrect_no_time(self):
        self.team.clue_time = timezone.now()
        self.team.current_landmark = self.game.landmarks.first()
        now = self.team.clue_time + datetime.timedelta(seconds=10)
        self.game.started = True
        self.assertEqual(Errors.WRONG_ANSWER, self.game.answer_question(now, self.team, "trash fire"),
                         "Incorrect Answer Returned True!")
        self.assertEqual(0, self.team.points, "Points did not increment correctly")
        self.assertEqual(self.game.landmarks.first(), self.team.current_landmark,
                         "Landmark Index Did not Properly increment")
        self.assertEqual(0, len(self.team.history.all()), "Time Log Did Not recieve a new entry")
        self.assertNotEqual(now, self.team.clue_time, "Clue Time Updated After Incorrect Answer!")
        # Attempt 2
        self.assertEqual(Errors.NO_ERROR, self.game.answer_question(now, self.team, "three disks"),
                         "Correct Answer Returned False After Incorrect Guess!")
        self.assertEqual(140, self.team.points, "Points did not increment correctly")
        self.assertEqual(140, Team.objects.get(username="Dummy").points, "DB points not updated")
        self.assertEqual(self.game.landmarks.all()[1], self.team.current_landmark,
                         "Landmark Index Did not Properly increment")
        self.assertEqual(1, self.team.history.all().count(), "Time Log Did Not recieve a new entry")
        temp = self.team.history.first()
        self.assertEqual(datetime.timedelta(seconds=10), temp.time_delta, "Time Log Did Not Save The Correct Time")
        self.assertEqual(140, temp.points, "History points not updated")
        self.assertFalse(temp.quit, "History quit field wrong")
        self.assertEqual(self.team.clue_time, now, "Clue Time Did Not Update!")

    def test_answer_question_time_penalty(self):
        self.team.clue_time = timezone.now()
        self.team.current_landmark = self.game.landmarks.first()
        now = self.team.clue_time + datetime.timedelta(seconds=16)
        self.game.started = True
        self.assertEqual(Errors.NO_ERROR, self.game.answer_question(now, self.team, "three disks"),
                         "Returned False after Correct Answer!")
        self.assertEqual(130, self.team.points, "Points did not increment correctly")
        self.assertEqual(130, Team.objects.get(username="Dummy").points, "DB points not updated")
        self.assertEqual(self.game.landmarks.all()[1], self.team.current_landmark,
                         "Landmark Index Did not Properly increment")
        self.assertEqual(1, self.team.history.all().count(), "Time Log Did Not recieve a new entry")
        temp = self.team.history.first()
        self.assertEqual(datetime.timedelta(seconds=16), temp.time_delta, "Time Log Did Not Save The Correct Time")
        self.assertEqual(130, temp.points, "History points not updated")
        self.assertEqual(self.team.clue_time, now, "Clue Time Did Not Update!")

    def test_answer_question_time_penalty2(self):
        self.team.clue_time = timezone.now()
        self.team.current_landmark = self.game.landmarks.first()
        now = self.team.clue_time + datetime.timedelta(minutes=1, seconds=16)
        self.game.started = True
        self.assertEqual(Errors.NO_ERROR, self.game.answer_question(now, self.team, "three disks"),
                         "Returned False After Correct Answer!")
        self.assertEqual(50, self.team.points, "Points did not increment correctly")
        self.assertEqual(50, Team.objects.get(username="Dummy").points, "DB points not updated")
        self.assertEqual(self.game.landmarks.all()[1], self.team.current_landmark,
                         "Landmark Index Did not Properly increment")
        self.assertEqual(1, self.team.history.all().count(), "Time Log Did Not recieve a new entry")
        temp = self.team.history.first()
        self.assertEqual(datetime.timedelta(minutes=1, seconds=16), temp.time_delta,
                         "Time Log Did Not Save The Correct Time")
        self.assertEqual(50, temp.points, "History not updated properly")
        self.assertEqual(now, self.team.clue_time, "Clue Time Did Not Update!")

    def test_answer_question_time_complex(self):
        self.team.clue_time = timezone.now()
        self.team.current_landmark = self.game.landmarks.first()
        now = self.team.clue_time + datetime.timedelta(minutes=1, seconds=16)
        self.game.started = True
        self.assertEqual(Errors.WRONG_ANSWER, self.game.answer_question(now, self.team, "two disks"),
                         "Returned True after Incorrect Answer!")
        self.assertEqual(0, self.team.points, "Points did not increment correctly")
        self.assertEqual(self.game.landmarks.first(), self.team.current_landmark,
                         "Landmark Index Did not Properly increment")
        self.assertEqual(0, len(self.team.history.all()), "Time Log Did Not recieve a new entry")
        self.assertNotEqual(now, self.team.clue_time, "Clue Time Updated After Incorrect Answer!")
        self.assertEqual(Errors.NO_ERROR, self.game.answer_question(now, self.team, "three disks"),
                         "Correct Answer Returned False After Incorrect Answer and Wait!")
        self.assertEqual(40, self.team.points, "Points did not increment correctly")
        self.assertEqual(40, Team.objects.get(username="Dummy").points, "DB points not updated")
        self.assertEqual(self.game.landmarks.all()[1], self.team.current_landmark,
                         "Landmark Index Did not Properly increment")
        self.assertEqual(1, self.team.history.all().count(), "Time Log Did Not recieve a new entry")
        temp = self.team.history.first()
        self.assertEqual(datetime.timedelta(minutes=1, seconds=16), temp.time_delta,
                         "Time Log Did Not Save The Correct Time")
        self.assertEqual(40, temp.points, "History points not updated")
        self.assertEqual(now, self.team.clue_time, "Clue Time Did Not Update!")

    def test_answer_question_time_max(self):
        self.team.clue_time = timezone.now()
        self.team.current_landmark = self.game.landmarks.first()
        now = self.team.clue_time + datetime.timedelta(days=2, hours=8, seconds=15)
        self.game.started = True
        self.assertTrue(self.game.answer_question(now, self.team, "three disks"),
                        "Returned False after Correct Answer!")
        self.assertEqual(0, self.team.points, "Team Earned Negative Points, Thats not fair!")
        self.assertEqual(self.game.landmarks.all()[1], self.team.current_landmark,
                         "Landmark Index Did not Properly increment")
        self.assertEqual(1, self.team.history.all().count(), "Time Log Did Not recieve a new entry")
        temp = self.team.history.first()
        self.assertEqual(datetime.timedelta(days=2, hours=8, seconds=15), temp.time_delta,
                         "Time Log did not Save The Correct Time")
        self.assertEqual(0, temp.points, "History not updated")
        self.assertEqual(self.team.clue_time, now, "Clue Time Did Not Update!")

    def test_answer_question_incorrect_max(self):
        self.team.clue_time = timezone.now()
        self.team.current_landmark = self.game.landmarks.first()
        now = self.team.clue_time
        self.game.started = True
        for _ in range(0, 16):
            self.assertEqual(Errors.WRONG_ANSWER, self.game.answer_question(now, self.team, "two disks"),
                             "Returned True after Incorrect Answer!")
        self.assertEqual(Errors.NO_ERROR, self.game.answer_question(now, self.team, "three disks"),
                         "Returned False After Correct Answer!")
        self.assertEqual(0, self.team.points, "Team Earned Negative Points, Thats not fair!")
        self.assertEqual(self.game.landmarks.all()[1], self.team.current_landmark,
                         "Landmark Index Did not Properly increment")
        self.assertEqual(1, self.team.history.all().count(), "Time Log Did Not recieve a new entry")
        temp = self.team.history.first()
        self.assertEqual(datetime.timedelta(), temp.time_delta, "Time Log did not Save The Correct Time")
        self.assertEqual(0, temp.points, "History points wrong")
        self.assertEqual(now, self.team.clue_time, "Clue Time Did Not Update!")

    def test_answer_question_incorrect_max_complex(self):
        self.team.clue_time = timezone.now()
        self.team.current_landmark = self.game.landmarks.first()
        now = self.team.clue_time + datetime.timedelta(minutes=1, seconds=45)
        self.game.started = True
        for _ in range(0, 11):
            self.assertEqual(Errors.WRONG_ANSWER, self.game.answer_question(now, self.team, "two disks"),
                             "Returned True after Incorrect Answer!")
        before_time = self.team.clue_time
        self.assertEqual(Errors.NO_ERROR, self.game.answer_question(now, self.team, "three disks"),
                         "Returned False After Correct Answer!")
        self.assertEqual(0, self.team.points, "Team Earned Negative Points, Thats not fair!")
        self.assertEqual(self.game.landmarks.all()[1], self.team.current_landmark,
                         "Landmark Index Did not Properly increment")
        self.assertEqual(1, self.team.history.all().count(), "Time Log Did Not recieve a new entry")
        temp = self.team.history.first()
        self.assertEqual(datetime.timedelta(minutes=1, seconds=45), temp.time_delta,
                         "Time Log did not Save The Correct Time")
        self.assertEqual(0, temp.points, "History points not correct")
        self.assertEqual(now, self.team.clue_time, "Clue Time Did Not Update!")
        temp = self.team.history.first()
        self.assertEqual(temp.time_delta, now - before_time,
                         "Time Log Did Not Save The Correct Time")


class TestQuitAndStatsProper(TestCase):
    def setUp(self):
        self.game = TEST_FACTORY('test')
        TeamFactory.get_team('abc', 'def', self.game)
        TeamFactory.get_team('ghi', 'jkl', self.game)
        LandmarkFactory().get_landmark("lm1", 'clue1', 'question1', 'answer1', self.game)
        LandmarkFactory().get_landmark("lm2", 'clue2', 'question2', 'answer2', self.game)
        LandmarkFactory().get_landmark("lm3", 'clue3', 'question3', 'answer3', self.game)
        self.game.start()
        self.game.save()

    def test_get_status_negative_time(self):
        temp = self.game.teams.get(username='abc')
        temp.clue_time = timezone.now()
        temp.points = 20
        temp.save()
        now = temp.clue_time - datetime.timedelta(hours=1)
        stat_str = ('You are in place {} of {} teams\n'
                    'Points:{}\n'
                    'You are on Landmark:{} of {}\n'
                    'Current Landmark Elapsed Time:{}\n'
                    'Total Time Taken:{}')
        self.assertEqual(stat_str.format(1, 2, 20, 1, 3, "0:00:00", "0:00:00"), self.game.get_status(now, 'abc'),
                         'get_status did not print the proper stats!')
        self.assertEqual(stat_str.format(2, 2, 0, 1, 3, "0:00:00", "0:00:00"), self.game.get_status(now, 'ghi'),
                         'get_status did not print the proper stats!')

    def test_get_status_place(self):
        TeamFactory.get_team('xyz', '123', self.game)
        temp = self.game.teams.get(username='abc')
        temp.points = 20
        temp.clue_time = timezone.now()
        temp.landmark_index = 2
        temp.save()
        temp = self.game.teams.get(username='ghi')
        temp.points = 30
        temp.save()
        temp = self.game.teams.get(username='xyz')
        temp.points = 10
        temp.save()
        now = temp.clue_time - datetime.timedelta(hours=1)
        stat_str = ('You are in place {} of {} teams\n'
                    'Points:{}\n'
                    'You are on Landmark:{} of {}\n'
                    'Current Landmark Elapsed Time:{}\n'
                    'Total Time Taken:{}')
        self.assertEqual(stat_str.format(2, 3, 20, 1, 3, "0:00:00", "0:00:00"), self.game.get_status(now, 'abc'),
                         'get_status did not print the proper stats!')

    def test_answer_question_negative_time(self):
        self.game.teams.get(username='abc').clue_time = timezone.now()
        now = self.game.teams.get(username='abc').clue_time - datetime.timedelta(hours=10, minutes=35, seconds=15)
        self.assertEqual(Errors.NO_ERROR, self.game.answer_question(now, self.game.teams.get(username='abc'),
                                                                    "answer1"), "Answer failed")
        self.assertEqual(self.game.teams.get(username='abc').history.first().time_delta,
                         datetime.timedelta(days=0, hours=0, minutes=0, seconds=0),
                         "Time Log did not Save The Correct Time")
        self.assertEqual(self.game.teams.get(username='abc').clue_time, now, "Clue Time Did Not Update!")

    def test_quit_question_negative_time(self):
        temp = self.game.teams.get(username='abc')
        temp.clue_time = timezone.now()
        temp.save()
        now = temp.clue_time - datetime.timedelta(hours=1)
        self.assertEqual(Errors.NO_ERROR, self.game.quit_question(now, self.game.teams.get(username='abc'), "def"),
                         "quit failed")
        history = self.game.teams.get(username='abc').history.first()
        self.assertEqual(datetime.timedelta(), history.time_delta, "Time Log did not Save The Correct Time")
        self.assertEqual(0, history.points, "History points not updated")
        self.assertTrue(history.quit, "History quit field wrong")
        self.assertEqual(self.game.teams.get(username='abc').clue_time, now, "Clue Time Did Not Update!")

    def test_quit_last_question(self):
        temp = self.game.teams.get(username='abc')
        temp.current_landmark = self.game.landmarks.all()[2]
        self.assertEqual(Errors.FINAL_ANSWER, self.game.quit_question(timezone.now(), temp, "def"),
                         "quit_question did not notice it was the final question")
        self.assertIsNone(temp.current_landmark, "Quit did not properly increase landmark")

    def test_quit_question_no_more(self):
        temp = self.game.teams.get(username='abc')
        temp.current_landmark = None
        self.assertEqual(Errors.LANDMARK_INDEX, self.game.quit_question(timezone.now(), temp, "def"),
                         "quit_question did not notice team has no more questions")
        self.assertIsNone(temp.current_landmark, "Quit incrimented landmark, even though there were none left")


class TestGameSnapShot(TestCase):
    def setUp(self):
        self.game = TEST_FACTORY('test')
        self.game.save()
        self.lm1 = LandmarkFactory().get_landmark("lm1", "c1", "q1", "a1", self.game)
        self.lm2 = LandmarkFactory().get_landmark("lm2", "c2", "q2", "a2", self.game)
        self.lm3 = LandmarkFactory().get_landmark("lm3", "c3", "q3", "a3", self.game)
        self.lm4 = LandmarkFactory().get_landmark("lm4", "c4", "q4", "a4", self.game)
        TeamFactory().get_team("Team1", "1232", self.game)

    def test_snapshot_no_game_running(self):
        self.assertEqual((Errors.NO_GAME, None), self.game.get_snapshot(), "incorrect Error returned")

    def test_get_snapshot_for_one_team(self):
        TeamFactory.get_team("Team2", "1234", None)
        self.game.started = True
        self.game.save()
        now = datetime.timedelta(hours=6, minutes=35, seconds=15)
        clue_time = datetime.timedelta(hours=0, minutes=20, seconds=50)
        clue_time2 = datetime.timedelta(hours=0, minutes=10, seconds=20)
        clue_time3 = datetime.timedelta(hours=0, minutes=2, seconds=0)
        temp = Team.objects.get(username="Team1")
        LandmarkStat.objects.create(time_delta=now - clue_time, team=temp, landmark=self.lm1, quit=False)
        LandmarkStat.objects.create(time_delta=now - clue_time2, team=temp, landmark=self.lm2, quit=False)
        LandmarkStat.objects.create(time_delta=now - clue_time3, team=temp, landmark=self.lm3, quit=False)
        temp.current_landmark = self.game.landmarks.all()[2]
        temp.points = 10
        temp.full_clean()
        temp.save()
        err, rtn = self.game.get_snapshot()
        self.assertEqual(Errors.NO_ERROR, err, "incorrent message")
        self.assertEqual("Team: Team1\nYou Are On Landmark 3\nTime Taken For Landmarks: 19:12:35\nTotal Points: 10\n",
                         rtn, "Format incorrect")

    def test_get_snapshot_for_several_teams(self):
        TeamFactory.get_team("Team2", "1232", self.game)
        TeamFactory.get_team("Team3", "1232", self.game)
        self.game.started = True
        self.game.save()
        now = datetime.timedelta(hours=6, minutes=35, seconds=15)
        clue_time = datetime.timedelta(hours=0, minutes=20, seconds=50)
        clue_time2 = datetime.timedelta(hours=0, minutes=10, seconds=20)
        clue_time3 = datetime.timedelta(hours=0, minutes=2, seconds=0)
        temp = Team.objects.get(username="Team1")
        LandmarkStat.objects.create(time_delta=now - clue_time, team=temp, landmark=self.lm1, quit=False)
        LandmarkStat.objects.create(time_delta=now - clue_time2, team=temp, landmark=self.lm2, quit=False)
        LandmarkStat.objects.create(time_delta=now - clue_time3, team=temp, landmark=self.lm3, quit=False)
        temp.current_landmark = self.game.landmarks.all()[2]
        temp.points = 10
        temp.full_clean()
        temp.save()
        temp = Team.objects.get(username="Team2")
        LandmarkStat.objects.create(time_delta=now - clue_time, team=temp, landmark=self.lm1, quit=False)
        LandmarkStat.objects.create(time_delta=now - clue_time2, team=temp, landmark=self.lm2, quit=False)
        temp.current_landmark = self.game.landmarks.all()[1]
        temp.points = 5
        temp.full_clean()
        temp.save()
        temp = Team.objects.get(username="Team3")
        LandmarkStat.objects.create(time_delta=now - clue_time, team=temp, landmark=self.lm1, quit=False)
        temp.current_landmark = self.game.landmarks.all()[0]
        temp.points = 0
        temp.full_clean()
        temp.save()
        err, rtn = self.game.get_snapshot()
        self.assertEqual(Errors.NO_ERROR, err, "incorrent message")
        self.assertEqual("Team: Team1\nYou Are On Landmark 3\nTime Taken For Landmarks: 19:12:35\nTotal Points: 10\n"
                         "Team: Team2\nYou Are On Landmark 2\nTime Taken For Landmarks: 12:39:20\nTotal Points: 5\n"
                         "Team: Team3\nYou Are On Landmark 1\nTime Taken For Landmarks: 6:14:25\nTotal Points: 0\n",
                         rtn, "Format incorrect")
