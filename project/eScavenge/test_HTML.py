from django.test import Client
from django.test import TestCase


class TestLogin(TestCase):
    def setUp(self):
        self.client = Client()

    def test_get_login_page(self):
        response = self.client.get('/')
        self.assertEqual(200, response.status_code, "Wrong status returned")
