from abc import ABC, abstractmethod


class Effect(ABC):
    def __init__(self, params, movie):
        self.params = params
        self.movie = movie
        self.has_frames = False
        self.allow_multiprocessing = True

    @abstractmethod
    def apply(self, frame, frame_number):
        return frame
