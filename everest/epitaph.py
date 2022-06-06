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

import numpy as _np

from everest.utilities import (
    word as _word, classtools as _classtools,
    TypeMap as _TypeMap,
    )
from everest import ur as _ur
from everest.armature import Armature as _Armature


_Callable = _collabc.Callable


class EvalSpace(_collections.UserDict):

    def __init__(self, deps, dct, /):
        self.deps = deps
        super().__init__(dct)

    def __getitem__(self, key, /):
        if key in self:
            return super().__getitem__(key)
        return self.deps[key].decode()


@_ur.Dat.register
class Epitaph(_classtools.Freezable):

    __slots__ = (
        'depdict', 'hexcode', 'content', 'taph', 'deps', 'args',
        '__weakref__', '_freezeattr', '_hashint', '_hashID',
        )

    def __init__(self, content, deps, hexcode, _process_content=False, /):
        depdict = self.depdict = _ur.DatDict({
            f"_{ind}":dep for ind, dep in enumerate(deps)
            })
        if _process_content and len(depdict) > 1:
            content = _Template(content).substitute(
                **{f"_{val}": key for key, val in depdict.items()}
                )
        self.hexcode = hexcode
        self.content = content
        self.taph = deps[0]
        self.deps = deps
        self.args = (self.content, self.deps, self.hexcode)
        self.freezeattr = True

    @property
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
    def hashint(self, /):
        try:
            return self._hashint
        except AttributeError:
            with self.mutable:
                out = self._hashint = int(self.hexcode, 16)
            return out

    @property
    def hashID(self, /):
        try:
            return self._hashID
        except AttributeError:
            with self.mutable:
                out = self._hashID = _word.get_random_proper(
                    2, seed=self.hexcode
                    )
            return out

    @property
    def __call__(self, /):
        return self.decode


class Epitaphable(_abc.ABC):

    @classmethod
    def __subclasshook__(cls, C, /):
        if cls is Epitaphable:
            if hasattr(C, 'epitaph'):
                return True
        return NotImplemented


class Taphonomy(_classtools.Freezable, _weakref.WeakValueDictionary):
   
    __slots__ = (
        'encoders', 'decoders',
        '_primitivemeths', 'evalspace', 'namespace',
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
        namespace = self.namespace = _ur.DatDict(namespace)
        self.encoders = _TypeMap(self.yield_encoders())
        decoders = self.decoders = _types.MappingProxyType(dict(
            self.yield_decoders()
            ))
        self._primitivemeths = {
            self.encode_string, self.encode_primitive,
            self.encode_tuple, self.encode_dict,
            }
        self.evalspace = _collections.ChainMap(decoders, namespace)
        super().__init__()
        self.freezeattr = True

    def enfence(self, arg: str, /, directive=''):
        '''Wraps a string in a fence, optionally with a 'directive'.'''
        return f"{directive}({arg})"

    def encode_module(self, arg: _types.ModuleType, /, *, deps: set = None):
        return self.enfence(repr(arg.__name__), 'm')

    def encode_pseudotype(self, arg: _ur.PseudoType, /, *, deps: set = None):
        return ''.join((
            self.encode_content(type(arg), deps=deps),
            self.encode_tuple(arg.args, deps=deps),
            ))

    _CONTENTTYPES = (
        type,
        _types.FunctionType,
        _types.MethodType,
        _types.BuiltinFunctionType,
        _types.BuiltinMethodType,
        )

    def encode_content(self, arg: _CONTENTTYPES, /, *, deps: set = None):
        '''
        Serialises 'content':
        objects that can be reached by qualname paths from a module.
        '''
        mod = _getmodule(arg)
        if mod.__name__ == 'builtins':
            return arg.__name__
        return f"{self.encode_module(mod)}.{arg.__qualname__}"

    def encode_string(self, arg: str, /, *, deps: set = None):
        return repr(arg)

    def encode_primitive(self, arg: _ur.Primitive, /, *, deps: set = None):
        return str(arg)

    def encode_dtuple(self, arg: _ur.DatTuple, /, *, deps: set = None):
        return 't' + self.encode_tuple(arg, deps=deps)

    def encode_tuple(self, arg: tuple, /, *, deps: set = None):
        if not arg:
            return '()'
        content =','.join(map(self.sub_part(deps), arg))
        if len(arg) == 1:
            content += ','
        return self.enfence(content)

    def encode_ddict(self, arg: _ur.DatDict, /, *, deps: set = None):
        return self.enfence(self.encode_dict(arg, deps=deps), 'd')

    def encode_dict(self, arg: dict, /, *, deps: set = None):
        pairs = zip(
            map(subencode, arg),
            map(self.sub_part(deps), arg.values()),
            )
        return "{" + ','.join(map(':'.join, pairs)) + "}"

    def encode_array(self, arg: _np.ndarray, /, *, deps: set = None):
        arg = _ur.DatArray(arg)
        content = f"{repr(bytes(arg._array))},{repr(str(arg.dtype))}"
        return self.enfence(content, 'a')

    def encode_armature(self, arg: _Armature, /, *, deps: set = None):
        typ = self.encode_content(arg.Base, deps=deps)
        content = self.encode_tuple(arg.params, deps)[1:-1]
        if not content:
            content = '()'
        return f"{typ}[{content}]"       

    def _encode_pickle(self,arg: object, /, *, deps: set = None) -> str:
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

    def decode_ddict(self:'d', arg: dict, /) -> _ur.DatDict:
        return _ur.DatDict(arg)

    def decode_dtuple(self:'t', /, *args: tuple) -> _ur.DatTuple:
        return _ur.DatTuple(args)

    def decode_array(self:'a', data: bytes, dtype: str, /) -> _ur.DatArray:
        return _ur.DatArray(data, dtype)

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

    def sub_encode(self, arg: object, /, deps: set = None):
        if hasattr(arg, 'epitaph'):
            epitaph = arg.epitaph
            if isinstance(epitaph, Epitaph):
                deps.add(epitaph)
                return f"$_{epitaph}"
        meth = self.encoders[type(arg)]
        encoded = meth(arg, deps=(subdeps:=set()))
        if subdeps:
            if len(encoded) <= 32:
                deps.update(subdeps)
                return encoded
            epitaph = self(encoded, subdeps)
            deps.add(epitaph)
            return f"$_{epitaph}"
        else:
            return encoded

    def encode(self, arg: object, /, deps: set = None) -> str:
        return self.encoders[type(arg)](arg, deps=deps)

    def __repr__(self, /):
        kwargs = self.namespace
        substr = ','.join(map(
            '='.join,
            zip(map(repr, kwargs), map(repr, kwargs.values()))
            ))
        return f"{self.__class__.__qualname__}({substr})"

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

    def getitem_epitaph(self, obj, arg, /):
        deps = set()
        if type(arg) is tuple:
            getstrn = self.encode_tuple(arg, deps=deps)
            if len(arg) > 0:
                getstrn = getstrn[1:-1]  # strip brackets
            if len(arg) == 1:
                getstrn += ','  # add trailing comma to form tuple
        else:
            getstrn = self.sub_encode(arg, deps)
        return self(f"{self.sub_encode(obj, deps)}[{getstrn}]", deps)

    def getattr_epitaph(self, obj, /, *args):
        deps = set()
        return self(f"{self.sub_encode(obj, deps)}.{'.'.join(args)}", deps)

    def __call__(
            self, content='None', deps=None, hexcode=None, /
            ) -> Epitaph:
        if deps is None:
            if isinstance(content, Epitaphable):
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
        return self.__class__, (dict(self.namespace),)


###############################################################################
###############################################################################
