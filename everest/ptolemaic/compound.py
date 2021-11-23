###############################################################################
''''''
###############################################################################


from collections import abc as _collabc

from everest.ptolemaic.sprite import Sprite as _Sprite
from everest.ptolemaic.resourcers import Resourcer as _Resourcer
from everest.ptolemaic import collections as _collections
from everest.ptolemaic.intt import Intt as _Intt


class Compound(_Sprite):

    _ptolemaic_knowntypes__ = (_Sprite,)

    CONVERSIONS = {
        _Resourcer.can_convert: _Resourcer,
        int.__instancecheck__: _Intt,
        }

    class Registrar:

        def process_param(self, arg, /):
            for key, val in Compound.CONVERSIONS.items():
                if key(arg):
                    return val(arg)
            return arg

        def __call__(self, /, *args, **kwargs):
            proc = self.process_param
            super().__call__(
                *map(proc, args),
                **dict(zip(kwargs, map(proc, kwargs.values()))),
                )


class Tuuple(_collections.TupleLike, Compound):

    @classmethod
    def parameterise(cls, register, arg0, /, *argn):
        if argn:
            arg0 = (arg0, *argn)
        else:
            arg0 = tuple(arg0)
        super().parameterise(register, *arg0)

    def __init__(self, /, *args):
        super().__init__(args)


class Mapp(_collections.DictLike, Compound):

    @classmethod
    def parameterise(cls, register, /, *args, **kwargs):
        if kwargs:
            if args:
                raise ValueError
            dct = kwargs
        else:
            arg0, *argn = args
            if isinstance(arg0, _collabc.Mapping) and not argn:
                dct = dict(arg0)
            else:
                dct = dict((arg0, *argn))
        super().parameterise(register, tuple(dct), tuple(dct.values()))

    def __init__(self, keys, values, /):
        super().__init__(dict(zip(keys, values)))

    def __getattr__(self, name, /):
        if name in (obj := self._obj):
            return obj[name]
        return super().__getattr__(name)


Compound.CONVERSIONS.update({
    tuple.__instancecheck__: Tuuple,
    dict.__instancecheck__: Mapp,
    })


###############################################################################
###############################################################################
