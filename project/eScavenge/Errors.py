from enum import Enum, auto


class Errors(Enum):
    NO_ERROR = auto()
    NO_GAME = auto()
    NEGATIVE_INDEX = auto()
    GAME_IN_PROGRESS = auto()
    CAN_ONLY_EDIT_ORDER_WHEN_GAME_IS_NEW = auto()
    LANDMARK_INDEX = auto()
    STRING_TO_INTEGER = auto()
    WRONG_ANSWER = auto()
    INVALID_LOGIN = auto()
    FINAL_ANSWER = auto()
    GAME_STARTED = auto()
    ALREADY_STARTED = auto()
    INTEGRITY_ERROR = auto()
