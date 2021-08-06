###############################################################################
''''''
###############################################################################


import functools as _functools
from abc import ABCMeta as _ABCMeta
import itertools as _itertools
from collections import abc as _collabc

from everest.utilities.misc import (
    TypeMap as _TypeMap,
    )
from everest.utilities import classtools as _classtools


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


_IncMethsLike = _collabc.Iterator[tuple[type, _collabc.Callable]]


@_classtools.Diskable
@_classtools.MROClassable
class Chora(metaclass=ChoraMeta):

    @classmethod
    def child_classes(cls):
        return iter(())

    @_classtools.MROClass
    class Element:
        __slots__ = ('context', 'index')
        def __init__(self, context, index):
            self.context, self.index = context, index
        def __call__(self):
            return self.context.retrieve(self.index)

    @_classtools.Diskable
    @_classtools.MROClass
    class Incision:

        def __init__(self, context, chora):
            self.context, self.chora = context, chora
            self.register_argskwargs(context, chora)

        @property
        def choracontext(self):
            return self.context

        def retrieve(self, arg):
            return self.context.retrieve(arg)

    @classmethod
    def decorate(cls, ACls, /):
        old_init = ACls.__init__
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
        def chora_extra_init(self, *args, **kwargs):
            old_init(self, *args, **kwargs)
            self.chora = cls(
                *self.chora_args(),
                **dict(self.chora_kwargs())
                )
        ACls.__init__ = chora_extra_init
        cls.add_defer_methods(ACls)
        return ACls

    @classmethod
    def add_defer_methods(cls, ACls, /):
        if not hasattr(ACls, 'choracontext'):
            ACls.choracontext = property(lambda x: x)
        def __getitem__(self, incisor):
            out = self.chora.__getitem__(incisor, context=self.choracontext)
            if isinstance(out, self.chora.Element):
                return out()
            return self.chora.Incision(self.choracontext, out)
        ACls.__getitem__ = __getitem__
        def __contains__(self, arg):
            return self.chora.__contains__(arg)
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
        self.register_argskwargs(criterion=criterion)
        if isinstance(type(criterion), type):
            criterionclass = criterion
            def criterion(arg):
                return isinstance(arg, criterionclass)
        elif not callable(criterion):
            raise TypeError(criterion)
        self.criterion = criterion

    def __getitem__(self, incisor, /, *, context):
        try:
            meth = self.incmeths[type(incisor)]
        except KeyError as exc:
            raise TypeError from exc
        return meth(self, incisor, context=context)

    def __contains__(self, arg, /):
        return self.criterion(arg)

    def incise_tuple(self, incisor, /, *, context):
        '''Captures the special behaviour implied by `context[a,b,c...]`'''
        raise TypeError("Tuple slicing not supported.")

    def incise_trivial(self, incisor=None, /, *, context):
        '''Captures the special behaviour implied by `context[...]`.'''
        return context

    def incise_strict(self, incisor, /, *, context):
        '''Captures the sense of retrieving a single item from `context`.'''
        return self.Element(context, incisor)


###############################################################################
###############################################################################
