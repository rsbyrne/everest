###############################################################################
''''''
###############################################################################


import itertools as _itertools
import more_itertools as _mitertools
import inspect as _inspect
import collections as _collections
import functools as _functools
import operator as _operator

from . import _utilities
from .eidos import Eidos as _Eidos
from . import params as _params


def ordered_set(itr):
    return tuple(_mitertools.unique_everseen(itr))


class Ptolemaic(_Eidos):
    '''
    The metaclass of all proper Ptolemaic classes.
    '''

    _ptolemaic_mergetuples__ = (
        '_req_slots__', '_ptolemaic_mroclasses__', '_ptolemaic_subclasses__'
        )
    _ptolemaic_mergedicts__ = ('_ptolemaic_annotations__',)
    _req_slots__ = ('params',)
    _ptolemaic_mroclasses__ = tuple()
    _ptolemaic_subclasses__ = tuple()
    _ptolemaic_fixedsubclasses__ = tuple()
    _ptolemaic_annotations__ = dict()

    @staticmethod
    def _gather_names(bases, name, methcall, /):
        return ordered_set(_itertools.chain.from_iterable(
            methcall(getattr(base, name))
            for base in bases if hasattr(base, name)
            ))

    def _merge_names(cls, name, /, *, mergetyp=tuple, itermeth='__iter__'):
        methcall = _operator.methodcaller(itermeth)
        meta = type(cls)
        merged = []
        merged.extend(cls._gather_names(
            (meta, *meta.__bases__),
            name,
            methcall,
            ))
        merged.extend(cls._gather_names(cls.__bases__, name, methcall))
        if name in cls.__dict__:
            merged.extend(ordered_set(methcall(getattr(cls, name))))
        merged = ordered_set(merged)
        setattr(cls, name, mergetyp(merged))

    def _merge_names_all(cls, overname, /, **kwargs):
        cls._merge_names(overname)
        for name in getattr(cls, overname):
            cls._merge_names(name, **kwargs)

    def _process_params(cls, /):
        annotations = dict()
        for mcls in reversed(cls.__mro__):
            if '__annotations__' not in mcls.__dict__:
                continue
            for name, annotation in mcls.__annotations__.items():
                if annotation is _params.Param:
                    annotation = _params.Param()
                elif not isinstance(annotation, _params.Param):
                    continue
                if name in annotations:
                    row = annotations[name]
                else:
                    row = annotations[name] = list()
                row.append(annotation)
        params = _collections.deque()
        for name, row in annotations.items():
            annotation = _functools.reduce(_operator.getitem, reversed(row))
            if hasattr(cls, name):
                att = getattr(cls, name)
                param = annotation(name, att)
            else:
                param = annotation(name)
            params.append(param)
        return _params.sort_params(params)

    def _add_mroclass(cls, name: str, /):
        adjname = f'_mroclassbase_{name}__'
        fusename = f'_mroclassfused_{name}__'
        if name in cls.__dict__:
            setattr(cls, adjname, cls.__dict__[name])
        inhclasses = []
        for mcls in cls.__mro__:
            if adjname in mcls.__dict__:
                inhcls = mcls.__dict__[adjname]
                if not inhcls in inhclasses:
                    inhclasses.append(inhcls)
        inhclasses = tuple(inhclasses)
        mroclass = type(name, inhclasses, {})
        setattr(cls, fusename, mroclass)
        setattr(cls, name, mroclass)

    def _add_mroclasses(cls, /):
        for name in cls._ptolemaic_mroclasses__:
            cls._add_mroclass(name)

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

    def _ptolemaic_signature__(cls, /):
        return _inspect.Signature(
            pm.parameter for pm in cls.classparams.values()
            )

    def __class_init__(cls, /):
        cls._merge_names_all('_ptolemaic_mergetuples__')
        cls._merge_names_all(
            '_ptolemaic_mergedicts__',
            mergetyp=_utilities.FrozenMap,
            itermeth='items',
            )
        if not hasattr(cls, '__annotations__'):
            cls.__annotations__ = dict()
        cls.__annotations__ = _utilities.FrozenMap(
            {**cls.__annotations__, **cls._ptolemaic_annotations__}
            )
        cls._add_mroclasses()
        cls._add_subclasses()
        cls.classparams = {pm.name: pm for pm in cls._process_params()}
        super().__class_init__()
        cls.Params = _params.Params[cls]

    def _ptolemaic_concrete_namespace__(cls, /):
        return super()._ptolemaic_concrete_namespace__() | cls.classparams

    def parameterise(cls, /, *args, **kwargs):
        return args, kwargs

    def instantiate(cls, params, /):
        obj = cls._ptolemaic_create_object__()
        obj.params = params
        obj.__init__()
        return obj

    def construct(cls, *args, **kwargs):
        params = cls.Params(*args, **kwargs)
        return cls.instantiate(params)


class SubClass(metaclass=Ptolemaic):

    @classmethod
    def _merge_names_all(cls, overname, /, **kwargs):
        cls.metacls._merge_names_all(cls, overname, **kwargs)
        if overname == '_ptolemaic_mergetuples__':
            if (name := cls.__name__) in cls._ptolemaic_subclasses__:
                cls._ptolemaic_subclasses__ = tuple(
                    nm for nm in cls._ptolemaic_subclasses__ if nm != name
                    )

#     @classmethod
#     def _add_subclasses(cls, /):
#         pass


###############################################################################
###############################################################################
