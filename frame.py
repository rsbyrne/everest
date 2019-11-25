import os

from . import disk
from . import mpi
from . import built

EXTENSION = 'frm'

def get_framepath(name, path):
    framepath = os.path.join(
        path,
        name + '.' + EXTENSION
        )
    return framepath

def make_frameDict(name, path = ''):
    builtsDict = {}
    framepath = get_framepath(name, path)
    builtKeys = []
    if mpi.rank == 0:
        with disk.h5File(framepath) as h5file:
            builtKeys.extend([*h5file.keys()])
    builtKeys = mpi.comm.bcast(builtKeys, root = 0)
    for key in sorted(builtKeys):
        builtsDict[key] = built.load(name, key, path)
    return builtsDict
