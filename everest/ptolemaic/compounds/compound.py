###############################################################################
''''''
###############################################################################


from collections import abc as _collabc

from everest import utilities as _utilities

# from .pleroma import Pleroma as _Pleroma
# from .essence import Essence as _Essence
# from .ousia import Ousia as _Ousia
from everest.ptolemaic.shades.shade import Shade as _Shade
from everest.ptolemaic.sprites.sprite import Sprite as _Sprite


class Compound(_Sprite):

    _ptolemaic_knowntypes__ = (_Sprite,)

    class Registrar:

        def process_param(self, arg, /):
            if isinstance(arg, tuple):
                return Tuuple(*arg)
            if isinstance(arg, dict):
                return Mapp(**arg)
            return arg

        def __call__(self, /, *args, **kwargs):
            proc = self.process_param
            super().__call__(
                *map(proc, args),
                **dict(zip(kwargs, map(proc, kwargs.values()))),
                )


class Proxy(_Shade):

    _ptolemaic_mergetuples__ = ('defermeths',)
    defermeths = ()

    _req_slots__ = ('_obj',)

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        for meth in cls.defermeths:
            _utilities.classtools.add_defer_meth(cls, meth, '_obj')


class ProxyCollection(Proxy, _collabc.Sequence):

    defermeths = ('__getitem__', '__len__', '__iter__')


class Tuuple(ProxyCollection, Compound, _collabc.Sequence):

    defermeths = ('__contains__', '__reversed__', 'index', 'count')

    def __init__(self, /, *args):
        self._obj = args

    def _repr(self, /):
        return ', '.join(map(repr, self._obj))


class Mapp(ProxyCollection, Compound, _collabc.Mapping):

    defermeths = (
        '__contains__', 'keys', 'items',
        'values', 'get', '__eq__', '__ne__',
        )

    def __init__(self, /, **kwargs):
        self._obj = kwargs

    def __getattr__(self, name):
        if name in (obj := self._obj):
            return obj[name]
        return super().__getattr__(name)

    def _repr(self, /):
        return ', '.join(
            '='.join((pair[0], repr(pair[1])))
            for pair in self._obj.items()
            )


###############################################################################
###############################################################################
