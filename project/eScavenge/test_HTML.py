from http import HTTPStatus
from datetime import timedelta
from functools import reduce

from django.test import Client, TestCase

from .CLI import CLI, COMMANDS
from .models import Team, Game

GM_NAME = "gamemaker"


class TestLogin(TestCase):
    def setUp(self):
        self.client = Client()

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

    def test_login_team(self):
        cli = CLI(COMMANDS)
        cli.command('create game1', GM_NAME)
        cli.command('addteam team1 1234', GM_NAME)
        response = self.client.post('/login', {'username': 'team1', 'password': '1234'})
        self.assertContains(response, '<title> Team: team1 </title>', html=True)


class TestTeamLogout(TestCase):
    def setUp(self):
        cli = CLI(COMMANDS)
        cli.command('create game1', GM_NAME)
        cli.command('addteam team1 1234', GM_NAME)
        self.client = Client()

    def test_logout(self):
        self.client.post('/login', {'username': 'team1', 'password': '1234'})
        response = self.client.post('/teamPage/', {'logoutbutton': 'Log out'})
        self.assertRedirects(response, expected_url='/', status_code=302, target_status_code=200)


class TestTeamPageGameStart(TestCase):
    def setUp(self):
        self.client = Client()
        self.cli = CLI(COMMANDS)
        self.cli.command('create game1', GM_NAME)
        self.cli.command('addteam team1 1234', GM_NAME)
        self.cli.command('addlandmark "ldm1" "New York" "Gift given by the French" "Statue of Liberty"', GM_NAME)
        self.cli.command('addlandmark "ldm2" "UWM" "Place we purchase coffee from" "Grind"', GM_NAME)

    def test_game_not_started(self):
        response = self.client.post('/login', {'username': 'team1', 'password': '1234'})
        self.assertContains(response, "Game Hasn't Started", html=True)
        self.assertContains(response, "Game Status: Not Started", html=True)

    def test_game_started(self):
        self.cli.command('start', GM_NAME)
        response = self.client.post('/login', {'username': 'team1', 'password': '1234'})
        self.assertContains(response, 'Clue <br>New York', html=True)


class TestTeamPageLeadBoards(TestCase):
    def setUp(self):
        self.client = Client()
        self.cli = CLI(COMMANDS)
        self.cli.command('create game1', GM_NAME)
        self.cli.command('addteam team1 1234', GM_NAME)
        self.cli.command('addteam team2 1234', GM_NAME)
        self.cli.command('start', GM_NAME)
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
        self.cli = CLI(COMMANDS)
        self.cli.command('create game1', GM_NAME)
        self.cli.command('addteam team1 1234', GM_NAME)
        self.cli.command('addlandmark "ldm1" "New York" "Gift given by the French" "Statue of Liberty"', GM_NAME)
        self.cli.command('addlandmark "ldm2" "UWM" "Place we purchase coffee from" "Grind"', GM_NAME)
        current_game = Game.objects.get(name="game1")
        current_game.landmark_points = 100
        current_game.save()
        self.cli.command('load game1', GM_NAME)
        self.cli.command('start', GM_NAME)
        self.cli.command("answer 'Statue of Liberty'", "team1")
        self.cli.command("answer 'Grind'", "team1")

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
        self.cli = CLI(COMMANDS)
        self.cli.command('create game1', GM_NAME)
        self.cli.command('addteam team1 1234', GM_NAME)
        self.cli.command('addlandmark "ldm1" "New York" "Gift given by the French" "Statue of Liberty"', GM_NAME)
        self.cli.command('addlandmark "ldm2" "UWM" "Place we purchase coffee from" "Grind"', GM_NAME)
        self.cli.command('start', GM_NAME)
        self.cli.command("answer 'Statue of Liberty'", "team1")
        self.cli.command("answer 'Grind'", "team1")

    def test_total_time(self):
        response = self.client.post('/login', {'username': 'team1', 'password': '1234'})
        team = Team.objects.get(username="team1")
        team_history = team.history.all()
        total_time = reduce(lambda x, y: x + y.time_delta, team_history, timedelta(0))
        self.assertContains(response, str(total_time).split('.')[0])


class TestTeamAnswer(TestCase):
    def setUp(self):
        self.client = Client()
        self.cli = CLI(COMMANDS)
        self.cli.command('create game1', GM_NAME)
        current_game = Game.objects.get(name="game1")
        current_game.landmark_points = 100
        current_game.penalty_value = 10
        current_game.save()
        self.cli.command('load game1', GM_NAME)
        self.cli.command('addteam team1 1234', GM_NAME)
        self.cli.command('addlandmark "ldm1" "New York" "Gift given by the French" "Statue of Liberty"', GM_NAME)
        self.cli.command('addlandmark "ldm2" "UWM" "Place we purchase coffee from" "Grind"', GM_NAME)
        self.cli.command('start', GM_NAME)

    def test_answer_correctly(self):
        response = self.client.post('/login', {'username': 'team1', 'password': '1234'})
        self.assertContains(response, "New York")
        self.assertContains(response, "<td>0</td>", html=True)
        response = self.client.post('/teamPage/', {'commandline': 'Statue of Liberty',
                                                   'answerQuestion': 'Answer Question'})
        self.assertContains(response, "Clue <br>UWM", html=True)
        self.assertContains(response, "That is Correct!", html=True)
        self.assertContains(response, "<td>100</td>", html=True)

    def test_answer_incorrectly(self):
        response = self.client.post('/login', {'username': 'team1', 'password': '1234'})
        self.assertContains(response, "New York")
        self.assertContains(response, "<td>0</td>", html=True)
        response = self.client.post('/teamPage/', {'commandline': 'WRONG ANSWER',
                                                   'answerQuestion': 'Answer Question'})

        expected_string = "Incorrect Answer!"
        self.assertContains(response, "New York")
        self.assertContains(response, expected_string, html=True)
        response = self.client.post('/teamPage/', {'commandline': 'Statue of Liberty',
                                                   'answerQuestion': 'Answer Question'})
        self.assertContains(response, "<td>90</td>", html=True)

    def test_answer_correct_followed_by_incorrect(self):
        response = self.client.post('/login', {'username': 'team1', 'password': '1234'})
        self.assertContains(response, "New York")
        self.assertContains(response, "<td>0</td>", html=True)
        response = self.client.post('/teamPage/', {'commandline': 'Statue of Liberty',
                                                   'answerQuestion': 'Answer Question'})
        self.assertContains(response, "UWM")
        expected_string = "Incorrect Answer!"
        response = self.client.post('/teamPage/', {'commandline': 'WRONG ANSWER', 'answerQuestion': 'Answer Question'})
        self.assertContains(response, expected_string, html=True)
        response = self.client.post('/teamPage/', {'commandline': 'WRONG ANSWER', 'answerQuestion': 'Answer Question'})
        self.assertContains(response, expected_string, html=True)
        response = self.client.post('/teamPage/', {'commandline': 'Grind', 'answerQuestion': 'Answer Question'})
        self.assertContains(response, "<td>80</td>", html=True) # needs to be 80, answered incorrectly twice (100-10-10)

    def test_answer_last_question(self):
        self.client.post('/login', {'username': 'team1', 'password': '1234'})
        self.client.post('/teamPage/', {'commandline': 'Statue of Liberty', 'answerQuestion': 'Answer Question'})
        response = self.client.post('/teamPage/', {'commandline': 'Grind', 'answerQuestion': 'Answer Question'})
        self.assertContains(response, "Final Landmark Answered", html=True)
        self.assertContains(response, "<td>200</td>") # something wrong with database, maybe missing a save somewhere


class TestTeamQuitQuestion(TestCase):
    def setUp(self):
        self.client = Client()
        self.cli = CLI(COMMANDS)
        self.cli.command('create game1', GM_NAME)
        current_game = Game.objects.get(name="game1")
        current_game.landmark_points = 100
        current_game.penalty_value = 10
        current_game.save()
        self.cli.command('load game1', GM_NAME)
        self.cli.command('addteam team1 1234', GM_NAME)
        self.cli.command('addlandmark "ldm1" "New York" "Gift given by the French" "Statue of Liberty"', GM_NAME)
        self.cli.command('addlandmark "ldm2" "UWM" "Place we purchase coffee from" "Grind"', GM_NAME)
        self.cli.command('start', GM_NAME)

    def test_quit_question(self):
        response = self.client.post('/login', {'username': 'team1', 'password': '1234'})
        self.assertContains(response, "New York")
        self.assertContains(response, "<td>0</td>", html=True)
        response = self.client.post('/teamPage/', {'quitQuestion': 'Quit Question'})
        self.assertContains(response, "UWM")
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
        self.cli = CLI(COMMANDS)
        self.cli.command('create game1', GM_NAME)
        current_game = Game.objects.get(name="game1")
        current_game.landmark_points = 100
        current_game.penalty_value = 10
        current_game.save()
        self.cli.command('load game1', GM_NAME)
        self.cli.command('addteam team1 1234', GM_NAME)

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

