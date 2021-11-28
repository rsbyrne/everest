###############################################################################
''''''
###############################################################################


from collections import deque as _deque
import functools as _functools
from importlib import import_module as _import_module
from inspect import getmodule as _getmodule
import types as _types
import re as _re

from everest.utilities import FrozenMap as _FrozenMap, TypeMap as _TypeMap


class _Epitaph_:

    @classmethod
    def __class_init__(cls, /):
        pass

    @classmethod
    def __init_subclass__(cls, /, **kwargs):
        super().__init_subclass__()
        cls.__class_init__()


class Epitaph(_Epitaph_):
    '''
    Defines and manages the Ptolemaic system's serialisation protocol.
    '''

    PRETAG = '<{0}:'
    POSTTAG = '>'
    PREPATTERN = _re.compile(PRETAG.format(r'\w*') + '$', flags=_re.A)
    POSTPATTERN = _re.compile(POSTTAG + '$', flags=_re.A)
    FULLPATTERN = _re.compile(
        PRETAG.format(r'\w*') + '.*' + POSTTAG,
        flags=_re.A,
        )

    @classmethod
    def enfence(cls, arg: str, /, directive=''):
        '''Wraps a string in a fence, optionally with a contained directive.'''
        return f"{cls.PRETAG.format(directive)}{arg}{cls.POSTTAG}"

    @classmethod
    def defence(cls, arg: str, /):
        '''Removes the outermost fences from a string.'''
        return arg[1:(ind:=arg.index(':'))], arg[ind+1:-1]

    @classmethod
    def _encode_t(cls, arg: tuple, /) -> str:
        return ''.join(map(cls.encode, arg))

    @classmethod
    def _decode_t(cls, /, *args) -> tuple:
        return args

    @classmethod
    def _encode_d(cls, arg: dict, /) -> str:
        return ''.join(map(cls.encode, arg.items()))

    @classmethod
    def _decode_d(cls, /, *pairs) -> dict:
        print(pairs)
        return dict(pairs)

    @classmethod
    def _encode_m(cls, arg: _types.ModuleType, /) -> str:
        '''Serialises module objects.'''
        return arg.__name__

    @classmethod
    def _decode_m(cls, arg: str, /):
        '''Deserialises module objects.'''
        return _import_module(arg)

    _CONTENTTYPES = (
        type,
        _types.FunctionType,
        _types.MethodType,
        _types.BuiltinFunctionType,
        _types.BuiltinMethodType,
        )

    @classmethod
    def _encode_c(cls, arg: _CONTENTTYPES, /) -> str:
        '''
        Serialises 'content':
        objects that can be reached by qualname paths from a module.
        '''
        arg0, arg1 = arg.__qualname__, _getmodule(arg).__name__
        return f"{arg0};{arg1}"

    @classmethod
    def _decode_c(cls, arg, /):
        '''
        Deserialises 'content':
        objects that can be reached by qualname paths from a module.
        '''
        name, path = arg.split(';')
        return _functools.reduce(
            getattr,
            name.split('.'),
            _import_module(path)
            )

    @classmethod
    def _encode_(cls, arg: object, /) -> str:
        return repr(arg)

    @classmethod
    def _decode_(cls, arg, /) -> object:
        return eval(arg)

    @classmethod
    def yield_encoders(cls, /):
        prefix = '_encode_'
        for attr in dir(cls):
            if attr.startswith(prefix):
                if attr == prefix:
                    continue
                meth = getattr(cls, attr)
                yield meth.__annotations__['arg'], meth
        yield object, cls._encode_

    @classmethod
    def yield_decoders(cls, /):
        prefix = '_decode_'
        for attr in dir(cls):
            if attr.startswith(prefix):
                if attr == prefix:
                    continue
                meth = getattr(cls, attr)
                yield attr.removeprefix(prefix), meth
        yield '', cls._decode_

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        cls.encoders = _TypeMap(cls.yield_encoders())
        cls.decoders = _FrozenMap(cls.yield_decoders())

    @classmethod
    def encode(cls, arg, /):
        meth = cls.encoders[type(arg)]
        methcode = meth.__name__.removeprefix('_encode_')
        arg = meth(arg)
        return cls.enfence(arg, directive=methcode)

    @classmethod
    def unpack_fences(cls, arg: str, /):
        '''Unpack nested fences as an iterable of level-content pairs.'''
        start, stop = cls.PRETAG[0], cls.POSTTAG[-1]
        stack = _deque()
        for i, c in enumerate(arg):
            if c == '<':
                stack.append(i)
            elif c == '>' and stack:
                start = stack.pop()
                yield (len(stack), arg[start + 1: i])

    @classmethod
    def unpack_pairs(cls, levelpairs, level=0, /):
        starti = 0
        results = _deque()
        for stopi, (lev, strn) in enumerate(levelpairs):
            if lev == level:
                directive, content = strn[:(ind:=strn.index(':'))], strn[ind+1:]
                args = cls.unpack_pairs(levelpairs[starti:stopi], level+1)
                results.append((directive, args if args else content))
                starti = stopi
        return tuple(results)

    @classmethod
    def decode_pair(cls, pair: tuple, /):
        directive, content = pair
        decoder = cls.decoders[directive]
        if isinstance(content, tuple):
            return decoder(*map(cls.decode_pair, content))
        return decoder(content)

    @classmethod
    def decode(cls, arg: str, /):
        toppair = cls.unpack_pairs(tuple(cls.unpack_fences(arg)))[0]
        return cls.decode_pair(toppair)



#     @classmethod
#     def decode_import

#     @classmethod
#     def decode

###############################################################################
###############################################################################
