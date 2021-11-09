###############################################################################
''''''
###############################################################################


import abc as _abc
from weakref import ref as _ref


class Constructor(_abc.ABC):

    __slots__ = ('makefn', '_call_')

    def __init__(self, makefn, /):
        self.makefn = makefn
        self.reset()

    def reset(self, ref=None, /):
        self._call_ = self._original_call__

    def _original_call__(self, /):
        out = self.makefn()
        self._call_ = _ref(out, self.reset)
        return out

    @property
    def __call__(self, /):
        return self._call_


###############################################################################
###############################################################################
