###############################################################################
''''''
###############################################################################


import abc as _abc
import itertools as _itertools
from collections import deque as _deque
import functools as _functools
from importlib import import_module as _import_module
from inspect import getmodule as _getmodule
import types as _types
import re as _re
import hashlib as _hashlib

from everest.utilities import FrozenMap as _FrozenMap, TypeMap as _TypeMap
from everest.primitive import Primitive as _Primitive


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

    def decode_call(self:'m',
            caller: callable, args: tuple, kwargs: dict, /,
            ) -> object:
        return caller(*args, **kwargs)

    def yield_encoders(self, /):
        prefix = 'encode_'
        for attr in dir(self):
            if attr.startswith(prefix):
                meth = getattr(self, attr)
                hint = meth.__annotations__['arg']
                yield hint, meth

    def yield_decoders(self, /):
        prefix = 'decode_'
        yield '', lambda x: x
        for attr in dir(self):
            if attr.startswith(prefix):
                meth = getattr(self, attr)
                yield meth.__annotations__['self'], meth

    def encode(self, arg, /):
        typ = type(arg)
        if issubclass(typ, Taphonomic):
            return typ.epitaph().__str__()
        if issubclass(typ, Epitaph):
            return arg.__str__()
        if issubclass(typ, _Primitive):
            return repr(arg)
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
        return Epitaph(obj, taphonomy=self)


TAPHONOMY = Taphonomy()


class Epitaph:

    __slots__ = ('taphonomy', '_epi')

    def __init__(self, obj, /, *, taphonomy: Taphonomy = TAPHONOMY):
        self.taphonomy = taphonomy
        self._epi = taphonomy.encode(obj)

    def __str__(self, /):
        return self._epi

    def __repr__(self, /):
        return f"{self.__class__.__qualname__}({self})"

    def decode(self, /):
        return self.taphonomy.decode(self.__str__())


def entomb(obj, /, *, taphonomy=TAPHONOMY):
    return taphonomy(obj)


###############################################################################
###############################################################################
