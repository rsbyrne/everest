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


def message(*args, **kwargs):
    COMM.barrier()
    if RANK == 0:
        print(*[*args, *kwargs.items()])
    COMM.barrier()

def share(obj):
    try:
        shareObj = COMM.bcast(obj, root = 0)
        allTypes = COMM.allgather(type(shareObj))
        if not len(set(allTypes)) == 1:
            raise simpliError
        return shareObj
    except OverflowError:
        tempfilename = 'temp.pkl' # PROBLEMATIC
        if RANK == 0:
            with open(tempfilename, 'w') as file:
                _pickle.dump(obj, file)
            shareObj = obj
        if not RANK == 0:
            with open(tempfilename, 'r') as file:
                shareObj = _pickle.load(file)
        if RANK == 0:
            _os.remove(tempfilename)
        return shareObj

def dowrap(func):
    @_wraps(func)
    def wrapper(*args, _mpiignore_ = False, **kwargs):
        if SIZE == 1:
            _mpiignore_ = True
        if _mpiignore_:
            return func(*args, **kwargs)
        else:
            COMM.barrier()
            output = MPIPlaceholderError()
            if RANK == 0:
                try:
                    output = func(*args, **kwargs)
                except:
                    exc_type, exc_val = _sys.exc_info()[:2]
                    output = exc_type(exc_val)
            output = share(output)
            COMM.barrier()
            if isinstance(output, Exception):
                raise output
            else:
                return output
    return wrapper


###############################################################################
###############################################################################
