from types import FunctionType
import operator

from .pyklet import Pyklet

class Prop(Pyklet):

    def __init__(self,
            *props
            ):

        self.props = props

        super().__init__(*props)

    def __call__(self, obj):

        for prop in self.props:
            obj = getattr(obj, prop)

        return obj

class Comparator(Pyklet):

    def __init__(self,
            *args,
            op : (str, FunctionType) = bool,
            asList = False,
            invert = False
            ):

        if type(op) is str:
            op = operator.__dict__[op]

        super().__init__(*args, op = op, asList = asList, invert = invert)

        self.args, self.op, self.asList, self.invert = \
            args, op, asList, invert

    def __call__(self, *queryArgs):

        queryArgs = iter(queryArgs)
        args = []
        for arg in self.args:
            if arg is None:
                args.append(next(queryArgs))
            elif type(arg) is Prop:
                args.append(arg(next(queryArgs)))
            else:
                args.append(arg)
        try:
            next(queryArgs)
            raise ValueError("Leftover args.")
        except StopIteration:
            pass

        if self.asList:
            out = bool(self.op(args))
        else:
            out = bool(self.op(*args))
        if self.invert:
            out = not out

        return out

    def close(self, *queryArgs):

        return Nullary(lambda: self(*queryArgs))

class Nullary:

    def __init__(self, fn):

        self.fn = fn

    def __bool__(self):

        return bool(fn())
