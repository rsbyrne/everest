from everest.builts._condition import Condition
from everest.builts import Built

class Threshold(Condition):
    def __init__(
            self,
            built : Built = None,
            prop : str = None,
            op : str = 'eq',
            val = None
            ):
        op = '__{a}__'.format(a = op)
        getProperty = lambda: getattr(built, prop)
        getOpFn = lambda: getattr(getProperty(), op)
        boolFn = lambda: getOpFn()(val)
        super().__init__(boolFn)

CLASS = Threshold
build = CLASS.build
