###############################################################################
''''''
###############################################################################


import itertools as _itertools

from .base import (
    AlgebraInstance as _AlgebraInstance,
    AlgebraMeta as _AlgebraMeta,
    )


class Operation(_AlgebraInstance):

    def __init__(self, /, *operands):
        self.operands = operands

    def _repr(self):
        return ', '.join(map(repr, self.operands))


class Operator(_AlgebraMeta):

    Operation = Operation

    def __new__(meta, *bases, name: str, valence: int, **kwargs):
        return super().__new__(
            meta,
            meta.__name__ + '_' + str(hash((bases, tuple(kwargs.items())))),
            tuple((*bases, meta.Operation)),
            dict(name=name, valence=valence, **kwargs)
            )

    def __init__(cls, *args, **kwargs):
        return super().__init__(cls)

    def _cls_repr(cls):
        return f"name={cls.name}, valence={cls.valence}"

    def __call__(cls, *operands, **kwargs):
        return super().__call__(*operands, **kwargs)


class FixedValence(Operator):

    def _cls_repr(cls):
        return f"name={cls.name}"


class Nullary(FixedValence):

    class Operation(FixedValence.Operation):

        def __init__(self):
            super().__init__()

    def __new__(meta, *bases, **kwargs):
        return super().__new__(meta, *bases, valence=0, **kwargs)


class Unary(FixedValence):

    class Operation(FixedValence.Operation):

        def __init__(self, operand, /, *, reps: int = 0):
            self.reps = reps
            self.operand = operand
            super().__init__(operand)

        def _repr(self):
            return f"{super()._repr()}, reps={self.reps}"

    def __new__(meta, *bases,
            valence=1, idempotent=False, reversible=False, **kwargs
            ):
        if idempotent and reversible:
            raise ValueError(
                "Unary operation cannot be both idempotent and reversible."
                )
        return super().__new__(meta,
            *bases,
            valence=1, idempotent=idempotent, reversible=reversible, **kwargs
            )

    def __call__(cls, operand, reps=0, **kwargs):
        if isinstance(operand, cls):
            if cls.idempotent:
                return operand
            elif cls.reversible:
                return operand.operand
            operand, reps = operand.operand, 1 + operand.reps + reps
        return super().__call__(operand, reps=reps, **kwargs)

    def _cls_repr(cls):
        args = []
        if cls.idempotent:
            args.append('idempotent')
        elif cls.reversible:
            args.append('reversible')
        return ', '.join((
            super()._cls_repr(),
            *args
            ))


class Binary(FixedValence):

    class Operation(FixedValence.Operation):
        ...

    def _unpack_operands_associative(cls, operands):
        for operand in operands:
            if isinstance(operand, cls):
                yield from operand.operands
            else:
                yield operand

    def _unpack_operands_commutative(cls, operands):
        return iter(sorted(operands, key=repr))

    def _unpack_operands_both(cls, operands):
        return cls._unpack_operands_commutative(
            cls._unpack_operands_associative(
                operands
                )
            )

    def _unpack_operands_neither(cls, operands):
        return operands

    def __new__(meta,
            *bases,
            associative: bool = False,
            commutative: bool = False,
            **kwargs
            ):
        cls = super().__new__(meta,
            *bases,
            valence=2,
            associative=associative,
            commutative=commutative,
            **kwargs
            )
        cls.unpack_operands = {
            (False, False): cls._unpack_operands_neither,
            (True, False): cls._unpack_operands_associative,
            (False, True): cls._unpack_operands_commutative,
            (True, True): cls._unpack_operands_both,
            }[associative, commutative]
        return cls

    def _cls_repr(cls):
        args = []
        if cls.associative:
            args.append('associative')
        if cls.commutative:
            args.append('commutative')
        return ', '.join((
            super()._cls_repr(),
            *args
            ))

    def __call__(cls, *operands):
        return super().__call__(*cls.unpack_operands(operands))


# class Repeat(_AlgebraInstance):

#     def __init__(self, val, reps: int):
#         self.val, self.reps = val, reps

#     def __iter__(self):
#         return _itertools.repeat(self.val, self.reps)

#     def _repr(self):
#         return f"{self.val};{self.reps}"

#     @classmethod
#     def bundle_operands(cls, operands):
#         yield from _itertools.chain.from_iterable(
#             _itertools.starmap(
#                 cls.process_operand,
#                 _itertools.groupby(operands)
#                 )
#             )

#     @classmethod
#     def process_operand(cls, val, grp):
#         grp = tuple(grp)
#         length = len(grp)
#         yield cls(val, length) if length > 1 else val


###############################################################################
###############################################################################
