###############################################################################
''''''
###############################################################################


import functools as _functools

from everest import ur as _ur
from everest.armature import Armature as _Armature

from . import ptolemaic as _ptolemaic
from .classbody import Directive as _Directive
from .essence import Essence as _Essence


def _fallback_getter(obj, instance, name, /):
    return obj

def _fallback_setter(obj, instance, name, val, /):
    raise AttributeError(
        f"Can't set attribute: {instance}, {name}"
        )

def _fallback_deleter(obj, instance, name, val, /):
    raise AttributeError(
        f"Can't set attribute: {instance}, {name}"
        )


class SmartAttr(_Directive, metaclass=_Armature):

    __merge_dyntyp__ = dict
    __merge_fintyp__ = _ptolemaic.PtolDict

    content: None
    hint: None = None

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        singlename = cls.__single_name__ = cls.__name__.lower()
        cls.__merge_name__ = f"__{singlename}s__"

    def __directive_call__(self, body, name, /):
        body[self.__merge_name__][name] = self.hint
        body.enroll_shade(name)
        return name, self.content

    @classmethod
    def __body_call__(cls, body, arg, /):
        return cls(arg)

    @classmethod
    def _get_getter_(cls, obj, /):
        try:
            return getattr(obj, f"__{cls.__single_name__}_get__")
        except AttributeError:
            return _functools.partial(_fallback_getter, obj)

    @classmethod
    def _get_setter_(cls, obj, /):
        try:
            return getattr(obj, f"__{cls.__single_name__}_set__")
        except AttributeError:
            return _functools.partial(_fallback_setter, obj)

    @classmethod
    def _get_deleter_(cls, obj, /):
        try:
            return getattr(obj, f"__{cls.__single_name__}_delete__")
        except AttributeError:
            return _functools.partial(_fallback_deleter, obj)


class Eidos(_Essence):

    @classmethod
    def _yield_bodymeths(meta, /):
        yield from super()._yield_bodymeths()
        for typ in meta._smartattrtypes:
            yield typ.__single_name__, getattr(typ, '__body_call__')
    
    @classmethod
    def _yield_smartattrtypes(meta, /):
        return
        yield

    @classmethod
    def _yield_mergenames(meta, body, /):
        yield from super()._yield_mergenames(body)
        for typ in meta._smartattrtypes:
            yield (
                typ.__merge_name__,
                typ.__merge_dyntyp__,
                typ.__merge_fintyp__,
                )

    @classmethod
    def __meta_init__(meta, /):
        meta._smartattrtypes = tuple(meta._yield_smartattrtypes())
        super().__meta_init__()


class _EidosBase_(metaclass=Eidos):

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        smartattrs = []
        for nm in ('_getters_', '_setters_', '_deleters_'):
            dct = _ur.DatDict(
                (name, getattr(typ, f"_get{nm[:-2]}_")(getattr(cls, name)))
                for typ in type(cls)._smartattrtypes
                for name in getattr(cls, typ.__merge_name__)
                )
            setattr(cls, nm, dct)
            smartattrs.extend(dct)
        cls._smartattrs_ = _ur.PrimitiveUniTuple(smartattrs)

    def __getattr__(self, name, /):
        kls = self.__ptolemaic_class__
        try:
            meth = kls._getters_[name]
        except AttributeError as exc:
            raise RuntimeError from exc
        except KeyError as exc:
            raise AttributeError from exc
        else:
            meth = val(self, name)
            if not name.startswith('_'):
                val = _ptolemaic.convert(val)
            object.__setattr__(self, name, val)
            return val

    def __setattr__(self, name, val, /):
        kls = self.__ptolemaic_class__
        try:
            meth = kls._setters_[name]
        except AttributeError as exc:
            raise RuntimeError from exc
        except KeyError as exc:
            super().__setattr__(name, val)
        else:
            meth(self, name, val)

    def __delattr__(self, name, /):
        kls = self.__ptolemaic_class__
        try:
            meth = kls._setters_[name]
        except AttributeError as exc:
            raise RuntimeError from exc
        except KeyError as exc:
            super().__delattr__(name, val)
        else:
            meth(self, name)


###############################################################################
###############################################################################
