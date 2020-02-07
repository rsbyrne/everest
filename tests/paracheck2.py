name = 'test'
outputPath = '.'
from everest import mpi
import os
fullpath = os.path.join(os.path.abspath(outputPath), name) + '.frm'
if mpi.rank == 0:
    if os.path.exists(fullpath):
        os.remove(fullpath)
from everest.builts import set_global_anchor
set_global_anchor(name, outputPath)

from everest.builts.container import Container
from everest.builts.vector import Vector

mycontainer = Container([Vector(n = n) for n in range(10)])

mpi.message(mycontainer.inputs)

mycontainer.initialise()
for ticket in mycontainer:
    mpi.message('-' * 10)
    mpi.message('Ticket:', ticket)
    mpi.message('Out:', mycontainer.reader[mycontainer.hashID, 'checkedOut'])
    mycontainer.checkBack(ticket)
    mpi.message('Returned:', mycontainer.reader[mycontainer.hashID, 'checkedBack'])
    mycontainer.complete(ticket)
    mpi.message('Complete:', mycontainer.reader[mycontainer.hashID, 'checkedComplete'])

mpi.message(mycontainer.checkedComplete)

import weakref
myref = weakref.ref(mycontainer)

del mycontainer

assert myref() is None

if mpi.rank == 0:
    if os.path.exists(fullpath):
        os.remove(fullpath)

mpi.message("Complete!")
