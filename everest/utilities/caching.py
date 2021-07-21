###############################################################################
''''''
###############################################################################


import os as _os
import pickle as _pickle
from functools import wraps as _wraps

from .makehash import quick_hash as _quick_hash


def softcache(propname):
    cachename = f'_{propname}'
    getfuncname = f'get_{propname}'
    @property
    def wrapper(self):
        try:
            return getattr(self, cachename)
        except AttributeError:
            getfunc = getattr(self, getfuncname)
            out = getfunc()
            setattr(self, cachename, out)
            return out
    return wrapper

def hard_cache(cachedir):
    def decorator(func):
        _os.makedirs(cachedir, exist_ok = True)
        path = _os.path.join(
            cachedir,
            f"hardcache_{func.__module__}_{func.__name__}"
            )
        @_wraps(func)
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
