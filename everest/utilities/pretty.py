###############################################################################
''''''
###############################################################################


import types as _types

import numpy as _np


def pretty(obj, p, cycle, root=''):
    try:
        meth = {
            dict: pretty_dict,
            _types.MappingProxyType: pretty_dict,
            tuple: pretty_tuple,
            _np.ndarray: pretty_array,
            _types.FunctionType: pretty_function,
            }[type(obj)]
    except KeyError:
        p.pretty(obj)
    else:
        meth(obj, p, cycle, root=root)


def pretty_function(obj, p, cycle, /, root=''):
    if root:
        raise ValueError
    p.text(obj.__module__)
    p.text('.')
    p.text(obj.__qualname__)


def pretty_kwargs(obj, p, cycle, /, root=''):
    if cycle:
        p.text(root + '(...)')
        return
    if not obj:
        p.text(root + '()')
        return
    with p.group(4, root + '(', ')'):
        kwargit = iter(obj.items())
        p.breakable()
        key, val = next(kwargit)
        p.text(key)
        p.text(' = ')
        pretty(val, p, cycle)
        p.text(',')
        for key, val in kwargit:
            p.breakable()
            p.text(key)
            p.text(' = ')
            pretty(val, p, cycle)
            p.text(',')
        p.breakable()


def pretty_argskwargs(obj, p, cycle, /, root=''):
    args, kwargs = obj
    if cycle:
        p.text(root + '(...)')
        return
    if not (args or kwargs):
        p.text(root + '()')
        return
    with p.group(4, root + '(', ')'):
        if args:
            for val in args:
                p.breakable()
                pretty(val, p, cycle)
                p.text(',')
        if kwargs:
            kwargit = iter(kwargs.items())
            p.breakable()
            key, val = next(kwargit)
            p.text(key)
            p.text(' = ')
            pretty(val, p, cycle)
            p.text(',')
            for key, val in kwargit:
                p.breakable()
                p.text(key)
                p.text(' = ')
                pretty(val, p, cycle)
                p.text(',')
        p.breakable()


def pretty_dict(obj, p, cycle, /, root=''):
    if cycle:
        p.text(root + '{...}')
        return
    if not obj:
        p.text(root + '{}')
        return
    with p.group(4, root + '{', '}'):
        kwargit = iter(obj.items())
        p.breakable()
        key, val = next(kwargit)
        pretty(key, p, cycle)
        p.text(': ')
        pretty(val, p, cycle)
        p.text(',')
        for key, val in kwargit:
            p.breakable()
            pretty(key, p, cycle)
            p.text(': ')
            pretty(val, p, cycle)
            p.text(',')
        p.breakable()


def pretty_array(data, p, cycle, /, root=''):
    if cycle:
        p.text(root + '{...}')
        return
    if not root:
        root = f"array(shape={data.shape}, dtype={data.dtype})"
    with p.group(4, root + '[', ']'):
        p.breakable()
        for row in _np.array2string(data, threshold=100)[:-1].split('\n'):
            p.text(row[1:])
            p.breakable()


def pretty_tuple(obj, p, cycle, /, root=''):
    if cycle:
        p.text(root + '(...)')
        return
    if not obj:
        p.text(root + '()')
        return
    with p.group(4, root + '(', ')'):
        for val in obj:
            p.breakable()
            pretty(val, p, cycle)
            p.text(',')
        p.breakable()


###############################################################################
###############################################################################
