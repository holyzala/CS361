import unittest
import datetime
import time


class Team:
    def __init__(self, Game):
        self.username = ""
        self.password = ""
        self.points = 0
        self.timelog = []
        self.currentLandmark = 0
        self.clueTime = 0
        self.game = Game

    def login(self, password):
        return "", False

    def answer_question(self, answer):
        return ""

    def get_status(self):
        return "self.points"

    def get_clue(self):
        return ""
    def question_quit(self,password):
        return""

class landmarkDummy:
    clue = "The Place we drink coffee and read books"
    question = "What is the name of the statue out front?"
    answer = "three disks"
    location = "uwm library"
    points = 150
    timer = datetime.time(0,0,15)
    timepenelty = 20
    answerpenalty = 10

class gameDummy:
    l1 = landmarkDummy()
    l2 = landmarkDummy()
    landmarks = [l1,l2]

class TestTeam(unittest.TestCase):
    def setUp(self):
        game = gameDummy()
        self.team = Team(game)
        self.team.points = 100
        self.team.currentLandmark = 1
        self.team.timelog = [datetime.time(0,20,15),datetime.time(0,35,25)]
        self.team.password = "password"
        
    def test_get_status(self):
        self.team.clueTime = datetime.time(5,30,50)    
        currenttimecalc = (str(datetime.datetime.now().hour-self.team.clueTime.hour)+":"+str(datetime.datetime.now().minute-self.team.clueTime.minute)+":"+str(datetime.datetime.now().second-self.team.clueTime.second))
        self.assertEqual(self.team.get_status(), 'Points:100;You Are On Landmark:2;Current Time:'+currenttimecalc+';Time Taken For Landmarks:00:55:40)', 'get_status did not print the proper stats!')
#The final assert of adding correct time to timelog may not work properly because though the test takes milliseconds,
#  it may go over the second threshold
    def test_quit_question(self):
        self.team.clueTime = datetime.datetime.now()
        self.team.question_quit("password")
        self.assertEqual(self.team.points,100,"Points Changed after Giving Up!")
        self.assertEqual(self.team.currentLandmark,2,"Landmark Index Did Not Properly Incriment")
        self.assertEqual(len(self.team.timelog),2,"Time log did not recieve new entry")
        self.assertEqual(self.team.timelog[2],clueTime,"Time Log Did Not Recieve The Correct Time") #this may not work correctly

    def test_answer_question_correct_no_time(self):
        self.team.clueTime = datetime.datetime.now()
        self.team.answer_question('three disks')
        self.assertEqual(self.team.points,250,"Points did not increment correctly")
        self.assertEqual(self.team.currentLandmark,2,"Landmark Index Did not Properly increment")
        self.assertEqual(len(self.team.timelog),3,"Time Log Did Not recieve a new entry")
        self.assertEqual(self.team.timelog[2],clueTime,"Time Log Did Not Save The Correct Time") #This may not work properly

    def test_answer_question_incorrect_no_time(self):
        self.team.clueTime = datetime.datetime.now()
        self.team.answer_question("trash fire")
        self.assertEqual(self.team.points,100,"Points did not increment correctly")
        self.assertEqual(self.team.currentLandmark,1,"Landmark Index Did not Properly increment")
        self.assertEqual(len(self.team.timelog),2,"Time Log Did Not recieve a new entry")
        self.team.answer_question("three disks")
        self.assertEqual(self.team.points,240,"Points did not increment correctly")
        self.assertEqual(self.team.currentLandmark,2,"Landmark Index Did not Properly increment")
        self.assertEqual(len(self.team.timelog),3,"Time Log Did Not recieve a new entry")
        self.assertEqual(self.team.timelog[2],clueTime,"Time Log Did Not Save The Correct Time")#This may not work properly

#TIME PENELTY TESTS HAVE A WAIT THAT WILl CAUSE THE TEST TO RUN A UNORMALLY LONG AMOUNT OF TIME, 
# IT IS RECCOMENDED TO HAVE THESE TESTS BE LAST IN THE SUITE

    def test_answer_question_time_penalty(self):
        self.team.clueTime = datetime.datetime.now()
        time.sleep(16)
        self.team.answer_question("three disks")
        self.assertEqual(self.team.points,230,"Points did not increment correctly")
        self.assertEqual(self.team.currentLandmark,2,"Landmark Index Did not Properly increment")
        self.assertEqual(len(self.team.timelog),3,"Time Log Did Not recieve a new entry")
        self.assertEqual(self.team.timelog[2],clueTime+datetime.time(00,00,16),"Time Log Did Not Save The Correct Time") #This may not work properly

    def test_answer_question_time_penalty2(self):
        self.team.clueTime = datetime.datetime.now()
        time.sleep(31)
        self.team.answer_question("three disks")
        self.assertEqual(self.team.points,210,"Points did not increment correctly")
        self.assertEqual(self.team.currentLandmark,2,"Landmark Index Did not Properly increment")
        self.assertEqual(len(self.team.timelog),3,"Time Log Did Not recieve a new entry")
        self.assertEqual(self.team.timelog[2],clueTime+datetime.time(00,00,31),"Time Log Did Not Save The Correct Time") #This may not work properly
   
    def test_answer_question_time_complex(self):
        self.team.clueTime = datetime.datetime.now()
        self.team.answer_question("two disks")
        self.assertEqual(self.team.points,100,"Points did not increment correctly")
        self.assertEqual(self.team.currentLandmark,1,"Landmark Index Did not Properly increment")
        self.assertEqual(len(self.team.timelog),2,"Time Log Did Not recieve a new entry")
        time.sleep(18)
        self.team.answer_question("three disks")
        self.assertEqual(self.team.points,220,"Points did not increment correctly")
        self.assertEqual(self.team.currentLandmark,2,"Landmark Index Did not Properly increment")
        self.assertEqual(len(self.team.timelog),3,"Time Log Did Not recieve a new entry")
        self.assertEqual(timelog[2],clueTime+datetime.time(00,00,18),"Time Log Did Not Save The Correct Time") #This may not work properly
    

suite = unittest.TestSuite()
suite.addTest(unittest.makeSuite(TestTeam))
runner = unittest.TextTestRunner()
res = runner.run(suite)
print(res)
print("*" * 20)
for i in res.failures: print(i[1])