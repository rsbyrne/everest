###############################################################################
''''''
###############################################################################


from inspect import getmodule as _getmodule
import abc as _abc

from everest.utilities import (
    caching as _caching,
    switch as _switch,
    FrozenMap as _FrozenMap,
    )
from everest import epitaph as _epitaph


class Pleroma(_abc.ABCMeta):

    def _pleroma_contains__(meta, _, /):
        raise NotImplementedError

    def __contains__(meta, arg, /):
        return meta._pleroma_contains__(arg)

    def _pleroma_getitem__(meta, arg, /):
        raise NotImplementedError

    def __getitem__(meta, arg, /):
        return meta._pleroma_getitem__(arg)

    def _pleroma_setitem__(meta, key, val, /):
        raise NotImplementedError

    def __setitem__(meta, key, val, /):
        return meta._pleroma_setitem__(key, val)

    def _pleroma_init__(meta, /):
        raise NotImplementedError

    def __init__(meta, /, *args, **kwargs):
        meta._meta_softcache = {}
        super().__init__(*args, **kwargs)
        meta._pleroma_init__()
        meta.metafreezeattr.toggle(True)

    @property
    def metafreezeattr(meta, /):
        try:
            return meta.__dict__['_metafreezeattr']
        except KeyError:
            super().__setattr__(
                '_metafreezeattr', switch := _switch.Switch(False)
                )
            return switch

    @property
    def metamutable(meta, /):
        return meta.metafreezeattr.as_(False)

    def __setattr__(meta, key, val, /):
        if meta.metafreezeattr:
            raise AttributeError(
                f"Setting attributes on an object of type {type(meta)} "
                "is forbidden at this time; "
                f"toggle switch `.metafreezeattr` to override."
                )
        super().__setattr__(key, val)

    def _pleroma_construct(meta, /):
        raise NotImplementedError

    def __call__(meta, /, *args, **kwargs):
        return meta._pleroma_construct(*args, **kwargs)

    @property
    def pleromabases(meta, /):
        return tuple(
            base for base in meta.__mro__ if isinstance(base, Pleroma)
            )

    def get_basetyp(meta, /):
        module = _getmodule(meta)
        try:
            return eval(f"{meta.__name__}Base", {}, module.__dict__)
        except NameError:
            bases = meta.pleromabases[1:]
            if bases:
                return Pleroma.get_basetyp(bases[0])
            return object

    @property
    def BaseTyp(meta, /):
        return meta.get_basetyp()

    @property
    def metataphonomy(meta, /):
        return _epitaph.TAPHONOMY


###############################################################################
###############################################################################
