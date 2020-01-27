from mpi4py import MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

from .exceptions import EverestException
class MPIError(EverestException):
    '''Something went wrong with an MPI thing.'''
    pass

def share(obj):
    obj = comm.bcast(obj, root = 0)
    allTypes = comm.allgather(type(obj))
    if not len(set(allTypes)) == 1:
        raise MPIError
    return obj

# def share_class(object):
#     strClass = None
#     if rank == 0:
#         strClass = str(type(object))[8:-2]
#     strClass = comm.bcast(strClass, root = 0)
#     try:
#         actualClass = eval(strClass)
#     except NameError:
#         splitClass = strClass.split('.')
#         exec("import " + splitClass[0])
#         actualClass = eval(strClass)
#     return actualClass

# def share_outputs(outputs):
#     try:
#         outputs = mpi.comm.bcast(outputs, root = 0)
#     except:
#         pass

# def share_outputs(outputs):
#     try:
#         outputs = comm.bcast(outputs, root = 0)
#     except:
#         outputsClass = share_class(outputs)
#         isIter = False
#         if rank == 0:
#             if type(outputs) in {list, tuple, set}:
#                 isIter = True
#         isIter = comm.bcast(isIter, root = 0)
#         if isIter:
#             outsLen = None
#             if rank == 0:
#                 outsLen = len(outputs)
#             outsLen = mpi.comm.bcast(outsLen)
#             if not rank == 0:
#                 outputs = [None for i in range(outsLen)]
#             subOutputs = [share_outputs(output) for output in outputs]
#             outputs = outputsClass(subOutputs)
#         else:
#             if rank == 0:
#                 outputs = str(outputs)
#             outputs = comm.bcast(outputs, root = 0)
#             outputs = outputsClass._unrepr(outputs)
#     return outputs
