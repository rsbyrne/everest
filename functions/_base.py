import operator
import builtins
from types import FunctionType
from collections.abc import Mapping

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
        self.terms = [Function() if t is None else t for t in terms]
        if len(terms) == 1:
            self.arg = terms[0]
        else:
            self.arg = terms
        self.args = self.terms
        self.kwargs = kwargs
        super().__init__(*terms, name = name, **kwargs)

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
        argslots = 0
        kwargslots = []
        for term in terms:
            if isinstance(term, Function):
                if type(term) is Slot:
                    if term.argslots:
                        argslots += 1
                    elif not term.name in kwargslots:
                        kwargslots.append(term.name)
                else:
                    kwargslots.extend(
                        k for k in term.kwargslots if not k in kwargslots
                        )
                    argslots += term.argslots
        return argslots, kwargslots
    def _add_slot_attrs(self):
        if not hasattr(self, '_slots'):
            self._argslots, self._kwargslots = self._count_slots()
            self._slots = self._argslots + len(self._kwargslots)
        else:
            pass
    @property
    def slots(self):
        self._add_slot_attrs()
        return self._slots
    @property
    def argslots(self):
        self._add_slot_attrs()
        return self._argslots
    @property
    def kwargslots(self):
        self._add_slot_attrs()
        return self._kwargslots
    @property
    def open(self):
        return bool(self.slots)
    def close(self,
            *queryArgs,
            **queryKwargs,
            ):
        badKeys = [k for k in queryKwargs if not k in self.kwargslots]
        if badKeys:
            raise FunctionException("Inappropriate kwargs:", badKeys)
        unmatchedKwargs = [k for k in self.kwargslots if not k in queryKwargs]
        if len(queryArgs) > self.argslots and len(unmatchedKwargs):
            excessArgs = queryArgs[-(len(queryArgs) - self.argslots):]
            extraKwargs = dict(zip(self.kwargslots, excessArgs))
            excessArgs = excessArgs[len(extraKwargs):]
            if len(excessArgs):
                raise FunctionException("Too many args:", excessArgs)
            queryKwargs.update(extraKwargs)
        queryArgs = iter(queryArgs[:self.argslots])
        terms = []
        changes = 0
        for t in self.terms:
            if type(t) is Slot:
                if t.argslots:
                    try:
                        t = next(queryArgs)
                        changes += 1
                    except StopIteration:
                        pass
                else:
                    if t.name in queryKwargs:
                        t = queryKwargs[t.name]
                        changes += 1
            elif isinstance(t, Function):
                if t.open:
                    queryArgs = list(queryArgs)
                    subArgs = queryArgs[:t.argslots]
                    leftovers = subArgs[t.argslots:]
                    subKwargs = {
                        k: queryKwargs[k]
                            for k in queryKwargs if k in t.kwargslots
                        }
                    t = t.close(
                        *queryArgs,
                        **subKwargs,
                        )
                    changes += 1
                    queryArgs = iter(leftovers)
            terms.append(t)
        if changes:
            outObj = type(self)(*terms, **self.kwargs)
        else:
            outObj = self
        return outObj

    # def __eq__(self, arg):
    #     return self.value == arg

    def _operate(self, *args, op = None, **kwargs):
        return Operation(self, *args, op = op, **kwargs)

    def __eq__(self, *args):
        return self._operate(*args, op = 'ne', comparative = True)
    def __ne__(self, *args):
        return self._operate(*args, op = 'ne', comparative = True)
    def __ge__(self, *args):
        return self._operate(*args, op = 'ge', comparative = True)
    def __le__(self, *args):
        return self._operate(*args, op = 'le', comparative = True)
    def __gt__(self, *args):
        return self._operate(*args, op = 'gt', comparative = True)
    def __lt__(self, *args):
        return self._operate(*args, op = 'lt', comparative = True)
    def __add__(self, *args):
        return self._operate(*args, op = 'add')
    def __floordiv__(self, *args):
        return self._operate(*args, op = 'floordiv')
    def __truediv__(self, *args):
        return self._operate(*args, op = 'truediv')
    def __mod__(self, *args):
        return self._operate(*args, op = 'mod')
    def __mul__(self, *args):
        return self._operate(*args, op = 'mul')
    def __pow__(self, *args):
        return self._operate(*args, op = 'pow')
    def __sub__(self, *args):
        return self._operate(*args, op = 'sub')
    def __truediv__(self, *args):
        return self._operate(*args, op = 'truediv')
    def __neg__(self, *args):
        return self._operate(*args, op = 'neg')

    def __bool__(self):
        try:
            return bool(self.value)
        except NullValueDetected:
            return False
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
        return self.not_fn(self)

    def __repr__(self):
        head = super().__repr__()
        if self.open:
            tail = 'open:' + str((self.argslots, self.kwargslots))
        else:
            tail = str(self)
        return '=='.join([head, tail])
    def __str__(self):
        try:
            return str(self.value)
        except NullValueDetected:
            return 'Null'
    def __call__(self, *args, **kwargs):
        if len(args) or len(kwargs):
            self = self.close(*args, **kwargs)
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
            if not len(args):
                return Slot
            elif len(args) > 1:
                return Getter
            else:
                arg = args[0]
                if is_numeric(arg):
                    return Value
                elif type(arg) is str:
                    return Slot
                else:
                    _ = len(arg)
                    return Array
        else:
            return Operation

# class Group(Function):
#
#     def __init__(self, *args, _funcDict = None, **kwargs):
#         if len(args):
#             if (not _funcDict is None) or len(kwargs):
#                 raise FunctionException("Bad Group inputs.")
#             _funcDict = {arg.name : arg for arg in args}
#         elif _funcDict is None:
#             _funcDict = **kwargs
#         else:
#             if len(kwargs):
#                 raise FunctionException("Provide dict OR kwargs to Group.")
#         for key, val in sorted({**_funcDict}.items()):
#             assert type(key) is str
#             if not isinstance(val, Function):
#                 val = Function(val, name = key)
#             if not val.name == key:
#                 raise ValueError("Input name does not equal provided key.")
#                 # val = type(val)(*val.args, name = key, **val.kwargs)
#         super().__init__(funcDict, **kwargs)
#     def __getitem__(self, key):
#         return self._funcDict[key]
#     def __getattr__(self, key):
#         if key in self._funcDict:
#             return self[key].value
#         else:
#             super().__getattr__(key)
#     def keys(self):
#         return self._funcDict.keys()
#     def _evaluate(self):
#         return OrderedDict((k, getattr(self, k)) for k in self.keys())

class Operation(Function):

    def __init__(self,
            *terms, op = None,
            asList = False,
            invert = False,
            comparative = False,
            ):
        if type(op) is tuple:
            sops, op = op[:-1], op[-1]
            for sop in sops:
                terms = Operation(*terms, op = sop)
                if not type(terms) is tuple:
                    terms = terms,
        self.op = self._getop(op)
        self.asList, self.invert = asList, invert
        self.comparative = comparative
        super().__init__(
            *terms,
            op = op,
            asList = asList,
            invert = invert,
            comparative = comparative
            )

    def _evaluate(self):
        try:
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
        except NullValueDetected:
            if self.comparative:
                return False
            else:
                raise NullValueDetected

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

class Slot(Function):

    def __init__(self, name = None):
        self._slots = 1
        super().__init__(name = name)
        if name is None:
            self._argslots = 1
            self._kwargslots = []
        else:
            self._argslots = 0
            self._kwargslots = [self.name]
    def close(self, *args, **kwargs):
        raise FunctionException("Cannot close a Slot function.")
