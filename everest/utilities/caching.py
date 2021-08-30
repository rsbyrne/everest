###############################################################################
''''''
###############################################################################


import os as _os
import pickle as _pickle
import functools as _functools
import inspect as _inspect
from collections import abc as _collabc

from .makehash import quick_hash as _quick_hash


def softcache(storage):
    if storage is None:
        store, retrieve = None, None
    else:
        store, retrieve = storage.__setitem__, storage.__getitem__
    def decorator(func):
        cachename = f"_softcache_{func.__name__}"
        parameters = _inspect.signature(func).parameters
        nonestorage = storage is None
        def wrapper(
                *args,
                cachename=cachename, storage=storage, func=func, **kwargs
                ):
            try:
                return storage[cachename]
            except KeyError:
                out = storage[cachename] = func(*args, **kwargs)
                return out
        if len(parameters) > (1 if nonestorage else 0):
            def wrapper(*args, storage=storage, func=wrapper, **kwargs):
                arghash = _quick_hash((args, tuple(kwargs.items())))
                cachename = f"{cachename}_{arghash}"
                return func(
                    *args,
                    storage=storage, cachename=cachename, **kwargs
                    )
        if nonestorage:
            def wrapper(arg0, *args, func=wrapper, **kwargs):
                try:
                    storage = arg0.__dict__['_softcache']
                except KeyError:
                    storage = arg0._softcache = dict()
                return func(arg0, *args, storage=storage, **kwargs)
        return _functools.wraps(func)(wrapper)
    return decorator


def hardcache(cachedir):
    def decorator(func):
        _os.makedirs(cachedir, exist_ok = True)
        path = _os.path.join(
            cachedir,
            f"hardcache_{func.__module__}_{func.__name__}"
            )
        @_functools.wraps(func)
        def wrapper(*args, refresh = False, cache = True, **kwargs):
            if args or kwargs:
                cachepath = f"{path}_{_quick_hash((args, tuple(kwargs.items())))}"
            else:
                cachepath = path
            if not refresh:
                try:
                    with open(cachepath, mode = 'rb') as file:
                        return _pickle.load(file)
                except FileNotFoundError:
                    pass
            out = func(*args, **kwargs)
            if cache:
                with open(cachepath, mode = 'wb') as file:
                    _pickle.dump(out, file)
            return out
        return wrapper
    return decorator


# def softcache_property(getfunc):
#     attname = getfunc.__name__.lstrip('get')
#     @property
#     @_wraps(getfunc)
#     def wrapper(self):
#         try:
#             return getattr(self, attname)
#         except AttributeError:
#             out = getfunc(self)
#             setattr(self, attname, out)
#             return out
#     return wrapper


###############################################################################
###############################################################################
