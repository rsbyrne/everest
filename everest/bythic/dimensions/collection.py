###############################################################################
''''''
###############################################################################

from .countable import Countable as _Countable

class Collection(_Countable):

    typ = None

    __slots__ = ('content',)

    def __init__(self, iterable, **kwargs):
        if self.typ is None:
            self.typ = type(next(iter(iterable)))
        try:
            self.iterlen = len(iterable)
        except AttributeError:
            pass
        self.iter_fn = iterable.__iter__
        super().__init__(**kwargs)
        self.register_argskwargs(iterable) # pylint: disable=E1101

###############################################################################
###############################################################################
