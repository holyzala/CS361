import unittest


class Game():
    def __init__(self):
        self.teams = []
        self.landmarks = []
        self.started = False
        self.penaltyValue = 0
        self.penaltyTime = 0

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
        pass

    def set_point_penalty(self, points):
        pass

    def set_time_penalty(self, time):
        pass

    def start(self):
        pass

    def end(self):
        pass

    
    

class TestGame(unittest.TestCase):
    def setUp(self):
        self.game = Game()
     
    def test_modify_team_name(self):
       self.addTeam(TeamFactory().getTeam("Team1", "21212"))
       assertTrue(self.modify_team("Team1", name="Team2")), "Team was not modified")
       
    def test_modifiy_team_password(self):
        self.addTeam(TeamFactory().getTeam("Team1", "1234"))
        assertTrue(self.modify_team("Team1", password="5678"), "password was not modified")
        

  
