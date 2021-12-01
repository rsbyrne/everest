###############################################################################
''''''
###############################################################################


import abc as _abc
import weakref as _weakref
import hashlib as _hashlib
import pickle as _pickle
import types as _types
from importlib import import_module as _import_module
from inspect import getmodule as _getmodule
import itertools as _itertools
import functools as _functools
import collections as _collections
from collections import abc as _collabc

from everest.utilities import caching as _caching, word as _word
from everest.utilities import FrozenMap as _FrozenMap, TypeMap as _TypeMap
from everest.primitive import Primitive as _Primitive


_Callable = _collabc.Callable


class EpitaphMeta(_abc.ABCMeta):

    def __call__(cls, taphonomy, code, deps=frozenset(), /):
        hashcode = '_' + _hashlib.md5(code.encode()).hexdigest()
        if hashcode in taphonomy:
            return taphonomy[hashcode]
        deps = tuple(sorted(deps))
        obj = super().__call__(taphonomy, code, deps, _str=hashcode)
        taphonomy[hashcode] = obj
        return obj


class EvalSpace(_collections.UserDict):

    def __init__(self, deps, dct, /):
        self.deps = deps
        super().__init__(dct)

    def __getitem__(self, key, /):
        if key in self:
            return super().__getitem__(key)
        return self.deps[key].decode()


class Epitaph(metaclass=EpitaphMeta):

    __slots__ = (
        'taphonomy', 'content', 'deps', '_str', '__weakref__'
        )

    @staticmethod
    def alt_depcode(dep):
        return '_' + str(dep)

    def __init__(self, taphonomy, content, deps, /, *, _str):
        self.taphonomy = taphonomy
        deps = self.deps = dict(zip(
            (f"_{ind}" for ind in range(len(deps))),
            deps,
            ))
        for key, val in deps.items():
            content = content.replace(str(val), key)
        self.content = content
        self._str = _str
        super().__init__()

    def __str__(self, /):
        return self._str

    def __repr__(self, /):
        return f"<{self.__class__.__qualname__}({self})>"

    def decode(self, /):
        return eval(
            self.content,
            {}, 
            EvalSpace(self.deps, self.taphonomy.evalspace),
            )

    def __lt__(self, other, /):
        return str(self) < other

    def __gt__(self, other, /):
        return str(self) < other


class Taphonomic(_abc.ABC):

    @classmethod
    def __subclasshook__(cls, C, /):
        if cls is Taphonomic:
            if hasattr(C, 'epitaph'):
                return True
        return NotImplemented


class Taphonomy(_weakref.WeakValueDictionary):
   
    __slots__ = (
        'encoders', 'variants', '_primitivemeths', 'evalspace',
        )

    def __init__(self, /, **namespace):
        self.encoders = _TypeMap(self.yield_encoders())
        decoders = _FrozenMap(self.yield_decoders())
        self.variants = _FrozenMap(self.yield_variants())
        self._primitivemeths = {
            self.encode_primitive, self.encode_tuple, self.encode_dict
            }
        self.evalspace = dict(_itertools.chain(
            self.yield_decoders(), namespace.items()
            ))
        super().__init__()

    def enfence(self, arg: str, /, directive=''):
        '''Wraps a string in a fence, optionally with a contained directive.'''
        return f"{directive}({arg})"

    def encode_tuple(self, arg: tuple, /, *, subencode: _Callable):
        return '(' + ','.join(map(subencode, arg)) + ')'

    def encode_dict(self, arg: dict, /, *, subencode: _Callable):
        return '{' + ','.join(map(
            ':'.join,
            zip(map(subencode, arg), map(subencode, arg.values()))
            )) + '}'

    def encode_primitive(self, arg: _Primitive, /, *, subencode=None):
        if isinstance(arg, str):
            return repr(arg)
        return str(arg)

    _CONTENTTYPES = (
        type,
        _types.ModuleType,
        _types.FunctionType,
        _types.MethodType,
        _types.BuiltinFunctionType,
        _types.BuiltinMethodType,
        )

    def encode_content(self,
            arg: _CONTENTTYPES, /, *, subencode: _Callable
            ):
        '''
        Serialises 'content':
        objects that can be reached by qualname paths from a module.
        '''
        if isinstance(arg, _types.ModuleType):
            return f"'{arg.__name__}',"
        if arg.__module__ == 'builtins':
            return self.enfence(arg.__name__)
        modname = _getmodule(arg).__name__
        if modname == 'builtins':
            return arg.__name__
        return self.enfence(f"'{arg.__qualname__}','{modname}'", 'c')

    def _encode_pickle(self,
            arg: object, /, *, subencode: _Callable
            ) -> str:
        return self.enfence(_pickle.dumps(arg), 'p')

    @property
    def _encode_fallback(self, /):
        return self._encode_pickle

    def yield_encoders(self, /):
        prefix = 'encode_'
        for attr in self.__class__.__dict__:
            if attr.startswith(prefix):
                meth = getattr(self, attr)
                hint = meth.__annotations__['arg']
                yield hint, meth
        yield object, self._encode_fallback

    def decode_content(self:'c', name: str, path: str, /):
        '''
        Deserialises 'content':
        objects that can be reached by qualname paths from a module.
        '''
        return _functools.reduce(
            getattr,
            name.split('.'),
            _import_module(path)
            )

    def decode_pickle(self:'p', arg: bytes, /) -> object:
        return _pickle.loads(arg)

    def yield_decoders(self, /):
        prefix = 'decode_'
        for attr in self.__class__.__dict__:
            if attr.startswith(prefix):
                meth = getattr(self, attr)
                yield meth.__annotations__['self'], meth

    def variant_call(self,
            arg: tuple[_Callable, _collabc.Sequence, _collabc.Mapping],
            /, *, subencode: _Callable
            ) -> str:
        caller, args, kwargs = arg
        return subencode(caller) + '(' + ','.join(_itertools.chain(
            map(subencode, args),
            map('='.join, zip(kwargs, map(subencode, kwargs.values()))),
            )) + ')'

    def yield_variants(self, /):
        prefix = 'variant_'
        for attr in self.__class__.__dict__:
            if attr.startswith(prefix):
                yield attr.removeprefix(prefix), getattr(self, attr)

    def encode(self, deps: set, arg: object, /, meth=None) -> str:
        subencode = _functools.partial(self.sub_encode, deps)
        if meth is None:
            meth = self.encoders[type(arg)]
        else:
            meth = getattr(self, meth)
        return meth(arg, subencode=subencode)

    def sub_encode(self, deps: set, arg: object, /):
        if isinstance(arg, Taphonomic):
            epitaph = arg.epitaph
        else:
            meth = self.encoders[type(arg)]
            if meth in self._primitivemeths:
                subencode = _functools.partial(self.sub_encode, deps)
                return meth(arg, subencode=subencode)
            subencode = _functools.partial(self.sub_encode, subdeps:=set())
            encoded = meth(arg, subencode=subencode)
            epitaph = Epitaph(self, encoded, subdeps)
        deps.add(epitaph)
        return str(epitaph)

    def get_epitaph(self, arg, /, meth=None) -> Epitaph:
        return Epitaph(self, self.encode(deps:=set(), arg, meth), deps)

    def __call__(self, arg, /, meth=None) -> Epitaph:
        if isinstance(arg, Taphonomic):
            return arg.epitaph
        return self.get_epitaph(arg, meth)

    def decode(self, /):
        return eval(
            self.content,
            {}, 
            EvalSpace(self, self.taphonomy.evalspace),
            )


TAPHONOMY = Taphonomy()


def get_epitaph(obj, /, *, taphonomy=TAPHONOMY):
    return taphonomy(obj)


###############################################################################
###############################################################################
