import unittest
from User2 import User


class Interface:
    def __init__(self):
        self.Users = {}
        self.CurrentUser = None

    def append_item(self, item):
        if not self.CurrentUser or self.CurrentUser not in self.Users:
            return False
        if item in self.Users[self.CurrentUser]:
            return False
        self.Users[self.CurrentUser].append(item)
        return True

    def remove_item(self, item):
        if not self.CurrentUser or self.CurrentUser not in self.Users:
            return False
        try:
            self.Users[self.CurrentUser].remove(item)
        except ValueError:
            return False
        return True

    def show_list(self):
        pass


class TestInit(unittest.TestCase):
    def test_init(self):
        cli = Interface()
        self.assertEqual({}, cli.Users, "Initial user dictionary not empty")
        self.assertIsNone(cli.CurrentUser, "Initial current user not empty")


class TestAppendItem(unittest.TestCase):
    def setUp(self):
        self.interface = Interface()
        self.user = User("Rob", "1234")
        self.interface.Users = {self.user: []}
        self.interface.CurrentUser = self.user

    def test_AppendNoCurrentUser(self):
        self.interface.CurrentUser = None
        self.assertFalse(self.interface.append_item("Car"))

    def test_AppendNewItem(self):
        item = "Buy something"
        self.assertTrue(self.interface.append_item(item), "Append didn't return True")
        self.assertEqual([item], self.interface.Users[self.user], "Did not add new Item")

    def test_AppendTwoItems(self):
        item1 = "Buy something"
        item2 = "Buy another thing"
        self.assertTrue(self.interface.append_item(item1), "Append didn't return True")
        self.assertTrue(self.interface.append_item(item2), "Append didn't return True")
        self.assertEqual([item1, item2], self.interface.Users[self.user], "Did not add new Item")

    def test_AppendItemAlreadyExits(self):
        item = "Buy something"
        self.interface.Users[self.user] = [item]
        self.assertFalse(self.interface.append_item(item), "Append didn't return False")
        self.assertEqual([item], self.interface.Users[self.user], "Item already exits, should not have added to list")


class TestRemoveItem(unittest.TestCase):
    def setUp(self):
        self.interface = Interface()
        self.user = User("Rob", "1234")
        self.interface.Users = {self.user: ["car", "clothes", "shoes"]}
        self.interface.CurrentUser = self.user

    def test_RemoveNoCurrentUser(self):
        self.interface.CurrentUser = None
        self.assertFalse(self.interface.remove_item("car"))

    def test_itemNotInList(self):
        self.assertFalse(self.interface.remove_item("randomItem"), "Item is not in list so should be false")

    def test_succesfullyRemoved(self):
        self.assertTrue(self.interface.remove_item("car"), "Item was not removed")
        self.assertTrue(self.interface.remove_item("clothes"), "Item was not removed")
        self.assertTrue(self.interface.remove_item("shoes"), "Item was not removed")


if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestInit))
    suite.addTest(unittest.makeSuite(TestAppendItem))
    suite.addTest(unittest.makeSuite(TestRemoveItem))
    runner = unittest.TextTestRunner()
    res = runner.run(suite)
    print(res)
    print("*" * 20)
    for i in res.failures: print(i[1])
