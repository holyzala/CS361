from abc import ABC, abstractmethod


class LandmarkI(ABC):
    @abstractmethod
    def check_answer(self, answer):
        pass

    @property
    @abstractmethod
    def answer(self):
        pass

    @answer.setter
    @abstractmethod
    def answer(self, answer):
        pass


class LandmarkFactory:
    def get_landmark(self, clue, question, answer):
        return self.Landmark(clue, question, answer)

    class Landmark(LandmarkI):
        def __init__(self, clue, question, answer):
            self.question = question
            self.clue = clue
            self.__answer = answer

        @property
        def answer(self):
            return None

        @answer.setter
        def answer(self, answer):
            self.__answer = answer

        def check_answer(self, answer):
            return self.__answer.lower() == answer.lower()

        def __eq__(self, other):
            return self.clue == other.clue
