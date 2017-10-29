import unittest


class Team():
    def __init__(self):
        self.username = ""
        self.password = ""

    def login(self, username, password):
        return "", False

    def answer_question(self, answer):
        return ""

    def get_status(self):
        return ""

    def get_clue(self):
        return ""


class TestTeam(unittest.TestCase):
    def setUp(self):
        self.team = Team()
    
    def test_team_login_success(self):
        self.username = "team1"
        self.password = "password123"
      
        self.assertTrue(login(self, "team1", "password123"))
                         
    def test_team_login_fail(self):
       self.username = "team1"
       self.password = "password123"
        
       self.assertFalse(login(self, "team1", "random"))
    
if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestLogin))
    runner = unittest.TextTestRunner()
    res = runner.run(suite)
    print(res)
    print("*" * 20)
    for i in res.failures: print(i[1]) 
    
                          
                    
