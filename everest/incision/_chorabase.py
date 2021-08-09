###############################################################################
''''''
###############################################################################


from abc import ABCMeta as _ABCMeta
from collections import abc as _collabc
import itertools as _itertools
import functools as _functools

from everest.utilities.misc import (
    TypeMap as _TypeMap,
    )
from . import _utilities


_classtools = _utilities.classtools


class ChoraMeta(_ABCMeta):

    def __init__(cls, /, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cls._cls_extra_init_()

    def add_child_class(cls, ACls):
        truename = ACls.__name__.strip('_')
        if ACls in cls.__mro__:
            addcls = cls
        else:
            classpath = []
            if 'classpath' in cls.__dict__:
                classpath.extend(cls.classpath)
            else:
                classpath.append(cls)
            addcls = type(
                truename,
                (ACls, cls),
                dict(classpath=tuple((*classpath, truename)))
                )
        setattr(cls, truename, addcls)


def yield_criteria(*criteria):
    for criterion in criteria:
        if isinstance(criterion, tuple):
            yield from yield_criteria(*criterion)
        else:
            if not callable(criterion):
                raise TypeError("Criteria must be callable.")
            yield criterion

@_functools.lru_cache
def get_single_criterion_function(criterion):
    if isinstance(criterion, type):
        def checktype(arg, argtyp=criterion, /):
            return isinstance(arg, argtyp)
        return checktype
    if not callable(criterion):
        print(criterion, type(criterion))
        raise TypeError(criterion)
    return criterion


def get_criterion_function(*criteria):
    criteria = tuple(yield_criteria(criteria))
    critfuncs = tuple(map(get_single_criterion_function, criteria))
    if len(critfuncs) == 1:
        criterion_function = critfuncs[0]
    else:
        def criterion_function(arg, funcs=critfuncs, /):
            return all(func(arg) for func in funcs)
    criterion_function.criteria = criteria
    return criterion_function


_IncMethsLike = _collabc.Iterator[tuple[type, _collabc.Callable]]


@_classtools.Diskable
class Incision:

    __slots__ = (
        'context', 'chora', 'retrieve',
        *_classtools.Diskable.reqslots
        )

    def __init__(self, context, chora):
        if isinstance(context, Incision):
            context = context.context
        self.context, self.chora = context, chora
        self.register_argskwargs(context, chora)
        self.retrieve = context.retrieve


class Element:

    __slots__ = ('index')

    def __init__(self, index):
        self.index = index


def generic_getitem(
        retrieve, choraget, incisor,
        eltyp=Element, inctyp=Incision, /
        ):
    out = choraget(incisor)
    return (
        retrieve(out.index) if isinstance(out, eltyp)
        else inctyp(out)
        )


@_classtools.Diskable
@_classtools.MROClassable
class ChoraBase(metaclass=ChoraMeta):

    Incision = Incision
    Element = Element

    @classmethod
    def child_classes(cls):
        return iter(())

    @classmethod
    def decorate(cls, ACls, /):

        ACls.Chora = cls

        if not hasattr(ACls, 'chora_args'):
            def chora_args(self):
                return iter(())
            ACls.chora_args = chora_args
        if not hasattr(ACls, 'chora_kwargs'):
            def chora_kwargs(self):
                return iter(())
            ACls.chora_kwargs = chora_kwargs
        if not hasattr(ACls, 'retrieve'):
            raise TypeError(
                "Incisable must provide a callable `.retrieve` attribute."
                )

        cls.add_defer_methods(ACls)
        return ACls

    @classmethod
    def add_defer_methods(cls, ACls, /):
                
        @_functools.cached_property
        def chora(self):
            return self.Chora(
                *self.chora_args(),
                **dict(self.chora_kwargs())
                )

        @_functools.cached_property
        def __getitem__(self):
            return _functools.partial(
                generic_getitem,
                self.retrieve, self.chora.__getitem__,
                )

        @_functools.cached_property
        def __contains__(self):
            return self.chora.__contains__(arg)

        ACls.chora = chora
        ACls.__getitem__ = __getitem__
        ACls.__contains__ = __contains__


    @classmethod
    def _cls_extra_init_(cls, /):
        cls.incmeths = cls._get_incmeths()
        cls.add_defer_methods(cls.Incision)
        for child in set(cls.child_classes()):
            cls.add_child_class(child)

    @classmethod
    def incision_methods(cls, /) -> _IncMethsLike:
        '''Returns acceptable incisor types and their associated getmeths.'''
        return iter(())

    @classmethod
    def priority_incision_methods(cls, /) -> _IncMethsLike:
        '''Returns like `.incision_methods` but takes priority.'''
        yield tuple, cls.incise_tuple
        yield type(Ellipsis), cls.incise_trivial

    @classmethod
    def _get_incmeths(cls, /) -> _TypeMap:
        return _TypeMap(
            _itertools.chain(
                cls.priority_incision_methods(),
                cls.incision_methods()
                ),
            )

    def __init__(self, /, *, criterion):
        crfn = self.criterion_function = get_criterion_function(criterion)
        self.register_argskwargs(criterion=crfn.criteria)

    def __getitem__(self, incisor, /):
        try:
            meth = self.incmeths[type(incisor)]
        except KeyError as exc:
            raise TypeError from exc
        return meth(self, incisor)

    @property
    def __contains__(self):
        return self.criterion_function

    def incise_tuple(self, incisor, /):
        '''Captures the special behaviour implied by `self[a,b,c...]`'''
        raise TypeError("Tuple slicing not supported.")

    def incise_trivial(self, incisor=None, /):
        '''Captures the special behaviour implied by `self[...]`.'''
        return self


###############################################################################
###############################################################################
