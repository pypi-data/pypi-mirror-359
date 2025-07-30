from enum import Enum


class Finger(Enum):
    THUMB = 0
    INDEX = 1
    MIDDLE = 2
    RING = 3
    PINKY = 4


class FingerData:
    def __init__(self, raw_data):
        if raw_data is None or len(raw_data) != 4:
            raise ValueError("raw_data must have exactly 4 elements")
        self.raw_data = raw_data
