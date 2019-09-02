import sys
import importlib
import inspect
from movie import Movie
from movie_out import MovieOutput
import numpy as np

if __name__ == '__main__':
    movie = Movie(sys.argv[1], 0)
    output = None
    effect_name = sys.argv[2].split("=")[0]
    effect_params = sys.argv[2][len(effect_name) + 1:]
    effect = None
    effect_module = importlib.import_module(effect_name)
    for name, obj in inspect.getmembers(effect_module):
        if inspect.isclass(obj) and obj.__name__.lower() == effect_name.lower():
            effect = obj(effect_params, movie)
    while movie.has_frames:
        frame = movie.get_next_frame()
        current_frame = movie.current_frame
        if frame is not None:
            applied_frame = effect.apply(frame, current_frame)
            movie.current_frame = current_frame
            if applied_frame is not None:
                if output is None:
                    output = MovieOutput(sys.argv[-1], applied_frame.shape, movie.average_frame_rate)
                output.append(np.clip(applied_frame, 0, 255))
    while effect.has_frames:
        applied_frame = effect.next_frame()
        if applied_frame is not None:
            output.append(np.clip(applied_frame, 0, 255))
