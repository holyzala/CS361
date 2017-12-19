from http import HTTPStatus
from datetime import timedelta
from functools import reduce

from django.test import Client, TestCase

from .CLI import CLI, COMMANDS
from .models import Team, Landmark

GM_NAME = "gamemaker"


class TestLogin(TestCase):
    def setUp(self):
        self.client = Client()
        self.clientGameMaker = Client()

    def test_post_index(self):
        response = self.client.post('/')
        self.assertEqual(HTTPStatus.METHOD_NOT_ALLOWED, response.status_code)

    def test_get_login(self):
        response = self.client.get('/login')
        self.assertEqual(HTTPStatus.METHOD_NOT_ALLOWED, response.status_code)

    def test_get_login_page(self):
        response = self.client.get('/')
        self.assertContains(response, 'eScavenge Login Page')

    def test_login_no_team(self):
        response = self.client.post('/login', {'username': 'team1', 'password': '1234'})
        self.assertContains(response, 'eScavenge Login Page', html=True)

    def test_login_game_maker(self):
        response = self.clientGameMaker.post('/login', {'username': 'gamemaker', 'password': '1234'}, follow=True)
        self.assertRedirects(response, '/gamemaker')
        self.assertContains(response, 'New Game', html=True)

    def test_login_team(self):
        response = self.clientGameMaker.post('/login', {'username': 'gamemaker', 'password': '1234'}, follow=True)
        self.assertRedirects(response, '/gamemaker')
        self.assertContains(response, 'New Game', html=True)
        response = self.clientGameMaker.post('/saveGame/', {'game_name': 'game1', 'game_penalty_value': '0',
                                                 'game_penalty_time': '0', 'game_points': '100',
                                                            'game_timer':'00:00:00', 'NewSubmit': 'blah'}, follow=True)
        self.assertContains(response, 'game1', html=True)
        response = self.clientGameMaker.post('/chooseGame', {'selected_game':'game1'}, follow=True)
        self.assertContains(response, 'game1', html=True)
        response = self.clientGameMaker.get('/editTeam?name=NewTeam')
        self.assertContains(response, "Add New Team", html=True)
        self.clientGameMaker.post('/editTeamAction', {'usernameedit': 'team1', 'passwordedit':'1234',
                                                      'old_name':'NewTeam'})
        response = self.client.post('/login', {'username': 'team1', 'password': '1234'}, follow=True)
        self.assertContains(response, '<title> Team: team1 </title>', html=True)


class TestTeamLogout(TestCase):
    def setUp(self):
        self.client = Client()
        self.clientGameMaker = Client()
        self.clientGameMaker.post('/login', {'username': 'gamemaker', 'password': '1234'}, follow=True)
        self.clientGameMaker.post('/saveGame/', {'game_name': 'game1', 'game_penalty_value': '0',
                                                            'game_penalty_time': '0', 'game_points': '100',
                                                            'game_timer': '00:00:00', 'NewSubmit': 'blah'}, follow=True)

        self.clientGameMaker.post('/chooseGame', {'selected_game': 'game1'}, follow=True)
        self.clientGameMaker.get('/editTeam?name=NewTeam')
        self.clientGameMaker.post('/editTeamAction', {'usernameedit': 'team1', 'passwordedit': '1234',
                                                      'old_name': 'NewTeam'})

    def test_logout(self):
        self.client.post('/login', {'username': 'team1', 'password': '1234'})
        response = self.client.post('/teamPage/', {'logoutbutton': 'Log out'})
        self.assertRedirects(response, expected_url='/logout', status_code=302, target_status_code=302)


class TestTeamPageGameStart(TestCase):
    def setUp(self):
        self.client = Client()
        self.clientGameMaker = Client()
        self.clientGameMaker.post('/login', {'username': 'gamemaker', 'password': '1234'}, follow=True)
        self.clientGameMaker.post('/saveGame/', {'game_name': 'game1', 'game_penalty_value': '0',
                                                 'game_penalty_time': '0', 'game_points': '100',
                                                 'game_timer': '00:00:00', 'NewSubmit': 'blah'}, follow=True)

        self.clientGameMaker.post('/chooseGame', {'selected_game': 'game1'}, follow=True)
        self.clientGameMaker.get('/editTeam?name=NewTeam')
        self.clientGameMaker.post('/editTeamAction', {'usernameedit': 'team1', 'passwordedit': '1234',
                                                      'old_name': 'NewTeam'})

        self.clientGameMaker.post('/chooseGame', {'selected_game': 'game1'}, follow=True)
        self.clientGameMaker.post('/editLandmark', {'landmark_name':'NewLandmark', 'editLMname':'ldm1',
                                                    'editLMclue':'clue1', 'editLMquestion':'q1', 'editLManswer':'answer'
            ,'editLandmark':'Submit'})
        self.clientGameMaker.post('/editLandmark', {'landmark_name': 'NewLandmark', 'editLMname': 'ldm2',
                                                    'editLMclue': 'clue2', 'editLMquestion': 'q2',
                                                    'editLManswer': 'a2','editLandmark':'Submit'})
        self.clientGameMaker.post('/chooseGame', {'selected_game': 'game1'}, follow=True)


    def test_game_not_started(self):
        response = self.client.post('/login', {'username': 'team1', 'password': '1234'})
        self.assertContains(response, "Game Hasn't Started", html=True)
        self.assertContains(response, "Game Status: Not Started", html=True)

    def test_game_started(self):
        self.clientGameMaker.post('/saveGame/', {'game_status': '1', 'game_name': 'game1', 'game_penalty_value': '0',
                                                 'game_penalty_time': '0', 'game_points': '100',
                                                 'game_timer': '00:00:00', 'submit': 'blah'}, follow=True)
        response = self.client.post('/login', {'username': 'team1', 'password': '1234'})
        print(response.content)
        self.assertContains(response, 'Clue <br>clue1', html=True)


class TestTeamPageLeadBoards(TestCase):
    def setUp(self):
        self.client = Client()
        self.clientGameMaker = Client()
        self.clientGameMaker.post('/login', {'username': 'gamemaker', 'password': '1234'}, follow=True)
        self.clientGameMaker.post('/saveGame/', {'game_name': 'game1', 'game_penalty_value': '0',
                                                 'game_penalty_time': '0', 'game_points': '100',
                                                 'game_timer': '00:00:00', 'NewSubmit': 'blah'}, follow=True)

        self.clientGameMaker.post('/chooseGame', {'selected_game': 'game1'}, follow=True)
        self.clientGameMaker.get('/editTeam?name=NewTeam')
        self.clientGameMaker.post('/editTeamAction', {'usernameedit': 'team1', 'passwordedit': '1234',
                                                      'old_name': 'NewTeam'})

        self.clientGameMaker.post('/chooseGame', {'selected_game': 'game1'}, follow=True)
        self.clientGameMaker.get('/editTeam?name=NewTeam')
        self.clientGameMaker.post('/editTeamAction', {'usernameedit': 'team2', 'passwordedit': '1234',
                                                      'old_name': 'NewTeam'})

        self.clientGameMaker.post('/chooseGame', {'selected_game': 'game1'}, follow=True)
        self.clientGameMaker.post('/editLandmark', {'landmark_name': 'NewLandmark', 'editLMname': 'ldm1',
                                                    'editLMclue': 'clue1', 'editLMquestion': 'q1',
                                                    'editLManswer': 'answer'
            , 'editLandmark': 'Submit'})
        self.clientGameMaker.post('/editLandmark', {'landmark_name': 'NewLandmark', 'editLMname': 'ldm2',
                                                    'editLMclue': 'clue2', 'editLMquestion': 'q2',
                                                    'editLManswer': 'a2', 'editLandmark': 'Submit'})
        self.clientGameMaker.post('/chooseGame', {'selected_game': 'game1'}, follow=True)
        team = Team.objects.get(username="team1")
        team.points = 120
        team.save()
        team = Team.objects.get(username="team2")
        team.points = 150
        team.save()

    def test_sort(self):
        response = self.client.post('/login', {'username': 'team1', 'password': '1234'})
        self.assertContains(response, '<tr><td>team2</td><td>150</td></tr><tr><td>team1</td><td>120</td></tr>',
                            html=True)


class TestTeamLandmarkHistory(TestCase):
    def setUp(self):
        self.client = Client()
        self.clientGameMaker = Client()
        self.clientGameMaker.post('/login', {'username': 'gamemaker', 'password': '1234'}, follow=True)
        self.clientGameMaker.post('/saveGame/', {'game_name': 'game1', 'game_penalty_value': '0',
                                                 'game_penalty_time': '0', 'game_points': '100',
                                                 'game_timer': '00:00:00', 'NewSubmit': 'blah'}, follow=True)

        self.clientGameMaker.post('/chooseGame', {'selected_game': 'game1'}, follow=True)
        self.clientGameMaker.get('/editTeam?name=NewTeam')
        self.clientGameMaker.post('/editTeamAction', {'usernameedit': 'team1', 'passwordedit': '1234',
                                                      'old_name': 'NewTeam'})

        self.clientGameMaker.post('/chooseGame', {'selected_game': 'game1'}, follow=True)
        self.clientGameMaker.post('/editLandmark', {'landmark_name': 'NewLandmark', 'editLMname': 'ldm1',
                                                    'editLMclue': 'clue1', 'editLMquestion': 'q1',
                                                    'editLManswer': 'answer', 'editLandmark': 'Submit'})
        self.clientGameMaker.post('/editLandmark', {'landmark_name': 'NewLandmark', 'editLMname': 'ldm2',
                                                    'editLMclue': 'clue2', 'editLMquestion': 'q2',
                                                    'editLManswer': 'a2', 'editLandmark': 'Submit'})
        self.clientGameMaker.post('/chooseGame', {'selected_game': 'game1'}, follow=True)
        self.clientGameMaker.post('/saveGame/', {'game_status': '1', 'game_name': 'game1', 'game_penalty_value': '0',
                                                 'game_penalty_time': '0', 'game_points': '100',
                                                 'game_timer': '00:00:00', 'submit': 'blah'}, follow=True)
        self.client.post('/login', {'username': 'team1', 'password': '1234'})
        self.client.post('/teamPage/', {'commandline': 'answer', 'answerQuestion': 'Answer Question'})
        self.client.post('/teamPage/', {'commandline': 'a2', 'answerQuestion': 'Answer Question'})

    def test_landmark_name(self):
        response = self.client.post('/login', {'username': 'team1', 'password': '1234'})
        team = Team.objects.get(username="team1")
        team_history_landmarks = team.history.values_list("landmark")
        for landmark in team_history_landmarks:
            expected_string = '<td>{}</td>'.format(landmark[0])
            self.assertContains(response, expected_string)

    def test_landmark_points(self):
        response = self.client.post('/login', {'username': 'team1', 'password': '1234'})
        team = Team.objects.get(username="team1")
        team_history_points = team.history.values_list("points")
        for points in team_history_points:
            expected_string = '<td>{}</td>'.format(points[0])
            self.assertContains(response, expected_string)

    def test_landmark_time_delta(self):
        response = self.client.post('/login', {'username': 'team1', 'password': '1234'})
        team = Team.objects.get(username="team1")
        team_history_time = team.history.values_list("time_delta")
        for time in team_history_time:
            expected_string = '<td>{}</td>'.format(str(time[0]).split('.')[0])
            self.assertContains(response, expected_string)


class TestTeamTotalTime(TestCase):
    def setUp(self):
        self.client = Client()
        self.clientGameMaker = Client()
        self.clientGameMaker.post('/login', {'username': 'gamemaker', 'password': '1234'}, follow=True)
        self.clientGameMaker.post('/saveGame/', {'game_name': 'game1', 'game_penalty_value': '0',
                                                 'game_penalty_time': '0', 'game_points': '100',
                                                 'game_timer': '00:00:00', 'NewSubmit': 'blah'}, follow=True)

        self.clientGameMaker.post('/chooseGame', {'selected_game': 'game1'}, follow=True)
        self.clientGameMaker.get('/editTeam?name=NewTeam')
        self.clientGameMaker.post('/editTeamAction', {'usernameedit': 'team1', 'passwordedit': '1234',
                                                      'old_name': 'NewTeam'})

        self.clientGameMaker.post('/chooseGame', {'selected_game': 'game1'}, follow=True)
        self.clientGameMaker.post('/editLandmark', {'landmark_name': 'NewLandmark', 'editLMname': 'ldm1',
                                                    'editLMclue': 'clue1', 'editLMquestion': 'q1',
                                                    'editLManswer': 'answer', 'editLandmark': 'Submit'})
        self.clientGameMaker.post('/editLandmark', {'landmark_name': 'NewLandmark', 'editLMname': 'ldm2',
                                                    'editLMclue': 'clue2', 'editLMquestion': 'q2',
                                                    'editLManswer': 'a2', 'editLandmark': 'Submit'})
        self.clientGameMaker.post('/chooseGame', {'selected_game': 'game1'}, follow=True)
        self.clientGameMaker.post('/saveGame/', {'game_status': '1', 'game_name': 'game1', 'game_penalty_value': '0',
                                                 'game_penalty_time': '0', 'game_points': '100',
                                                 'game_timer': '00:00:00', 'submit': 'blah'}, follow=True)
        self.client.post('/login', {'username': 'team1', 'password': '1234'})
        self.client.post('/teamPage/', {'commandline': 'answer', 'answerQuestion': 'Answer Question'})
        self.client.post('/teamPage/', {'commandline': 'a2', 'answerQuestion': 'Answer Question'})

    def test_total_time(self):
        response = self.client.post('/login', {'username': 'team1', 'password': '1234'})
        team = Team.objects.get(username="team1")
        team_history = team.history.all()
        total_time = reduce(lambda x, y: x + y.time_delta, team_history, timedelta(0))
        self.assertContains(response, str(total_time).split('.')[0])


class TestTeamAnswer(TestCase):
    def setUp(self):
        self.client = Client()
        self.clientGameMaker = Client()
        self.clientGameMaker.post('/login', {'username': 'gamemaker', 'password': '1234'}, follow=True)
        self.clientGameMaker.post('/saveGame/', {'game_name': 'game1', 'game_penalty_value': '10',
                                                 'game_penalty_time': '0', 'game_points': '100',
                                                 'game_timer': '00:00:00', 'NewSubmit': 'blah'}, follow=True)

        self.clientGameMaker.post('/chooseGame', {'selected_game': 'game1'}, follow=True)
        self.clientGameMaker.get('/editTeam?name=NewTeam')
        self.clientGameMaker.post('/editTeamAction', {'usernameedit': 'team1', 'passwordedit': '1234',
                                                      'old_name': 'NewTeam'})
        self.clientGameMaker.post('/chooseGame', {'selected_game': 'game1'}, follow=True)
        self.clientGameMaker.post('/editLandmark', {'landmark_name': 'NewLandmark', 'editLMname': 'ldm1',
                                                    'editLMclue': 'clue1', 'editLMquestion': 'q1',
                                                    'editLManswer': 'answer', 'editLandmark': 'Submit'})
        self.clientGameMaker.post('/editLandmark', {'landmark_name': 'NewLandmark', 'editLMname': 'ldm2',
                                                    'editLMclue': 'clue2', 'editLMquestion': 'q2',
                                                    'editLManswer': 'a2', 'editLandmark': 'Submit'})
        self.clientGameMaker.post('/chooseGame', {'selected_game': 'game1'}, follow=True)
        self.clientGameMaker.post('/saveGame/', {'game_status': '1', 'game_name': 'game1', 'game_penalty_value': '0',
                                                 'game_penalty_time': '0', 'game_points': '100',
                                                 'game_timer': '00:00:00', 'submit': 'blah'}, follow=True)

    def test_answer_correctly(self):
        response = self.client.post('/login', {'username': 'team1', 'password': '1234'})
        self.assertContains(response, "clue1")
        self.assertContains(response, "<td>0</td>", html=True)
        response = self.client.post('/teamPage/', {'commandline': 'answer', 'answerQuestion': 'Answer Question'})
        self.assertContains(response, "Clue <br>clue2", html=True)
        self.assertContains(response, "That is Correct!", html=True)
        self.assertContains(response, "<td>100</td>", html=True)

    def test_answer_incorrectly(self):
        response = self.client.post('/login', {'username': 'team1', 'password': '1234'})
        self.assertContains(response, "clue1")
        self.assertContains(response, "<td>0</td>", html=True)
        response = self.client.post('/teamPage/', {'commandline': 'WRONG ANSWER',
                                                   'answerQuestion': 'Answer Question'})

        expected_string = "Incorrect Answer!"
        self.assertContains(response, "clue1")
        self.assertContains(response, expected_string, html=True)
        response = self.client.post('/teamPage/', {'commandline': 'answer',
                                                   'answerQuestion': 'Answer Question'})
        print(response.content)
        self.assertContains(response, 'Clue <br>clue2', html=True)

    def test_answer_correct_followed_by_incorrect(self):
        response = self.client.post('/login', {'username': 'team1', 'password': '1234'})
        self.assertContains(response, "clue1")
        self.assertContains(response, "<td>0</td>", html=True)
        response = self.client.post('/teamPage/', {'commandline': 'answer',
                                                   'answerQuestion': 'Answer Question'})
        self.assertContains(response, "clue2")
        expected_string = "Incorrect Answer!"
        response = self.client.post('/teamPage/', {'commandline': 'WRONG ANSWER', 'answerQuestion': 'Answer Question'})
        self.assertContains(response, expected_string, html=True)
        response = self.client.post('/teamPage/', {'commandline': 'WRONG ANSWER', 'answerQuestion': 'Answer Question'})
        self.assertContains(response, expected_string, html=True)
        response = self.client.post('/teamPage/', {'commandline': 'a2', 'answerQuestion': 'Answer Question'})

    def test_answer_last_question(self):
        self.client.post('/login', {'username': 'team1', 'password': '1234'})
        self.client.post('/teamPage/', {'commandline': 'answer', 'answerQuestion': 'Answer Question'})
        response = self.client.post('/teamPage/', {'commandline': 'a2', 'answerQuestion': 'Answer Question'})
        self.assertContains(response, "Final Landmark Answered", html=True)


class TestTeamQuitQuestion(TestCase):
    def setUp(self):
        self.client = Client()
        self.clientGameMaker = Client()
        self.clientGameMaker.post('/login', {'username': 'gamemaker', 'password': '1234'}, follow=True)
        self.clientGameMaker.post('/saveGame/', {'game_name': 'game1', 'game_penalty_value': '10',
                                                 'game_penalty_time': '0', 'game_points': '100',
                                                 'game_timer': '00:00:00', 'NewSubmit': 'blah'}, follow=True)

        self.clientGameMaker.post('/chooseGame', {'selected_game': 'game1'}, follow=True)
        self.clientGameMaker.get('/editTeam?name=NewTeam')
        self.clientGameMaker.post('/editTeamAction', {'usernameedit': 'team1', 'passwordedit': '1234',
                                                      'old_name': 'NewTeam'})
        self.clientGameMaker.post('/chooseGame', {'selected_game': 'game1'}, follow=True)
        self.clientGameMaker.post('/editLandmark', {'landmark_name': 'NewLandmark', 'editLMname': 'ldm1',
                                                    'editLMclue': 'clue1', 'editLMquestion': 'q1',
                                                    'editLManswer': 'answer', 'editLandmark': 'Submit'})
        self.clientGameMaker.post('/editLandmark', {'landmark_name': 'NewLandmark', 'editLMname': 'ldm2',
                                                    'editLMclue': 'clue2', 'editLMquestion': 'q2',
                                                    'editLManswer': 'a2', 'editLandmark': 'Submit'})
        self.clientGameMaker.post('/chooseGame', {'selected_game': 'game1'}, follow=True)
        self.clientGameMaker.post('/saveGame/', {'game_status': '1', 'game_name': 'game1', 'game_penalty_value': '0',
                                                 'game_penalty_time': '0', 'game_points': '100',
                                                 'game_timer': '00:00:00', 'submit': 'blah'}, follow=True)

    def test_quit_question(self):
        response = self.client.post('/login', {'username': 'team1', 'password': '1234'})
        self.assertContains(response, "clue1")
        self.assertContains(response, "<td>0</td>", html=True)
        response = self.client.post('/teamPage/', {'quitQuestion': 'Quit Question'})
        self.assertContains(response, "clue2")
        self.assertContains(response, "<td>0</td>")

    def test_quit_last_question(self):
        self.client.post('/login', {'username': 'team1', 'password': '1234'})
        self.client.post('/teamPage/', {'quitQuestion': 'Quit Question'})
        response = self.client.post('/teamPage/', {'quitQuestion': 'Quit Question'})
        self.assertContains(response, "Final Landmark Answered")
        self.assertContains(response, "<td>0</td>")


class TestTeamEdit(TestCase):
    def setUp(self):
        self.client = Client()
        self.clientGameMaker = Client()
        self.clientGameMaker.post('/login', {'username': 'gamemaker', 'password': '1234'}, follow=True)
        self.clientGameMaker.post('/saveGame/', {'game_name': 'game1', 'game_penalty_value': '10',
                                                 'game_penalty_time': '0', 'game_points': '100',
                                                 'game_timer': '00:00:00', 'NewSubmit': 'blah'}, follow=True)

        self.clientGameMaker.post('/chooseGame', {'selected_game': 'game1'}, follow=True)
        self.clientGameMaker.get('/editTeam?name=NewTeam')
        self.clientGameMaker.post('/editTeamAction', {'usernameedit': 'team1', 'passwordedit': '1234',
                                                      'old_name': 'NewTeam'})
        self.clientGameMaker.post('/chooseGame', {'selected_game': 'game1'}, follow=True)

    def test_edit_team_name(self):
        self.client.post('/login', {'username': 'team1', 'password': '1234'})
        response = self.client.post('/teamPage/', {'changeteam': 'Submit', 'changeusername': 'teamx'})
        self.assertContains(response, "teamx", html=True)

    def test_edit_team_pass(self):
        self.client.post('/login', {'username': 'team1', 'password': '1234'})
        self.client.post('/teamPage/', {'changeteam': 'Submit', 'changepassword': 'newpass'})
        self.assertEqual('newpass', Team.objects.get(username='team1').password)

    def test_edit_team_name_and_pass(self):
        self.client.post('/login', {'username': 'team1', 'password': '1234'})
        response = self.client.post('/teamPage/', {'changeteam': 'Submit', 'changeusername': 'teamx',
                                                   'changepassword': 'newpass'})
        self.assertContains(response, "teamx", html=True)
        self.assertEqual('newpass', Team.objects.get(username='teamx').password)

    def test_gm_edit_team(self):
        self.clientGameMaker.get('/editTeam?name=team1')
        self.clientGameMaker.post('/editTeamAction', {'usernameedit': 'teamX', 'passwordedit': 'newpass',
                                                      'old_name': 'NewTeam'})
        response = self.clientGameMaker.post('/chooseGame', {'selected_game': 'game1'}, follow=True)
        self.assertContains(response, 'teamX', html=True)


class TestAddLandmark(TestCase):
    def test_add_two_landmark(self):
        self.client = Client()
        self.clientGameMaker = Client()
        self.clientGameMaker.post('/login', {'username': 'gamemaker', 'password': '1234'}, follow=True)
        self.clientGameMaker.post('/saveGame/', {'game_name': 'game1', 'game_penalty_value': '10',
                                                 'game_penalty_time': '0', 'game_points': '100',
                                                 'game_timer': '00:00:00', 'NewSubmit': 'blah'}, follow=True)

        self.clientGameMaker.post('/chooseGame', {'selected_game': 'game1'}, follow=True)
        self.clientGameMaker.post('/editLandmark', {'landmark_name': 'NewLandmark', 'editLMname': 'ldm1',
                                                    'editLMclue': 'clue1', 'editLMquestion': 'q1',
                                                    'editLManswer': 'answer', 'editLandmark': 'Submit'})
        self.clientGameMaker.post('/editLandmark', {'landmark_name': 'NewLandmark', 'editLMname': 'ldm2',
                                                    'editLMclue': 'clue2', 'editLMquestion': 'q2',
                                                    'editLManswer': 'a2', 'editLandmark': 'Submit'})
        response = self.clientGameMaker.post('/chooseGame', {'selected_game': 'game1'}, follow=True)
        self.assertContains(response, 'ldm1', html=True)
        self.assertContains(response, 'ldm2', html=True)


class TestEditLandmark(TestCase):
    def setUp(self):
        self.client = Client()
        self.clientGameMaker = Client()
        self.clientGameMaker.post('/login', {'username': 'gamemaker', 'password': '1234'}, follow=True)
        self.clientGameMaker.post('/saveGame/', {'game_name': 'game1', 'game_penalty_value': '10',
                                                 'game_penalty_time': '0', 'game_points': '100',
                                                 'game_timer': '00:00:00', 'NewSubmit': 'blah'}, follow=True)

        self.clientGameMaker.post('/chooseGame', {'selected_game': 'game1'}, follow=True)
        self.clientGameMaker.post('/editLandmark', {'landmark_name': 'NewLandmark', 'editLMname': 'ldm1',
                                                    'editLMclue': 'clue1', 'editLMquestion': 'q1',
                                                    'editLManswer': 'answer', 'editLandmark': 'Submit'})

    def test_edit_landmark_name(self):
        self.clientGameMaker.post('/editLandmark', {'landmark_name': 'ldm1', 'editLMname': 'LDM2',
                                                    'editLMclue': 'clue1', 'editLMquestion': 'q1',
                                                    'editLManswer': 'answer', 'editLandmark': 'Submit'})
        response = self.clientGameMaker.post('/chooseGame', {'selected_game': 'game1'}, follow=True)
        self.assertContains(response, 'LDM2', html=True)

    def test_edit_landmark_all_fields(self):
        self.clientGameMaker.post('/editLandmark', {'landmark_name': 'ldm1', 'editLMname': 'LDM2',
                                                    'editLMclue': 'NEWCLUE', 'editLMquestion': 'NEWQUESTION',
                                                    'editLManswer': 'NEWANSWER', 'editLandmark': 'Submit'})
        response = self.clientGameMaker.post('/chooseGame', {'selected_game': 'game1'}, follow=True)
        self.assertContains(response, 'LDM2', html=True)
        landmark = Landmark.objects.get(name='LDM2')
        self.assertEqual('NEWCLUE', landmark.clue)
        self.assertEqual('NEWANSWER', landmark.answer)
        self.assertEqual('NEWQUESTION', landmark.question)

