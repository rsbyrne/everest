###############################################################################
''''''
###############################################################################


import abc as _abc
from collections import abc as _collabc
import operator as _operator

from everest import ur as _ur

from .sprite import Sprite as _Sprite


_UNARYOPS = _ur.DatDict(
    inv='~',
    pos='+',
    neg='-',
    )

_BINARYOPS = _ur.DatDict({
    'lt': '<',
    'le': '<=',
    'eq': '==',
    'ne': '!=',
    'ge': '>=',
    'gt': '>',
    'add': '+',
    'and': '&',
    'floordiv': '//',
    'lshift': '<<',
    'mod': '%',
    'mul': '*',
    'matmul': '@',
    'or': '|',
    'pow': '**',
    'rshift': '>>',
    'sub': '-',
    'truediv': '/',
    'xor': '^',
    })


def get_evalstr(obj, /):
    if isinstance(obj, Shadow):
        return obj.evalstr
    return repr(obj)


class Shadow(metaclass=_Sprite):

    __slots__ = ('evalstr',)

    def __init__(self, /):
        super().__init__()
        self.evalstr = self.get_evalstr()

    for methname in _UNARYOPS:
        exec('\n'.join((
            f"def __{methname}__(self, other, /):",
            f"    return Unary('{_UNARYOPS[methname]}', self)",
            )))

    for methname in _BINARYOPS:
        exec('\n'.join((
            f"def __{methname}__(self, other, /):",
            f"    return Binary('{_BINARYOPS[methname]}', self, other)",
            )))

    for methname in (
            'radd', 'rand', 'rfloordiv', 'rlshift', 'rmod', 'rmul',
            'rmatmul', 'ror', 'rpow', 'rrshift', 'rsub', 'rtruediv',
            'rxor',
            ):
        methname = methname.removeprefix('r')
        exec('\n'.join((
            f"def __r{methname}__(self, other, /):",
            f"    return Binary('{_BINARYOPS[methname]}', other, self)",
            )))
        
    del methname

    def __hash__(self, /):  # Has to be added manually due to richops ^^^
        return hash((self.Base, self.params))

    @_abc.abstractmethod
    def get_evalstr(self, /):
        raise NotImplementedError

    # @_abc.abstractmethod
    # def resolve(self, operands: _collabc.Mapping, /):
    #     raise NotImplementedError


class Shade(Shadow):

    name: str
    prefix: str = None

    def __get__(self, instance, /):
        return getattr(instance, self.name)

    def get_evalstr(self, /):
        if (prefix := self.prefix) is None:
            return self.name
        return f"{prefix}.{self.name}"

#     def resolve(self, operands, /):
#         return operands[self.name]


class Operation(Shadow):

    op: str

    __slots__ = ('_shades',)

    @_abc.abstractmethod
    def yield_shades(self, /):
        raise NotImplementedError

    @property
    def shades(self, /):
        try:
            return self._shades
        except AttributeError:
            with self.mutable:
                shades = self._shades = _ur.DatUniTuple(self.yield_shades())
            return shades


class Unary(Operation):

    arg: None

    def yield_shades(self, /):
        arg = self.arg
        if isinstance(arg, Shade):
            yield arg
        else:
            yield from arg.yield_shades()

    def get_evalstr(self, /):
        return self.op + get_evalstr(self.arg)

    # def resolve(self, operands, /):
    #     return self.operator(arg.resolve(operands))


class Binary(Operation):

    op: str
    arg1: None
    arg2: None

    def yield_shades(self, /):
        for arg in (self.arg1, self.arg2):
            if isinstance(arg, Shadow):
                if isinstance(arg, Shade):
                    yield arg
                else:
                    yield from arg.yield_shades()

    # def resolve(self, operands, /):
    #     return self.operator(*(
    #         arg.resolve(operands) if isinstance(arg, Shadow) else arg
    #         for arg in (self.arg1, self.arg2)
    #         ))

    def get_evalstr(self, /):
        return f"({self.op.join(map(get_evalstr, (self.arg1, self.arg2)))})"


###############################################################################
###############################################################################
