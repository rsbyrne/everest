import collections

from . import mpi

def message(*args):
    for arg in args:
        if mpi.rank == 0:
            print(arg)

def unique_list(inList):
    return list(sorted(set(inList)))

def flatten(d, parent_key = '', sep = '_'):
    # by Imran@stackoverflow
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)
