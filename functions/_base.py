import operator
import builtins
from types import FunctionType

import numpy as np

from ..pyklet import Pyklet
from ..utilities import w_hash, get_hash, is_numeric
from ..exceptions import *

class FunctionException(EverestException):
    pass
class FunctionMissingAsset(MissingAsset, FunctionException):
    pass

class Function(Pyklet):

    def __new__(cls, *args, **kwargs):
        if cls is Function:
            cls = cls._getcls(*args, **kwargs)
        return super().__new__(cls)

    def __init__(self, *terms, name = None, **kwargs):
        self._name = name
        self.terms = terms
        if len(terms) == 1:
            self.arg = terms[0]
        else:
            self.arg = terms
        self.kwargs = kwargs
        super().__init__(*terms, **kwargs)

    def evaluate(self):
        if self.open:
            raise FunctionException("Cannot evaluate open function.")
        else:
            return self._evaluate()
    def _evaluate(self):
        raise FunctionMissingAsset
    @property
    def value(self):
        return self.evaluate()
    @property
    def null(self):
        return self._isnull()
    def _isnull(self):
        return False
    @property
    def name(self):
        return str(self._name)

    def _count_slots(self):
        terms = self.terms
        slots = 0
        for term in terms:
            if isinstance(term, Function):
                slots += term.slots
            elif term is None:
                slots += 1
        return slots
    @property
    def slots(self):
        if not hasattr(self, '_slots'):
            self._slots = self._count_slots()
        return self._slots
    @property
    def open(self):
        return bool(self.slots)
    def close(self, *queryArgs):
        if not len(queryArgs) == self.slots:
            raise ValueError("Must provide one argument for each slot.")
        queryArgs = iter(queryArgs)
        terms = []
        for t in self.terms:
            if isinstance(t, Function) and hasattr(t, 'slots'):
                closeArgs = [next(queryArgs) for _ in range(t.slots)]
                closed = t.close(*closeArgs)
                terms.append(closed)
            elif t is None:
                terms.append(next(queryArgs))
            else:
                terms.append(t)
        return type(self)(*terms, **self.kwargs)

    def __eq__(self, arg):
        return self.value == arg

    def _operate(self, *args, op = None):
        return Operation(self, *args, op = op)

    def __ne__(self, *args): return self._operate(*args, op = 'ne')
    def __ge__(self, *args): return self._operate(*args, op = 'ge')
    def __le__(self, *args): return self._operate(*args, op = 'le')
    def __gt__(self, *args): return self._operate(*args, op = 'gt')
    def __lt__(self, *args): return self._operate(*args, op = 'lt')
    def __add__(self, *args): return self._operate(*args, op = 'add')
    def __floordiv__(self, *args): return self._operate(*args, op = 'floordiv')
    def __truediv__(self, *args): return self._operate(*args, op = 'truediv')
    def __mod__(self, *args): return self._operate(*args, op = 'mod')
    def __mul__(self, *args): return self._operate(*args, op = 'mul')
    def __pow__(self, *args): return self._operate(*args, op = 'pow')
    def __sub__(self, *args): return self._operate(*args, op = 'sub')
    def __truediv__(self, *args): return self._operate(*args, op = 'truediv')
    def __neg__(self, *args): return self._operate(*args, op = 'neg')

    def __bool__(self):
        return bool(self.value)

    @staticmethod
    def bool(arg):
        return Operation(*args, op = bool)
    @staticmethod
    def all(*args):
        return Operation(*args, op = all)
    @staticmethod
    def any(*args):
        return Operation(*args, op = any)
    @staticmethod
    def not_fn(*args):
        return Operation(*args, op = bool, invert = True)
    def __invert__(self):
        return self._not(self)

    def __str__(self):
        if self.null:
            return 'NullVal'
        else:
            return str(self.value)

    def __repr__(self):
        return super().__repr__() + '==' + str(self.value)
    def __str__(self):
        return str(self.value)

    def __call__(self, *args):
        if len(args):
            self = self.close(*args)
        return self.evaluate()

    @staticmethod
    def _getop(op):
        if op is None:
            return lambda *args: args
        elif type(op) is str:
            try:
                return getattr(builtins, op)
            except AttributeError:
                return getattr(operator, op)
        else:
            return op

    @classmethod
    def _getcls(cls, *args, op = None, **kwargs):
        if op is None:
            if len(args) > 1:
                return Getter
            else:
                arg = args[0]
                if is_numeric(arg):
                    return Value
                else:
                    _ = len(arg)
                    return Array
        else:
            return Operation

class Operation(Function):

    def __init__(self, *terms, op = None, asList = False, invert = False):
        if type(op) is tuple:
            sops, op = op[:-1], op[-1]
            for sop in sops:
                terms = Operation(*terms, op = sop)
                if not type(terms) is tuple:
                    terms = terms,
        self.op = self._getop(op)
        self.asList, self.invert = asList, invert
        super().__init__(*terms, op = op, asList = asList, invert = invert)

    def _evaluate(self):
        ts = [
            t.value if isinstance(t, Function) else t
                for t in self.terms
            ]
        if self.asList:
            out = self.op(ts)
        else:
            out = self.op(*ts)
        if self.invert:
            out = not out
        return out

class ValueException(EverestException):
    pass
class ValueForbiddenAttribute(Forbidden, ValueException):
    pass
class NullValueDetected(ValueException):
    pass

class Value(Function):

    def __init__(self, value, null = False, name = None):
        if not is_numeric(value):
            raise TypeError("Value must be numeric.")
        self.initial = value
        if np.issubdtype(type(value), np.integer):
            self._plain = int(value)
            self.type = np.int32
        else:
            self._plain = float(value)
            self.type = np.float64
        if null:
            self._value = None
        else:
            self._value = self.type(value)
        super().__init__(value, null = null, name = name)

    @property
    def plain(self):
        return self._plain

    def _isnull(self):
        return self._value is None

    def __setattr__(self, item, value):
        if item in self.__dict__:
            if item in {'type', 'initial'}:
                raise ValueForbiddenAttribute()
            elif item == 'value':
                if value is None:
                    self.__dict__['_value'] = None
                    self.__dict__['_plain'] = None
                    return None
                else:
                    try:
                        if np.issubdtype(type(value), np.integer):
                            plain = int(value)
                        else:
                            plain = float(value)
                        value = self.type(value)
                        self.__dict__['_value'] = value
                        self.__dict__['_plain'] = plain
                    except TypeError:
                        raise TypeError((value, type(value)))
                    return None
        self.__dict__[item] = value

    def _evaluate(self):
        if self.null: raise NullValueDetected(self._value)
        return self._value

    def _reassign(self, arg, op = None):
        self.value = self._operate(arg, op = op).value
        return self
    def __iadd__(self, arg): return self._reassign(arg, op = 'add')
    def __ifloordiv__(self, arg): return self._reassign(arg, op = 'floordiv')
    def __imod__(self, arg): return self._reassign(arg, op = 'mod')
    def __imul__(self, arg): return self._reassign(arg, op = 'mul')
    def __ipow__(self, arg): return self._reassign(arg, op = 'pow')
    def __isub__(self, arg): return self._reassign(arg, op = 'sub')
    def __itruediv__(self, arg): return self._reassign(arg, op = 'truediv')

    def _hashID(self):
        return self.name

class Array(Function):

    def __init__(self, values, null = False, name = None):
        values = np.array(values)
        self.initial = values
        self._value = values
        self._null = null
        self.type = self._value.dtype
        super().__init__(values, null = null, name = name)

    @property
    def plain(self):
        return list(self._value)

    def _isnull(self):
        return self._null

    def __setattr__(self, item, value):
        if item in self.__dict__:
            if item == 'type':
                print(self.type)
                raise ValueForbiddenAttribute(
                    "Forbidden to manually set 'type'."
                    )
            elif item == 'value':
                if value is None:
                    self._null = True
                    return None
                else:
                    try:
                        self._value[...] = value
                        self._null = False
                    except TypeError:
                        raise TypeError((value, type(value)))
                    return None
        self.__dict__[item] = value

    def _evaluate(self):
        if self.null: raise NullValueDetected(self._value)
        return self._value

    def _reassign(self, arg, op = None):
        self.value = self._operate(arg, op = op).value
        return self
    def __iadd__(self, arg): return self._reassign(arg, op = 'add')
    def __ifloordiv__(self, arg): return self._reassign(arg, op = 'floordiv')
    def __imod__(self, arg): return self._reassign(arg, op = 'mod')
    def __imul__(self, arg): return self._reassign(arg, op = 'mul')
    def __ipow__(self, arg): return self._reassign(arg, op = 'pow')
    def __isub__(self, arg): return self._reassign(arg, op = 'sub')
    def __itruediv__(self, arg): return self._reassign(arg, op = 'truediv')

    def _hashID(self):
        return self.name

class Getter(Function):

    def __init__(self,
            target,
            *props
            ):
        self.target, self.props = target, props
        super().__init__(target, *props)

    def _evaluate(self):
        target, *props = self.terms
        if target is None:
            raise ValueError
        for prop in props:
            try:
                target = getattr(target, prop)
            except (AttributeError, TypeError):
                target = target.__getitem__(prop)
        return target

    def _hashID(self):
        return '.'.join([
            get_hash(self.terms[0]),
            *[str(t) for t in self.terms[1:]]
            ])
