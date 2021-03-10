################################################################################

from abc import abstractmethod as _abstractmethod
from functools import cached_property as _cached_property

from . import _Function, _generic, _construct_base, _Gruple
from ._seqmerge import muddle as _muddle
from ._seqiterable import SeqIterable as _SeqIterable

from .exceptions import *

class Derived(_Function):

    __slots__ = (
        '_slots',
        '_argslots',
        '_kwargslots',
        )

    def __init__(self, *terms, **kwargs):
        assert len(terms)
        self.terms = _Gruple(self._derived_convert(t) for t in terms)
        super().__init__(*terms, **kwargs)
        for term in self.baseTerms:
            term.register_downstream(self)

    @staticmethod
    def _derived_convert(obj):
        if isinstance(obj, (_generic.Primitive, _Function)):
            obj
        else:
            return _construct_base(obj)

    @_abstractmethod
    def _evaluate(self):
        raise _generic.FuncyAbstractMethodException
    def _resolve_terms(self):
        return (self._value_resolve(t) for t in self.terms)
    def _normal_evaluate(self):
        return self._evaluate(self._resolve_terms())
    def _muddle_terms(self):
        return _muddle(self._resolve_terms())
    def _iter(self):
        return (self._evaluate(s) for s in self._muddle_terms())
    def _seq_evaluate(self):
        return _SeqIterable(self)
    @_cached_property
    def evaluate(self):
        if self.isSeq: return self._seq_evaluate
        else: return self._normal_evaluate
    @_cached_property
    def value(self):
        return self.evaluate()

    def refresh(self):
        for term in self.baseTerms:
            term.refresh()
    def purge(self):
        try:
            del self.value
        except AttributeError:
            pass

#     def __call__(self, *args, **kwargs):
#         if args or kwargs:
#             return self._value_resolve(self.close(*args, **kwargs))
#         else:
#             return self.evaluate()
    def _add_slots(self):
        self._argslots, self._kwargslots, self._slots = self._count_slots()
    def _count_slots(self):
        argslots = 0
        kwargslots = []
        for term in self.openTerms:
            if type(term) is Fn.slot:
                if term.argslots:
                    argslots += 1
                elif not term.name in kwargslots:
                    kwargslots.append(term.name)
            else:
                kwargslots.extend(
                    k for k in term.kwargslots if not k in kwargslots
                    )
                argslots += term.argslots
        return argslots, kwargslots, argslots + len(kwargslots)
    @_cached_property
    def fnTerms(self):
        return [t for t in self.terms if isinstance(t, _Function)]
    @_cached_property
    def baseTerms(self):
        out = []
        for t in self.fnTerms:
            if isinstance(t, Derived):
                out.extend(t.baseTerms)
            else:
                out.append(t)
        return tuple(set(out))
    @_cached_property
    def derivedTerms(self):
        return [t for t in self.fnTerms if not t in self.baseTerms]
    @_cached_property
    def openTerms(self):
        return [t for t in self.fnTerms if t.open]
    @_cached_property
    def seqTerms(self):
        return [t for t in self.derivedTerms if t.isSeq]
    @_cached_property
    def isSeq(self):
        return bool(self.seqTerms)

    @_cached_property
    def argslots(self):
        try:
            return self._argslots
        except AttributeError:
            self._add_slots()
            return self._argslots
    @_cached_property
    def kwargslots(self):
        try:
            return self._kwargslots
        except AttributeError:
            self._add_slots()
            return self._kwargslots
    @_cached_property
    def slots(self):
        try:
            return self._slots
        except AttributeError:
            self._add_slots()
            return self._slots
    @_cached_property
    def slotVars(self):
        argVars, kwargVars = list(), OrderedDict()
        for term in self.fnTerms:
            if isinstance(term, Fn.slot):
                if term.argslots:
                    argVars.append(term)
                else:
                    kwargList = kwargVars.setdefault(term.name, [])
                    kwargList.append(term)
            elif term.open:
                subArgVars, subKwargVars = term.slotVars
                argVars.extend(subArgVars)
                for k, v in subKwargVars.items():
                    kwargList = kwargVars.setdefault(k, [])
                    kwargList.extend(v)
        return argVars, kwargVars
    @_cached_property
    def open(self):
        return bool(self.slots)
    def allclose(self, arg):
        target = self
        while target.open:
            target = target.close(arg)
        assert not target.open
        return target
    def close(self, *queryArgs, **queryKwargs):
        if not self.open:
            raise NothingToClose
        return self._close(*queryArgs, **queryKwargs)
    def _close(self,
            *queryArgs,
            **queryKwargs
            ):
        badKeys = [k for k in queryKwargs if not k in self.kwargslots]
        if badKeys:
            raise FuncyException("Inappropriate kwargs:", badKeys)
        unmatchedKwargs = [k for k in self.kwargslots if not k in queryKwargs]
        if len(queryArgs) > self.argslots and len(unmatchedKwargs):
            excessArgs = queryArgs[-(len(queryArgs) - self.argslots):]
            extraKwargs = dict(zip(self.kwargslots, excessArgs))
            excessArgs = excessArgs[len(extraKwargs):]
            if len(excessArgs):
                raise FuncyException("Too many args:", excessArgs)
            queryKwargs.update(extraKwargs)
        queryArgs = iter(queryArgs[:self.argslots])
        terms = []
        changes = 0
        for t in self.terms:
            if isinstance(t, Fn.slot):
                if t.argslots:
                    try:
                        t = t(next(queryArgs))
                        changes += 1
                    except StopIteration:
                        pass
                else:
                    if t.name in queryKwargs:
                        t = t(queryKwargs[t.name])
                        changes += 1
            elif isinstance(t, Fn.base):
                if t.open:
                    queryArgs = list(queryArgs)
                    subArgs = queryArgs[:t.argslots]
                    leftovers = queryArgs[t.argslots:]
                    subKwargs = {
                        k: queryKwargs[k]
                            for k in queryKwargs if k in t.kwargslots
                        }
                    t = t.close(
                        *subArgs,
                        **subKwargs,
                        )
                    changes += 1
                    queryArgs = iter(leftovers)
            terms.append(t)
        if changes:
            outObj = type(self)(*terms, **self.kwargs)
        else:
            outObj = self
        if outObj.fnTerms:
            return outObj
        else:
            return outObj.value

################################################################################
