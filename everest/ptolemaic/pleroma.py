###############################################################################
''''''
###############################################################################


import weakref as _weakref
import itertools as _itertools
import more_itertools as _mitertools
import inspect as _inspect
import collections as _collections
import functools as _functools
import operator as _operator

from . import _utilities
from .ousia import Ousia as _Ousia
from . import params as _params


def ordered_set(itr):
    return tuple(_mitertools.unique_everseen(itr))


class Pleroma(_Ousia):
    '''
    The metaclass of all proper Ptolemaic classes.
    '''

    _pleroma_concrete__ = False

    _pleroma_mergetuples__ = (
        '_pleroma_slots__', '_pleroma_mroclasses__', '_pleroma_subclasses__'
        )
    _pleroma_mergedicts__ = ('_pleroma_annotations__',)
    _pleroma_slots__ = ('_softcache', '_weakcache', 'params', '__weakref__')
    _pleroma_mroclasses__ = tuple()
    _pleroma_subclasses__ = tuple()
    _pleroma_fixedsubclasses__ = tuple()
    _pleroma_annotations__ = dict()

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
        for name in cls._pleroma_mroclasses__:
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
        cls._pleroma_subclass_classes__.append(subcls)

    def _add_subclasses(cls, /):
        cls._pleroma_subclass_classes__ = []
        for name in cls._pleroma_subclasses__:
            cls._add_subclass(name)
        attrname = '_pleroma_fixedsubclasses__'
        if attrname in cls.__dict__:
            for name in cls.__dict__[attrname]:
                cls._add_subclass(name)
        cls._pleroma_subclass_classes__ = tuple(
            cls._pleroma_subclass_classes__
            )

    @classmethod
    def __prepare__(meta, name, bases, /):
        return dict()

    def __new__(meta, name, bases, namespace, /, *, _concrete=False):
        if any(isinstance(base, Concrete) for base in bases):
            raise TypeError("Cannot subclass a Concrete type.")
        if _concrete:
            return super().__new__(meta, name, bases, namespace)
        namespace['__slots__'] = ()
        return super().__new__(meta, name, bases, namespace)

    def __init__(cls, /, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if cls._pleroma_concrete__:
            return
        cls._merge_names_all('_pleroma_mergetuples__')
        cls._merge_names_all(
            '_pleroma_mergedicts__',
            mergetyp=_utilities.FrozenMap,
            itermeth='items',
            )
#         if not hasattr(cls, '__annotations__'):
#             cls.__annotations__ = dict()
#         cls.__annotations__ = {**cls.__annotations__, **cls._pleroma_annotations__}
        cls._add_mroclasses()
        cls._add_subclasses()
        params = cls._process_params()
        cls.classparams = {pm.name: pm for pm in params}
        cls.__signature__ = _inspect.Signature(pm.parameter for pm in params)
        cls.Params = _params.Params[cls]
        cls.Concrete = Concrete(cls)
        cls._cls_inits_()

    def _cls_inits_(cls, /):
        for name in dir(cls):
            if name.startswith('_cls_') and name.endswith('_init_'):
                getattr(cls, name)()

    def parameterise(cls, /, *args, **kwargs):
        return args, kwargs

    def _create_object(cls, /):
        obj = object.__new__(cls.Concrete)
        obj._softcache = dict()
        obj._weakcache = _weakref.WeakValueDictionary()
        return obj

    def instantiate(cls, params, /):
        obj = cls._create_object()
        obj.params = params
        obj.__init__()
        return obj

    def construct(cls, *args, **kwargs):
        params = cls.Params(*args, **kwargs)
        return cls.instantiate(params)

    def __call__(cls, /, *args, **kwargs):
        return cls.construct(*args, **kwargs)

#     def __class_getitem__(cls, arg, /):
#         if isinstance(arg, cls.Params):
#             return cls.instantiate(arg)
#         raise TypeError(type(arg))

    def _cls_repr(cls, /):
        return super().__repr__()

    def __repr__(cls, /):
        return cls._cls_repr()

    def __contains__(cls, arg, /):
        return cls._pleroma_contains__(arg)

    def _pleroma_contains__(cls, arg, /):
        return isinstance(arg, cls)

#     def __iter__(cls, arg, /):
#         return cls._pleroma_contains__(arg)

#     def _pleroma_contains__(cls, arg, /):
#         return False


class Concrete(Pleroma):

    def __new__(meta, base, /,):
        name = f"{base.__qualname__}.Concrete"
        namespace = dict(
            __slots__=base._pleroma_slots__,
            basecls=base,
            _pleroma_concrete__=True,
            ) | base.classparams
        bases = (base,)
        return super().__new__(meta, name, bases, namespace, _concrete=True)

    def __init__(cls, /, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cls.__signature__ = cls.basecls.__signature__

    def __call__(cls, /, *args, **kwargs):
        raise TypeError("Cannot directly call a Concrete class.")


class SubClass(metaclass=Pleroma):

    @classmethod
    def _merge_names_all(cls, overname, /, **kwargs):
        type(cls)._merge_names_all(cls, overname, **kwargs)
        if overname == '_pleroma_mergetuples__':
            if (name := cls.__name__) in cls._pleroma_subclasses__:
                cls._pleroma_subclasses__ = tuple(
                    nm for nm in cls._pleroma_subclasses__ if nm != name
                    )

#     @classmethod
#     def _add_subclasses(cls, /):
#         pass


###############################################################################
###############################################################################
