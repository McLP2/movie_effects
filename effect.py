from abc import ABC, abstractmethod


class Effect(ABC):
    def __init__(self, params, movie):
        self.params = params
        self.movie = movie

    @abstractmethod
    def apply(self, frame, frame_number):
        return frame
