from collections import defaultdict
from typing import Dict, List, Generator

from math import sqrt

from . import Frame
from pathlib import Path
from .rows import get_rows
from itertools import cycle, islice
import random
import time

effects = {
}  # type: Dict[str, Effect]


class Effect:
    @staticmethod
    def init_frames(d) -> List[Frame]:
        if isinstance(d, (Path, str)):
            frames = []
            for file in Path(d).iterdir():
                frames.append(Frame(get_rows(file)))
        else:
            # function to generate frames
            frames = d()
        return frames

    def __init__(self, name, pattern, delay=0.05):
        self.name = name
        self.pattern = Effect.init_frames(pattern)
        self.delay = delay

        effects[name] = self

    def play(self, device):
        for frame in self.pattern:
            frame.draw(device)
            time.sleep(self.delay)


def _effect(f_or_name: (str, Generator[Frame, None, None]), delay=0.05):
    def decorate(f, name=f_or_name):
        return Effect(name, f, delay)

    if isinstance(f_or_name, str):
        return decorate
    return decorate(f_or_name, name=f_or_name.__name__)


FRAME_WIDTH = 0x10
FRAME_HEIGHT = 6


def wave_down_base(color_generator):
    color_cache = []
    while True:
        while len(color_cache) <= FRAME_HEIGHT:
            color_cache.insert(0, next(color_generator))

        # pop last
        color_cache.pop()

        # make a frame out of them
        yield Frame([color] * FRAME_WIDTH for color in color_cache)


@_effect('waveDown')
def wave_down():
    red = (255, 0, 0)
    green = (0, 255, 0)
    blue = (0, 0, 255)
    orange = (255, 100, 0)
    yellow = (255, 255, 0)
    white = (255, 255, 255)
    black = (0, 0, 0)

    yield from wave_down_base(cycle([red, green, blue, orange, yellow, white, black]))


@_effect('waveDownRandom')
def wave_down_random():
    def random_color_generator():
        while True:
            yield random.randrange(256), random.randrange(256), random.randrange(256)

    yield from wave_down_base(random_color_generator())


def pixel_base(pixel_cb, before_frame_cb=None):
    while True:
        if before_frame_cb:
            do_exit = before_frame_cb()
            if do_exit:
                return
        frame = Frame()
        for y in range(FRAME_HEIGHT):
            row = []
            for x in range(FRAME_WIDTH):
                row.append(pixel_cb(x, y))
            frame.set_row(y, row)
        yield frame


@_effect('pixelRandom')
def pixel_random():
    yield from pixel_base(lambda x, y: (random.randrange(256), random.randrange(256), random.randrange(256)))


@_effect('pixelRandomSticky')
def pixel_random():
    pixel_field = defaultdict(lambda: defaultdict(lambda: (0, 0, 0)))
    sticky = defaultdict(lambda: defaultdict(lambda: False))

    def tick_field():
        for x in range(FRAME_WIDTH):
            for y in range(FRAME_HEIGHT):
                if not sticky[x][y]:
                    pixel_field[x][y] = (random.randrange(256), random.randrange(256), random.randrange(256))
                    if random.randrange(100) > 90:
                        sticky[x][y] = True

    def render(x, y):
        return pixel_field[x][y]

    yield from pixel_base(render, tick_field)


@_effect('waveDiagonalDown', delay=0.1)
def wave_diagonal_down():
    red = (255, 0, 0)
    green = (0, 255, 0)
    blue = (0, 0, 255)
    orange = (255, 100, 0)
    yellow = (255, 255, 0)
    white = (255, 255, 255)
    black = (0, 0, 0)

    colors = cycle([red, green, blue, orange, yellow, white, black])

    color_cache = [next(colors) for _ in range(FRAME_WIDTH + FRAME_HEIGHT)]

    def setup_diagonal():
        color_cache.insert(0, next(colors))
        color_cache.pop()

    def diagonal(x, y):
        color_index = x + y
        return color_cache[color_index]

    yield from pixel_base(diagonal, setup_diagonal)


@_effect('rain')
def rain():
    def infinite_green():
        while True:
            yield 0, 255, 0

    yield from rain_gen(infinite_green())


@_effect('rainRandom')
def rain():
    def randomness():
        while True:
            yield random.randrange(256), random.randrange(256), random.randrange(256)

    yield from rain_gen(randomness())


def merge_colors(a, b):
    ar, ag, ab = a
    br, bg, bb = b
    weight = 1
    fr = sqrt(((ar ** 2) * weight + br ** 2) / (1 + weight))
    fg = sqrt(((ar ** 2) * weight + bg ** 2) / (1 + weight))
    fb = sqrt(((ar ** 2) * weight + bb ** 2) / (1 + weight))
    return int(fr), int(fg), int(fb)


def rain_gen(color_gen):
    elements = []
    pool_color = None
    pool_row_size = 50
    pool_count = 0
    draining = False

    def tick_rain():
        nonlocal pool_color, pool_count, draining
        for i in range(len(elements) - 1, -1, -1):
            e = elements[i]
            e[1] += 1
            if e[1] >= FRAME_HEIGHT:
                if draining:
                    pool_count -= 10
                else:
                    pool_count += 1
                if pool_color is None:
                    pool_color = e[2]
                else:
                    pool_color = merge_colors(pool_color, e[2])
                del elements[i]
        if random.randrange(100) > 25:
            elements.append([random.randrange(FRAME_WIDTH), 0, next(color_gen)])

    def render(x, y):
        nonlocal draining
        pool_cutoff = pool_count // pool_row_size
        y_cutoff = FRAME_HEIGHT - pool_cutoff - 1
        if y_cutoff < 0:
            draining = True
        if pool_count == 0:
            draining = False
        if y_cutoff < y:
            return pool_color
        gen = filter(lambda e: (e[0] == x and e[1] == y), elements)
        try:
            first = next(gen)
        except StopIteration:
            first = None
        if first is not None:
            return first[2]
        return 0, 0, 0

    yield from pixel_base(render, tick_rain)


__all__ = ['effects']
