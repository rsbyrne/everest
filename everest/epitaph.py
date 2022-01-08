###############################################################################
''''''
###############################################################################


import abc as _abc
import weakref as _weakref
import hashlib as _hashlib
import pickle as _pickle
import types as _types
# import typing as _typing
from importlib import import_module as _import_module
from inspect import getmodule as _getmodule
import itertools as _itertools
import functools as _functools
import collections as _collections
from collections import abc as _collabc
from string import Template as _Template

from everest.utilities import (
    caching as _caching, word as _word, classtools as _classtools,
    TypeMap as _TypeMap,
    )
from everest.primitive import Primitive as _Primitive


_Callable = _collabc.Callable


class EvalSpace(_collections.UserDict):

    def __init__(self, deps, dct, /):
        self.deps = deps
        super().__init__(dct)

    def __getitem__(self, key, /):
        if key in self:
            return super().__getitem__(key)
        return self.deps[key].decode()


class Epitaph(_classtools.Freezable):

    __slots__ = (
        'depdict', 'hexcode', 'content', 'taph', 'deps', 'args',
        '__weakref__', '_freezeattr', '_softcache',
        )

    def __init__(self, content, deps, hexcode, _process_content=False, /):
        depdict = self.depdict = _types.MappingProxyType({
            f"_{ind}":dep for ind, dep in enumerate(deps)
            })
        if _process_content:
            content = _Template(content).substitute(
                **{f"_{val}": key for key, val in depdict.items()}
                )
        self.hexcode = hexcode
        self.content = content
        self.taph = deps[0]
        self.deps = deps
        self.args = (self.content, self.deps, self.hexcode)
        self._softcache = dict()
        self.freezeattr = True

    @property
    def softcache(self, /):
        return self._softcache

    @property
    @_caching.soft_cache()
    def degenerate(self, /):
        return len() >= len(self.content)

    def __str__(self, /):
        return self.hexcode

    def __repr__(self, /):
        return f"<{self.__class__.__qualname__}({self.hexcode})>"

    def decode(self, /):
        evalspace = EvalSpace(self.depdict, self.taph.evalspace)
        return eval(self.content, {}, evalspace)

    def __lt__(self, other, /):
        return self.hexcode < other

    def __gt__(self, other, /):
        return self.hexcode > other

    def __reduce__(self, /):
        return self.taph, self.args

    @property
    @_caching.soft_cache()
    def hashint(self, /):
        return int(self.hexcode, 16)

    @property
    @_caching.soft_cache()
    def hashID(self, /):
        return _word.get_random_proper(2, seed=self.hexcode)


class Taphonomic(_abc.ABC):

    @classmethod
    def __subclasshook__(cls, C, /):
        if cls is Taphonomic:
            if hasattr(C, 'epitaph'):
                return True
        return NotImplemented


class Taphonomy(_classtools.Freezable, _weakref.WeakValueDictionary):
   
    __slots__ = (
        'encoders', 'decoders',
        '_primitivemeths', 'evalspace', '_softcache', 'namespace',
        '_freezeattr',
        )

    def __init__(self, namespace=None, /, **kwargs):
        if namespace is None:
            namespace = kwargs
        else:
            if kwargs:
                raise ValueError(
                    "Cannot pass namespace as both arg and kwargs."
                    )
        namespace = self.namespace = \
            _types.MappingProxyType(namespace)
        self.encoders = _TypeMap(self.yield_encoders())
        decoders = self.decoders = \
            _types.MappingProxyType(dict(self.yield_decoders()))
        self._primitivemeths = {
            self.encode_string, self.encode_primitive,
            self.encode_tuple, self.encode_dict,
            }
        self.evalspace = _collections.ChainMap(decoders, namespace)
        super().__init__()
        self._softcache = dict()
        self.freezeattr = True

    @property
    def softcache(self, /):
        return self._softcache

    def enfence(self, arg: str, /, directive=''):
        '''Wraps a string in a fence, optionally with a 'directive'.'''
        return f"{directive}({arg})"

    def encode_string(self, arg: str, /, *, subencode=None):
        return repr(arg)

    def encode_primitive(self, arg: _Primitive, /, *, subencode=None):
        return str(arg)

    def encode_tuple(self, arg: tuple, /, *, subencode: _Callable):
        content = ','.join(map(subencode, arg))
        if content:
            content += ','
        return f"({content})"

    def encode_dict(self, arg: dict, /, *, subencode: _Callable):
        pairs = zip(map(subencode, arg), map(subencode, arg.values()))
        return "{" + ','.join(map(':'.join, pairs)) + "}"

    def encode_mappingproxy(self,
            arg: _types.MappingProxyType, /, *, subencode: _Callable
            ):
        return self.enfence(self.encode_dict(arg, subencode=subencode), 'd')

#         return self.enfence(','.join(_itertools.starmap(
#             "({0},{1})".format,
#             zip(map(subencode, arg), map(subencode, arg.values()))
#             )), 'd')

    def encode_module(self, arg: _types.ModuleType, /, *, subencode=None):
        return self.enfence(repr(arg.__name__), 'm')

    _CONTENTTYPES = (
        type,
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
        mod = _getmodule(arg)
        if mod.__name__ == 'builtins':
            return arg.__name__
        return f"{self.encode_module(mod)}.{arg.__qualname__}"

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

#     def decode_dict(self:'d', /, *items) -> dict:
#         return dict(items)

    def decode_mappingproxy(self:'d', arg: dict, /) -> _types.MappingProxyType:
        return _types.MappingProxyType(arg)

    def decode_module(self:'m', name: str, /) -> _types.ModuleType:
        return _import_module(name)

    def decode_pickle(self:'p', arg: bytes, /) -> object:
        return _pickle.loads(arg)

    def yield_decoders(self, /):
        prefix = 'decode_'
        for attr in self.__class__.__dict__:
            if attr.startswith(prefix):
                meth = getattr(self, attr)
                yield meth.__annotations__['self'], meth

    def sub_part(self, deps, /):
        return _functools.partial(self.sub_encode, deps=deps)

    def sub_encode(self, arg: object, /, deps: set):
        if hasattr(arg, 'epitaph'):
            epitaph = arg.epitaph
            if isinstance(epitaph, Epitaph):
                deps.add(epitaph)
                return f"$_{epitaph}"
        meth = self.encoders[type(arg)]
        encoded = meth(arg, subencode=self.sub_part(subdeps:=set()))
        if subdeps:
            if len(encoded) <= 32:
                deps.update(subdeps)
                return encoded
            epitaph = self(encoded, subdeps)
            deps.add(epitaph)
            return f"$_{epitaph}"
        else:
            return encoded

    def encode(self, arg: object, /, deps: set) -> str:
        return self.encoders[type(arg)](arg, subencode=self.sub_part(deps))

    def _repr(self, /):
        kwargs = self.namespace
        substr = ','.join(map(
            '='.join,
            zip(map(repr, kwargs), map(repr, kwargs.values()))
            ))
        return f"{self.__class__.__qualname__}({substr})"

    @_caching.soft_cache()
    def __repr__(self, /):
        return self._repr()

    def get_hexcode(self, content: str, /) -> str:
        return _hashlib.sha3_256(
            (repr(self) + content).encode()
            ).hexdigest()

    def auto_epitaph(self, arg, /) -> Epitaph:
        return self(self.encode(arg, deps:=set()), deps)

    @classmethod
    def posformat_callsig(cls, caller, /, *args, **kwargs):
        n = 0
        count = _itertools.count(n+1)
        wrap = lambda it: (f"$_{next(count)}" for _ in it)
        strn = ','.join(_itertools.chain(
            wrap(args),
            map('='.join, zip(kwargs, wrap(kwargs))),
            ))
        deps = (caller, *args, *kwargs.values())
        keys = (f"_{n}" for n in range(len(deps)))
        return f"$_{n}({strn})", dict(zip(keys, deps))

    def custom_encode(self, strn: str, /, substitutions: dict, *, deps: set):
        sub = self.sub_part(deps)
        substitutions = dict(zip(
            substitutions,
            map(sub, substitutions.values())
            ))
        return _Template(strn).substitute(substitutions)

    def custom_epitaph(self, strn, /, **substitutions):
        deps = set()
        encoded = self.custom_encode(strn, substitutions, deps=deps)
        return self(encoded, deps)

    def callsig_epitaph(self, caller, /, *args, **kwargs):
        strn, subs = self.posformat_callsig(caller, *args, **kwargs)
        return self.custom_epitaph(strn, **subs)

    def __call__(self, content, deps=None, hexcode=None, /) -> Epitaph:
        if deps is None:
            if isinstance(content, Taphonomic):
                return content.epitaph
            return self.auto_epitaph(content)
        if hexnone := (hexcode is None):
            hexcode = self.get_hexcode(content)
        if hexcode in self:
            return self[hexcode]
        if hexnone:
            deps = (self, *sorted(deps))
        epitaph = Epitaph(content, deps, hexcode, hexnone)
        self[hexcode] = epitaph
        return epitaph

    def __reduce__(self, /):
        return self.__class__, (self.namespace.content,)


TAPHONOMY = Taphonomy()


def entomb(obj, /):
    return TAPHONOMY(obj)

def revive(content, deps, hexcode):
    return TAPHONOMY(content, deps, hexcode)


###############################################################################
###############################################################################
