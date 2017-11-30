import datetime
from django.test import TestCase
from django.utils import timezone
from .Errors import Errors
from .Game import GameFactory, make_game
from .Landmark import LandmarkFactory, Landmark
from .Team import TeamFactory, TimeDelta, Team


TEST_FACTORY = GameFactory(make_game).create_game


class TestSetPenaltyValue(TestCase):
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


class TestSetPenaltyTime(TestCase):
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


class TestAddTeam(TestCase):
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


class TestRemoveTeam(TestCase):
    # pylint: disable=protected-access,no-member
    def setUp(self):
        self.game = TEST_FACTORY()
        self.game._Game__started = False
        self.game._Game__teams["Team1"] = TeamFactory.get_team("Team1", "1232")

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


class TestStartGame(TestCase):
    # pylint: disable=protected-access,no-member
    def setUp(self):
        self.game = TEST_FACTORY()
        self.game._Game__started = False

    def test_start_game(self):
        self.game.start()
        self.assertTrue(self.game._Game__started, "game in progress value not set")


class TestAddLandmark(TestCase):
    # pylint: disable=protected-access,no-member
    def setUp(self):
        self.game = TEST_FACTORY()
        self.game._Game__started = False

    def test_add_landmark(self):
        self.assertTrue(self.game.add_landmark("lm1", "New York", "Gift given by the French", "statue of liberty"),
                        "Failed to add landmark")

    def test_add_landmark_game_in_progress(self):
        self.game._Game__started = True
        self.assertFalse(self.game.add_landmark("lm1", "New York", "Gift given by the French", "statue of liberty"),
                         "Cannot add landmark once game has started")

    def test_add_landmark_duplicates(self):
        ld = LandmarkFactory().get_landmark("lm1", "New York", "Gift given by the French", "statue of liberty")
        self.game._Game__landmarks.append(ld)
        self.assertFalse(self.game.add_landmark("lm1", "New York", "Gift given by the French", "statue of liberty"),
                         "Cannot add duplicate landmarks")


class TestEditLandmarkOrder(TestCase):
    def setUp(self):
        self.game = TEST_FACTORY()
        self.game._Game__started = False
        self.game._Game__ended = False
        self.game._Game__landmarks.append(LandmarkFactory().get_landmark("lm1", "Chicago", "Where the Bears play",
                                                                         "Soldier Field"))
        self.game._Game__landmarks.append(LandmarkFactory().get_landmark("lm2", "GreenBay", "Where the Packers play",
                                                                         "Lambeau Field"))
        self.game._Game__landmarks.append(LandmarkFactory().get_landmark("lm3", "Los Angeles", "Where the Lakers play",
                                                                         "Staples Center"))
        self.game._Game__landmarks.append(LandmarkFactory().get_landmark("lm4", "Milwaukee", "Where the Brewers play",
                                                                         "Miller Park"))

    def test_swap_front_back(self):
        self.assertEqual(Errors.NO_ERROR, self.game.edit_landmark_order(0, 3), "should have succeeded swapping")
        self.assertEqual("lm2", self.game._Game__landmarks[0].name, "Order changed")
        self.assertEqual("lm1", self.game._Game__landmarks[3].name, "Order changed")

    def test_swap_middle(self):
        self.assertEqual(Errors.NO_ERROR, self.game.edit_landmark_order(1, 2), "should have succeeded swapping")
        self.assertEqual("lm3", self.game._Game__landmarks[1].name, "Swapping failed")
        self.assertEqual("lm2", self.game._Game__landmarks[2].name, "Swapping failed")

    def test_swap_double(self):
        self.assertEqual(Errors.NO_ERROR, self.game.edit_landmark_order(1, 2), "should have succeeded swapping")
        self.assertEqual(Errors.NO_ERROR, self.game.edit_landmark_order(1, 2), "should have succeeded swapping")
        self.assertEqual("lm2", self.game._Game__landmarks[1].name,
                         "Swapping should have reverted back to original order")
        self.assertEqual("lm3", self.game._Game__landmarks[2].name,
                         "Swapping should have reverted back to original order")

    def test_swap_negative_index_with_positive(self):
        self.assertEqual(Errors.LANDMARK_INDEX, self.game.edit_landmark_order(-10, 3), "negative index!!")
        self.assertEqual("lm4", self.game._Game__landmarks[3].name, "Swapping should not have occurred")

    def test_swap_negative_index_with_negative(self):
        self.assertEqual(Errors.LANDMARK_INDEX, self.game.edit_landmark_order(-12, -1), "negative index!!")

    def test_swap_index_greater_than_length(self):
        self.assertEqual(Errors.LANDMARK_INDEX, self.game.edit_landmark_order(4, 3), "Index out of range")
        self.assertEqual("lm4", self.game._Game__landmarks[3].name, "Swapping should not have occurred")

    def test_swap_from_empty_list(self):
        self.game._Game__landmarks.clear()
        self.assertEqual(Errors.LANDMARK_INDEX, self.game.edit_landmark_order(4, 3), "negative index!!")

    def test_swap_after_game_started(self):
        self.game._Game__started = True
        self.assertEqual(Errors.CAN_ONLY_EDIT_ORDER_WHEN_GAME_IS_NEW, self.game.edit_landmark_order(1, 2), "can not change order after start of game")
        self.assertEqual("lm2", self.game._Game__landmarks[1].name, "Swapping failed")
        self.assertEqual("lm3", self.game._Game__landmarks[2].name, "Swapping failed")


class TestModifyLandmark(TestCase):
    # pylint: disable=protected-access,no-member
    def setUp(self):
        self.game = TEST_FACTORY()
        self.game._Game__landmarks.append(LandmarkFactory().get_landmark("lm1", "Chicago", "Where the Bears play",
                                                                         "Soldier Field"))

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
    # pylint: disable=protected-access,no-member
    def setUp(self):
        self.game = TEST_FACTORY()
        self.game._Game__teams["Team1"] = TeamFactory.get_team("Team1", "1234")

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


class TestEndGame(TestCase):
    # pylint: disable=protected-access,no-member
    def setUp(self):
        self.game = TEST_FACTORY()
        self.game._Game__started = True

    def test_end_game_command(self):
        self.assertTrue(self.game._Game__started, "Game in progress")
        self.game.end()
        self.assertTrue(self.game.ended, "Game Has Ended")


class TestDeleteLandmarks(TestCase):
    # pylint: disable=protected-access,no-member
    def setUp(self):
        self.game = TEST_FACTORY()
        self.game._Game__started = False

    def test_delete_landmark(self):
        landmark1 = LandmarkFactory().get_landmark("lm1", "ABC", "DEF", "GHI")
        self.game._Game__landmarks.append(landmark1)
        self.game.remove_landmark("lm1")
        self.assertNotIn(landmark1, self.game._Game__landmarks, "Failed to remove landmark")
        with self.assertRaises(Landmark.DoesNotExist):
            Landmark.objects.get(name="lm1").name

    def test_delete_multi_landmarks(self):
        landmark1 = LandmarkFactory().get_landmark("lm1", "ABC", "DEF", "GHI")
        landmark2 = LandmarkFactory().get_landmark("lm2", "JKL", "MNO", "PQR")
        self.game._Game__landmarks.append(landmark1)
        self.game._Game__landmarks.append(landmark2)
        self.game.remove_landmark("lm1")
        self.assertNotIn(landmark1, self.game._Game__landmarks, "Failed to remove landmark")
        with self.assertRaises(Landmark.DoesNotExist):
            Landmark.objects.get(name="lm1").name
        self.game.remove_landmark("lm2")
        self.assertNotIn(landmark2, self.game._Game__landmarks, "Failed to remove Landmark2")
        with self.assertRaises(Landmark.DoesNotExist):
            Landmark.objects.get(name="lm2").name

    def test_delete_landmark_does_not_exist(self):
        self.assertFalse(self.game.remove_landmark("lm1"), "landmark does not exist")

    def test_delete_landmark_from_empty_landmark_list(self):
        landmark1 = LandmarkFactory().get_landmark("lm1", "ABC", "DEF", "GHI")
        landmark2 = LandmarkFactory().get_landmark("lm2", "JKL", "MNO", "PQR")
        self.game._Game__landmarks.append(landmark1)
        self.game._Game__landmarks.append(landmark2)
        self.game._Game__landmarks.clear()
        Landmark.objects.all().delete()
        self.assertFalse(self.game.remove_landmark("lm1"), "Failed to remove landmark, list of teams empty")
        with self.assertRaises(Landmark.DoesNotExist):
            Landmark.objects.get(name="lm2").name

    def test_remove_landmark_game_started(self):
        self.game._Game__started = True
        landmark1 = LandmarkFactory().get_landmark("lm1", "ABC", "DEF", "GHI")
        self.game._Game__landmarks.append(landmark1)
        self.assertFalse(self.game.remove_landmark("lm1"), "should not remove landmark once game starts")
        self.assertEqual("lm1", Landmark.objects.get(name="lm1").name, "Landmark shouldnt have been delete from database")


class TestAddLandmark2(TestCase):
    # pylint: disable=protected-access,no-member
    def setUp(self):
        self.game = TEST_FACTORY()

    def test_add_landmark(self):
        self.assertTrue(self.game.add_landmark("lm1", "ABC", "DEF", "GHI"), "not added")
        landmark = Landmark.objects.get(name="lm1")
        self.assertIn(landmark, self.game._Game__landmarks, "Landmark was not successfully added")

    def test_add_multiple_landmarks2(self):
        self.assertTrue(self.game.add_landmark("lm1", "ABC", "DEF", "GHI"), "not added")
        self.assertTrue(self.game.add_landmark("lm2", "ABC", "DEF", "GHI"), "not added")
        landmark = Landmark.objects.get(name="lm1")
        landmark2 = Landmark.objects.get(name="lm2")
        self.assertIn(landmark, self.game._Game__landmarks, "Landmark was not successfully added")
        self.assertIn(landmark2, self.game._Game__landmarks, "Landmark was not successfully added")
        self.assertEqual((self.game._Game__landmarks[0], self.game._Game__landmarks[1]), (landmark, landmark2),
                         "Adding not indexing properly")


class TestGameTeam(TestCase):
    # pylint: disable=protected-access,no-member
    def setUp(self):
        self.team = TeamFactory.get_team("Dummy", "password")
        self.game = GameFactory(make_game).create_game()
        l1 = LandmarkFactory().get_landmark("lm1", "The Place we drink coffee and read books",
                                            "What is the name of the statue out front?", "three disks")
        l2 = LandmarkFactory().get_landmark("lm2", "The Place we drink coffee and read books",
                                            "What is the name of the statue out front?", "three disks")
        l3 = LandmarkFactory().get_landmark("lm3", "The Place we drink coffee and read books",
                                            "What is the name of the statue out front?", "three disks")
        self.game._Game__landmarks = [l1, l2, l3]
        self.game._Game__penalty_time = 20
        self.game._Game__penalty_value = 10
        self.game.timer = datetime.timedelta(hours=0, minutes=0, seconds=15)
        self.game.landmark_points = 150
        self.game._Game__teams[self.team.username] = self.team

    def test_get_status(self):
        self.team.clue_time = timezone.now()
        now = self.team.clue_time + datetime.timedelta(hours=1, minutes=4, seconds=25)
        self.game._Game__started = True
        self.assertEqual(self.game.get_status(now, self.team.username), 'Points:0;You Are On Landmark:1;' +
                         'Current Landmark Elapsed Time:1:04:25;Time Taken For Landmarks:0:00:00',
                         'get_status did not print the proper stats!')

    def test_get_landmarks_index(self):
        landmarks = "0: The Place we drink coffee and read books\n"
        landmarks += "1: The Place we drink coffee and read books\n"
        landmarks += "2: The Place we drink coffee and read books\n"
        self.assertEqual(landmarks, self.game.get_landmarks_index(), "Landmarks aren't correctly returned")

    def test_team_question(self):
        self.assertEqual("What is the name of the statue out front?", self.game.get_team_question(self.team), "Team question isn't correct")

    def test_quit_question_incorrectpass(self):
        self.game._Game__started = True
        self.team.clue_time = timezone.now()
        now = self.team.clue_time + datetime.timedelta(hours=18, minutes=54, seconds=53)
        self.assertEqual(Errors.INVALID_LOGIN, self.game.quit_question(now, self.team, "incorrectpasswerd"),
                         "Quit Question Returned True After Incorrect Password!")
        self.assertEqual(self.team.points, 0, "Points Changed after Failing Give Up!")
        self.assertEqual(self.team.current_landmark, 0, "Landmark Index Increased after Failed Password")
        self.assertEqual(len(self.team.time_log.all()), 0, "Time log logged a new entry after failied password")
        self.assertNotEqual(self.team.clue_time, now, "Clue Time Updated After Incorrect Password!")

    def test_quit_question(self):
        self.team.clue_time = timezone.now()
        now = self.team.clue_time + datetime.timedelta(hours=18, minutes=54, seconds=53)
        self.game._Game__started = True
        self.assertTrue(self.game.quit_question(now, self.team, "password"),
                        "Quit Question Returned False After Correct Password!")
        self.assertEqual(self.team.points, 0, "Points Changed after Giving Up!")
        self.assertEqual(self.team.current_landmark, 1, "Landmark Index Did Not Properly Incriment")
        self.assertEqual(len(self.team.time_log.all()), 1, "Time log did not recieve new entry")
        temp = self.team.time_log.first()
        self.assertEqual(temp.time_delta, datetime.timedelta(days=0, hours=18, minutes=54, seconds=53),
                         "Time Log Did Not Recieve The Correct Time")  # this may not work correctly
        self.assertEqual(self.team.clue_time, now, "Clue Time Did Not Update!")

    def test_answer_question_correct_no_time(self):
        self.team.clue_time = timezone.now()
        now = self.team.clue_time + datetime.timedelta(seconds=10)
        self.game._Game__started = True
        self.assertEqual(Errors.NO_ERROR, self.game.answer_question(now, self.team, "three disks"),
                         "Correct Answer Returned False!")
        self.assertEqual(self.team.points, 150, "Points did not increment correctly")
        self.assertEqual(self.team.current_landmark, 1, "Landmark Index Did not Properly increment")
        self.assertEqual(len(self.team.time_log.all()), 1, "Time Log Did Not recieve a new entry")
        temp = self.team.time_log.first()
        self.assertEqual(temp.time_delta, datetime.timedelta(days=0, hours=0, minutes=0, seconds=10),
                         "Time Log Did Not Save The Correct Time")
        self.assertEqual(self.team.clue_time, now, "Clue Time Did Not Update!")

    def test_answer_question_incorrect_no_time(self):
        self.team.clue_time = timezone.now()
        now = self.team.clue_time + datetime.timedelta(seconds=10)
        self.game._Game__started = True
        self.assertEqual(Errors.WRONG_ANSWER, self.game.answer_question(now, self.team, "trash fire"),
                         "Incorrect Answer Returned True!")
        self.assertEqual(self.team.points, 0, "Points did not increment correctly")
        self.assertEqual(self.team.current_landmark, 0, "Landmark Index Did not Properly increment")
        self.assertEqual(len(self.team.time_log.all()), 0, "Time Log Did Not recieve a new entry")
        self.assertNotEqual(self.team.clue_time, now, "Clue Time Updated After Incorrect Answer!")
        # Attempt 2
        self.assertEqual(Errors.NO_ERROR, self.game.answer_question(now, self.team, "three disks"),
                         "Correct Answer Returned False After Incorrect Guess!")
        self.assertEqual(self.team.points, 140, "Points did not increment correctly")
        self.assertEqual(self.team.current_landmark, 1, "Landmark Index Did not Properly increment")
        self.assertEqual(len(self.team.time_log.all()), 1, "Time Log Did Not recieve a new entry")
        temp = self.team.time_log.first()
        self.assertEqual(temp.time_delta, datetime.timedelta(days=0, hours=0, minutes=0, seconds=10),
                         "Time Log Did Not Save The Correct Time")
        self.assertEqual(self.team.clue_time, now, "Clue Time Did Not Update!")

    def test_answer_question_time_penalty(self):
        self.team.clue_time = timezone.now()
        now = self.team.clue_time + datetime.timedelta(seconds=16)
        self.game._Game__started = True
        self.assertEqual(Errors.NO_ERROR, self.game.answer_question(now, self.team, "three disks"),
                         "Returned False after Correct Answer!")
        self.assertEqual(self.team.points, 130, "Points did not increment correctly")
        self.assertEqual(self.team.current_landmark, 1, "Landmark Index Did not Properly increment")
        self.assertEqual(len(self.team.time_log.all()), 1, "Time Log Did Not recieve a new entry")
        temp = self.team.time_log.first()
        self.assertEqual(temp.time_delta, datetime.timedelta(hours=0, minutes=00, seconds=16),
                         "Time Log Did Not Save The Correct Time")
        self.assertEqual(self.team.clue_time, now, "Clue Time Did Not Update!")

    def test_answer_question_time_penalty2(self):
        self.team.clue_time = timezone.now()
        now = self.team.clue_time + datetime.timedelta(minutes=1, seconds=16)
        self.game._Game__started = True
        self.assertEqual(Errors.NO_ERROR, self.game.answer_question(now, self.team, "three disks"),
                         "Returned False After Correct Answer!")
        self.assertEqual(self.team.points, 50, "Points did not increment correctly")
        self.assertEqual(self.team.current_landmark, 1, "Landmark Index Did not Properly increment")
        self.assertEqual(len(self.team.time_log.all()), 1, "Time Log Did Not recieve a new entry")
        temp = self.team.time_log.first()
        self.assertEqual(temp.time_delta, datetime.timedelta(hours=0, minutes=1, seconds=16),
                         "Time Log Did Not Save The Correct Time")
        self.assertEqual(self.team.clue_time, now, "Clue Time Did Not Update!")

    def test_answer_question_time_complex(self):
        self.team.clue_time = timezone.now()
        now = self.team.clue_time + datetime.timedelta(minutes=1, seconds=16)
        self.game._Game__started = True
        self.assertEqual(Errors.WRONG_ANSWER, self.game.answer_question(now, self.team, "two disks"),
                         "Returned True after Incorrect Answer!")
        self.assertEqual(self.team.points, 0, "Points did not increment correctly")
        self.assertEqual(self.team.current_landmark, 0, "Landmark Index Did not Properly increment")
        self.assertEqual(len(self.team.time_log.all()), 0, "Time Log Did Not recieve a new entry")
        self.assertNotEqual(self.team.clue_time, now, "Clue Time Updated After Incorrect Answer!")
        self.assertEqual(Errors.NO_ERROR, self.game.answer_question(now, self.team, "three disks"),
                         "Correct Answer Returned False After Incorrect Answer and Wait!")
        self.assertEqual(self.team.points, 40, "Points did not increment correctly")
        self.assertEqual(self.team.current_landmark, 1, "Landmark Index Did not Properly increment")
        self.assertEqual(len(self.team.time_log.all()), 1, "Time Log Did Not recieve a new entry")
        temp = self.team.time_log.first()
        self.assertEqual(temp.time_delta, datetime.timedelta(hours=0, minutes=1, seconds=16),
                         "Time Log Did Not Save The Correct Time")  # This may not work properly
        self.assertEqual(self.team.clue_time, now, "Clue Time Did Not Update!")

    def test_answer_question_time_max(self):
        self.team.clue_time = timezone.now()
        now = self.team.clue_time + datetime.timedelta(days=2, hours=8, seconds=15)
        self.game._Game__started = True
        self.assertTrue(self.game.answer_question(now, self.team, "three disks"),
                        "Returned False after Correct Answer!")
        self.assertEqual(self.team.points, 0, "Team Earned Negative Points, Thats not fair!")
        self.assertEqual(self.team.current_landmark, 1, "Landmark Index Did not Properly increment")
        self.assertEqual(len(self.team.time_log.all()), 1, "Time Log Did Not recieve a new entry")
        temp = self.team.time_log.first()
        self.assertEqual(temp.time_delta, datetime.timedelta(days=2, hours=8, minutes=0, seconds=15),
                         "Time Log did not Save The Correct Time")
        self.assertEqual(self.team.clue_time, now, "Clue Time Did Not Update!")

    def test_answer_question_incorrect_max(self):
        self.team.clue_time = timezone.now()
        now = self.team.clue_time
        self.game._Game__started = True
        for _ in range(0, 16):
            self.assertEqual(Errors.WRONG_ANSWER, self.game.answer_question(now, self.team, "two disks"),
                             "Returned True after Incorrect Answer!")
        self.assertEqual(Errors.NO_ERROR, self.game.answer_question(now, self.team, "three disks"),
                         "Returned False After Correct Answer!")
        self.assertEqual(self.team.points, 0, "Team Earned Negative Points, Thats not fair!")
        self.assertEqual(self.team.current_landmark, 1, "Landmark Index Did not Properly increment")
        self.assertEqual(len(self.team.time_log.all()), 1, "Time Log Did Not recieve a new entry")
        temp = self.team.time_log.first()
        self.assertEqual(temp.time_delta, datetime.timedelta(days=0, hours=0, minutes=0, seconds=0),
                         "Time Log did not Save The Correct Time")
        self.assertEqual(self.team.clue_time, now, "Clue Time Did Not Update!")

    def test_answer_question_incorrect_max_complex(self):
        self.team.clue_time = timezone.now()
        now = self.team.clue_time + datetime.timedelta(minutes=1, seconds=45)
        self.game._Game__started = True
        for _ in range(0, 11):
            self.assertEqual(Errors.WRONG_ANSWER, self.game.answer_question(now, self.team, "two disks"),
                             "Returned True after Incorrect Answer!")
        before_time = self.team.clue_time
        self.assertEqual(Errors.NO_ERROR, self.game.answer_question(now, self.team, "three disks"),
                         "Returned False After Correct Answer!")
        self.assertEqual(self.team.points, 0, "Team Earned Negative Points, Thats not fair!")
        self.assertEqual(self.team.current_landmark, 1, "Landmark Index Did not Properly increment")
        self.assertEqual(len(self.team.time_log.all()), 1, "Time Log Did Not recieve a new entry")
        temp = self.team.time_log.first()
        self.assertEqual(temp.time_delta, datetime.timedelta(days=0, hours=0, minutes=1, seconds=45),
                         "Time Log did not Save The Correct Time")
        self.assertEqual(self.team.clue_time, now, "Clue Time Did Not Update!")
        temp = self.team.time_log.first()
        self.assertEqual(temp.time_delta, now - before_time,
                         "Time Log Did Not Save The Correct Time")  # This may not work properly


class TestAnswerQuit(TestCase):
    # pylint: disable=protected-access,no-member
    def setUp(self):
        self.game = TEST_FACTORY()
        self.game._Game__teams['abc'] = TeamFactory.get_team('abc', 'def')
        self.game._Game__teams['ghi'] = TeamFactory.get_team('ghi', 'jkl')
        self.game._Game__landmarks.append(LandmarkFactory().get_landmark("lm1", 'clue1', 'question1', 'answer1'))
        self.game._Game__landmarks.append(LandmarkFactory().get_landmark("lm2", 'clue2', 'question2', 'answer2'))
        self.game._Game__landmarks.append(LandmarkFactory().get_landmark("lm3", 'clue3', 'question3', 'answer3'))

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


class TestGameSnapShot(TestCase):
    def setUp(self):
        self.game = TEST_FACTORY()
        self.game._Game__landmarks.append(LandmarkFactory().get_landmark("lm1", "c1", "q1", "a1"))
        self.game._Game__landmarks.append(LandmarkFactory().get_landmark("lm2", "c2", "q2", "a2"))
        self.game._Game__landmarks.append(LandmarkFactory().get_landmark("lm3", "c3", "q3", "a3"))
        self.game._Game__landmarks.append(LandmarkFactory().get_landmark("lm4", "c4", "q4", "a4"))
        self.game._Game__teams["Team1"] = TeamFactory().get_team("Team1", "1232")

    def test_snapshot_no_game_running(self):
        now = datetime.timedelta(hours=6, minutes=35, seconds=15)
        self.assertEqual((Errors.NO_GAME, None), self.game.get_snapshot(now), "incorrect Error returned")

    def test_get_snapshot_for_one_team(self):
        self.game._Game__started = True
        now = datetime.timedelta(hours=6, minutes=35, seconds=15)
        clue_time = datetime.timedelta(hours=0, minutes=20, seconds=50)
        clue_time2 = datetime.timedelta(hours=0, minutes=10, seconds=20)
        clue_time3 = datetime.timedelta(hours=0, minutes=2, seconds=0)
        temp = Team.objects.get(username="Team1")
        TimeDelta.objects.create(time_delta=now-clue_time, team=temp)
        TimeDelta.objects.create(time_delta=now-clue_time2, team=temp)
        TimeDelta.objects.create(time_delta=now-clue_time3, team=temp)
        temp.current_landmark = 2
        temp.points = 10
        temp.full_clean()
        temp.save()
        err, rtn = self.game.get_snapshot(now)
        self.assertEqual(Errors.NO_ERROR, err, "incorrent message")
        self.assertEqual("Team: Team1\nYou Are On Landmark 3\nTime Taken For Landmarks: 19:12:35\nTotal Points: 10\n",
                         rtn, "Format incorrect")

    def test_get_snapshot_for_several_teams(self):
        self.game._Game__teams["Team2"] = TeamFactory.get_team("Team2", "1232")
        self.game._Game__teams["Team3"] = TeamFactory.get_team("Team3", "1232")
        self.game._Game__started = True
        now = datetime.timedelta(hours=6, minutes=35, seconds=15)
        clue_time = datetime.timedelta(hours=0, minutes=20, seconds=50)
        clue_time2 = datetime.timedelta(hours=0, minutes=10, seconds=20)
        clue_time3 = datetime.timedelta(hours=0, minutes=2, seconds=0)
        temp = Team.objects.get(username="Team1")
        TimeDelta.objects.create(time_delta=now-clue_time, team=temp)
        TimeDelta.objects.create(time_delta=now-clue_time2, team=temp)
        TimeDelta.objects.create(time_delta=now-clue_time3, team=temp)
        temp.current_landmark = 2
        temp.points = 10
        temp.full_clean()
        temp.save()
        temp = Team.objects.get(username="Team2")
        TimeDelta.objects.create(time_delta=now-clue_time, team=temp)
        TimeDelta.objects.create(time_delta=now-clue_time2, team=temp)
        temp.current_landmark = 1
        temp.points = 5
        temp.full_clean()
        temp.save()
        temp = Team.objects.get(username="Team3")
        TimeDelta.objects.create(time_delta=now-clue_time, team=temp)
        temp.current_landmark = 0
        temp.points = 0
        temp.full_clean()
        temp.save()
        err, rtn = self.game.get_snapshot(now)
        self.assertEqual(Errors.NO_ERROR, err, "incorrent message")
        self.assertEqual("Team: Team1\nYou Are On Landmark 3\nTime Taken For Landmarks: 19:12:35\nTotal Points: 10\n"
                         "Team: Team2\nYou Are On Landmark 2\nTime Taken For Landmarks: 12:39:20\nTotal Points: 5\n"
                         "Team: Team3\nYou Are On Landmark 1\nTime Taken For Landmarks: 6:14:25\nTotal Points: 0\n",
                         rtn, "Format incorrect")
