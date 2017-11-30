from django.test import TestCase
from django.core.exceptions import ValidationError
from .Team import TeamFactory, Team


class TestInit(TestCase):
    def test_init(self):
        team = TeamFactory.get_team("TeamA", "2123")
        self.assertEqual("TeamA", team.username, "username value improperly set")
        self.assertEqual("2123", team.password, "password value improperly set")


class TestPassword(TestCase):
    def setUp(self):
        self.team = TeamFactory.get_team("Team1", "1234")

    def test_get_password(self):
        self.assertEqual("1234", self.team.password, "Got some password")

    def test_set_password(self):
        self.team.password = "2132"
        self.team.full_clean()
        self.team.save()
        self.team = Team.objects.get(username=self.team.username)
        self.assertEqual("2132", self.team.password, "Password not set properly")


class TestPoints(TestCase):
    def setUp(self):
        self.team = TeamFactory.get_team("Team 1", "1234")

    def test_get_points(self):
        self.team.points = 32
        self.team.full_clean()
        self.team.save()
        self.team = Team.objects.get(username=self.team.username)
        self.assertEqual(32, self.team.points, "Failed to read 32 points properly")

    def test_add_once_positive(self):
        self.team.points = 100
        self.team.full_clean()
        self.team.save()
        self.team = Team.objects.get(username=self.team.username)
        self.assertEqual(100, self.team.points, "Failed to set 100 points properly")

    def test_add_cumulative_positive(self):
        self.team.points = 100
        self.team.full_clean()
        self.team.save()
        self.team = Team.objects.get(username=self.team.username)
        self.assertEqual(100, self.team.points, "Failed to set 100 points properly")
        self.team.points = 15
        self.team.full_clean()
        self.team.save()
        self.team = Team.objects.get(username=self.team.username)
        self.assertEqual(15, self.team.points, "Failed to set 15 points properly")

    def test_add_once_negative(self):
        self.team.points = -15
        with self.assertRaises(ValidationError):
            self.team.full_clean()

    def test_add_cumulative_posandneg(self):
        self.team.points = 100
        self.team.full_clean()
        self.team.save()
        self.team = Team.objects.get(username=self.team.username)
        self.assertEqual(100, self.team.points, "Failed to set 100 points properly")
        self.team.points = -15
        with self.assertRaises(ValidationError):
            self.team.full_clean()


class TestTeamLogin(TestCase):
    def setUp(self):
        self.team = TeamFactory().get_team("team1", "password123")

    def test_team_login_success(self):
        user = self.team.login("team1", "password123")
        self.assertEqual(self.team, user, "Different user returned")
        self.assertEqual(self.team.username, user.username)
        self.assertFalse(user.is_admin())

    def test_team_login_fail(self):
        user = self.team.login("team1", "wrong password")
        self.assertEqual(None, user, "Invalid user returned")


class TestAddCurrentPenalty(TestCase):
    def setUp(self):
        self.team = TeamFactory().get_team("Team2", "password123")

    def test_add_pos_points(self):
        self.assertTrue(self.team.add_penalty(1), "Incorrect Penalty Value")

    def test_add_neg_points(self):
        self.assertFalse(self.team.add_penalty(-1), "Penalty points are being given neg values")
