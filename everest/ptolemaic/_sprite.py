###############################################################################
''''''
###############################################################################


import hashlib as _hashlib
import itertools as _itertools
import pickle as _pickle
import inspect as _inspect
from collections import abc as _collabc

from everest.utilities.classtools import add_defer_meths as _add_defer_meths

from everest.ptolemaic.ousia import Ousia as _Ousia
from everest.ptolemaic.aspect import Aspect as _Aspect
from everest.ptolemaic.primitive import Primitive as _Primitive
from everest.ptolemaic.chora import Sliceable as _Sliceable


class Sprite(metaclass=_Ousia):

    _ptolemaic_knowntypes__ = (_Primitive,)


class ByteWrap(_Aspect):

    _req_slots__ = ('content', '_getitem')

    def __init__(self, data: bytes, /):
        content = self.content = _pickle.loads(data)
        self._getitem = content.__getitem__
        super().__init__()

    def _repr(self, /):
        return repr(self.content)[1:-1]


@_add_defer_meths(
    'content',
    '__iter__', '__len__', 'index', 'count',
    )
class Tuuple(ByteWrap, Sprite):
  
    @classmethod
    def parameterise(cls, register, arg: _collabc.Iterable, /):
        if not isinstance(arg, bytes):
            arg = _pickle.dumps(tuple(register.process_params(arg)))
        register(arg)

    def __getitem__(self, arg, /):
        out = self._getitem(arg)
        if isinstance(arg, slice):
            return self.construct(out)
        return out


@_add_defer_meths(
    'content',
    '__iter__', '__len__', 'index', 'count',
    )
class Mapp(ByteWrap, Sprite):
  
    @classmethod
    def parameterise(cls, register, arg: _collabc.Iterable, /):
        if not isinstance(arg, bytes):
            arg = dict(arg)
            arg = _pickle.dumps(dict(zip(
                register.process_params(arg),
                register.process_params(arg.values()),
                )))
        register(arg)

    def __getitem__(self, arg, /):
        out = self._getitem(arg)
        if isinstance(arg, slice):
            return self.construct(out)
        return out


###############################################################################
###############################################################################
