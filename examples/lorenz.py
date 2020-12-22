import numpy as np

from funcy import Fn

from everest.frames._traversable import Traversable
from everest.frames._chronable import Chronable

class Lorenz(Traversable, Chronable):

    __slots__ = ('coords', 'chron', '_integrate')

    def __init__(self,
            # params
                s = 10,
                r = 28,
                b = 2.667,
                dt = 0.01,
            # _configs
                coords = [0., 1., 1.05],
            **kwargs
            ):

        super().__init__(**kwargs)

        def integrate(cs, chron):
            cs += (
                dt * (s * (cs[1] - cs[0])),
                dt * (r * cs[0] - cs[1] - cs[0] * cs[2]),
                dt * (cs[0] * cs[1] - b * cs[2]),
                )
            chron += dt

        self.cs, self.chron = self.state['coords'], self.indices['chron']
        self._integrate = integrate

    def _iterate(self):
        self._integrate(self.cs, self.chron)
        super()._iterate()

        # x, y, z = cs = self.state['coords']
        # chron = self.indices['chron']
        # fn = Fn(
        #     x + dt * s * (y - x),
        #     y + dt * (r * x - y - x * z),
        #     z + dt * (x * y - b * z),
        #     )
        # def integrate():
        #     cs.value = fn
        #     chron.value += dt
        # self._integrate = integrate

# s, r, b, dt = (np.array(p) for p in self.inputs.params.values())
