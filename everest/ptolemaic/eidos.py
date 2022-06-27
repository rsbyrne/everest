###############################################################################
''''''
###############################################################################


from everest import ur as _ur

from . import ptolemaic as _ptolemaic
from .essence import Essence as _Essence
from .smartattr import SmartAttr as _SmartAttr


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
    def _yield_mergenames(meta, /):
        yield from super()._yield_mergenames()
        for typ in meta._smartattrtypes:
            yield (
                typ.__merge_name__,
                typ.__merge_dyntyp__,
                typ.__merge_fintyp__,
                )

    @classmethod
    def __meta_init__(meta, /):
        typs = meta._smartattrtypes = tuple(meta._yield_smartattrtypes())
        if not all(issubclass(typ, _SmartAttr) for typ in typs):
            raise TypeError("SmartAttrs must be of the SmartAttr type.")
        super().__meta_init__()


class _EidosBase_(metaclass=Eidos):

    @classmethod
    def _yield_slots(cls, /):
        yield from super()._yield_slots()
        for typ in type(cls)._smartattrtypes:
            yield from getattr(cls, typ.__merge_name__).items()

    @classmethod
    def _get_smartattrset(cls, nm, /):
        return _ur.DatDict(
            (name, getattr(val, f"_get{nm[:-2]}_")(getattr(cls, name), name))
            for typ in type(cls)._smartattrtypes
            for name, val in getattr(cls, typ.__merge_name__).items()
            )

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        smartattrs = []
        for nm in ('_getters_', '_setters_', '_deleters_'):
            dct = cls._get_smartattrset(nm)
            setattr(cls, nm, dct)
            smartattrs.extend(dct)
        cls._smartattrs_ = _ur.PrimitiveUniTuple(smartattrs)

    def __getattr__(self, name, /):
        try:
            meth = object.__getattribute__(self, '_getters_')[name]
        except AttributeError as exc:
            raise RuntimeError from exc
        except KeyError as exc:
            raise AttributeError from exc
        else:
            val = meth(self)
            if not name.startswith('_'):
                val = _ptolemaic.convert(val)
            object.__setattr__(self, name, val)
            return val
        # return object.__getattribute__(name)

    def __setattr__(self, name, val, /):
        try:
            meth = object.__getattribute__(self, '_setters_')[name]
        except AttributeError as exc:
            raise RuntimeError from exc
        except KeyError as exc:
            super().__setattr__(name, val)
        else:
            meth(self, val)

    def __delattr__(self, name, /):
        try:
            meth = object.__getattribute__(self, '_deleters_')[name]
        except AttributeError as exc:
            raise RuntimeError from exc
        except KeyError as exc:
            super().__delattr__(name, val)
        else:
            meth(self)


###############################################################################
###############################################################################