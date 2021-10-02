###############################################################################
''''''
###############################################################################


from collections import abc as _collabc

from . import _Ptolemaic
from . import _shades


def pass_func(arg, /):
    return arg


class Schema(_shades.Singleton, _Ptolemaic):

    Brace = _Ptolemaic.BadParameter.trigger
    Mapp = _Ptolemaic.BadParameter.trigger

    @classmethod
    def _process_dictlike(cls, arg, /):
        return cls.Mapp(arg)

    @classmethod
    def _process_tuplelike(cls, arg, /):
        return cls.Brace(arg)

    @classmethod
    def _process_slicelike(cls, arg, /):
        return cls.Slyce(arg)

    @classmethod
    def yield_checktypes(cls, /):
        yield _collabc.Mapping, cls._process_dictlike
        yield _collabc.Sequence, cls._process_tuplelike
        yield slice, cls._process_slicelike

    @classmethod
    def prekey(cls, params):
        return params.hashID

    def _repr(self):
        return self.params.hashID


class Brace(_shades.TupleLike, Schema):
    ...


class Mapp(_shades.DictLike, Brace):

    _pairtype = Brace


class Slyce(_shades.SliceLike, Schema):
    ...
    


Schema.Brace = Brace
Schema.Mapp = Mapp
Schema.Slyce = Slyce


###############################################################################
###############################################################################
