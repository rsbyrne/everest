import everest
import math

def build(*args, **kwargs):
    return MyObject1(*args, **kwargs)

class MyObject1(everest.Built):

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
        super().__init__(
            inputs,
            self.script,
            update = self.update,
            iterate = self.iterate,
            initialise = self.initialise,
            out = self.out
            )

    def update(self):
        self.var.value = math.sin(self.time() ** self.a)

    def iterate(self):
        self.time.value += self.b

    def initialise(self):
        self.time.value = self.outget('initial_time')

    def out(self):
        return self.var()
