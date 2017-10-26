import unittest


class CLI():
    def command(self, args):
        return ''


class TestCLI(unittest.TestCase):
    def setUp(self):
        self.cli = CLI()