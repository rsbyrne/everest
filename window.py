import h5py
import operator
from functools import partial

class Fetch:

    operations = operator.__dict__
    operations[None] = lambda *args: True

    def __init__(
            self,
            *args,
            operation = None
            ):
        self.args = args
        self.operation = operation

    def __call__(self, context = None):
        if context is None:
            context = lambda *inp: inp
        try:
            args = context(*self.args)
            return self.operations[self.operation](*args)
        except KeyError:
            return False

    def __lt__(self, *args):
        return Fetch(*self.args, *args, operation = 'lt')
    def __le__(self, *args):
        return Fetch(*self.args, *args, operation = 'le')
    def __eq__(self, *args):
        return Fetch(*self.args, *args, operation = 'eq')
    def __ne__(self, *args):
        return Fetch(*self.args, *args, operation = 'ne')
    def __ge__(self, *args):
        return Fetch(*self.args, *args, operation = 'ge')
    def __gt__(self, *args):
        return Fetch(*self.args, *args, operation = 'gt')

def _readwrap(func):
    def wrapper(*args, **kwargs):
        self = args[0]
        h5filename = self.h5filename
        with h5py.File(h5filename, 'r') as h5file:
            self.h5file = h5file
            outputs = func(*args, **kwargs)
        return outputs
    return wrapper

class Reader:
    def __init__(
            self,
            h5filename
            ):
        self.h5file = None
        self.h5filename = h5filename

    def __getitem__(self, inp):
        if type(inp) is tuple:
            allouts = [self.__getitem__(subInp) for subInp in inp]
            return set.intersection(*allouts)
        if isinstance(inp, Fetch):
            return self._get_fetch(inp)
        raise TypeError

    def _context(self, superkey, *args):
        args = list(args)
        key = args.pop(0)
        try: out = self.h5file[superkey].attrs[key]
        except: out = self.h5file[superkey][key]
        return (out, *args)

    @_readwrap
    def _get_fetch(self, fetch):
        outs = set()
        for superkey in self.h5file:
            context = partial(
                self._context,
                superkey
                )
            if fetch(context):
                outs.add(superkey)
        return outs
