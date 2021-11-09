###############################################################################
''''''
###############################################################################


from everest.ptolemaic.metas.inherence import Inherence as _Inherence


class Eidos(_Inherence):

    _ptolemaic_mergetuples__ = (
        '_ptolemaic_subclasses__',
        '_ptolemaic_fixedsubclasses__',
        )
    _ptolemaic_subclasses__ = tuple()
    _ptolemaic_fixedsubclasses__ = tuple()

    class ConcreteMetaBase(_Ousia.ConcreteMetaBase):

        def subclass(cls, /, *args, **kwargs):
            return cls.basecls(*args, **kwargs)

    def subclass(cls, /, *bases, name=None, **namespace):
        bases = (*bases, cls)
        if name is None:
            name = '_'.join(map(repr, bases))
        return type(name, bases, namespace)

    def _ptolemaic_contains__(cls, arg, /):
        return issubclass(type(arg), cls)

    def __contains__(cls, arg, /):
        return cls._ptolemaic_contains__(arg)

    def _ptolemaic_getitem__(cls, arg, /):
        if isinstance(arg, type):
            if issubclass(arg, cls):
                return arg
            return cls.subclass(arg)
        raise TypeError(arg, type(arg))

    def __getitem__(cls, arg, /):
        return cls._ptolemaic_getitem__(arg)

    def _add_subclass(cls, name: str, /):
        adjname = f'_subclassbase_{name}__'
        fusename = f'_subclassfused_{name}__'
        if not hasattr(cls, adjname):
            if hasattr(cls, name):
                setattr(cls, adjname, getattr(cls, name))
            else:
                raise AttributeError(
                    f"No subclass base of name '{name}' or '{adjname}' "
                    "could be found."
                    )
        base = getattr(cls, adjname)
        subcls = type(name, (base, cls, SubClass), {'superclass': cls})
        setattr(cls, fusename, subcls)
        setattr(cls, name, subcls)
        cls._ptolemaic_subclass_classes__.append(subcls)

    def _add_subclasses(cls, /):
        cls._ptolemaic_subclass_classes__ = []
        for name in cls._ptolemaic_subclasses__:
            cls._add_subclass(name)
        attrname = '_ptolemaic_fixedsubclasses__'
        if attrname in cls.__dict__:
            for name in cls.__dict__[attrname]:
                cls._add_subclass(name)
        cls._ptolemaic_subclass_classes__ = tuple(
            cls._ptolemaic_subclass_classes__
            )

    def __init__(cls, /, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cls._add_subclasses()


# class SubClass(metaclass=_Ousia):

#     @classmethod
#     def _merge_names_all(cls, overname, /, **kwargs):
#         cls.metacls._merge_names_all(cls, overname, **kwargs)
#         if overname == '_ptolemaic_mergetuples__':
#             if (name := cls.__name__) in cls._ptolemaic_subclasses__:
#                 cls._ptolemaic_subclasses__ = tuple(
#                     nm for nm in cls._ptolemaic_subclasses__ if nm != name
#                     )


###############################################################################
###############################################################################
