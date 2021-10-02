###############################################################################
''''''
###############################################################################


from abc import abstractmethod as _abstractmethod
from collections.abc import Mapping as _Mapping

from . import _Param

from .tuplelike import TupleLike as _TupleLike


class DictLike(_Mapping, _TupleLike):

    reqslots = ('dct',)

    pairtype = _TupleLike

    @classmethod
    def parameterise(cls, arg, /, *args):
        if not args:
            if isinstance(arg, _Mapping):
                arg = arg.items()
            return super().parameterise(arg)
        return super().parameterise(arg, *args)

    @classmethod
    def check_param(cls, arg, /):
        if not isinstance(arg, pairtype := cls.pairtype):
            arg = pairtype(arg)
        if not len(arg) == 2:
            raise ValueError("Input pairs must be of length 2.")
        return super().check_param(arg)

    def __init__(self, /):
        super().__init__()
        self.dct = dict(self.args)

    def __getitem__(self, arg, /):
        return self.dct.__getitem__(arg)

    def __iter__(self, /):
        return iter(self.dct)

    def __len__(self, /):
        return self._len

    def __str__(self, /):
        return ', '.join(map(
            ': '.join,
            zip(map(str, self.keys()), map(str, self.values())),
            ))


###############################################################################
###############################################################################
