################################################################################

from collections.abc import Sequence, Mapping, Collection

def construct_variable(*args, stack = False, **kwargs):
    from .scalar import Scalar
    from .array import Array
    from .stack import Stack
    if stack:
        return Stack(*args, **kwargs)
    totry = Scalar, Array
    errors = []
    for kind in totry:
        try:
            return kind(*args, **kwargs)
        except TypeError as e:
            errors.append(e)
    raise TypeError(errors)

def ordered_unpack(keys, arg1, arg2):
    keys = tuple(keys)
    if arg1 is Ellipsis:
        seqChoice = range(len(keys))
        mapChoice = keys
    elif type(arg1) is str:
        seqChoice = [keys.index(arg1),]
        mapChoice = [arg1,]
    elif type(arg1) is int:
        seqChoice = [arg1,]
        mapChoice = [keys[arg1],]
    elif type(arg1) is tuple:
        if len(set([type(o) for o in arg1])) > 1:
            raise ValueError
        if type(arg1[0]) is str:
            seqFn = lambda arg: keys.index(arg)
            seqChoice = [seqFn(arg) for arg in arg1]
            mapChoice = arg1
        elif type(arg1[0] is int):
            mapFn = lambda arg: keys[arg]
            seqChoice = arg1
            mapChoice = [mapFn(arg) for arg in arg1]
        else:
            raise TypeError
    if type(arg2) is tuple:
        out = dict((keys[i], arg2[i]) for i in seqChoice)
    elif isinstance(arg2, Mapping):
        out = dict((k, arg2[k]) for k in mapChoice)
    else:
        out = dict((keys[i], arg2) for i in seqChoice)
    if arg1 is Ellipsis and type(arg2) is tuple:
        if not len(arg2) == len(out):
            raise IndexError("Not enough arguments.")
    return out

################################################################################
