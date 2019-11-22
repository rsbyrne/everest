import os
from timeit import timeit

import planetengine

outputPath = '../out'
name = 'test'
extension = 'frm'
path = os.path.join(outputPath, name + '.' + extension)
if planetengine.mpi.rank == 0:
    if os.path.exists(path):
        os.remove(path)

system = planetengine.systems.isovisc.build(res = 16)
system.anchor(name, outputPath)
def testfn():
    for i in range(3):
        for i in range(3):
            system.go(3)
            system.store()
        system.save()
    system.load(3)
    system.iterate()
    system.store()
    system.save()
    system_loaded = everest.built.load(
        name,
        system.hashID,
        outputPath
        )
    system_loaded.load(4)
    system_loaded.iterate()
    system_loaded.store()
    system.iterate()
    system.store()

timing = timeit(testfn, number = 3) / 3.

planetengine.message(timing)
system.show()
