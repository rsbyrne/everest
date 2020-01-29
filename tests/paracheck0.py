from everest.builts.iterator import build
pimachine = build()

import os
from everest import mpi
message = mpi.message

if mpi.rank == 0:
    if os.path.exists('./test.frm'):
        os.remove('./test.frm')
pimachine.reset()
pimachine.anchor('test', '.')
for i in range(3):
    for _i in range(3):
        pimachine.iterate(3)
        pimachine.store()
    pimachine.save()

message(pimachine.counts_captured)

pimachine.load(12)

pimachine.iterate(15)

message(pimachine.count)

message(pimachine.state)

pimachine.load(3)

message(pimachine.state)

message(pimachine)

hashID = pimachine.hashID

message(hashID)

del pimachine
from everest.builts import _PREBUILTS
del _PREBUILTS[hashID]

from everest.builts import load
pimachine = load(hashID, 'test', '..')

message(pimachine)

message(pimachine.counts_captured)

pimachine.load(27)

pimachine.iterate(100)

message(pimachine.state)
