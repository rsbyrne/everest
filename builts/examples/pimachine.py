import numpy as np

from everest.builts._iterator import Iterator

class PiMachine(Iterator):
    # Implements the Bailey-Borwein-Plouffe formula;
    # default args yield pi.
    def __init__(
            self,
            s : int = 1,
            b : int = 16,
            A : list = [4, 0, 0, -2, -1, -1, 0, 0],
            **kwargs
            ):
        self.state = 0.
        self.kth = lambda k: \
            1. / b **k \
            * sum([a / (len(A) * k + (j + 1))**s \
                for j, a in enumerate(A)
                ])
        def out():
            yield np.array(self.state)
        def initialise():
            self.state = self.kth(0)
        def iterate():
            kthVal = self.kth(self.count())
            self.state += kthVal
        def load(loadDict):
            self.state = loadDict['pi']
        super().__init__(
            initialise,
            iterate,
            out,
            ['pi',],
            load,
            **kwargs
            )

CLASS = PiMachine
build = CLASS.build
get = CLASS.get
