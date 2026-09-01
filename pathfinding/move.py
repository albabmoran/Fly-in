from enum import Enum


class Move(int, Enum):
    still = 0
    connect = 1
    move = 2
