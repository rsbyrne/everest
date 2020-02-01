from types import FunctionType

from . import Built

class Condition(Built):
    def __init__(
            self,
            _bool_meta_fn = all,
            **kwargs
            ):
        self._pre_bool_fns = []
        self._bool_fns = []
        self._post_bool_fns = []
        self._bool_meta_fn = _bool_meta_fn
        super().__init__(**kwargs)
    def __bool__(self):
        for fn in self._pre_bool_fns: fn()
        truth = _bool_meta_fn(self._bool_fns)
        for fn in self._post_bool_fns: fn()
        return truth

# # Unary
# class Not(Condition):
#     def __init__(self, condition, **kwargs):
#         boolFn = lambda: not condition
#         super().__init__(boolFn, **kwargs)
#
# # Binary
# class And(Condition):
#     def __init__(self, condition1, condition2, **kwargs):
#         boolFn = lambda: condition1 and condition2
#         super().__init__(boolFn, **kwargs)
#
# class Any(Condition):
#     def __init__(self, *conditions, **kwargs):
#         boolFn = lambda: any(conditions)
#         super().__init__(boolFn, **kwargs)
#
# class All(Condition):
#     def __init__(self, *boolFns, **kwargs):
#         boolFn = lambda: all([boolFn() for boolFn in boolFns])
#         super().__init__(boolFn, **kwargs)
#
# class Either(Condition):
#     def __init__(self, *boolFns, **kwargs):
#         boolFn = lambda: all([boolFn() for boolFn in boolFns])
#         super().__init__(boolFn, **kwargs)
