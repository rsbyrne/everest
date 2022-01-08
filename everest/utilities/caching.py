###############################################################################
''''''
###############################################################################


import weakref as _weakref
import os as _os
import pickle as _pickle
import functools as _functools
import inspect as _inspect
from collections import abc as _collabc

from .makehash import quick_hash as _quick_hash


def soft_cache(storage='softcache', storetyp=dict):

    if not isinstance(storage, (str, _collabc.Collection)):
        raise TypeError("Storage must be str or Collection type.")

    def decorator(func, storage=storage):

#         cachename = f"_softcache_{func.__name__}"
        cachename = func.__name__
        sig = _inspect.signature(func)
        attrstorage = isinstance(storage, str)

        def wrapper(
                *args,
                cachename=cachename, storage=storage, func=func, **kwargs
                ):
            try:
                return storage[cachename]
            except KeyError:
                out = storage[cachename] = func(*args, **kwargs)
                return out

        if len(sig.parameters) > (1 if attrstorage else 0):

            def wrapper(
                    *args,
                    cachename=cachename, storage=storage, func=wrapper,
                    _sig=sig,
                    **kwargs
                    ):
                inps = _sig.bind(*args, **kwargs)
                inps.apply_defaults()
                cachename = f"{cachename}_{_quick_hash(repr(inps))}"
                return func(
                    *args,
                    storage=storage, cachename=cachename,
                    **kwargs
                    )

        if attrstorage:

            def wrapper(
                    arg0, *args,
                    func=wrapper, storage=storage, storetyp=storetyp,
                    **kwargs,
                    ):
                try:
                    storage = getattr(arg0, storage)
                except AttributeError:
                    setattr(arg0, storage, storage := storetyp())
                return func(arg0, *args, storage=storage, **kwargs)

        return _functools.wraps(func)(wrapper)

    return decorator


def weak_cache(storage='weakcache'):
    return soft_cache(storage, _weakref.WeakValueDictionary)


def hard_cache(cachedir, /, *subcaches):

    def decorator(func, /, subcaches=subcaches, cachedir=cachedir):

        _os.makedirs(cachedir, exist_ok = True)
        cachename = _os.path.join(
            cachedir,
            f"hardcache_{func.__module__}_{func.__name__}"
            )

        sig = _inspect.signature(func)

        def wrapper(
                *args,
                cachename=cachename, func=func, subcaches=subcaches,
                refresh=0, **kwargs,
                ):
#             deeprefresh = int(refresh) - 1
#             if deeprefresh > 0:
#                 for subcache in subcaches
            if not refresh:
                try:
                    with open(cachename, mode='rb') as file:
                        return _pickle.load(file)
                except FileNotFoundError:
                    pass
            out = func(*args, **kwargs)
            with open(cachename, mode='wb') as file:
                _pickle.dump(out, file)
            return out

        if sig.parameters:

            def wrapper(
                    *args,
                    _sig=sig, cachename=cachename, func=wrapper,
                    refresh=False, **kwargs
                    ):
                inps = _sig.bind(*args, **kwargs)
                inps.apply_defaults()
                cachename = f"{cachename}_{_quick_hash(repr(inps))}"
                return func(
                    *args,
                    cachename=cachename, refresh=refresh,
                    **kwargs
                    )

        return _functools.wraps(func)(wrapper)

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
