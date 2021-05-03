###############################################################################
''''''
###############################################################################

from . import _special

from .dimension import Dimension as _Dimension
from .primary import Arbitrary as _Arbitrary


def process_depth(
        args: tuple, depth: int, /,
        filler = None,
        ):
    args = tuple(arg if arg != slice(None) else filler for arg in args)
    if (not depth < _special.infint) and (Ellipsis in args):
        raise ValueError("Cannot use ellipsis when depth is infinite.")
    nargs = len(args)
    if nargs == 0:
        return args
    if nargs == 1:
        if args[0] is Ellipsis:
            return tuple(filler for _ in range(depth))
        return args
    if nargs < depth:
        nellipses = len(tuple(el for el in args if el is Ellipsis))
        if nellipses == 0:
            return args
        if nellipses == 1:
            out = []
            for arg in args:
                if arg is Ellipsis:
                    for _ in range(depth - nargs):
                        out.append(filler)
                else:
                    out.append(arg)
            return tuple(out)
        raise IndexError(f"Too many ellipses ({nellipses} > 1)")
    if nargs == depth:
        return tuple(filler if arg is Ellipsis else arg for arg in args)
    raise IndexError(
        f"Not enough depth to accommodate requested levels:"
        f" levels = {nargs} > depth = {depth})"
        )


class Multi(_Dimension):

    __slots__ = ('dimensions', 'depth', 'collapsed')

    def __init__(self, **dimensions):
        self.dimnames =
        self.dimensions = dimensions
        self.depth = len(dimensions)
        self.collapsed = ()
        super().__init__()
        self.register_argskwargs(**dimensions)

    def __getitem__(self, dimensions):
        if isinstance(dimensions, dict):
            return self.incise(**dimensions)
        if isinstance(dimensions, tuple):
            dimensions = process_depth(dimensions, len(self.dimensions))
        else:
            dimensions = (dimensions,)
        return self.incise(**dict(zip(self.dimensions, dimensions)))

    def incise(self, **incisors):
        newincs = {**self.dimensions}
        for dimname, incisor in incisors.items():
            if incisor is None:
                continue
            preinc = newincs[dimname]
            if preinc is None:
                newinc = incisor
            else:
                newinc = preinc[newinc]
            newincs[dimname] = newinc
        return type(self)(**newincs)

    def __repr__(self):
        return f"{type(self).__name__}[{self.dimensions}]"

###############################################################################
###############################################################################
