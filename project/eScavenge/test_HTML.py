from http import HTTPStatus
from django.test import Client
from django.test import TestCase
from .CLI import CLI, COMMANDS


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
        self.assertContains(response, 'eScavenge Login Page')

    def test_login_team(self):
        cli = CLI(COMMANDS)
        gm = 'gamemaker'
        cli.command('create game1', gm)
        cli.command('addteam team1 1234', gm)
        response = self.client.post('/login', {'username': 'team1', 'password': '1234'})
        self.assertContains(response, '<title> Team: team1 </title>')
