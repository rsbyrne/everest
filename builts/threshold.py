from everest.builts._condition import Condition
from everest.builts import Built

class Threshold(Condition):
    def __init__(
            self,
            built : Built = None,
            prop : str = None,
            op : str = 'eq',
            arg = None
            ):
        op = '__{a}__'.format(a = op)
        getProperty = lambda: getattr(built, prop)
        getOpFn = lambda: getattr(getProperty(), op)
        boolFn = lambda: getOpFn()(arg)
        super().__init__()
        self._bool_fns.append(boolFn)

CLASS = Threshold
build = CLASS.build
get = CLASS.get
