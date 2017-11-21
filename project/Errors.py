from enum import Enum, auto


class Errors(Enum):
    NO_ERROR = auto()
    NO_GAME = auto()
    NEGATIVE_INDEX = auto()
    GAME_NOT_STARTED = auto()
    LANDMARK_INDEX = auto()
    STRING_TO_INTEGER = auto()
    WRONG_ANSWER = auto()
    INVALID_LOGIN = auto()
    FINAL_ANSWER = auto()
