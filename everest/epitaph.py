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
from collections import abc as _collabc

from everest.utilities import caching as _caching, word as _word
from everest.utilities import FrozenMap as _FrozenMap, TypeMap as _TypeMap
from everest.primitive import Primitive as _Primitive


_Callable = _collabc.Callable


class Epitaph:

    __slots__ = ('taphonomy', 'code', 'dependencies', '_str', '__weakref__')

    def __init__(self, taphonomy, code, dependencies=frozenset(), /):
        self.taphonomy = taphonomy
        self.code = code
        self.dependencies = frozenset(dependencies)
        _str = self._str = '_' + _hashlib.md5(code.encode()).hexdigest()
        taphonomy[_str] = self
        super().__init__()

    def __str__(self, /):
        return self._str

    def __repr__(self, /):
        return f"<{self.__class__.__qualname__}({self})>"

    def decode(self, /):
        return eval(self.code, {}, self.taphonomy)


class Encodable(_abc.ABC):

    @classmethod
    def __subclasshook__(cls, C, /):
        if cls is Encodable:
            if hasattr(C, 'encode'):
                return True
        return NotImplemented


class Taphonomy(_weakref.WeakValueDictionary):
   
    __slots__ = ('encoders', 'decoders')

    def __init__(self, /):
        self.encoders = _TypeMap(self.yield_encoders())
        self.decoders = _FrozenMap(self.yield_decoders())
        super().__init__()

    def enfence(self, arg: str, /, directive=''):
        '''Wraps a string in a fence, optionally with a contained directive.'''
        return f"{directive}({arg})"

    def encode_encodable(self, arg: Encodable, /, *, subencode: _Callable):
        return arg.encode()

    def encode_tuple(self, arg: tuple, /, *, subencode: _Callable):
        return ','.join(map(subencode, arg))

    def encode_dict(self, arg: dict, /, *, subencode: _Callable):
        return '{' + ','.join(map(
            ':'.join,
            zip(map(subencode, arg), map(subencode, arg.values()))
            )) + '}'

    def encode_str(self, arg: str, /, *, subencode: _Callable):
        return repr(arg)

    def encode_primitive(self, arg: _Primitive, /, *, subencode: _Callable):
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
        yield '', lambda x: x
        for attr in self.__class__.__dict__:
            if attr.startswith(prefix):
                meth = getattr(self, attr)
                yield meth.__annotations__['self'], meth

    def encode(self, arg, /, *, subencode: _Callable) -> str:
        if hasattr(arg, '__module__'):
            if arg.__module__ == 'builtins':
                return arg.__name__
        return self.encoders[type(arg)](arg, subencode=subencode)

    def sub_encode(self, deps: set, arg, /):
        out = self(arg)
        deps.add(out)
        return str(out)

    def __call__(self, arg, /, meth=None) -> Epitaph:
        deps = set()
        subencode = _functools.partial(self.sub_encode, deps)
        if meth is None:
            meth = self.encode
        elif isinstance(meth, str):
            meth = getattr(self, meth)
        return Epitaph(self, meth(arg, subencode=subencode), deps)

    def __getitem__(self, key, /):
        if key in (decoders := self.decoders):
            return decoders[key]
        return super().__getitem__(key).decode()

    def option_encode_call(self,
            arg: tuple[_Callable, _collabc.Sequence, _collabc.Mapping],
            /, *, subencode: _Callable
            ) -> str:
        caller, args, kwargs = arg
        return subencode(caller) + '(' + ','.join(_itertools.chain(
            map(subencode, args),
            map('='.join, zip(kwargs, map(subencode, kwargs.values()))),
            )) + ')'


TAPHONOMY = Taphonomy()


def entomb(obj, /, *, taphonomy=TAPHONOMY):
    return taphonomy(obj)


###############################################################################
###############################################################################


#     def unpack_fences(self, arg: str, /):
#         '''Unpack nested fences as an iterable of level-content pairs.'''
#         pretag, posttag = self.pretag, self.posttag
#         start = pretag
#         stack = _deque()
#         for i, c in enumerate(arg):
#             if c == pretag:
#                 stack.append(i)
#             elif c == posttag and stack:
#                 start = stack.pop()
#                 yield (len(stack), arg[start: i+1])

#     def replace_substrns(self, content, subs, /):
#         for ashash, strn in subs:
#             content = content.replace(strn, ashash)
#         return content

#     def recursive_decode(self, dct: dict, levelpairs, level=0, /):
#         starti = 0
#         results = _deque()
#         for stopi, (lev, strn) in enumerate(levelpairs):
#             if lev == level:
#                 ashash = self.hash_codestr(strn)
#                 if ashash not in dct:
#                     directive, content = (
#                         strn[1:(ind:=strn.index(self.dirtag))],
#                         strn[ind+1:-1],
#                         )
#                     subs = self.recursive_decode(
#                         dct,
#                         levelpairs[starti:stopi],
#                         level+1,
#                         )
#                     content = self.replace_substrns(content, subs)
#                     meth = self.decoders[directive]
#                     dct[ashash] = meth(eval(content, {}, dct))
#                 yield ashash, strn
#                 starti = stopi

#     def decode(self, content: str, /):
#         levelpairs = tuple(self.unpack_fences(content))
#         subs = tuple(self.recursive_decode(dct:={}, levelpairs))
#         content = self.replace_substrns(content, subs)
#         return eval(content, {}, dct)