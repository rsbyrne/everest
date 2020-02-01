from types import FunctionType

from . import Built

class Condition(Built):
    def __init__(
            self,
            boolFn : FunctionType,
            **kwargs
            ):
        self.boolFn = boolFn
        super().__init__(**kwargs)
    def __bool__(self):
        return self.boolFn()

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
