from django.test import Client
from django.test import TestCase
from .CLI import CLI, COMMANDS
from .models import GMFactory


class TestLogin(TestCase):
    def setUp(self):
        self.client = Client()

    def test_get_login_page(self):
        response = self.client.get('/')
        self.assertContains(response, 'eScavenge Login Page')

    def test_login_no_team(self):
        response = self.client.post('/login', {'username': 'team1', 'password': '1234'})
        self.assertContains(response, 'eScavenge Login Page')

    def test_login_team(self):
        cli = CLI(COMMANDS)
        gm = 'gamemaker'
        cli.command('create game1', gm)
        cli.command('addteam team1 1234', gm)
        response = self.client.post('/login', {'username': 'team1', 'password': '1234'})
        self.assertContains(response, '<title> Team: team1 </title>')


class TestTeamPage(TestCase):
    def setUp(self):
        self.client = Client()
        cli = CLI(COMMANDS)
        gm = 'gamemaker'
        cli.command('create game1', gm)
        cli.command('addteam team1 1234', gm)
        cli.command('addlandmark "ldm1" "New York" "Gift given by the French" "Statue of Liberty"', gm)
        cli.command('addlandmark "ldm2" "UWM" "Place we purchase coffee from" "Grind"', gm)