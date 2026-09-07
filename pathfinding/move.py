from enum import Enum


class Move(int, Enum):
    """
    Defines the possible movement states of a drone.

    Each state is represented by an integer value used to identify the
    drone's current movement status.
    """

    still = 0
    connect = 1
    move = 2
