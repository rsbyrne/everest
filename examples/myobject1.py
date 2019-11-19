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
            b = 2.
            ):
        inputs = locals().copy()
        self.var = everest.value.Value(0.)
        self.time = everest.value.Value(0.)
        self.a = a
        self.b = b
        super().__init__(
            inputs,
            self.script,
            iterate = self.iterate,
            initialise = self.initialise,
            out = self.out
            )

    def iterate(self):
        self.var.value = math.sin(self.time() ** self.a)
        self.time.value += self.b

    def initialise(self, time = 0.):
        self.time.value = time

    def out(self):
        return self.var()
