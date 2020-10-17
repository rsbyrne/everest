import random

GLOBALSEED = 0

class Reseed:
    active = False
    def __init__(self, randomseed = None):
        global GLOBALSEED
        if randomseed is None:
            randomseed = GLOBALSEED
        self.randomseed = randomseed
    def __enter__(self):
        global GLOBALSEED
        random.seed(self.randomseed)
        GLOBALSEED += 1
        self.active = True
    def __exit__(self, *args):
        random.seed()
        self.active = False

from functools import wraps
def reseed(func):
    @wraps(func)
    def wrapper(*args, randomseed = None, **kwargs):
        if Reseed.active:
            return func(*args, **kwargs)
        else:
            with Reseed(randomseed):
                return func(*args, **kwargs)
    return wrapper

@reseed
def randint(digits = 12):
    low = int(10 ** digits)
    high = int(10 ** (digits + 1)) - 1
    return random.randint(low, high)
