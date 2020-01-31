import sys
from mpi4py import MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

from .exceptions import EverestException
class MPIError(EverestException):
    '''Something went wrong with an MPI thing.'''
    pass
class SubMPIError(EverestException):
    '''Something went wrong inside an MPI block.'''
    pass

def message(*args, **kwargs):
    comm.barrier()
    if rank == 0:
        print(*args, **kwargs)
    comm.barrier()

def share(obj):
    comm.barrier()
    shareObj = comm.bcast(obj, root = 0)
    allTypes = comm.allgather(type(shareObj))
    if not len(set(allTypes)) == 1:
        raise MPIError
    comm.barrier()
    return shareObj

def dowrap(func):
    def wrapper(*args, **kwargs):
        output = None
        if rank == 0:
            try:
                output = func(*args, **kwargs)
            except:
                exc_type, exc_val = sys.exc_info()[:2]
                output = exc_type(exc_val)
        output = share(output)
        if isinstance(output, Exception):
            raise output
        else:
            return output
    return wrapper
