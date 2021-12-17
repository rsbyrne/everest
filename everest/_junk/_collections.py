###############################################################################
''''''
###############################################################################


from collections import abc as _collabc

from everest.ptolemaic.deferrer import DeferrerClass as _DeferrerClass


class Collection(_DeferrerClass, _collabc.Collection):

    _DEFERMETHS = ('__getitem__', '__len__', '__iter__')

    _PYTYP = _collabc.Collection

    def __init__(self, arg, /):
        if not isinstance(arg, self._PYTYP):
            raise TypeError(arg, type(arg))
        super().__init__(arg)


class TupleLike(Collection, _collabc.Sequence):

    _DEFERMETHS = ('__contains__', '__reversed__', 'index', 'count')

    _PYTYP = _collabc.Sequence


class DictLike(Collection, _collabc.Mapping):

    _DEFERMETHS = (
        '__contains__', 'keys', 'items',
        'values', 'get', '__eq__', '__ne__',
        )

    _PYTYP = _collabc.Mapping


###############################################################################
###############################################################################
