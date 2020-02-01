import collections
import inspect
import numpy as np

from . import mpi

message = mpi.message

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

def get_default_kwargs(func):
    allargs = {
        key: val.default for key, val \
            in inspect.signature(func).parameters.items()
        }
    kwargs = {
        key: val for key, val \
            in allargs.items() if not val is inspect.Parameter.empty
        }
    return kwargs
