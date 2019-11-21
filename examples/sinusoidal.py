import numpy as np

import everest
from planetengine import mapping
import underworld as uw

def build(*args, name = None, **kwargs):
    built = Sinusoidal(*args, **kwargs)
    if type(name) == str:
        built.name = name
    return built

class Sinusoidal(everest.built.Built):

    def __init__(
            self,
            pert = 0.2,
            freq = 1.,
            phase = 0.
            ):

        inputs = locals().copy()

        self.valRange = (0., 1.)

        self.freq = freq
        self.phase = phase
        self.pert = pert

        super().__init__(
            inputs,
            __file__
            )

    def evaluate(self, coordArray):
        valMin, valMax = self.valRange
        deltaVal = self.valRange[1] - self.valRange[0]
        pertArray = \
            self.pert \
            * np.cos(np.pi * (self.phase + self.freq * coordArray[:,0])) \
            * np.sin(np.pi * coordArray[:,1])
        outArray = valMin + deltaVal * (coordArray[:,1]) + pertArray
        outArray = np.clip(outArray, valMin, valMax)
        outArray = np.array([[item] for item in outArray])
        return outArray

    def apply(self, var):
        if type(var) == uw.mesh.MeshVariable:
            box = mapping.box(var.mesh, var.mesh.data)
        elif type(var) == uw.swarm.SwarmVariable:
            box = mapping.box(var.swarm.mesh, var.swarm.data)
        data = self.evaluate(box)
        var.data[...] = data
