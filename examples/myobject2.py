import everest

def build(*args, **kwargs):
    return MyObject2(*args, **kwargs)
    
class MyObject2(everest.Built):

    name = 'myobject2'
    script = __file__

    def __init__(
            self,
            val = 0
            ):
        inputs = locals().copy()
        def out():
            return val
        super().__init__(
            inputs,
            self.script,
            out = out
            )
