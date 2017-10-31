import unittest


class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.wishlist = []
        self.accessList = []

    def login(self, password):
        return self.password is password

    def append(self, item):
        if item in self.wishlist:
            return False
        else:
            self.wishlist.append(item)
            return True

    def remove(self, item):
        if item not in self.wishlist:
            return False
        self.wishlist.remove(item)
        return True

    def getList(self):
        return self.wishlist

    def share(self, user):
        if self is user or user in self.accessList:
            return False
        self.accessList.append(user)
        return True

    def revoke(self, user):
        if self is user or user not in self.accessList:
            return False
        self.accessList.remove(user)
        return True

    def canAccess(self, username):
        return username in self.accessList


class TestUserShow(unittest.TestCase):
    def setUp(self):
        self.user = User("Rob", "1234")

    def test_getListBlank(self):
        self.user.wishlist = []
        self.assertEqual([], self.user.getList(), "Blank list not returned")

    def test_getListFull(self):
        fullList = ["This", "is", "a", "list", 2, {"this": "dict"}]
        self.user.wishlist = fullList
        self.assertEqual(fullList, self.user.getList(), "Full list not returned")


class TestCanAccess(unittest.TestCase):
    def setUp(self):
        self.user = User("Rob", "1234")
        self.accessor = User("Gary", "1234")

    def test_canAccessFalse(self):
        self.user.accessList = []
        self.assertFalse(self.user.canAccess(self.accessor), "User incorrectly granted access")

    def test_canAccessTrue(self):
        self.user.accessList = [self.accessor]
        self.assertTrue(self.user.canAccess(self.accessor), "User incorrectly denied acccess")


class TestAppend(unittest.TestCase):
    def setUp(self):
        self.user = User("Rob", "1234")

    def test_AppendNewItem(self):
        item = "Buy something"
        self.assertTrue(self.user.append(item), "Append didn't return True")
        self.assertEqual([item], self.user.wishlist, "Did not add new Item")

    def test_AppendTwoItems(self):
        item1 = "Buy something"
        item2 = "Buy another thing"
        self.assertTrue(self.user.append(item1), "Append didn't return True")
        self.assertTrue(self.user.append(item2), "Append didn't return True")
        self.assertEqual([item1, item2], self.user.wishlist, "Did not add new Item")

    def test_AppendItemAlreadyExits(self):
        item = "Buy something"
        self.user.wishlist = [item]
        self.assertFalse(self.user.append(item), "Append didn't return False")
        self.assertEqual([item], self.user.wishlist, "Item already exits, should not have added to list")


class TestUserInit(unittest.TestCase):
    def test_init(self):
        user = User("Bryan", "1234");
        self.assertTrue(user.username, "user")
        self.assertTrue(user.password, "pass")


class TestUserLogin(unittest.TestCase):
    def setUp(self):
        self.user = User("Bryan", "1234")

    def test_failedlogin(self):
        self.assertFalse(self.user.login("2345"), "Incorrect Password")
        self.assertTrue(self.user.login("1234"), "Login Successful")


class TestUserShare(unittest.TestCase):
    def setUp(self):
        self.user1 = User("Rob", "1234")
        self.user2 = User("Bob", "1234")
        self.user3 = User("Charlie", "1234")

    def test_userAddSelf(self):
        self.assertFalse(self.user1.share(self.user1), "returned true when adding self")
        self.assertNotIn(self.user1, self.user1.accessList, "cannot share with itself")

    def test_ShareOne(self):
        self.assertEquals(True, self.user1.share(self.user2), "user1 does not return true when sharing")
        self.assertEquals(1, len(self.user1.accessList), "User2 share list incorrect size")
        self.assertIn(self.user2, self.user1.accessList, "User1 not properly added to User2 share list")
        self.assertEquals(0, len(self.user2.accessList), "User being added increased size")

    def test_shareTwo(self):
        self.user1.share(self.user2)

        self.assertTrue(self.user1.share(self.user3), "share does not return true when adding a valid second user")
        self.assertEquals(2, len(self.user1.accessList), "User1 share list incorrect size")
        self.assertIn(self.user2, self.user1.accessList, "User2 not properly added to User1 accessList list")
        self.assertIn(self.user3, self.user1.accessList, "User3 not properly added to User1 accessList list")

    def test_userAlreadyExisting(self):
        self.user1.share(self.user2)

        self.assertFalse(self.user1.share(self.user2),
                         "Did not return false when trying to add already existing user")
        self.assertEquals(1, len(self.user1.accessList), "Already Existing User Added Again")
        self.assertIn(self.user2, self.user1.accessList, "User2 is not in User1 accessList list after adding *2")


class TestUserRevoke(unittest.TestCase):
    def setUp(self):
        self.user1 = User("Rob", "1234")
        self.user2 = User("Bob", "1234")
        self.user3 = User("Charlie", "1234")
        self.user4 = User("Ron", "1234")

    def test_RevokeEmpty(self):
        self.assertFalse(self.user1.revoke(self.user2), "Did not return false when trying to revoke from an empty list")
        self.assertEquals(0, len(self.user1.accessList), "user1 is not empty after removing from empty")

    def test_RevokeOne(self):
        self.user1.accessList = [self.user2, self.user3]
        self.assertTrue(self.user1.revoke(self.user2), "revoke did not return true when revoking valid user")
        self.assertEqual(1, len(self.user1.accessList))
        self.assertNotIn(self.user2, self.user3.accessList, "user2 not revoked!")

    def test_revokeTwo(self):
        self.user1.accessList = [self.user2, self.user3, self.user4]
        self.user1.revoke(self.user2)
        self.user1.revoke(self.user3)
        self.assertEquals(1, len(self.user1.accessList), "too many or too little elements removed")

    def test_removeNonExisting(self):
        self.user1.accessList = [self.user2, self.user3]
        self.assertFalse(self.user1.revoke(self.user4), "attempting to remove invalid user does not return false")
        self.assertEquals(2, len(self.user1.accessList), "elements modified while trying to remove invalid")


class TestRemove(unittest.TestCase):
    def setUp(self):
        self.user = User("Martin", "1234")
        self.user.wishlist = ["car", "ps3", "shoes", "clothes"]

    def test_itemNotInList(self):
        self.assertFalse(self.user.remove("randomItem"), "Item is not in list so should be false")

    def test_succesfullyRemoved(self):
        self.assertTrue(self.user.remove("car"), "Item was not removed")
        self.assertTrue(self.user.remove("clothes"), "Item was not removed")
        self.assertTrue(self.user.remove("shoes"), "Item was not removed")


suite = unittest.TestSuite()
suite.addTest(unittest.makeSuite(TestUserShow))
suite.addTest(unittest.makeSuite(TestCanAccess))
suite.addTest(unittest.makeSuite(TestAppend))
suite.addTest(unittest.makeSuite(TestUserInit))
suite.addTest(unittest.makeSuite(TestUserLogin))
suite.addTest(unittest.makeSuite(TestUserRevoke))
suite.addTest(unittest.makeSuite(TestUserShare))
suite.addTest(unittest.makeSuite(TestRemove))
runner = unittest.TextTestRunner()
res = runner.run(suite)
print(res)
print("*" * 20)
for i in res.failures: print(i[1])
