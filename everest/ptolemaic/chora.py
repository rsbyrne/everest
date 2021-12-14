###############################################################################
''''''
###############################################################################


import abc as _abc
import functools as _functools
import inspect as _inspect
import collections as _collections

from everest import abstract as _abstract
from everest.utilities import (
    TypeMap as _TypeMap, MultiTypeMap as _MultiTypeMap
    )

from everest.ptolemaic.essence import Essence as _Essence
from everest.ptolemaic.ptolemaic import Ptolemaic as _Ptolemaic


class Element(_Ptolemaic):

    __slots__ = ('chora', 'index',)

    def __init__(self, chora, index, /):
        self.chora, self.index = chora, index

    def _repr(self, /):
        return f"{self.chora}[{self.index}]"

    def get_epitaph(self, /):
        return self.taphonomy.custom_epitaph(
            '$a[$b]',
            dict(a=self.chora, b=self.index),
            )


class Incision(_Ptolemaic):

    __slots__ = ('incised', 'chora')

    def __init__(self, incised, chora, /):
        self.incised, self.chora = incised, chora

    def incise(self, chora, /):
        return type(self)(self.incised, chora)

    def __getitem__(self, arg, /):
        return self.chora.getitem(self, arg)

    def __getattr__(self, arg, /):
        superget = super().__getattribute__
        try:
            return superget(arg)
        except AttributeError:
            return getattr(superget('incised'), arg)

    def _repr(self, /):
        return f"{self.incised}, {self.chora}"

    def get_epitaph(self, /):
        return self.taphonomy.custom_epitaph(
            '$A($a,$b)',
            dict(A=type(self)._ptolemaic_class__, a=self.incised, b=self.chora),
            )


def default_meth(obj, caller, incisor, /):
    raise TypeError(type(incisor))


def default_incise(obj, chora, /):
    return Incision(obj, chora)


class ChoraBase(metaclass=_Essence):

    _ptolemaic_mergetuples = ('CALLERREQS',)

    CALLERREQS = ('retrieve', 'chora')

    def incise(self, chora, /):
        return chora

    def retrieve(self, index, /):
        return Element(self, index)

    def __getitem__(self, arg, /):
        return self.getitem(self, arg)

    @_abc.abstractmethod
    def getitem(self, caller, arg, /):
        raise NotImplementedError

    @classmethod
    def decorate(cls, other, /):

        with other.clsmutable:

            reqs = cls.CALLERREQS
            if not all(map(dir(other).__contains__, reqs)):
                raise TypeError(f"Class {other} cannot be decorated by {cls}.")

            other.Chora = cls

            exec('\n'.join((
                f"def __getitem__(self, arg, /):",
                f"    return self.chora.getitem(self, arg)",
                )))

            other.__getitem__ = eval('__getitem__')

            if not hasattr(other, 'incise'):

                def incise(self, chora, /):
                    return Incised(self, chora)

                other.incise = default_incise

            for name, meth in cls.chorameths.items():

                params = tuple(_inspect.signature(meth).parameters.values())[1:]
                argstrn = ', '.join(
                    param.name for param in params if param.kind.value == 0
                    )

                exec('\n'.join((
                    f"@_functools.wraps(meth)",
                    f"def {name}(self, {argstrn}):",
                    f"    return meth(self.chora, self, {argstrn})",
                    )))

                setattr(other, name, eval(name))

        return other


class Basic(ChoraBase):

    _ptolemaic_mergetuples = ('PREFIX',)

    PREFIXES = ('getitem', 'trivial', 'incise', 'retrieve', 'fallback')

    def getitem_tuple(self, caller, incisor: tuple, /):
        '''Captures the special behaviour implied by `self[a,b,...]`'''
        length = len(incisor)
        if length == 0:
            return caller
        arg0, *argn = incisor
        out = self.getitem(caller, arg0)
        if argn:
            raise NotImplementedError
        return out

    def getitem_element(self, caller, incisor: Element, /):
        return self.getitem(caller, incisor.index)

    def trivial_none(self, caller, incisor: type(None), /):
        '''Captures the special behaviour implied by `self[None]`.'''
        return caller

    def trivial_ellipsis(self, caller, incisor: type(Ellipsis), /):
        '''Captures the special behaviour implied by `self[...]`.'''
        return caller

    def incise_chora(self, caller, incisor: ChoraBase, /):
        '''Returns the composition of two choras, i.e. f(g(x)).'''
        return caller.incise(Composition(self, incisor))

    @classmethod
    def _yield_chorameths(cls, /):
        for name in cls.attributes:
            for prefix in cls.PREFIXES:
                if name.startswith(prefix + '_'):
                    yield name, getattr(cls, name)
                    break

    @classmethod
    def _get_chorameths(cls, /):
        return dict(cls._yield_chorameths())

    @classmethod
    def _yield_getmeths(cls, /):
        for meth in cls.chorameths.values():
            if 'incisor' in meth.__annotations__:
                yield meth.__annotations__['incisor'], meth

    @classmethod
    def _get_getmeths(cls, /):
        return _TypeMap(cls._yield_getmeths())

    @classmethod
    def _get_default_getmeth(cls, /):
        if hasattr(cls, 'default_getmeth'):
            return cls.default_getmeth
        return default_meth

    @classmethod
    def _get_getitem(cls, /):
        exec('\n'.join((
            f"def getitem(self,",
            f"        caller, arg, /, *,",
            f"        get_meth=cls.get_meth,"
            f"        default_getmeth=cls.default_getmeth,",
            f"        ):",
            f"    return get_meth(type(arg), default_getmeth)(self, caller, arg)",
            )))
        return eval('getitem')

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        cls.chorameths = cls._get_chorameths()
        getmeths = cls.getmeths = cls._get_getmeths()
        cls.get_meth = getmeths.get
        cls.default_getmeth = cls._get_default_getmeth()
        cls.getitem = cls._get_getitem()


class Composition(ChoraBase, _Ptolemaic):

    __slots__ = ('fchora', 'gchora')

    def __init__(self, fchora: ChoraBase, gchora: ChoraBase, /):
        self.fchora, self.gchora = fchora, gchora
        super().__init__()

#     @staticmethod
#     def _sub_default_getmeth(chora, self, incisor, /):
#         return self[incisor][chora]

    def getitem(self, caller, incisor: object, /):
        fchora, gchora = self.fchora, self.gchora
        sub = gchora[incisor]
        if sub is gchora:
            return caller
        return fchora.getitem(caller, sub)

    def get_epitaph(self, /):
        return self.taphonomy.custom_epitaph(
            '$a[$b]',
            dict(a=self.fchora, b=self.gchora),
            )

    def _repr(self, /):
        return f"{self.fchora}[{self.gchora}]"


class Sliceable(Basic):

    def getitem_slice(self, caller, incisor: slice, /):
        slcargs = (incisor.start, incisor.stop, incisor.step)
        meth = self.slcgetmeths[tuple(map(type, slcargs))]
        return meth(self, caller, *slcargs)

    def slice_trivial_none(self, caller,
            start: type(None), stop: type(None), step: type(None), /
            ):
        '''Captures the special behaviour implied by `self[:]`.'''
        return caller

    @classmethod
    def _yield_slcmeths(cls, /):
        for name in cls.attributes:
            for prefix in map('slice_'.__add__, cls.PREFIXES):
                if name.startswith(prefix + '_'):
                    yield name, getattr(cls, name)
                    break

    @classmethod
    def _get_slcmeths(cls, /):
        return dict(cls._yield_slcmeths())

    @classmethod
    def _yield_slcgetmeths(cls, /):
        parnames = ('start', 'stop', 'step')
        for methname, meth in cls.slcmeths.items():
            hint = tuple(map(meth.__annotations__.__getitem__, parnames))
            yield hint, meth

    @classmethod
    def _get_slcgetmeths(cls, /):
        return _MultiTypeMap(cls._yield_slcgetmeths())

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        cls.slcmeths = cls._get_slcmeths()
        cls.slcgetmeths = cls._get_slcgetmeths()


class Chora(Sliceable, _Ptolemaic):

    def retrieve_default(self, caller, incisor: object, /):
        return caller.retrieve(incisor)

    def get_epitaph(self, /):
        return self.taphonomy.custom_epitaph(
            '$A()',
            dict(A=type(self)._ptolemaic_class__),
            )


###############################################################################
###############################################################################
