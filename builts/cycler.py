from . import Built

class Cycler(Built):
    def __init__(self, cycleFn, cycleCondition = True, **kwargs):
        self.cycleFn = cycleFn
        self.cycleCondition = cycleCondition
        super().__init__(**kwargs)
    def cycle(self):
        if cycleCondition:
            cycleFn()
