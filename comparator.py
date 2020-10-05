from types import FunctionType
import builtins
import operator

from .pyklet import Pyklet

class Prop(Pyklet):

    def __init__(self,
            target,
            *props
            ):

        for prop in props:
            if not type(prop) is str:
                raise TypeError

        super().__init__(target, *props)

        self.target, self.props = target, props

    def __call__(self, obj = None):

        if obj is None:
            obj = self.target
        for prop in self.props:
            obj = getattr(obj, prop)

        return obj

class Comparator(Pyklet):

    def __init__(self,
            *terms,
            op : (str, FunctionType) = bool,
            asList = False,
            invert = False
            ):

        terms = [Prop(t[0], *t[1:]) if type(t) is tuple else t for t in terms]

        if type(op) is str:
            try:
                op = getattr(builtins, op)
            except AttributeError:
                try:
                    op = getattr(operator, op)

        super().__init__(*terms, op = op, asList = asList, invert = invert)

        self.terms, self.op, self.asList, self.invert = \
            terms, op, asList, invert

    def __call__(self, *queryArgs):

        queryArgs = iter(queryArgs)
        terms = []
        for t in self.terms:
            if type(t) is Prop:
                if t.target is None:
                    t = t(next(queryArgs))
                else:
                    t = t()
            elif t is None:
                t = next(queryArgs)
            terms.append(t)
        terms.extend(list(queryArgs))

        if self.asList:
            out = bool(self.op(terms))
        else:
            out = bool(self.op(*terms))
        if self.invert:
            out = not out

        return out

    def __bool__(self):
        return bool(self())

#     def close(self, *queryArgs):
#
#         return Nullary(self, queryArgs)
#
# class Evaluator(Pyklet):
#
#     def __init__(self, comparator, queryArgs):
#
#         self.comparator, self.queryArgs = comparator, queryArgs
#         super().__init__(comparator, queryArgs)
#
#     def __bool__(self):
#
#         return self.comparator(self.queryArgs)
