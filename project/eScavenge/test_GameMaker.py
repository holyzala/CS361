from django.test import TestCase
from .GameMaker import GMFactory


class TestLogin(TestCase):
    def setUp(self):
        self.gm = GMFactory().get_gm()

    def test_login_success(self):
        user = self.gm.login("gamemaker", "1234")
        self.assertEqual(self.gm, user, "Failed to return the same GameMaker object")
        self.assertEqual("gamemaker", user.username, "Username not correct")
        self.assertTrue(user.is_admin(), "Admin rights not correct")

    def test_login_bad_password(self):
        user = self.gm.login("gamemaker", "4321")
        self.assertEqual(None, user, "Bad password return the user object")

    def test_login_bad_username(self):
        user = self.gm.login("___", "1234")
        self.assertEqual(None, user, "Bad username returned the user object")
