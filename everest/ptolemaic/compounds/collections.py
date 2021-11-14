###############################################################################
''''''
###############################################################################


from collections import abc as _collabc

from everest.ptolemaic.shades.deferrer import \
    DeferrerClass as _DeferrerClass
from everest.ptolemaic.compounds.compound import Compound as _Compound


class Collection(_DeferrerClass, _collabc.Sequence):

    defermeths = ('__getitem__', '__len__', '__iter__')


class Tuuple(Collection, _Compound, _collabc.Sequence):

    defermeths = ('__contains__', '__reversed__', 'index', 'count')

    @classmethod
    def parameterise(cls, register, arg0, /, *argn):
        if argn:
            arg0 = (arg0, *argn)
        else:
            arg0 = tuple(arg0)
        super().parameterise(register, *arg0)

    def __init__(self, /, *args):
        super().__init__(args)


class Mapp(Collection, _Compound, _collabc.Mapping):

    defermeths = (
        '__contains__', 'keys', 'items',
        'values', 'get', '__eq__', '__ne__',
        )

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


_Compound.conversions.update({
    tuple.__instancecheck__: Tuuple,
    dict.__instancecheck__: Mapp,
    })


###############################################################################
###############################################################################
