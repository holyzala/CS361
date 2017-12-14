from http import HTTPStatus
from django.test import Client
from django.test import TestCase
from .CLI import CLI, COMMANDS
from .models import GMFactory, Team, Game, Landmark
from datetime import timedelta
from functools import reduce


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
        gm = 'gamemaker'
        cli.command('create game1', gm)
        cli.command('addteam team1 1234', gm)
        response = self.client.post('/login', {'username': 'team1', 'password': '1234'})
        self.assertContains(response, '<title> Team: team1 </title>', html=True)


class TestTeamPageGameStart(TestCase):
    def setUp(self):
        self.client = Client()
        self.cli = CLI(COMMANDS)
        self.gm = 'gamemaker'
        self.cli.command('create game1', self.gm)
        self.cli.command('addteam team1 1234', self.gm)
        self.cli.command('addlandmark "ldm1" "New York" "Gift given by the French" "Statue of Liberty"', self.gm)
        self.cli.command('addlandmark "ldm2" "UWM" "Place we purchase coffee from" "Grind"', self.gm)

    def test_game_not_started(self):
        response = self.client.post('/login', {'username': 'team1', 'password': '1234'})
        self.assertContains(response, "Game Hasn't Started", html=True)
        self.assertContains(response, "Game Status: Not Started", html=True)

    def test_game_started(self):
        self.cli.command('start', self.gm)
        response = self.client.post('/login', {'username': 'team1', 'password': '1234'})
        print(response.content)
        self.assertContains(response, '<p class="landmarkname">ldm1\n        <p class="landmarkclue">New York\n        '
                                      '<p class="landmarkquestion">Gift given by the French\n        ')


class TestTeamPageLeadBoards(TestCase):
    def setUp(self):
        self.client = Client()
        self.cli = CLI(COMMANDS)
        self.gm = 'gamemaker'
        self.cli.command('create game1', self.gm)
        self.cli.command('addteam team1 1234', self.gm)
        self.cli.command('addteam team2 1234', self.gm)
        self.cli.command('start', self.gm)
        team = Team.objects.get(username="team1")
        team.points = 120
        team.save()
        team = Team.objects.get(username="team2")
        team.points = 150
        team.save()

    def test_sort(self):
        response = self.client.post('/login', {'username': 'team1', 'password': '1234'})
        print(response.content)
        self.assertContains(response, '<td>team2</td>\n                <td>150</td>\n            </tr>\n        \n     '
                                      '       <tr>\n                <td>team1</td>\n                <td>120</td>\n     '
                                      '       </tr>')


class TestTeamLandmarkHistory(TestCase):
    def setUp(self):
        self.client = Client()
        self.cli = CLI(COMMANDS)
        self.gm = 'gamemaker'
        self.cli.command('create game1', self.gm)
        self.cli.command('addteam team1 1234', self.gm)
        self.cli.command('addlandmark "ldm1" "New York" "Gift given by the French" "Statue of Liberty"', self.gm)
        self.cli.command('addlandmark "ldm2" "UWM" "Place we purchase coffee from" "Grind"', self.gm)
        current_game = Game.objects.get(name="game1")
        current_game.landmark_points = 100
        current_game.save()
        self.cli.command('load game1', self.gm)
        self.cli.command('start', self.gm)
        self.cli.command("answer 'Statue of Liberty'", "team1")
        self.cli.command("answer 'Grind'", "team1")

    def test_landmark_name(self):
        response = self.client.post('/login', {'username': 'team1', 'password': '1234'})
        team = Team.objects.get(username="team1")
        teamHistoryTimeDelta = team.history.values_list("landmark")
        for x in teamHistoryTimeDelta:
            expected_string = '<td>{}</td>'.format(x[0])
            self.assertContains(response, expected_string)

    def test_landmark_points(self):
        response = self.client.post('/login', {'username': 'team1', 'password': '1234'})
        team = Team.objects.get(username="team1")
        teamHistoryTimeDelta = team.history.values_list("points")
        for x in teamHistoryTimeDelta:
            expected_string = '<td>{}</td>'.format(x[0])
            self.assertContains(response, expected_string)

    def test_landmark_time_delta(self):
        response = self.client.post('/login', {'username': 'team1', 'password': '1234'})
        team = Team.objects.get(username="team1")
        teamHistoryTimeDelta = team.history.values_list("time_delta")
        for x in teamHistoryTimeDelta:
            expected_string = '<td>{}</td>'.format(str(x[0]).split('.')[0])
            self.assertContains(response, expected_string)


class TestTeamTotalTime(TestCase):
    def setUp(self):
        self.client = Client()
        self.cli = CLI(COMMANDS)
        self.gm = 'gamemaker'
        self.cli.command('create game1', self.gm)
        self.cli.command('addteam team1 1234', self.gm)
        self.cli.command('addlandmark "ldm1" "New York" "Gift given by the French" "Statue of Liberty"', self.gm)
        self.cli.command('addlandmark "ldm2" "UWM" "Place we purchase coffee from" "Grind"', self.gm)
        self.cli.command('start', self.gm)
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
        self.gm = 'gamemaker'
        self.cli.command('create game1', self.gm)
        current_game = Game.objects.get(name="game1")
        current_game.landmark_points = 100
        current_game.penalty_value = 10
        current_game.save()
        self.cli.command('load game1', self.gm)
        self.cli.command('addteam team1 1234', self.gm)
        self.cli.command('addlandmark "ldm1" "New York" "Gift given by the French" "Statue of Liberty"', self.gm)
        self.cli.command('addlandmark "ldm2" "UWM" "Place we purchase coffee from" "Grind"', self.gm)
        self.cli.command('start', self.gm)

    def test_answer_correctly(self):
        response = self.client.post('/login', {'username': 'team1', 'password': '1234'})
        self.assertContains(response, "New York")
        self.assertContains(response, "<td>0</td>", html=True)
        response = self.client.post('/teamPage/', {'commandline': 'Statue of Liberty',
                                                   'answerQuestion': 'Answer Question'})
        self.assertContains(response, "UWM")
        self.assertContains(response, "<td>100</td>", html=True)

    def test_answer_incorrectly(self):
        response = self.client.post('/login', {'username': 'team1', 'password': '1234'})
        self.assertContains(response, "New York")
        self.assertContains(response, "<td>0</td>", html=True)
        response = self.client.post('/teamPage/', {'commandline': 'WRONG ANSWER',
                                                   'answerQuestion': 'Answer Question'})
        self.assertContains(response, "New York")
        response = self.client.post('/teamPage/', {'commandline': 'Statue of Liberty',
                                                   'answerQuestion': 'Answer Question'})
        self.assertContains(response,"<td>90</td>", html=True)

    def test_answer_correct_followed_by_incorrect(self):
        response = self.client.post('/login', {'username': 'team1', 'password': '1234'})
        self.assertContains(response, "New York")
        self.assertContains(response, "<td>0</td>", html=True)
        response = self.client.post('/teamPage/', {'commandline': 'Statue of Liberty',
                                                   'answerQuestion': 'Answer Question'})
        self.assertContains(response, "UWM")
        self.client.post('/teamPage/', {'commandline': 'WRONG ANSWER',
                                                   'answerQuestion': 'Answer Question'})
        self.client.post('/teamPage/', {'commandline': 'WRONG ANSWER',
                                                   'answerQuestion': 'Answer Question'})
        response = self.client.post('/teamPage/', {'commandline': 'Grind',
                                                   'answerQuestion': 'Answer Question'})
        self.assertContains(response, "<td>80</td>", html=True)

    def test_answer_last_question(self):
        self.client.post('/login', {'username': 'team1', 'password': '1234'})
        self.client.post('/teamPage/', {'commandline': 'Statue of Liberty',
                                                   'answerQuestion': 'Answer Question'})
        response = self.client.post('/teamPage/', {'commandline': 'Grind',
                                                   'answerQuestion': 'Answer Question'})
        self.assertContains(response, "Final Landmark Answered", html=True)
        self.assertContains(response, "<td>200</td>")


class TestTeamEdit(TestCase):
    def setUp(self):
        self.client = Client()
        self.cli = CLI(COMMANDS)
        self.gm = 'gamemaker'
        self.cli.command('create game1', self.gm)
        current_game = Game.objects.get(name="game1")
        current_game.landmark_points = 100
        current_game.penalty_value = 10
        current_game.save()
        self.cli.command('load game1', self.gm)
        self.cli.command('addteam team1 1234', self.gm)
        self.cli.command('addlandmark "ldm1" "New York" "Gift given by the French" "Statue of Liberty"', self.gm)
