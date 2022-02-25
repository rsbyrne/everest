###############################################################################
''''''
###############################################################################


import sys as _sys
import pickle as _pickle
import functools as _functools

from mpi4py import MPI as _MPI

from everest.exceptions import EverestException as _EverestException

from everest.utilities import reseed as _reseed

comm = _MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()


class MPIError(_EverestException):
    ...


class SubMPIError(MPIError):
    '''Something went wrong inside an MPI block.'''
    pass


class MPIPlaceholderError(MPIError):
    '''An MPI broadcast operation failed.'''
    pass


def message(*args, **kwargs):
    comm.barrier()
    if rank == 0:
        print(*[*args, *kwargs.items()])
    comm.barrier()

    
def share(obj):
    try:
        shareObj = comm.bcast(obj, root = 0)
        allTypes = comm.allgather(type(shareObj))
        if not len(set(allTypes)) == 1:
            raise MPIError
        return shareObj
    except OverflowError:
        tempfilename = _reseed.rstr(16) + '.pkl'
        if rank == 0:
            with open(tempfilename, 'w') as file:
                _pickle.dump(obj, file)
            shareObj = obj
        if rank != 0:
            with open(tempfilename, 'r') as file:
                shareObj = _pickle.load(file)
        if rank == 0:
            os.remove(tempfilename)
        return shareObj


def mpi_wrap(func):
    @_functools.wraps(func)
    def wrapper(*args, _mpiignore_ = False, **kwargs):
        if size == 1:
            _mpiignore_ = True
        if _mpiignore_:
            return func(*args, **kwargs)
        else:
            comm.barrier()
            output = MPIPlaceholderError()
            if rank == 0:
                try:
                    output = func(*args, **kwargs)
                except:
                    exc_type, exc_val = _sys.exc_info()[:2]
                    output = exc_type(exc_val)
            output = share(output)
            comm.barrier()
            if isinstance(output, Exception):
                raise output
            else:
                return output
    return wrapper


###############################################################################
###############################################################################
