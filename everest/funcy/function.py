################################################################################

from functools import cached_property as _cached_property
import weakref

from . import _wordhash, _reseed, _cascade

from . import utilities as _utilities
from .generic import FuncyEvaluable as _FuncyEvaluable

from .exceptions import *

# class NameProxy(cls):
#     def __init__(self, cls, *terms, **kwargs):
#         self.cls, self.terms, self.kwargs = cls, terms, kwargs
#     @property
#     def kwargstr(self):
#         return self.cls._kwargstr(self)
#     @property
#     def titlestr(self):
#         return self.cls._titlestr(self)
#     @property
#     def namestr(self):
#         return self.cls._namestr(self)
#     @property
#     def hashID(self):
#         return self.cls._hashID(self)

class Function(_FuncyEvaluable):

    __slots__ = (
        'terms',
        'prime',
        'kwargs',
#         '__weakref__',
#         '__dict__',
        )

    unique = False

    _premade = weakref.WeakValueDictionary()

    @classmethod
    def _construct(cls, *terms, unique = False, **kwargs):
        prox = cls(*terms, **kwargs)
        if (unique or cls.unique):
            return cls(*terms, **kwargs)
        else:
            try:
                return cls._premade[prox.hashID]
            except KeyError:
                cls._premade[prox.hashID] = prox
                return prox

    def __init__(self, *terms, **kwargs):
        self.terms = terms
        self.kwargs = kwargs
        if len(self.terms):
            self.prime = self.terms[0]
        super().__init__()
    @_cached_property
    def _Fn(self):
        from .constructor import Fn as _Fn
        return _Fn

    @classmethod
    def _value_resolve(cls, val):
        while True:
            try:
                val = val.value
            except AttributeError:
                break
        return val

    @_cached_property
    def _ops(self):
        from .ops import ops
        return ops
    @_cached_property
    def _seqops(self):
        from .ops import seqops
        return seqops
    def op(self, *args, op, rev = False, **kwargs):
        if rev: return self._ops(op, *(*args, self), **kwargs)
        else: return self._ops(op, self, *args, **kwargs)
    def seqop(self, *args, op, rev = False, **kwargs):
        if rev: return self._seqops(op, *(*args, self), **kwargs)
        else: return self._seqops(op, self, *args, **kwargs)
    def arithmop(self, *args, **kwargs):
        return self.op(*args, **kwargs)

    def __add__(self, other):
        return self.arithmop(other, op = 'add')
    def __sub__(self, other):
        return self.arithmop(other, op = 'sub')
    def __mul__(self, other):
        return self.arithmop(other, op = 'mul')
    def __matmul__(self, other):
        return self.arithmop(other, op = 'matmul')
    def __truediv__(self, other):
        return self.arithmop(other, op = 'truediv')
    def __floordiv__(self, other):
        return self.arithmop(other, op = 'floordiv')
    def __mod__(self, other):
        return self.arithmop(other, op = 'mod')
    def __divmod__(self, other):
        return self.arithmop(other, op = 'divmod')
    def __pow__(self, other):
        return self.arithmop(other, op = 'pow')
    # def __lshift__(self, other): return self.arithmop(other, op = 'lshift')
    # def __rshift__(self, other): return self.arithmop(other, op = 'rshift')
    def __and__(self, other):
        return self.arithmop(other, op = 'amp')
    def __xor__(self, other):
        return self.arithmop(other, op = 'hat')
    def __or__(self, other):
        return self.arithmop(other, op = 'bar')

    def __radd__(self, other):
        return self.arithmop(other, op = 'add', rev = True)
    def __rsub__(self, other):
        return self.arithmop(other, op = 'sub', rev = True)
    def __rmul__(self, other):
        return self.arithmop(other, op = 'mul', rev = True)
    def __rmatmul__(self, other):
        return self.arithmop(other, op = 'matmul', rev = True)
    def __rtruediv__(self, other):
        return self.arithmop(other, op = 'truediv', rev = True)
    def __rfloordiv__(self, other):
        return self.arithmop(other, op = 'floordiv', rev = True)
    def __rmod__(self, other):
        return self.arithmop(other, op = 'mod', rev = True)
    def __rdivmod__(self, other):
        return self.arithmop(other, op = 'divmod', rev = True)
    def __rpow__(self, other):
        return self.arithmop(other, op = 'pow', rev = True)
    def __rlshift__(self, other):
        return self.arithmop(other, op = 'lshift', rev = True)
    def __rrshift__(self, other):
        return self.arithmop(other, op = 'rshift', rev = True)
    def __rand__(self, other):
        return self.arithmop(other, op = 'amp', rev = True)
    def __rxor__(self, other):
        return self.arithmop(other, op = 'hat', rev = True)
    def __ror__(self, other):
        return self.arithmop(other, op = 'bar', rev = True)

    def __neg__(self):
        return self.arithmop(op = 'neg')
    def __pos__(self):
        return self.arithmop(op = 'pos')
    def __abs__(self):
        return self.arithmop(op = 'abs')
    def __invert__(self):
        return self.arithmop(op = 'inv')

    def __complex__(self):
        return self.arithmop(op = 'complex')
    def __int__(self):
        return self.arithmop(op = 'int')
    def __float__(self):
        return self.arithmop(op = 'float')
    #
    # def __index__(self): raise NullValueDetected # for integrals

    def __round__(self, ndigits = 0):
        return self.arithmop(ndigits, op = 'round')
    # def __trunc__(self): raise NullValueDetected
    def __floor__(self):
        return self.arithmop(op = 'floor')
    def __ceil__(self):
        return self.arithmop(op = 'ceil')

    def __lt__(self, other):
        return self.arithmop(other, op = 'lt')
    def __le__(self, other):
        return self.arithmop(other, op = 'le')
    # def __eq__(self, other): return self.arithmop(other, op = 'eq')
    # def __ne__(self, other): return self.arithmop(other, op = 'ne')
    def __gt__(self, other):
        return self.arithmop(other, op = 'gt')
    def __ge__(self, other):
        return self.arithmop(other, op = 'ge')

    def __bool__(self):
        return bool(self.value)

    def pipe_out(self, arg):
        raise NotYetImplemented

    @_cached_property
    def titlestr(self):
        return f"funcy.{self._titlestr()}"
    def _titlestr(self):
        return type(self).__name__
    @_cached_property
    def namestr(self):
        return self._namestr()
    def _namestr(self):
        out = self.titlestr + self.kwargstr
        termstr = lambda t: t.namestr if hasattr(t, 'namestr') else str(t)
        if len(self.terms):
            termstr = ', '.join(termstr(t) for t in self.terms)
            out += f'({termstr})'
        return out
    @_cached_property
    def kwargstr(self):
        return self._kwargstr()
    def _kwargstr(self):
        if not len(self.kwargs):
            return ''
        else:
            return _utilities.kwargstr(**self.kwargs)
    @property
    def valstr(self):
        return self._valstr()
    def _valstr(self):
        try:
            return str(self.value)
        except (NullValueDetected, EvaluationError):
            return 'null'
    def __repr__(self):
        return self.namestr
    def __str__(self):
        # return ' == '.join([self.namestr, self.valstr])
        return self.valstr

    def _hashID(self):
        return _wordhash.w_hash((self.__class__, self.terms, self.kwargs))
    @_cached_property
    def hashID(self):
        return self._hashID()
    @_cached_property
    def _hashInt(self):
        return _reseed.digits(12, seed = self.hashID)
    def __hash__(self):
        return self._hashInt

    def reduce(self, op = 'call'):
        target = self.terms[0]
        for term in self.terms[1:]:
            target = self._ops(op, target, term)
        return target

    def copy(self):
        return type(self(*self.terms, **self.kwargs))

    def __getitem__(self, key):
        return self.op(key, op = 'getitem')
    def __len__(self):
        return len(self.value)
    def __iter__(self):
        for i in range(len(self)):
            yield self[i]

    def __reduce__(self):
        return (self._construct, (self.terms, self.kwargs))
    @classmethod
    def _unreduce(cls, terms, kwargs):
        return cls._construct(*terms, **kwargs)

################################################################################
