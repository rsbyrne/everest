from . import Built

class Condition(Built):
    def __init__(self, boolFn, **kwargs):
        self.boolFn = boolFn
        super().__init__(**kwargs)
    def __bool__(self):
        return self.boolFn()
