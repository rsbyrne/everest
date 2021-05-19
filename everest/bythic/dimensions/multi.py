###############################################################################
''''''
###############################################################################

import operator as _operator
from functools import reduce as _reduce, partial as _partial

from . import _special, _everestutilities

from .dimension import Dimension as _Dimension
from .collection import Collection as _Collection

_Collapsed = _Dimension.Collapsed

_muddle = _everestutilities.seqmerge.muddle


class Set(_Dimension):

    __slots__ = ('metrics', 'prime', 'aux',)

    def __init__(self, *args):
        metrics = []
        for arg in args:
            if isinstance(arg, tuple):
                metrics.extend(arg)
            elif isinstance(arg, _Dimension):
                metrics.append(arg)
            else:
                raise TypeError(type(arg))
        metrics = self.metrics = tuple(metrics)
        self.prime, self.aux = metrics[0], metrics[1:]
        self.iterlen = min(len(met) for met in metrics)
        self.iter_fn = lambda: zip(*self.metrics)
        super().__init__()
        self.register_argskwargs(*metrics) # pylint: disable=E1101

    # def __getitem__(self, *args):
    #     try:
    #         return self.prime[*args]
    #


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

    __slots__ = (
        'dimnames', 'dimensions', 'dimdict', 'depth',
        'noncollapsed', 'noncolldepth', 'noncollkeys',
        )

    def __init__(self, *argdims, **kwargdims):
        if argdims:
            if kwargdims:
                raise ValueError(
                    f"Cannot provide both args and kwargs to {type(self)}"
                    )
            kwargdims = dict((str(i), val) for i, val in enumerate(argdims))
        self.dimdict = kwargdims
        dimnames, dimensions = self.dimnames, self.dimensions = tuple(
            _Collection(it) for it in zip(*kwargdims.items())
            )
        self.depth = len(dimensions)
        noncollfn = lambda x: not isinstance(x, _Collapsed)
        noncollinds = dimensions.apply(noncollfn, typ = bool)
        noncollapsed = self.noncollapsed = dimensions[noncollinds]
        self.noncollkeys = self.noncollapsed = dimnames[noncollinds]
        self.noncolldepth = len(noncollapsed)
        self.iterlen = _reduce(
            _operator.mul, (dim.iterlen for dim in dimensions), 1
            )
        self.iter_fn = _partial(_muddle, dimensions)
        super().__init__()
        self.register_argskwargs(**kwargdims) # pylint: disable=E1101

    def __getitem__(self, arg):
        if isinstance(arg, dict):
            return self.incise(**arg)
        if isinstance(arg, tuple):
            arg = process_depth(arg, self.noncolldepth)
        else:
            arg = (arg,)
        return self.incise(**dict(zip(self.noncollkeys, arg)))

    def incise(self, **incisors):
        newincs = {**self.dimdict}
        for dimname, incisor in incisors.items():
            if incisor is None:
                continue
            preinc = newincs[dimname]
            if preinc is None:
                newinc = incisor
            else:
                newinc = preinc[incisor]
            newincs[dimname] = newinc
        return type(self)(**newincs)

    def get_valstr(self):
        return str([repr(dim) for dim in self.dimensions])

###############################################################################
###############################################################################
