import everest
import math

def build(*args, **kwargs):
    return MyObject1(*args, **kwargs)

class MyObject1(everest.built.Iterative):

    name = 'myobject1'
    script = __file__

    def __init__(
            self,
            a = 1,
            b = 2.,
            initial_time = 0.
            ):
        inputs = locals().copy()
        self.var = everest.value.Value(0.)
        self.time = everest.value.Value(0.)
        self.a = a
        self.b = b
        self.initial_time = initial_time
        super().__init__(
            inputs,
            self.script,
            out = self.out,
            outkeys = ['time', 'var'],
            update = self.update,
            iterate = self.iterate,
            initialise = self.initialise,
            load = self.load
            )

    def update(self):
        self.var.value = math.sin(self.time() ** self.a)

    def iterate(self):
        self.time.value += self.b

    def initialise(self):
        initialTime = self.initial_time
        if isinstance(initialTime, everest.built.Built):
            initialTime = initialTime.val
        self.time.value = initialTime

    def out(self):
        return [self.time(), self.var()]

    def load(self, loadDict):
        self.var.value = loadDict['var']
        self.time.value = loadDict['time']
