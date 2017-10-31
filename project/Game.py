import unittest
import datetime
import time

class Game:
    def __init__(self):
        self.teams = []
        self.landmarks = []
        self.started = False
        self.ended = False
        self.penaltyValue = 0
        self.penaltyTime = 0
        self.timer = datetime.time(0,0,0)
        self.curteam = 0

    def add_team(self, team):
        pass

    def remove_team(self, name):
        pass

    def modify_team(self, oldname, name=None, password=None):
        pass

    def add_landmark(self, landmark):
        pass

    def remove_landmark(self, landmark):
        pass

    def modify_landmark(self, oldlandmark, newlandmark):
        self.landmarks = [x.replace(oldlandmark, newlandmark) for x in self.landmarks]

    def set_point_penalty(self, points):
        pass

    def set_time_penalty(self, time):
        pass

    def start(self):
        pass

    def end(self):
        self.ended = True

    def get_status(self):
        pass

    def answer_question(self,answer):
        pass
    
    def quit_question(self,password):
        pass    

class TestGame(unittest.TestCase):
    def setUp(self):
        self.game = Game()

class TestEditLandmarkClue(unittest.TestCase):
    def setUp(self):
        self.game = Game()

    def test_edit_clue(self):
        self.game.landmarks = ["Chicago", "Madison"]
        self.assertTrue(self.game.landmarks, "List is empty")
        self.game.modify_landmark("Chicago", "Vegas")
        self.assertIn("Vegas", self.game.landmarks, "Landmark edited incorrectly")

class TestEndGame(unittest.TestCase):
    def setUp(self):
       self.game = Game()

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

class landmarkDummy:
    clue = "The Place we drink coffee and read books"
    question = "What is the name of the statue out front?"
    answer = "three disks"
    location = "uwm library"
    points = 150
    timer = datetime.time(0,0,15)
    timepenelty = 20
    answerpenalty = 10

class teamDummy:
    points = 100
    currentLandmark = 1
    timelog = [datetime.time(0,20,15),datetime.time(0,35,25)]
    password = "password"
    clueTime = datetime.time(0,0,0)

class Test_Game_Team(unittest.TestCase):
    def setUp(self):
        self.game = Game()
        l1 = landmarkDummy()
        l2 = landmarkDummy()
        l3 = landmarkDummy()
        self.game.landmarks=[l1,l2,l3]
        self.game.curteam = teamDummy()
        self.game.penaltyTime = 20
        self.game.penaltyValue = 10
        self.game.timer = datetime.time(00,00,15)

    def test_get_status(self):
        self.game.curteam.clueTime = datetime.time(5,30,50)    
        currenttimecalc = (str(datetime.datetime.now().hour-self.game.curteam.clueTime.hour)+":"+str(datetime.datetime.now().minute-self.game.curteam.clueTime.minute)+":"+str(datetime.datetime.now().second-self.game.curteam.clueTime.second))
        self.assertEqual(self.game.get_status(), 'Points:100;You Are On Landmark:2;Current Time:'+currenttimecalc+';Time Taken For Landmarks:00:55:40)', 'get_status did not print the proper stats!')

        #The final assert of adding correct time to timelog may not work properly because though the test takes milliseconds,
        #  it may go over the second threshold
    def test_quit_question(self):
        self.game.curteam.clueTime = datetime.datetime.now()
        self.game.quit_question("password")
        self.assertEqual(self.game.curteam.points,100,"Points Changed after Giving Up!")
        self.assertEqual(self.game.curteam.currentLandmark,2,"Landmark Index Did Not Properly Incriment")
        self.assertEqual(len(self.game.curteam.timelog),2,"Time log did not recieve new entry")
        self.assertEqual(self.game.curteam.timelog[2],self.game.curteam.clueTime,"Time Log Did Not Recieve The Correct Time") #this may not work correctly

    def test_answer_question_correct_no_time(self):
        self.game.curteam.clueTime = datetime.datetime.now()
        self.game.answer_question("three disks")
        self.assertEqual(self.game.curteam.points,250,"Points did not increment correctly")
        self.assertEqual(self.game.curteam.currentLandmark,2,"Landmark Index Did not Properly increment")
        self.assertEqual(len(self.game.curteam.timelog),3,"Time Log Did Not recieve a new entry")
        self.assertEqual(self.game.curteam.timelog[2],self.game.curteam.clueTime,"Time Log Did Not Save The Correct Time") #This may not work properly

    def test_answer_question_incorrect_no_time(self):
        self.game.curteam.clueTime = datetime.datetime.now()
        self.game.answer_question("trash fire")
        self.assertEqual(self.game.curteam.points,100,"Points did not increment correctly")
        self.assertEqual(self.game.curteam.currentLandmark,1,"Landmark Index Did not Properly increment")
        self.assertEqual(len(self.game.curteam.timelog),2,"Time Log Did Not recieve a new entry")
        self.game.answer_question("three disks")
        self.assertEqual(self.game.curteam.points,240,"Points did not increment correctly")
        self.assertEqual(self.game.curteam.currentLandmark,2,"Landmark Index Did not Properly increment")
        self.assertEqual(len(self.game.curteam.timelog),3,"Time Log Did Not recieve a new entry")
        self.assertEqual(self.game.curteam.timelog[2],self.game.curteam.clueTime,"Time Log Did Not Save The Correct Time")#This may not work properly

        #TIME PENELTY TESTS HAVE A WAIT THAT WILl CAUSE THE TEST TO RUN A UNORMALLY LONG AMOUNT OF TIME, 
        # IT IS RECCOMENDED TO HAVE THESE TESTS BE LAST IN THE SUITE

    def test_answer_question_time_penalty(self):
        self.game.curteam.clueTime = datetime.datetime.now()
        time.sleep(16)
        self.game.answer_question("three disks")
        self.assertEqual(self.game.curteam.points,230,"Points did not increment correctly")
        self.assertEqual(self.game.curteam.currentLandmark,2,"Landmark Index Did not Properly increment")
        self.assertEqual(len(self.game.curteam.timelog),3,"Time Log Did Not recieve a new entry")
        self.assertEqual(self.game.curteam.timelog[2],self.game.curteam.clueTime+datetime.time(00,00,16),"Time Log Did Not Save The Correct Time") #This may not work properly

    def test_answer_question_time_penalty2(self):
        self.game.curteam.clueTime = datetime.datetime.now()
        time.sleep(31)
        self.game.answer_question("three disks")
        self.assertEqual(self.game.curteam.points,210,"Points did not increment correctly")
        self.assertEqual(self.game.curteam.currentLandmark,2,"Landmark Index Did not Properly increment")
        self.assertEqual(len(self.game.curteam.timelog),3,"Time Log Did Not recieve a new entry")
        self.assertEqual(self.game.curteam.timelog[2],self.game.curteam.clueTime+datetime.time(00,00,31),"Time Log Did Not Save The Correct Time") #This may not work properly

    def test_answer_question_time_complex(self):
        self.game.curteam.clueTime = datetime.datetime.now()
        self.game.answer_question("two disks")
        self.assertEqual(self.game.curteam.points,100,"Points did not increment correctly")
        self.assertEqual(self.game.curteam.currentLandmark,1,"Landmark Index Did not Properly increment")
        self.assertEqual(len(self.game.curteam.timelog),2,"Time Log Did Not recieve a new entry")
        time.sleep(18)
        self.game.answer_question("three disks")
        self.assertEqual(self.game.curteam.points,220,"Points did not increment correctly")
        self.assertEqual(self.game.curteam.currentLandmark,2,"Landmark Index Did not Properly increment")
        self.assertEqual(len(self.game.curteam.timelog),3,"Time Log Did Not recieve a new entry")
        self.assertEqual(self.timelog[2],self.game.curteam.clueTime+datetime.time(00,00,18),"Time Log Did Not Save The Correct Time") #This may not work properly


if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestEndGame))
    suite.addTest(unittest.makeSuite(TestEditLandmarkClue))
    suite.addTest(unittest.makeSuite(TestGame))
    suite.addTest(unittest.makeSuite(Test_Game_Team))
    runner = unittest.TextTestRunner()
    res = runner.run(suite)
    print(res)
    print("*" * 20)
    for i in res.failures: print(i[1])