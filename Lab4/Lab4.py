import unittest

"""
These classes are part of a program that manages the score boards at  baseball game. The operator will have a console with buttons for ball, strike, foul, hit and walk (for this problem other methods of getting on base are ignored). Both walk and hit advance any necessary runners (by calling advance(1)) , then put a runner on first base. Finally, the operator can advance runners using a button for each base: advance
(1), advance(2) and advance(3). When a runner advances fro third runs goes up by 1. When an at-bat is over (due to walk, strike-out or hit) it is stored in the list of at-bats in the inning.
Examples of advance:
Runners at 1st and 3rd, advance(1) results in runners at 2nd and 3rd
Runners at 1st and 2nd, advance(1) results in runners at 2nd and 3rd
Runners at 1st and 3rd, advance(2) results in runners at 1st and 3rd (no change)
Runners at 1st, 2nd, and 3rd, advance(2) results in runners at 1st and 3rd (and a run scores)
"""


class AtBat:
    def __init__(self):
        self.balls = 0  # a value 0-4
        self.strikes = 0  # a value 0-3

    def ball(self):  # call when umpire calls a ball: increment balls
        if self.balls == 4:  # calling ball when balls=4 should have no effect
            return

        if 0 <= self.balls < 4:
            self.balls += 1
        else:
            self.balls = 0

    def strike(self):  # call when umpire calls a strike: increment strikes
        if self.strikes == 3:
            return

        if self.strikes > 3 or self.strikes < 0:
            self.strikes = 0
        else:
          self.strikes += 1

    def foul(self):  # call when a foul ball is called; only increment strikes if < 2
        if self.strikes >= 3 or self.strikes < 0:
            return

        self.strikes += 1

    def isWalk(self):  # returns true if umpire should call a walk (4 balls), false otherwise
        return self.balls == 4

    def isOut(self):  # returns true if umpire should call batter out (3 strikes), false otherwise
        return self.strikes >= 3

    def isNew(self):  # returns true only if all variables set to start at bat values: balls=0 strikes=0
        return self.balls == 0 and self.strikes == 0

    def print(self):
        pass


class HalfInning:
    def __init__(self):
        self.on = [False, False, False]  # runners on the bases: on[0] is first, on[1] is second, on[2] is third
        self.outs = 0  # a value 0-3
        self.hits = 0  # total hits in this half of the inning
        self.runs = 0  # total runs in this half of the inning
        self.atBat = []  # a list of all at-bats in the inning, most recent last

    def advance(self, b=1):  # move all runners at base b or farther up one position; advance to home increments runs
        if not self.on[b - 1]:
            return

        if self.on[2]:
            self.runs += 1

        for i in range(2, b - 1):
            self.on[i] = self.on[i - 1]

    def print(self):  # print the state of the inning and current at-bat
        pass


class TestAtBatInit(unittest.TestCase):
    def test_init(self):
        atBat = AtBat()
        self.assertEqual(0, atBat.strikes)
        self.assertEqual(0, atBat.balls)


class TestAtBatBall(unittest.TestCase):
    def setUp(self):
        self.atBat = AtBat()

    def test_ZeroToOne(self):
        self.assertEqual(0, self.atBat.balls, "0-->1: balls not intially 0")
        self.atBat.ball()
        self.assertEqual(1, self.atBat.balls, "0-->: balls not incremented on call to ball()")

    def test_OneToTwo(self):
        self.atBat.balls = 1
        self.assertEqual(1, self.atBat.balls)
        self.atBat.ball()
        self.assertEqual(2, self.atBat.balls)

    def test_TwoToThree(self):
        self.atBat.balls = 2
        self.assertEqual(2, self.atBat.balls)
        self.atBat.ball()
        self.assertEqual(3, self.atBat.balls)

    def test_ThreeToFour(self):
        self.atBat.balls = 3
        self.assertEqual(3, self.atBat.balls)
        self.atBat.ball()
        self.assertEqual(4, self.atBat.balls)

    def test_Four(self):  # calling ball when balls=4 should have no effect
        self.atBat.balls = 4
        self.assertEqual(4, self.atBat.balls)
        self.atBat.ball()
        self.assertEqual(4, self.atBat.balls)

    def test_InvalidState(self):  # calling ball when balls is not an int between 0 and 4 should reset
        self.atBat.balls = -1
        self.assertEqual(-1, self.atBat.balls)
        self.atBat.ball()
        self.assertEqual(0, self.atBat.balls)


class TestAtBatStrike(unittest.TestCase):
    def setUp(self):
        self.atBat = AtBat()

    def test_ZeroToOne(self):
        self.assertEqual(0, self.atBat.strikes, "0-->1, Strikes not Initialized to 0")
        self.atBat.strike()
        self.assertEqual(1, self.atBat.strikes, "0-->1, Strikes not Properly Increased")

    def test_OneToTwo(self):
        self.atBat.strikes = 1
        self.assertEqual(1, self.atBat.strikes, "1-->2, Strikes not Properly set to 1")
        self.atBat.strike()
        self.assertEqual(2, self.atBat.strikes, "1-->2, Strikes not Properly Increased")

    def test_TwoToThree(self):
        self.atBat.strikes = 2
        self.assertEqual(2, self.atBat.strikes, "2-->3, Strikes not properly set to 2")
        self.atBat.strike()
        self.assertEqual(3, self.atBat.strikes, "2-->3, Strikes not properly Increased")

    def test_ThreeToFour(self):
        self.atBat.strikes = 3
        self.assertEqual(3, self.atBat.strikes, "3-->4, Strikes not properly set to 3")
        self.atBat.strike()
        self.assertEqual(3, self.atBat.strikes, "3-->4, Strikes out of range")

    def test_Invalid(self):
        self.atBat.strikes = -2
        self.atBat.strike()
        self.assertEqual(0, self.atBat.strikes, "Strikes is out of range(below 0")
        self.atBat.strikes = 4
        self.atBat.strike()
        self.assertEqual(0, self.atBat.strikes, "Strikes is out of range(above 3)")


class TestAtBatFoul(unittest.TestCase):
    def setUp(self):
        self.atBat = AtBat()

    def test_ZeroToOneFoul(self):
        self.atBat.foul()
        self.assertIs(1, self.atBat.strikes, "0-->: strikes not incremented on call to foul ()")

    def test_OneToTwoFoul(self):
        self.atBat.strikes = 1
        self.atBat.foul()
        self.assertIs(2, self.atBat.strikes, "1-->: strikes not incremented on call to foul ()")

    def test_TwoStrikesFoul(self):
        self.atBat.strikes = 2
        self.atBat.foul()
        self.assertIs(self.atBat.strikes, 3, "Strikes = 2, foul ball does not increment")

    def test_invalidStateFoul(self):
        self.atBat.strikes = -1
        self.assertLess(self.atBat.strikes, 0, "Foul ball is out of range, -1")


class TestAtBatIsOut(unittest.TestCase):
    def setUp(self):
        self.atBat = AtBat()

    def test_whenStrikesZero(self):
        self.assertFalse(self.atBat.isOut(), "Is out when strikes at 0")

    def test_whenStrikesOne(self):
        self.atBat.strikes = 1
        self.assertFalse(self.atBat.isOut(), "Is out when strikes at 1")

    def test_whenStrikesTwo(self):
        self.atBat.strikes = 2
        self.assertFalse(self.atBat.isOut(), "Is out when strikes at 2")

    def test_strikesAtThree(self):
        self.atBat.strikes = 3
        self.assertTrue(self.atBat.isOut(), "When strikes at 3 it's not equal to out")

    def test_whenBallsFour(self):
        self.atBat.balls = 4
        self.assertFalse(self.atBat.isOut(), "Is out is set to true when balls is equal to 4")


class TestIsWalk(unittest.TestCase):
    def setUp(self):
        self.atBat = AtBat()

    def test_ZeroBall(self):
        self.atBat.balls = 0
        self.assertFalse(self.atBat.isWalk(), "Empire should not call a walk")

    def test_OneBall(self):
        self.atBat.balls = 1
        self.assertFalse(self.atBat.isWalk(), "Empire should not call a walk")

    def test_TwoBall(self):
        self.atBat.balls = 2
        self.assertFalse(self.atBat.isWalk(), "Empire should not call a walk")

    def test_ThreeBall(self):
        self.atBat.balls = 3
        self.assertFalse(self.atBat.isWalk(), "Empire should not call a walk")

    def test_Four(self):
        self.atBat.balls = 4
        self.assertTrue(self.atBat.isWalk(), "Empire should have called a walk")


class TestHalfInningInit(unittest.TestCase):
    def test_init(self):
        halfInning = HalfInning()
        self.assertEqual(3, len(halfInning.on))
        for base in halfInning.on:
            self.assertFalse(base)
        self.assertEqual(0, halfInning.outs)
        self.assertEqual(0, halfInning.hits)
        self.assertEqual(0, halfInning.runs)
        self.assertEqual([], halfInning.atBat)


class TestHalfInningAdvance(unittest.TestCase):
    def setUp(self):
        self.halfInning = HalfInning()

    def test_FalseFalseFalseAdvance1(self):
        self.assertEqual([False, False, False], self.halfInning.on, "Initial state not set correctly")
        self.halfInning.advance()
        self.assertEqual([False, False, False], self.halfInning.on, "Advance added a player on base")

    def test_FalseFalseFalseAdvance2(self):
        self.assertEqual([False, False, False], self.halfInning.on, "Initial state not set correctly")
        self.halfInning.advance(2)
        self.assertEqual([False, False, False], self.halfInning.on, "Advance added a player on base")

    def test_FalseFalseFalseAdvance3(self):
        self.assertEqual([False, False, False], self.halfInning.on, "Initial state not set correctly")
        self.halfInning.advance(3)
        self.assertEqual([False, False, False], self.halfInning.on, "Advance added a player on base")

    def TrueTrueTrueAdvanceOne(self):
        self.HalfInning.runs = 0
        self.assertEqual(True, True, True, self.HalfInning.on)
        self.HalfInning.advance(1)
        self.assertEqual(False, True, True, self.HalfInning.on)
        self.assertEqual(1, self.HalfInning.runs, "Runs not incrementing")

    def TrueTrueTrueAdvanceTwo(self):
        self.HalfInning.runs = 0
        self.assertEqual(True, True, True, self.HalfInning.on)
        self.HalfInning.advance(2)
        self.assertEqual(False, False, True, self.HalfInning.on)
        self.assertEqual(2, self.HalfInning.runs, "Runs not incrementing")

    def TrueTrueTrueAdvanceThree(self):
        self.HalfInning.runs = 0
        self.assertEqual(True, True, True, self.HalfInning.on)
        self.HalfInning.advance(3)
        self.assertEqual(False, False, False, self.HalfInning.on)
        self.assertEqual(3, self.HalfInning.runs, "Runs not incrementing")


class TestHalfInningIsNew(unittest.TestCase):
    def test_isNew(self):
        atBat = AtBat()
        self.assertEqual(0, atBat.balls, "Balls not set to 0")
        self.assertEqual(0, atBat.strikes, "Balls not set to 0")


suite = unittest.TestSuite()
suite.addTest(unittest.makeSuite(TestAtBatBall))
suite.addTest(unittest.makeSuite(TestAtBatInit))
suite.addTest(unittest.makeSuite(TestAtBatStrike))
suite.addTest(unittest.makeSuite(TestAtBatFoul))
suite.addTest(unittest.makeSuite(TestAtBatIsOut))
suite.addTest(unittest.makeSuite(TestIsWalk))
suite.addTest(unittest.makeSuite(TestHalfInningInit))
suite.addTest(unittest.makeSuite(TestHalfInningIsNew))
suite.addTest(unittest.makeSuite(TestHalfInningAdvance))
runner = unittest.TextTestRunner()
res = runner.run(suite)
print(res)
print("*" * 20)
for i in res.failures: print(i[1])
