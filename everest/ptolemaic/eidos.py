###############################################################################
''''''
###############################################################################


from functools import partial as _partial

from everest import ur as _ur

from . import ptolemaic as _ptolemaic
from .essence import Essence as _Essence
from .smartattr import SmartAttr as _SmartAttr
from .pathget import PathGet as _PathGet


class Eidos(_Essence):

    @classmethod
    def _yield_bodymeths(meta, body, /):
        yield from super()._yield_bodymeths(body)
        for typ in meta._smartattrtypes:
            yield (
                typ.__single_name__,
                _partial(getattr(typ, '__body_call__'), body),
                )

    _yield_smartattrtypes = _Essence._generic_yielder

    @classmethod
    def _yield_mergenames(meta, /):
        yield from super()._yield_mergenames()
        for typ in meta._smartattrtypes:
            yield (
                typ.__merge_name__,
                (typ.__merge_dyntyp__, typ.__merge_fintyp__)
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
        out = {}
        methname = f"_get{nm[:-2]}_"
        for typ in type(cls)._smartattrtypes:
            for name, val in getattr(cls, typ.__merge_name__).items():
                getter = getattr(val, methname)
                meth = getter(
                    getattr(cls, name, NotImplemented), name
                    )
                try:
                    meths = out[name]
                except KeyError:
                    meths = out[name] = []
                meths.append(meth)
        return _ur.DatDict(out)

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
            return object.__getattribute__(self, name)
        except AttributeError:
            val = type(self)._getattr_(self, name)
            if not name.startswith('_'):
                if isinstance(val, _PathGet):
                    val = val(self)
                else:
                    val = object.__getattribute__(
                        self, '__ptolemaic_class__'
                        ).convert(val)
            object.__setattr__(self, name, val)
            return val

    def _getattr_(self, name, /):
        try:
            getters = object.__getattribute__(self, '_getters_')
        except AttributeError as exc:
            raise RuntimeError from exc
        else:
            try:
                meths = getters[name]
            except KeyError as exc:
                raise AttributeError from exc
        for meth in meths:
            val = meth(self)
            if val is NotImplemented:
                continue
            return val
        raise AttributeError(name)
        # return object.__getattribute__(name)

    def __setattr__(self, name, val, /):
        try:
            meths = object.__getattribute__(self, '_setters_')[name]
        except AttributeError as exc:
            raise RuntimeError from exc
        except KeyError as exc:
            return super().__setattr__(name, val)
        for meth in meths:
            signal = meth(self, val)
            if signal is not NotImplemented:
                return
        raise AttributeError(name)

    def __delattr__(self, name, /):
        try:
            meths = object.__getattribute__(self, '_deleters_')[name]
        except AttributeError as exc:
            raise RuntimeError from exc
        except KeyError as exc:
            return super().__delattr__(name)
        for meth in meths:
            signal = meth(self)
            if signal is not NotImplemented:
                return
        raise AttributeError(name)


###############################################################################
###############################################################################
