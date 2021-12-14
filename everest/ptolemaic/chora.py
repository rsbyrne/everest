###############################################################################
''''''
###############################################################################


import abc as _abc
import functools as _functools
import inspect as _inspect
import collections as _collections

from everest.abstract import *
from everest.utilities import (
    TypeMap as _TypeMap, MultiTypeMap as _MultiTypeMap
    )

from everest.ptolemaic.essence import Essence as _Essence
from everest.ptolemaic.ptolemaic import Ptolemaic as _Ptolemaic


# class Element(_Ptolemaic):

#     __slots__ = ('chora', 'index',)

#     def __init__(self, chora, index, /):
#         self.chora, self.index = chora, index

#     def _repr(self, /):
#         return f"{self.chora}[{self.index}]"

#     def get_epitaph(self, /):
#         return self.taphonomy.custom_epitaph(
#             '$a[$b]',
#             dict(a=self.chora, b=self.index),
#             )


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
        return index

#     def retrieve(self, index, /):
#         return Element(self, index)

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


class Chora(ChoraBase):

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

#     def getitem_element(self, caller, incisor: Element, /):
#         return self.getitem(caller, incisor.index)

    def trivial_none(self, caller, incisor: NoneType, /):
        '''Captures the special behaviour implied by `self[None]`.'''
        return caller

    def trivial_ellipsis(self, caller, incisor: EllipsisType, /):
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
        return (
            (next(iter(meth.__annotations__.values())), meth)
            for meth in cls.chorameths.values()
            )

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


class Sliceable(Chora):

    def getitem_slice(self, caller, incisor: slice, /):
        slcargs = (incisor.start, incisor.stop, incisor.step)
        meth = self.slcgetmeths[tuple(map(type, slcargs))]
        return meth(self, caller, *slcargs)

    def slice_trivial_none(self, caller,
            start: NoneType, stop: NoneType, step: NoneType, /
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
        for methname, meth in cls.slcmeths.items():
            hint = tuple(meth.__annotations__.values())[:3]
            yield hint, meth

    @classmethod
    def _get_slcgetmeths(cls, /):
        return _MultiTypeMap(cls._yield_slcgetmeths())

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        cls.slcmeths = cls._get_slcmeths()
        cls.slcgetmeths = cls._get_slcgetmeths()


# class Chora(Sliceable, _Ptolemaic):

#     def retrieve_default(self, caller, incisor: object, /):
#         return caller.retrieve(incisor)

#     def get_epitaph(self, /):
#         return self.taphonomy.custom_epitaph(
#             '$A()',
#             dict(A=type(self)._ptolemaic_class__),
#             )


# class Bounds(_DataPtolemaic):

#     FIELDS = ('lbnd', 'ubnd')


# class Sampler(_DataPtolemaic):

#     FIELDS = ('sampler',)


class Traversable(Sliceable):

#     def getitem_slice(self, caller, incisor: slice, /):
#         lbnd, ubnd, sampler = (incisor.start, incisor.stop, incisor.step)
#         bounds, sampler = Bounds(lbnd, ubnd), Sampler(sampler)
#         return caller[bounds][sampler]

#     def getitem_bounds(self, caller, incisor: Bounds, /):
#         lbnd, ubnd = incisor.lbnd, incisor.ubnd
#         meth = self.bndgetmeths[type(lbnd), type(ubnd)]
#         return meth(self, caller, lbnd, ubnd)

#     def getitem_sampler(self, caller, incisor: Sampler, /):
#         sampler = incisor.sampler
#         meth = self.samplegetmeths[type(sampler)]
#         return meth(self, caller, sampler)

    def slice_incise_bound(self, caller,
            lbnd: object, ubnd: object, _: NoneType, /
            ):
        meth = self.bndgetmeths[type(lbnd), type(ubnd)]
        return meth(self, caller, lbnd, ubnd)

    def slice_incise_sample(self, caller,
            _: NoneType, __: NoneType, sampler: NotNone, /
            ):
        meth = self.samplegetmeths[type(sampler)]
        return meth(self, caller, sampler)

    def slice_incise_boundsample(self, caller,
            lbnd: object, ubnd: object, sampler: NotNone, /
            ):
        '''Equivalent to `caller[lbnd:ubnd][::sampler]`.'''
        return (
            self.slice_incise_bound(self, lbnd, ubnd, None)
            .slice_incise_sample(caller, None, None, sampler)
            )
            

    def bound_trivial_none(self, caller, lbnd: NoneType, ubnd: NoneType):
        '''Captures the special behaviour implied by `self[:]`.'''
        return caller

    def sample_trivial_none(self, caller, sampler: NoneType):
        '''Captures the special behaviour implied by `self[::None]`.'''
        return caller

    def sample_trivial_ellipsis(self, caller, sampler: NoneType):
        '''Captures the special behaviour implied by `self[::...]`.'''
        return caller

    @classmethod
    def _yield_bndmeths(cls, /):
        for name in cls.attributes:
            for prefix in map('bound_'.__add__, cls.PREFIXES):
                if name.startswith(prefix + '_'):
                    yield name, getattr(cls, name)
                    break

    @classmethod
    def _get_bndmeths(cls, /):
        return dict(cls._yield_bndmeths())

    @classmethod
    def _yield_bndgetmeths(cls, /):
        for meth in cls.bndmeths.values():
            hint = tuple(meth.__annotations__.values())[:3]
            yield hint, meth

    @classmethod
    def _get_bndgetmeths(cls, /):
        return _MultiTypeMap(cls._yield_bndgetmeths())

    @classmethod
    def _yield_samplemeths(cls, /):
        for name in cls.attributes:
            for prefix in map('sample_'.__add__, cls.PREFIXES):
                if name.startswith(prefix + '_'):
                    yield name, getattr(cls, name)
                    break

    @classmethod
    def _get_samplemeths(cls, /):
        return dict(cls._yield_samplemeths())

    @classmethod
    def _yield_samplegetmeths(cls, /):
        return (
            (next(iter(meth.__annotations__.values())), meth)
            for meth in cls.samplemeths.values()
            )

    @classmethod
    def _get_samplegetmeths(cls, /):
        return _TypeMap(cls._yield_samplegetmeths())

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        cls.bndmeths = cls._get_bndmeths()
        cls.bndgetmeths = cls._get_bndgetmeths()
        cls.samplemeths = cls._get_samplemeths()
        cls.samplegetmeths = cls._get_samplegetmeths()


###############################################################################
###############################################################################
