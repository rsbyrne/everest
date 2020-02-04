import numpy as np

from . import Built

class Vector(Built):
    from .vector import __file__ as _file_
    def __init__(self, **kwargs):
        self.keys = sorted(kwargs.keys())
        self.vals = [kwargs[key] for key in self.keys]
        self.data = np.array(self.vals)
        super().__init__()
    def __iter__(self):
        for key, inp in sorted(self.inputs.items()):
            yield (key, inp)
    def __len__(self):
        return len(self.inputs)
    def __getitem__(self, key):
        return self.inputs[key]
