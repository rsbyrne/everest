import math
import numpy as np

def is_numeric(arg):
    try:
        _ = arg + 1
        return True
    except:
        return False

from collections import OrderedDict
from collections.abc import Sequence, Mapping

def ordered_unpack(keys, arg1, arg2):
    keys = list(keys)
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
    if isinstance(arg2, Sequence):
        mapDict = OrderedDict((keys[i], arg2[i]) for i in seqChoice)
    elif isinstance(arg2, Mapping):
        mapDict = OrderedDict((k, arg2[k]) for k in mapChoice)
    else:
        mapDict = OrderedDict((keys[i], arg2) for i in seqChoice)
    return mapDict
