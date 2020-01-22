import collections
import inspect
import numpy as np

from . import mpi

def message(*args):
    for arg in args:
        if mpi.rank == 0:
            print(arg)

def _obtain_dtype(object):
    if type(object) == np.ndarray:
        dtype = object.dtype
    else:
        dtype = type(object)
    return dtype

def unique_list(inList):
    return list(sorted(set(inList)))

def flatten(d, parent_key = '', sep = '_'):
    # by Imran@stackoverflow
    items = []
    parent_key = parent_key.strip(sep)
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten(v, new_key, sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

def get_default_args(func):
    # only works with kwargs
    argspec = inspect.getfullargspec(func)
    argspec.args.remove('self')
    defaultInps = {
        key: val \
            for key, val \
                in zip(
                    argspec.args,
                    argspec.defaults
                    )
        }
    return defaultInps
