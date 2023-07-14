###############################################################################
''''''
###############################################################################


import weakref as _weakref
import os as _os
import types as _types
import pickle as _pickle
import functools as _functools
import inspect as _inspect
from collections import abc as _collabc

from .makehash import quick_hash as _quick_hash


def soft_cache(storage='softcache', storetyp=dict):

    if isinstance(storage, _types.FunctionType):
        return soft_cache()(storage)

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

    if isinstance(cachedir, _types.FunctionType):
        return hard_cache()(cachedir)

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


def func_cache(arg=None):

    if isinstance(arg, _types.FunctionType):
        return func_cache()(arg)

    def decorator(func, /):

        if _inspect.signature(func).parameters:
            raise RuntimeError(
                "`func_cache` can only be used on functions with zero arguments."
                )

        @_functools.wraps(func)
        def wrapper():
            try:
                return func._value
            except AttributeError:
                _value = func._value = func()
                return _value

        return wrapper

    return decorator


def attr_cache(prefix=None, /, weak=False, dictlook=False):

    if isinstance(prefix, _types.FunctionType):
        return attr_cache()(prefix)
    elif prefix is None:
        prefix = '_cached'

    def decorator(func, /):

        if len(_inspect.signature(func).parameters) != 1:
            raise TypeError("Only functions of one argument can be attr-cached.")

        storedname = f"{prefix}_{func.__name__}"

        if weak:

            if dictlook:

                def wrapper(obj, /):
                    try:
                        ref = obj.__dict__[storedname]
                    except KeyError:
                        pass
                    else:
                        out = ref()
                        if out is not None:
                            return out
                    out = func(obj)
                    setattr(obj, storedname, _weakref.ref(out))
                    return out

            else:

                def wrapper(obj, /):
                    try:
                        ref = getattr(obj, storedname)
                    except AttributeError:
                        pass
                    else:
                        out = ref()
                        if out is not None:
                            return out
                    out = func(obj)
                    setattr(obj, storedname, _weakref.ref(out))
                    return out

        else:

            if dictlook:

                def wrapper(obj, /):
                    try:
                        return obj.__dict__[storedname]
                    except KeyError:
                        out = func(obj)
                        setattr(obj, storedname, out)
                        return out

            else:

                def wrapper(obj, /):
                    try:
                        return getattr(obj, storedname)
                    except AttributeError:
                        out = func(obj)
                        setattr(obj, storedname, out)
                        return out

        wrapper = _functools.wraps(func)(wrapper)
        wrapper.__attr_cache_storedname__ = storedname

        return wrapper

    return decorator


@_functools.wraps(attr_cache)
def attr_property(arg0=None, /, *args, **kwargs):
    if not (args or kwargs):
        if isinstance(arg0, _types.FunctionType):
            return attr_property()(arg0)
    return lambda x: property(attr_cache(arg0, *args, **kwargs)(x))


def dict_cache(prefix=None, /, weak=False):

    if isinstance(prefix, _types.FunctionType):
        return dict_cache()(prefix)
    elif prefix is None:
        prefix = '_cached'

    def decorator(func, /):

        if len(_inspect.signature(func).parameters) != 1:
            raise TypeError("Only functions of one argument can be attr-cached.")

        storedname = f"{prefix}_{func.__name__}"

        if weak:

            @_functools.wraps(func)
            def wrapper(obj, /):
                try:
                    ref = obj.__dict__[storedname]
                except AttributeError:
                    pass
                else:
                    out = ref()
                    if out is not None:
                        return out
                out = func(obj)
                setattr(obj, storedname, _weakref.ref(out))
                return out

        else:

            @_functools.wraps(func)
            def wrapper(obj, /):
                try:
                    return getattr(obj, storedname)
                except AttributeError:
                    out = func(obj)
                    setattr(obj, storedname, out)
                    return out

        wrapper.__attr_cache_storedname__ = storedname

        return wrapper

    return decorator


@_functools.wraps(attr_cache)
def dict_property(arg0=None, /, *args, **kwargs):
    if not (args or kwargs):
        if isinstance(arg0, _types.FunctionType):
            return dict_property()(arg0)
    return lambda x: property(dict_cache(arg0, *args, **kwargs)(x))


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
