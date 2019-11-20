import h5py
import os

import everest
import planetengine

IC = everest.examples.sinusoidal.build()
system = everest.examples.isovisc.build(
    Ra = 1e5,
    res = 4,
    temperatureFieldIC = IC
    )

outputPath = '..'
name = 'test'
extension = 'h5'
path = os.path.join(outputPath, name + '.' + extension)
if everest.mpi.rank == 0:
    if os.path.exists(path):
        os.remove(path)

system.anchor(path)

for i in range(3):
    system.go(3)
    system.store()
system.save()
for i in range(3):
    system.go(3)
    system.store()
system.save()
system.load(9)
for i in range(3):
    system.go(3)
    system.store()
system.save()

planetengine.quickShow(system.temperatureField)

if everest.mpi.rank == 0:
    with h5py.File(path) as h5file:
        print(h5file[system.hashID]['temperatureField']['data'][...])
