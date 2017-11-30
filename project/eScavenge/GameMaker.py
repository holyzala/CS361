from abc import ABC, abstractmethod


class UserABC(ABC):
    @abstractmethod
    def login(self, username, password):
        pass

    @abstractmethod
    def is_admin(self):
        pass


class GMFactory:
    def get_gm(self):
        return self.GameMaker()

    class GameMaker(UserABC):
        def __init__(self):
            self.username = "gamemaker"
            self.__password = "1234"

        def login(self, username, password):
            if self.username == username and self.__password == password:
                return self
            return None

        @staticmethod
        def is_admin():
            return True
