import numpy as np
import hashlib
from . import mpi
from . import wordhash

def message(*args):
    for arg in args:
        if mpi.rank == 0:
            print(arg)

def unique_list(inList):
    return list(sorted(set(inList)))
