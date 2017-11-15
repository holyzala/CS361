from enum import Enum, auto


class Errors(Enum):
    NO_ERROR = auto()
    NO_GAME = auto()
    LANDMARK_INDEX = auto()
    WRONG_ANSWER = auto()
    INVALID_LOGIN = auto()
