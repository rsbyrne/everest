###############################################################################
''''''
###############################################################################


import abc as _abc
import weakref as _weakref
import itertools as _itertools
from collections import deque as _deque, abc as _collabc
import functools as _functools
from importlib import import_module as _import_module
from inspect import getmodule as _getmodule
import types as _types
import re as _re
import hashlib as _hashlib

from everest.utilities import caching as _caching, word as _word
from everest.utilities import FrozenMap as _FrozenMap, TypeMap as _TypeMap
from everest.primitive import Primitive as _Primitive


class Epitaph:

    __slots__ = (
        'taphonomy', 'encoded', '_softcache',
#         '_weakcache',
        )

    def __init__(self, taphonomy, encoded, /):
        self.taphonomy = taphonomy
        self.encoded = encoded

#     @_caching.weak_cache()
    def decode(self, /) -> object:
        return self.taphonomy.decode(self.encoded)

    @property
    def obj(self, /):
        return self.decode()

    def get_hashcode(self):
        return _hashlib.md5(self.encoded.encode()).hexdigest()

    @property
    @_caching.soft_cache()
    def hashcode(self):
        return self.get_hashcode()

    @property
    @_caching.soft_cache()
    def hashint(self):
        return int(self.hashcode, 16)

    @property
    @_caching.soft_cache()
    def hashID(self):
        return _word.get_random_english(seed=self.hashint, n=2)

    def __str__(self, /):
        return self.encoded

    def __repr__(self, /):
        return f"<{self.__class__.__qualname__}({self.hashID})>"


class Taphonomic(_abc.ABC):

    def __init__(self, /):
        raise TypeError("Abstract class: should not be instantiated.")

    @classmethod
    def __subclasshook__(cls, C):
        if cls is Taphonomic:
            if any("epitaph" in B.__dict__ for B in C.__mro__):
                return True
        return NotImplemented


class Taphonomy:
    '''
    Defines and manages the Ptolemaic system's serialisation protocol.
    '''

    __slots__ = ('pretag', 'posttag', 'dirtag', 'encoders', 'decoders')

    def __init__(self, pretag='<', posttag='>', dirtag=':', /):
        self.pretag, self.posttag, self.dirtag = pretag, posttag, dirtag
        self.encoders = _TypeMap(self.yield_encoders())
        self.decoders = _FrozenMap(self.yield_decoders())
        super().__init__()

    def enfence(self, arg: str, /, directive=''):
        '''Wraps a string in a fence, optionally with a contained directive.'''
        return f"{self.pretag}{directive}{self.dirtag}{arg}{self.posttag}"

    def defence(self, arg: str, /):
        '''Removes the outermost fences from a string.'''
        return arg[1:(ind:=arg.index(':'))], arg[ind+1:-1]

    def encode_str(self, arg: str) -> str:
        return arg

    def encode_epitaph(self, arg: Epitaph) -> str:
        return str(arg)

    def encode_taphonomic(self, arg: Taphonomic) -> str:
        return self.encode_epitaph(arg.epitaph)

    def encode_primitive(self, arg: _Primitive) -> str:
        return repr(arg)

    _CONTENTTYPES = (
        type,
        _types.ModuleType,
        _types.FunctionType,
        _types.MethodType,
        _types.BuiltinFunctionType,
        _types.BuiltinMethodType,
        )

    def encode_content(self, arg: _CONTENTTYPES, /):
        '''
        Serialises 'content':
        objects that can be reached by qualname paths from a module.
        '''
        if isinstance(arg, _types.ModuleType):
            return f"'{arg.__name__}',"
        if arg.__module__ == 'builtins':
            return self.enfence(arg.__name__)
        arg0, arg1 = arg.__qualname__, _getmodule(arg).__name__
        return self.enfence(f"'{arg0}','{arg1}'", directive='c')

    def decode_content(self:'c', arg, /):
        '''
        Deserialises 'content':
        objects that can be reached by qualname paths from a module.
        '''
        name, path = arg
        return _functools.reduce(
            getattr,
            name.split('.'),
            _import_module(path)
            )

    def call_encode(self,
            caller: _collabc.Callable,
            args: _collabc.Sequence = (),
            kwargs: _collabc.Mapping = _FrozenMap(),
            /) -> object:
        return self.enfence(
            self.encode((caller, args, kwargs)),
            directive='f',
            )

    def decode_call(self:'f', arg: tuple):
        caller, args, kwargs = arg
        return caller(*args, **kwargs)

    def yield_encoders(self, /):
        prefix = 'encode_'
        for attr in self.__class__.__dict__:
            if attr.startswith(prefix):
                meth = getattr(self, attr)
                hint = meth.__annotations__['arg']
                yield hint, meth

    def yield_decoders(self, /):
        prefix = 'decode_'
        yield '', lambda x: x
        for attr in self.__class__.__dict__:
            if attr.startswith(prefix):
                meth = getattr(self, attr)
                yield meth.__annotations__['self'], meth

    def encode(self, arg, /):
        typ = type(arg)
        if typ is tuple:
            return '(' + ','.join(map(self.encode, arg)) + ')'
        if typ is dict:
            return '{' + ','.join(map(
                ':'.join,
                zip(map(self.encode, arg), map(self.encode, arg.values()))
                )) + '}'
        if hasattr(arg, '__module__'):
            if arg.__module__ == 'builtins':
                return arg.__name__
        meth = self.encoders[typ]
        return meth(arg)

    def unpack_fences(self, arg: str, /):
        '''Unpack nested fences as an iterable of level-content pairs.'''
        pretag, posttag = self.pretag, self.posttag
        start = pretag
        stack = _deque()
        for i, c in enumerate(arg):
            if c == pretag:
                stack.append(i)
            elif c == posttag and stack:
                start = stack.pop()
                yield (len(stack), arg[start: i+1])

    def replace_substrns(self, content, subs, /):
        for ashash, strn in subs:
            content = content.replace(strn, ashash)
        return content

    def hash_codestr(self, arg: str, /):
        return '_' + _hashlib.md5(arg.encode()).hexdigest()

    def recursive_decode(self, dct: dict, levelpairs, level=0, /):
        starti = 0
        results = _deque()
        for stopi, (lev, strn) in enumerate(levelpairs):
            if lev == level:
                ashash = self.hash_codestr(strn)
                if ashash not in dct:
                    directive, content = (
                        strn[1:(ind:=strn.index(self.dirtag))],
                        strn[ind+1:-1],
                        )
                    subs = self.recursive_decode(
                        dct,
                        levelpairs[starti:stopi],
                        level+1,
                        )
                    content = self.replace_substrns(content, subs)
                    meth = self.decoders[directive]
                    dct[ashash] = meth(eval(content, {}, dct))
                yield ashash, strn
                starti = stopi

    def decode(self, content: str, /):
        levelpairs = tuple(self.unpack_fences(content))
        subs = tuple(self.recursive_decode(dct:={}, levelpairs))
        content = self.replace_substrns(content, subs)
        return eval(content, {}, dct)

    def __call__(self, obj, /):
        return Epitaph(self, self.encode(obj))


TAPHONOMY = Taphonomy()


def entomb(obj, /, *, taphonomy=TAPHONOMY):
    return taphonomy(obj)


###############################################################################
###############################################################################
