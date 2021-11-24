###############################################################################
''''''
###############################################################################


import functools as _functools

from everest.ptolemaic.inherence import Inherence as _Inherence
from everest.ptolemaic.chora import Chora as _Chora


class Eidos(_Inherence):

#     def retrieve(cls, retriever, /):
#         return cls.class_retrieve(retriever)

#     def incise(cls, incisor, /):
#         return cls.class_incise(incisor)

#     def _class_defer_chora_methods(cls, /):
#         clschora = cls.clschora
#         for methname, meth in cls.chorameths.items():
#             @classmethod
#             @_functools.wraps(meth)
#             def chora_wrap_meth(cls, *args, **kwargs
#             wrapmeth = _functools.wraps(chorameth)(
#                 _functools.partial(chorameth, caller=cls)
#                 )
#             setattr(cls, f"class_{attr}", meth)

    def _get_clsgetitem(cls, /):

        clschora = cls.clschora
        prefixes = clschora.PREFIXES
        defkws = clschora._get_defkws((f"cls.class_{st}" for st in prefixes))
        passkws = clschora._get_defkws(prefixes)

        exec('\n'.join((
            f"@classmethod",
            f"def _ptolemaic_getitem__(cls, /, *args, chora=clschora, {defkws}):",
            f"    return chora.__getitem__(*args, {passkws})"
            )))

        return eval('_ptolemaic_getitem__')

    def __init__(cls, /, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cls.clschora = cls._get_clschora()
        cls._ptolemaic_getitem__ = cls._get_clsgetitem()
#         cls._class_defer_chora_methods()

    class BASETYP(_Inherence.BASETYP):

        __slots__ = ()

        @classmethod
        def _get_clschora(cls, /) -> _Chora:
            raise NotImplementedError

        @classmethod
        def __contains__(cls, arg, /):
            return cls.clschora.__contains__(arg)

    _ptolemaic_mroclasses__ = ('ChoraHandler')


###############################################################################
###############################################################################


#     _ptolemaic_mergetuples__ = (
#         '_ptolemaic_subclasses__',
#         '_ptolemaic_fixedsubclasses__',
#         )
#     _ptolemaic_subclasses__ = tuple()
#     _ptolemaic_fixedsubclasses__ = tuple()

#     class BASETYP(_Inherence.BASETYP):

#         __slots__ = ()

#         @classmethod
#         def subclass(cls, /, *bases, name=None, **namespace):
#             bases = (*bases, cls)
#             if name is None:
#                 name = '_'.join(map(repr, bases))
#             return type(name, bases, namespace)

#         @classmethod
#         def _ptolemaic_contains__(cls, arg, /):
#             return issubclass(type(arg), cls)

#         @classmethod
#         def _ptolemaic_getitem__(cls, arg, /):
#             if isinstance(arg, type):
#                 if issubclass(arg, cls):
#                     return arg
#                 return cls.subclass(arg)
#             raise TypeError(arg, type(arg))

#     class ConcreteMetaBase(_Inherence.ConcreteMetaBase):

#         def subclass(cls, /, *args, **kwargs):
#             return cls.basecls(*args, **kwargs)

#     def _add_subclass(cls, name: str, /):
#         adjname = f'_subclassbase_{name}__'
#         fusename = f'_subclassfused_{name}__'
#         if not hasattr(cls, adjname):
#             if hasattr(cls, name):
#                 setattr(cls, adjname, getattr(cls, name))
#             else:
#                 raise AttributeError(
#                     f"No subclass base of name '{name}' or '{adjname}' "
#                     "could be found."
#                     )
#         base = getattr(cls, adjname)
#         subcls = type(name, (base, cls, SubClass), {'superclass': cls})
#         setattr(cls, fusename, subcls)
#         setattr(cls, name, subcls)
#         cls._ptolemaic_subclass_classes__.append(subcls)

#     def _add_subclasses(cls, /):
#         cls._ptolemaic_subclass_classes__ = []
#         for name in cls._ptolemaic_subclasses__:
#             cls._add_subclass(name)
#         attrname = '_ptolemaic_fixedsubclasses__'
#         if attrname in cls.__dict__:
#             for name in cls.__dict__[attrname]:
#                 cls._add_subclass(name)
#         cls._ptolemaic_subclass_classes__ = tuple(
#             cls._ptolemaic_subclass_classes__
#             )

#     def __init__(cls, /, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         cls._add_subclasses()


# class SubClass(metaclass=_Ousia):

#     @classmethod
#     def _merge_names_all(cls, overname, /, **kwargs):
#         cls.metacls._merge_names_all(cls, overname, **kwargs)
#         if overname == '_ptolemaic_mergetuples__':
#             if (name := cls.__name__) in cls._ptolemaic_subclasses__:
#                 cls._ptolemaic_subclasses__ = tuple(
#                     nm for nm in cls._ptolemaic_subclasses__ if nm != name
#                     )
