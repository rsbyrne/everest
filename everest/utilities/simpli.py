###############################################################################
''''''
###############################################################################


import sys as _sys
import os as _os
import pickle as _pickle
from functools import wraps as _wraps

from mpi4py import MPI

from .import exceptions as _exceptions


class SimpliError(_exceptions.UtilitiesException):
    '''Something went wrong with an MPI thing.'''
    pass
class SubMPIError(SimpliError):
    '''Something went wrong inside an MPI block.'''
    pass
class MPIPlaceholderError(SimpliError):
    '''An MPI broadcast operation failed.'''
    pass


COMM = MPI.COMM_WORLD
RANK = COMM.Get_rank()
SIZE = COMM.Get_size()
DOWRAPPED = False


def message(*args, **kwargs):
    COMM.barrier()
    if RANK == 0:
        print(*[*args, *kwargs.items()])
    COMM.barrier()

def share(obj):
    if SIZE == 1 or DOWRAPPED:
        return obj
    try:
        shareobj = COMM.bcast(obj, root = 0)
        alltypes = COMM.allgather(type(shareobj))
        if not len(set(alltypes)) == 1:
            raise SimpliError
        return shareobj
    except OverflowError:
        tempfilename = 'temp.pkl' # PROBLEMATIC
        try:
            if RANK == 0:
                with open(tempfilename, 'w') as file:
                    _pickle.dump(obj, file)
                shareobj = obj
            if not RANK == 0:
                with open(tempfilename, 'r') as file:
                    shareobj = _pickle.load(file)
        finally:
            if RANK == 0:
                _os.remove(tempfilename)
        return shareobj

def dowrap(func):
    @_wraps(func)
    def wrapper(*args, _mpiignore_ = False, **kwargs):
        if any((_mpiignore_, SIZE == 1, DOWRAPPED)):
            output = func(*args, **kwargs)
        else:
            COMM.barrier()
            global DOWRAPPED
            DOWRAPPED = True
            output = MPIPlaceholderError()
            if RANK == 0:
                try:
                    output = func(*args, **kwargs)
                except:
                    exc_type, exc_val = _sys.exc_info()[:2]
                    output = exc_type(exc_val)
            output = share(output)
            DOWRAPPED = False
            COMM.barrier()
            if isinstance(output, Exception):
                raise output
        return output
    return wrapper


###############################################################################
###############################################################################
