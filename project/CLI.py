import unittest


class CLI():
    def __init__(self):
        self.gm = None

    def command(self, args):
        return ''


class TestCLI(unittest.TestCase):
    def setUp(self):
        self.cli = CLI()