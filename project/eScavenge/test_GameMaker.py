from django.test import TestCase

from .models import GMFactory


class TestLogin(TestCase):
    def setUp(self):
        self.game_maker = GMFactory().get_gm()

    def test_login_success(self):
        user = self.game_maker.login("gamemaker", "1234")
        self.assertEqual(self.game_maker, user, "Failed to return the same GameMaker object")
        self.assertEqual("gamemaker", user.username, "Username not correct")
        self.assertTrue(user.is_admin(), "Admin rights not correct")

    def test_login_bad_password(self):
        user = self.game_maker.login("gamemaker", "4321")
        self.assertEqual(None, user, "Bad password return the user object")

    def test_login_bad_username(self):
        user = self.game_maker.login("___", "1234")
        self.assertEqual(None, user, "Bad username returned the user object")
