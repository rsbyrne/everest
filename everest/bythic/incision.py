###############################################################################
''''''
###############################################################################

from abc import ABC as _ABC, abstractmethod as _abstractmethod

from . import _special
from . import _mroclass


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


@_mroclass.Overclass
class Incision:

    '''An object that can be 'incised'.'''
    __slots__ = ('source', 'incisors', 'depth',)

    def __new__(cls, source, **incisors):
        obj = super().__new__(cls)

    def __init__(self, source, **incisors):
        self.source = source
        self.incisors = incisors
        super().__init__()

    def __getitem__(self, incisors):
        if isinstance(incisors, dict):
            return self.incise(**incisors)
        if isinstance(incisors, tuple):
            incisors = process_depth(incisors, len(self.incisors))
        else:
            incisors = (incisors,)
        return self.incise(**dict(zip(self.incisors, incisors)))

    def incise(self, **incisors):
        newincs = {**self.incisors}
        for dimname, incisor in incisors.items():
            if incisor is None:
                continue
            preinc = newincs[dimname]
            if preinc is None:
                newinc = incisor
            elif isinstance(preinc, tuple):
                newinc = (*preinc, incisor)
            else:
                newinc = (preinc, incisor)
            newincs[dimname] = newinc
        return type(self)(self.source, **newincs)

    def __repr__(self):
        return f"{repr(self.source)}_{type(self).__name__}[{self.incisors}]"


@property
def get_incision(obj):
    try:
        return obj._incision
    except AttributeError:
        incision = obj._incision = obj.Incision(obj)
        return incision

@property
def get_getitem(obj):
    return obj.incision.__getitem__

@property
def get_incise(obj):
    return obj.incision.incise


class Incisable(_mroclass.MROClassable):

    @classmethod
    def __subclasshook__(cls, C):
        if cls is Incisable:
            try:
                Inc = getattr(cls, 'Incision')
                if issubclass(Inc, Incision) and issubclass(Inc, C):
#                     if 'resol'
                    return True
            except AttributeError:
                pass
        return NotImplemented

    def __new__(cls, ACls):
        '''Class decorator for designating an Incisable.'''
        ACls = super().__new__(cls, ACls)
        if not hasattr(ACls, 'Incision'):
            setattr(ACls, 'Incision', Incision)
        if not hasattr(ACls, 'incision'):
            ACls.incision = get_incision
        if not hasattr(ACls, '__getitem__'):
            ACls.__getitem__ = get_getitem
        if not hasattr(ACls, 'incise'):
            ACls.incise = get_incise
        return ACls

###############################################################################
###############################################################################
