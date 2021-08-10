###############################################################################
''''''
###############################################################################


import itertools as _itertools
from abc import ABCMeta as _ABCMeta

from . import _utilities

_TypeMap = _utilities.misc.TypeMap


class _Element_(metaclass=_ABCMeta):

    __slots__ = ('index')

    def __init__(self, index):
        self.index = index

class _Incisor_(metaclass=_ABCMeta):
    ...

# class _Incision_:
#     ...


class IncisableMeta(_ABCMeta):

    def __init__(cls, /, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for child in set(cls.child_classes()):
            cls._add_child_class(child)
        Element = cls._add_rider_class(_Element_)
        for typ in cls.element_types():
            _ = Element.register(typ)
        incmeths = cls.incmeths = cls._get_incmeths()
        Incisor = cls._add_rider_class(_Incisor_)
        for typ in incmeths:
            _ = Incisor.register(typ)
#         cls._add_child_class('_Incision_')
        cls._cls_extra_init_()

    def _cls_extra_init_():
        pass

    def child_classes(cls, /):
        return iter(())

    def incision_methods(cls, /):
        return iter(())

    def priority_incision_methods(cls, /):
        return iter(())

    def element_types(cls, /):
        return iter(())

    def _get_incmeths(cls, /) -> _TypeMap:
        return _TypeMap(
            _itertools.chain(
                cls.priority_incision_methods(),
                cls.incision_methods()
                ),
            )

    def _add_child_class(cls, ACls, /):
        name = ACls.__name__.strip('_')
        if ACls in cls.__mro__:
            addcls = cls
        else:
            classpath = []
            if 'classpath' in cls.__dict__:
                classpath.extend(cls.classpath)
            else:
                classpath.append(cls)
            addcls = type(
                name,
                (ACls, cls),
                dict(classpath=tuple((*classpath, name)))
                )
        setattr(cls, name, addcls)
        return addcls

    def _add_rider_class(cls, ACls, /):
        name = ACls.__name__.strip('_')
        bases = tuple(
            getattr(BCls, name)
            for BCls in cls.__bases__
            if hasattr(BCls, name)
            )
        rider = type(
            f'{cls.__name__}_{name}',
            bases if bases else (ACls,),
            dict(classpath=(cls, name)),
            )
        setattr(cls, name, rider)
        return rider


###############################################################################
###############################################################################
