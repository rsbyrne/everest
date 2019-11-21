import everest

def build(*args, **kwargs):
    return MyObject2(*args, **kwargs)

class MyObject2(everest.built.Built):

    name = 'myobject2'

    def __init__(
            self,
            val = 0.
            ):
        inputs = locals().copy()
        self.val = val
        super().__init__(
            inputs,
            __file__
            )
