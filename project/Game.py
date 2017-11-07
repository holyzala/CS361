import unittest
import datetime
import time
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
    def add_landmark(self, location, clue, answer):
        pass

    @abstractmethod
    def remove_landmark(self, landmark):
        pass

    @abstractmethod
    def modify_landmark(self, oldlandmark, newlandmark):
        pass

    @abstractmethod
    def set_point_penalty(self, points):
        pass

    @abstractmethod
    def set_time_penalty(self, time):
        pass

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def end(self):
        pass

    @abstractmethod
    def get_status(self,team):
        pass

    @abstractmethod
    def get_status(self,now,team):
        pass

    @abstractmethod
    def answer_question(self,now,team,answer):
        pass

    @abstractmethod
    def quit_question(self,now,team,password):
        pass


class Game(GameInterface):
    def __init__(self):
        self.teams = {}
        self.landmarks = []
        self.started = False
        self.ended = False
        self.penaltyValue = 0
        self.penaltyTime = 0
        self.timer = datetime.timedelta(seconds=0)
        self.landmarkPoints = 0

    def add_team(self, name, password):
        if not self.started:
            if name in self.teams:
                return False
            self.teams[name] = TeamFactory().getTeam(name, password)
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
                self.teams[oldname].changePassword(newpassword)
            if newname:
                self.teams[oldname].changeName(newname)
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

    def modify_landmark(self, oldlandmark, newlandmark):
        self.landmarks = [x.replace(oldlandmark, newlandmark) for x in self.landmarks]

    def set_point_penalty(self, points):
        if not self.started:
            try:
                self.penaltyValue = int(points)
                return True
            except ValueError:
                return False
        return False

    def set_time_penalty(self, time):
        if not self.started:
            try:
                self.penaltyTime = int(time)
                return True
            except ValueError:
                return False
        return False

    def start(self):
        self.started = True

    def end(self):
        self.ended = True

    def quit_question(self, now , team, password):
        if(team.password==password):
            team.currentLandmark+=1
            if(now<team.clueTime):
                team.timelog.append(datetime.timedelta(days=0,hours=0,minutes=0,seconds=0))
            else:
                team.timelog.append(now-team.clueTime)
            team.clueTime=now
            team.penaltyCount = 0
            return True
        return False

    def answer_question(self, now, team, answer):
        lm = self.landmarks[team.currentLandmark]
        if(lm.answer!=answer):
            team.penaltyCount+=self.penaltyValue
            return False
        else:
            if(now<team.clueTime):
                team.timelog.append(datetime.timedelta(days=0,hours=0,minutes=0,seconds=0))
            else:
                team.timelog.append(now-team.clueTime)
            team.currentLandmark+=1
            team.penaltyCount+=(int(((now-team.clueTime)/self.timer))*self.penaltyTime)
            if (team.penaltyCount<=self.landmarkPoints):
                team.points+=(self.landmarkPoints-team.penaltyCount)
            team.clueTime=now
            team.penaltyCount=0
            return True

    def get_status(self, now, team):
        currenttimecalc = (now-team.clueTime)
        totaltime = datetime.timedelta(days=0, hours=0,minutes=0,seconds=0)
        for t in team.timelog:
            totaltime+=t
        return('Points:'+str(team.points)+';You Are On Landmark:'+str(team.currentLandmark)+';Current Landmark Elapsed Time:'+ str(currenttimecalc) +';Time Taken For Landmarks:'+str(totaltime))

    def get_clue(self, team):
        if not self.started:
            return "Game not started yet"
        return self.landmarks[team.current_landmark].get_clue()


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
        self.assertEquals(10, self.game.penaltyValue, "Penalty Value not setting correctly")

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
        self.assertEqual(10, self.game.penaltyValue, "Time value not setting correctly")

    def test_set_penalty_time_negative(self):
        pointValue = -10
        self.assertFalse(self.game.set_time_penalty(pointValue), "Set Time allowing negative values")

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
        self.game.teams["Team1"] = TeamFactory().getTeam("Team1", "1232")

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


class TestEditLandmarkClue(unittest.TestCase):
    def setUp(self):
        self.game = TEST_FACTORY()

    def test_edit_clue(self):
        self.game.landmarks = ["Chicago", "Madison"]
        self.assertTrue(self.game.landmarks, "List is empty")
        self.game.modify_landmark("Chicago", "Vegas")
        self.assertIn("Vegas", self.game.landmarks, "Landmark edited incorrectly")


class TestModifyTeam(unittest.TestCase):
    def setUp(self):
        self.game = TEST_FACTORY()
        self.game.teams["Team1"] = TeamFactory().getTeam("Team1", "1234")

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

    def test_end_game_command(self):
        self.game.started = True
        self.assertTrue(self.game.started, "Game in progress")
        self.game.end()
        self.assertTrue(self.game.ended, "Game Has Ended")

    # how does this test work? Not understanding setting "Final cue sloved" to a landmark list
    def test_completed_game(self):
        self.game.landmarks = "Final Clue solved"
        self.assertEqual(self.game.landmarks, "Final Clue solved", "Final clue has been solved, the game is over")
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
        landmark1 = LandmarkFactory().get_landmark("ABC", "DEF", "GHI")
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
        self.game.add_landmark(landmark1.location, landmark1.clue, landmark1.answer)
        self.assertIn(landmark1, self.game.landmarks, "Landmark was not successfully added")

    def test_add_landmark(self):
        landmark1 = LandmarkFactory().get_landmark("ABC", "DEF", "GHI")
        landmark2 = LandmarkFactory().get_landmark("JKL", "MNO", "PQR")
        self.assertNotIn(landmark1, self.game.landmarks, "Landmark already Exists")
        self.game.add_landmark(landmark1.clue, landmark1.question, landmark1.answer)
        self.assertIn(landmark1, self.game.landmarks, "Landmark1 was not successfully added")
        self.game.add_landmark(landmark2.clue, landmark2.question, landmark2.answer)
        self.assertIn(landmark2, self.game.landmarks, "Landmark2 was not sucessfully added")
        self.assertEqual((self.game.landmarks[0], self.game.landmarks[1]), (landmark1, landmark2), "Adding not indexing properly")

class landmarkDummy:
    def __init__(self):
        self.clue = "The Place we drink coffee and read books"
        self.question = "What is the name of the statue out front?"
        self.answer = "three disks"
        self.location = "uwm library"


class teamDummy:
    def __init__(self):
        self.points = 100
        self.currentLandmark = 1
        self.timelog = [datetime.timedelta(hours=0,minutes=20,seconds=15),datetime.timedelta(hours=0,minutes=35,seconds=25)]
        self.clueTime = datetime.timedelta(hours=0,minutes=0,seconds=0)
        self.password = "password"
        self.penaltyCount = 0

class Test_Game_Team(unittest.TestCase):
    def setUp(self):
        self.team = teamDummy()
        self.game = GameFactory(make_game).create_game()
        l1 = landmarkDummy()
        l2 = landmarkDummy()
        l3 = landmarkDummy()
        self.game.landmarks=[l1,l2,l3]
        self.game.penaltyTime = 20
        self.game.penaltyValue = 10
        self.game.timer = datetime.timedelta(hours = 0, minutes = 0, seconds = 15)
        self.game.landmarkPoints = 150

    def test_get_status(self):
        self.team.clueTime = datetime.timedelta(hours=5,minutes=30,seconds=50)
        now=datetime.timedelta(hours=6,minutes=35,seconds=15)
        self.assertEqual(self.game.get_status(now,self.team), 'Points:100;You Are On Landmark:1;Current Landmark Elapsed Time:1:04:25;Time Taken For Landmarks:0:55:40', 'get_status did not print the proper stats!')

    def test_quit_question_incorrectpass(self):
        self.team.clueTime = self.team.clueTime = datetime.timedelta(days=15,hours=12,minutes=30,seconds=15)#datetime.timedelta(hours=datetime.datetime.now().hour,minutes=datetime.datetime.now().minute,seconds=datetime.datetime.now().second)
        now = datetime.timedelta(days=16,hours=7,minutes=25,seconds=8)
        self.assertFalse(self.game.quit_question(now,self.team,"incorrectpasswerd"),"Quit Question Returned True After Incorrect Password!")
        self.assertEqual(self.team.points,100,"Points Changed after Failing Give Up!")
        self.assertEqual(self.team.currentLandmark,1,"Landmark Index Increased after Failed Password")
        self.assertEqual(len(self.team.timelog),2,"Time log logged a new entry after failied password")
        self.assertNotEqual(self.team.clueTime,now,"Clue Time Updated After Incorrect Password!")

    def test_quit_question(self):
        self.team.clueTime = datetime.timedelta(days=15,hours=12,minutes=30,seconds=15)
        now = datetime.timedelta(days=16,hours=7,minutes=25,seconds=8)
        self.assertTrue(self.game.quit_question(now,self.team,"password"),"Quit Question Returned False After Correct Password!")
        self.assertEqual(self.team.points,100,"Points Changed after Giving Up!")
        self.assertEqual(self.team.currentLandmark,2,"Landmark Index Did Not Properly Incriment")
        self.assertEqual(len(self.team.timelog),3,"Time log did not recieve new entry")
        self.assertEqual(self.team.timelog[2],datetime.timedelta(days=0,hours=18,minutes=54,seconds=53),"Time Log Did Not Recieve The Correct Time") #this may not work correctly
        self.assertEqual(self.team.clueTime,now,"Clue Time Did Not Update!")

    def test_answer_question_correct_no_time(self):
        self.team.clueTime = datetime.timedelta(days=20,hours=9,minutes=24,seconds=10)
        now = datetime.timedelta(days=20,hours=9,minutes=24,seconds=20)
        self.assertTrue(self.game.answer_question(now,self.team,"three disks"),"Correct Answer Returned False!")
        self.assertEqual(self.team.points,250,"Points did not increment correctly")
        self.assertEqual(self.team.currentLandmark,2,"Landmark Index Did not Properly increment")
        self.assertEqual(len(self.team.timelog),3,"Time Log Did Not recieve a new entry")
        self.assertEqual(self.team.timelog[2],datetime.timedelta(days=0,hours=0,minutes=0,seconds=10),"Time Log Did Not Save The Correct Time")
        self.assertEqual(self.team.clueTime,now,"Clue Time Did Not Update!")

    def test_answer_question_incorrect_no_time(self):
        self.team.clueTime = datetime.timedelta(days=20,hours=9,minutes=24,seconds=10)
        now = datetime.timedelta(days=20,hours=9,minutes=24,seconds=20)
        self.assertFalse(self.game.answer_question(now,self.team,"trash fire"),"Incorrect Answer Returned True!")
        self.assertEqual(self.team.points,100,"Points did not increment correctly")
        self.assertEqual(self.team.currentLandmark,1,"Landmark Index Did not Properly increment")
        self.assertEqual(len(self.team.timelog),2,"Time Log Did Not recieve a new entry")
        self.assertNotEqual(self.team.clueTime,now,"Clue Time Updated After Incorrect Answer!")
       #Attempt 2
        self.assertTrue(self.game.answer_question(now,self.team,"three disks")," Correct Answer Returned False After Incorrect Guess!")
        self.assertEqual(self.team.points,240,"Points did not increment correctly")
        self.assertEqual(self.team.currentLandmark,2,"Landmark Index Did not Properly increment")
        self.assertEqual(len(self.team.timelog),3,"Time Log Did Not recieve a new entry")
        self.assertEqual(self.team.timelog[2],datetime.timedelta(days=0,hours=0,minutes=0,seconds=10),"Time Log Did Not Save The Correct Time")
        self.assertEqual(self.team.clueTime,now,"Clue Time Did Not Update!")

    def test_answer_question_time_penalty(self):
        self.team.clueTime = datetime.timedelta(days=20,hours=9,minutes=24,seconds=10)
        now = datetime.timedelta(days=20,hours=9,minutes=24,seconds=26)        
        self.assertTrue(self.game.answer_question(now,self.team,"three disks"),"Returned False after Correct Answer!")
        self.assertEqual(self.team.points,230,"Points did not increment correctly")
        self.assertEqual(self.team.currentLandmark,2,"Landmark Index Did not Properly increment")
        self.assertEqual(len(self.team.timelog),3,"Time Log Did Not recieve a new entry")
        self.assertEqual(self.team.timelog[2],datetime.timedelta(hours=0,minutes=00,seconds=16),"Time Log Did Not Save The Correct Time")
        self.assertEqual(self.team.clueTime,now,"Clue Time Did Not Update!")

    def test_answer_question_time_penalty2(self):
        self.team.clueTime = datetime.timedelta(days=20,hours=9,minutes=24,seconds=10)
        now = datetime.timedelta(days=20,hours=9,minutes=25,seconds=26)
        self.assertTrue(self.game.answer_question(now,self.team,"three disks"), "Returned False After Correct Answer!")
        self.assertEqual(self.team.points,150,"Points did not increment correctly")
        self.assertEqual(self.team.currentLandmark,2,"Landmark Index Did not Properly increment")
        self.assertEqual(len(self.team.timelog),3,"Time Log Did Not recieve a new entry")
        self.assertEqual(self.team.timelog[2],datetime.timedelta(hours=0,minutes=1,seconds=16),"Time Log Did Not Save The Correct Time")
        self.assertEqual(self.team.clueTime,now,"Clue Time Did Not Update!")

    def test_answer_question_time_complex(self):
        self.team.clueTime = datetime.timedelta(days=20,hours=9,minutes=24,seconds=10)
        now = datetime.timedelta(days=20,hours=9,minutes=25,seconds=26)
        self.assertFalse(self.game.answer_question(now,self.team,"two disks"),"Returned True after Incorrect Answer!")
        self.assertEqual(self.team.points,100,"Points did not increment correctly")
        self.assertEqual(self.team.currentLandmark,1,"Landmark Index Did not Properly increment")
        self.assertEqual(len(self.team.timelog),2,"Time Log Did Not recieve a new entry")
        self.assertNotEqual(self.team.clueTime,now,"Clue Time Updated After Incorrect Answer!")
        self.assertTrue(self.game.answer_question(now,self.team,"three disks"),"Correct Answer Retruned False After Incorrect Answer and Wait!")
        self.assertEqual(self.team.points,140,"Points did not increment correctly")
        self.assertEqual(self.team.currentLandmark,2,"Landmark Index Did not Properly increment")
        self.assertEqual(len(self.team.timelog),3,"Time Log Did Not recieve a new entry")
        self.assertEqual(self.team.timelog[2],datetime.timedelta(hours=0,minutes=1,seconds=16),"Time Log Did Not Save The Correct Time") #This may not work properly
        self.assertEqual(self.team.clueTime,now,"Clue Time Did Not Update!")
    
    def test_answer_question_time_max(self):
        self.team.clueTime = datetime.timedelta(days=3,hours=12,minutes=30,seconds=0)
        now = datetime.timedelta(days=5,hours=20,minutes=30,seconds=15)
        self.assertTrue(self.game.answer_question(now,self.team,"three disks"),"Returned False after Correct Answer!")
        self.assertEquals(self.team.points,100,"Team Earned Negative Points, Thats not fair!")
        self.assertEqual(self.team.currentLandmark,2,"Landmark Index Did not Properly increment")
        self.assertEqual(len(self.team.timelog),3,"Time Log Did Not recieve a new entry")
        self.assertEquals(self.team.timelog[2],datetime.timedelta(days=2,hours=8,minutes=0,seconds=15),"Time Log did not Save The Correct Time")
        self.assertEqual(self.team.clueTime,now,"Clue Time Did Not Update!")
   
    def test_answer_question_incorrect_max(self):
        self.team.clueTime = datetime.timedelta(days=3,hours=12,minutes=30,seconds=0)
        now = datetime.timedelta(days=3,hours=12,minutes=30,seconds=0)
        for x in range(0,16):
            self.assertFalse(self.game.answer_question(now,self.team,"two disks"),"Returned True after Incorrect Answer!")
        self.assertTrue(self.game.answer_question(now,self.team,"three disks"), "Returned False After Correct Answer!")
        self.assertEquals(self.team.points,100,"Team Earned Negative Points, Thats not fair!")
        self.assertEqual(self.team.currentLandmark,2,"Landmark Index Did not Properly increment")
        self.assertEqual(len(self.team.timelog),3,"Time Log Did Not recieve a new entry")
        self.assertEqual(self.team.timelog[2],datetime.timedelta(days=0,hours=0,minutes=0,seconds=0),"Time Log did not Save The Correct Time")
        self.assertEqual(self.team.clueTime,now,"Clue Time Did Not Update!")
    
    def test_answer_question_incorrect_max_complex(self):
        self.team.clueTime = datetime.timedelta(days=3,hours=12,minutes=30,seconds=0)
        now = datetime.timedelta(days=3,hours=12,minutes=31,seconds=45)
        for x in range(0,11):
            self.assertFalse(self.game.answer_question(now,self.team,"two disks"),"Returned True after Incorrect Answer!")
        self.assertTrue(self.game.answer_question(now,self.team,"three disks"), "Returned False After Correct Answer!")
        self.assertEquals(self.team.points,100,"Team Earned Negative Points, Thats not fair!")
        self.assertEqual(self.team.currentLandmark,2,"Landmark Index Did not Properly increment")
        self.assertEqual(len(self.team.timelog),3,"Time Log Did Not recieve a new entry")
        self.assertEqual(self.team.timelog[2],datetime.timedelta(days=0,hours=0,minutes=1,seconds=45),"Time Log did not Save The Correct Time")
        self.assertEqual(self.team.clueTime,now,"Clue Time Did Not Update!")
        self.assertEqual(self.timelog[2],self.team.clueTime+datetime.time(00,00,18),"Time Log Did Not Save The Correct Time") #This may not work properly


class TestGetClue(unittest.TestCase):
    def setUp(self):
        self.game = TEST_FACTORY()
        self.game.teams['abc'] = TeamFactory().getTeam('abc', 'def')
        self.game.teams['ghi'] = TeamFactory().getTeam('ghi', 'jkl')
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
        self.team.clueTime = datetime.timedelta(days=2,hours=5,minutes=30,seconds=50)
        now=datetime.timedelta(days=1,hours=0,minutes=35,seconds=15)
        self.assertEqual(self.game.get_status(now,self.team), 'Points:100;You Are On Landmark:1;Current Time:0:00:00;Time Taken For Landmarks:0:55:40', 'get_status did not print the proper stats!')
    
    def answer_question_negative_time(self):
        self.team.clueTime = datetime.timedelta(days=2,hours=5,minutes=30,seconds=50)
        now=datetime.timedelta(days=1,hours=0,minutes=35,seconds=15)
        self.game.answer_question(now,self.team,"three disks")
        self.assertEqual(self.timelog[2],datetime.timedelta(days=0,hours=0,minutes=0,seconds=0),"Time Log did not Save The Correct Time")
        self.assertEqual(self.team.clueTime,now,"Clue Time Did Not Update!")
    
    def quit_question_negative_time(self):
        self.team.clueTime = datetime.timedelta(days=2,hours=5,minutes=30,seconds=50)
        now=datetime.timedelta(days=1,hours=0,minutes=35,seconds=15)
        self.game.quit_question(now,self.team,"password")
        self.assertEqual(self.timelog[2],datetime.timedelta(days=0,hours=0,minutes=0,seconds=0),"Time Log did not Save The Correct Time")
        self.assertEqual(self.team.clueTime,now,"Clue Time Did Not Update!")

if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSetPenaltyValue))
    suite.addTest(unittest.makeSuite(TestSetPenaltyTime))
    suite.addTest(unittest.makeSuite(TestDeleteLandmarks))
    suite.addTest(unittest.makeSuite(TestModifyTeam))
    suite.addTest(unittest.makeSuite(TestAddTeam))
    suite.addTest(unittest.makeSuite(TestRemoveTeam))
    suite.addTest(unittest.makeSuite(TestStartGame))
    suite.addTest(unittest.makeSuite(TestAddLandmark))
    suite.addTest(unittest.makeSuite(TestAddLandmark2))
    suite.addTest(unittest.makeSuite(TestEditLandmarkClue))
    suite.addTest(unittest.makeSuite(TestEndGame))
    suite.addTest(unittest.makeSuite(TestGetClue))
    suite.addTest(unittest.makeSuite(Test_Game_Team))
    runner = unittest.TextTestRunner()
    res = runner.run(suite)
    print(res)
    print("*" * 20)
    for i in res.failures: print(i[1])
