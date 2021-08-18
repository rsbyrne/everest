###############################################################################
'''Generally useful code snippets.'''
###############################################################################


from abc import ABC as _ABC
from collections import abc as _collabc
import collections as _collections
import itertools as _itertools
import functools as _functools
import operator as _operator
import os as _os
import random as _random

import numpy as _np


RICHOPS = ('lt', 'le', 'eq', 'ne', 'ge', 'gt')
BOOLOPS = ('not', 'truth', 'is', 'is_not',)
ARITHMOPS = (
    'abs', 'add', 'and', 'floordiv', 'index', 'inv',
    'lshift', 'mod', 'mul', 'matmul', 'neg', 'or',
    'pos', 'pow', 'rshift', 'sub', 'truediv', 'xor'
    )
REVOPS = (
    'radd', 'rand', 'rfloordiv', 'rlshift', 'rmod', 'rmul',
    'rmatmul', 'ror', 'rpow', 'rrshift', 'rsub', 'rtruediv',
    'rxor',
    )
SEQOPS = ('concat', 'contains', 'countOf', 'indexOf', )
ALLOPS = (*RICHOPS, *BOOLOPS, *ARITHMOPS, *SEQOPS)


def unpackable(obj):
    return all(
        isinstance(obj, _collabc.Iterable),
        not isinstance(obj, _collabc.Collection),
        )


def unpacker_zip(arg1, arg2, /):
    arg1map, arg2map = (
        isinstance(arg, _collabc.Mapping)
            for arg in (arg1, arg2)
        )
    if arg1map and arg2map:
        arg1, arg2 = zip(*((arg1[k], arg2[k]) for k in arg1 if k in arg2))
        arg1, arg2 = iter(arg1), iter(arg2)
    elif arg1map:
        arg1 = arg1.values()
    elif arg2map:
        arg2 = arg2.values()
    if unpackable(arg1):
        if not unpackable(arg2):
            arg2 = _itertools.repeat(arg2)
        for sub1, sub2 in zip(arg1, arg2):
            yield from unpacker_zip(sub1, sub2)
    else:
        yield arg1, arg2

def kwargstr(**kwargs):
    outs = []
    for key, val in sorted(kwargs.items()):
        if not type(val) is str:
            try:
                val = val.namestr
            except AttributeError:
                try:
                    val = val.__name__
                except AttributeError:
                    val = str(val)
        outs.append(': '.join((key, val)))
    return '{' + ', '.join(outs) + '}'

def process_scalar(scal):
    return scal.dtype.type(scal)

def add_headers(path, header = '#' * 80, footer = '#' * 80, ext = '.py'):
    path = _os.path.abspath(path)
    for filename in _os.listdir(path):
        subPath = _os.path.join(path, filename)
        if _os.path.isdir(subPath):
            add_headers(subPath)
        filename, extension = _os.path.splitext(filename)
        if extension == ext:
            with open(subPath, mode = 'r+') as file:
                content = file.read()
                file.seek(0, 0)
                if not content.strip('\n').startswith(header):
                    content = f"{header}\n\n{content}"
                if not content.strip('\n').endswith(footer):
                    content = f"{content}\n\n{footer}\n"
                file.write(content)


def unpack_criterion(criterion):
    if isinstance(criterion, tuple):
        return criterion
    elif isinstance(criterion, list):
        yield from unpack_criterion(*criterion)
    else:
        if not callable(criterion):
            raise TypeError("Criteria must be callable.")
        yield criterion


def process_criterion(criterion):
    if isinstance(criterion, _collabc.Iterable):
        if not (istup := isinstance(criterion, tuple)):
            criteria = unpack_criterion(criterion)
        criteria = tuple(map(process_criterion, criterion))
        if (ncrit := len(criteria)) == 0:
            raise ValueError
        if ncrit == 1:
            criterion = criteria[0]
        elif istup:
            def criterion(args, /, *, funcs=criteria):
                return all(
                    func(arg)
                    for func, arg in _itertools.zip_longest(funcs, args)
                    )
        else:
            def criterion(arg, /, *, funcs=criteria):
                return all(
                    func(arg)
                    for func in funcs
                    )
    elif isinstance(criterion, type):
        def criterion(arg, argtyp=criterion, /):
            return isinstance(arg, argtyp)
    elif not callable(criterion):
        raise TypeError(criterion)
    return criterion


def process_criteria(*criteria):
    func = process_criterion(criteria)
    def criterion(*args, func=func):
        return func(args)
    return criterion


class FrozenMap(_collabc.Mapping):

    def __init__(self, *args, defertos=(), **kwargs):
        content = dict(*args, **kwargs)
        self.content = dict(zip(
            map(self.process_key, content),
            content.values()
            ))
        self.defertos = tuple(defertos)

    @classmethod
    def process_key(cls, key):
        return key

    @classmethod
    def process_req(cls, req):
        return req

    def __getitem__(self, name):
        try:
            return self.content.__getitem__(self.process_req(name))
        except KeyError:
            return self._getitem_deferred(name)

    def __len__(self):
        return len(self.content) + sum(map(len, self.defertos))

    def __iter__(self):
        return _itertools.chain(
            self.content,
            _itertools.chain(*self.defertos)
            )

    def merge(self):
        return _functools.reduce(
            _operator.__or__,
            (self.content, *self.defertos)
            )

    @property
    def __or__(self):
        return self.merge().__or__

    def _getitem_deferred(self, key):
        for deferto in self.defertos:
            try:
                return deferto[key]
            except KeyError:
                continue
        raise KeyError(key)

    def __repr__(self):
        return (
            f"{type(self).__name__}(len=={len(self)})"
            + repr(self.content)
            )

    def __hash__(self):
        try:
            return self._hashint
        except AttributeError:
            hashint = self._hashint = _random.randint(
                int(1e12),
                int(1e13) - 1
                )
            return hashint


class BoolMap(FrozenMap):

    @classmethod
    def process_key(cls, key):
        if not isinstance(key, tuple):
            key = (key,)
        return process_criteria(*key)

    def __getitem__(self, req):
        if not isinstance(req, tuple):
            req = (req,)
        for dkey, dval in self.items():
            if dkey(*req):
                return dval
        return self._getitem_deferred(req)

    @property
    def items(self):
        return self.content.items

    def __contains__(self, req):
        try:
            _ = self[req]
            return True
        except KeyError:
            return False


class TypeMap(BoolMap):

    @classmethod
    def process_key(cls, key):
        def keyfunc(arg, /, *, key=key):
            return issubclass(arg, key)
        return keyfunc

    @_functools.lru_cache
    def __getitem__(self, req):
        return super().__getitem__(req)

    @_functools.lru_cache
    def __contains__(self, key):
        return super().__getitem__(req)


class MultiTypeMap(TypeMap):

    @classmethod
    def process_key(cls, key):
        if isinstance(key, tuple):
            def keyfunc(*args, keys=key):
                return all(map(issubclass, args, keys))
            return keyfunc
        return super().process_key(key)


class SliceLike(_ABC):
    ...
_ = SliceLike.register(slice)

class Slyce:

    __slots__ = (
        'start', 'stop', 'step',
        'slc', 'args', 'hasargs',
        'trueargs',
        )

    def __init__(self, start = None, stop = None, step = None, /):
        args = self.args = self.start, self.stop, self.step = \
            start, stop, step
        hasargs = self.hasargs = tuple(x is not None for x in args)
        self.trueargs = tuple(_itertools.compress(args, hasargs))
        self.slc = slice(start, stop, step)

    def __iter__(self):
        return iter(self.args)

    def __len__(self):
        return 3

    def __getitem__(self, arg):
        return self.args[arg]

    def __repr__(self):
        return f"Slyce({self.start}, {self.stop}, {self.step})"

_ = SliceLike.register(Slyce)

def slyce(arg, *args):
    if isinstance(arg, slice) and not args:
        return Slyce(arg.start, arg.stop, arg.step)
    return Slyce(arg, *args)


# def inject_extra_init(cls, func):
#     cls.__init__ = 
#     old_init = cls.__init__
#     def extra_init(self, *args, **kwargs):
#         args, kwargs = func(self, old_init, *args, **kwargs)
#     cls.__init__ = extra_init


# def delim_split(seq, /, sep = ...):
#     g = []
#     for el in seq:
#         if el == sep:
#             if g:
#                 if not (len(g) == 1 and g[0] == sep):
#                     yield tuple(g)
#             g.clear()
#         g.append(el)
#     if g:
#         if not (len(g) == 1 and g[0] == sep):
#             yield tuple(g)

###############################################################################
###############################################################################
