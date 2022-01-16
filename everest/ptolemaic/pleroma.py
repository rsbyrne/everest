###############################################################################
''''''
###############################################################################


from inspect import getmodule as _getmodule

from everest.utilities import (
    caching as _caching,
    switch as _switch,
    FrozenMap as _FrozenMap,
    )
from everest import epitaph as _epitaph


class Pleroma(type):

#     def __meta_contains__(meta, _, /):
#         raise NotImplementedError

#     def __contains__(meta, arg, /):
#         return meta.__meta_contains__(arg)

#     def __meta_getitem__(meta, arg, /):
#         raise NotImplementedError

#     def __getitem__(meta, arg, /):
#         return meta.__meta_getitem__(arg)

    def __meta_init__(meta, /):
        pass

    def __init__(meta, /, *args, **kwargs):
        meta._meta_softcache = {}
        super().__init__(*args, **kwargs)
        meta.__meta_init__()
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

    def __meta_call__(meta, /, *_, **__):
        raise NotImplementedError

    @property
    def __call__(meta, /):
        return meta.__meta_call__

    @property
    def pleromabases(meta, /):
        return tuple(
            base for base in meta.__mro__ if isinstance(base, Pleroma)
            )

    @property
    def basetypname(meta, /):
        metaname = meta.__name__
        if metaname.endswith(suffix := 'Meta'):
            return metaname.removesuffix(suffix)
        return f"{metaname}Base"

    def get_basetyp(meta, /):
        module = _getmodule(meta)
        try:
            return eval(meta.basetypname, {}, module.__dict__)
        except (NameError, SyntaxError):
            bases = meta.pleromabases[1:]
            if bases:
                return Pleroma.get_basetyp(bases[0])
            return object

    @property
    def BaseTyp(meta, /):
        return meta.get_basetyp()

    def yield_basetypes(meta, /):
        seen = set()
        seen.add(typ := meta.BaseTyp)
        yield typ
        for pleromabase in meta.pleromabases:
            basetyp = pleromabase.BaseTyp
            if basetyp not in seen:
                seen.add(basetyp)
                yield basetyp

    @property
    def basetypes(meta, /):
        return tuple(meta.yield_basetypes())

    @property
    def taphonomy(meta, /):
        return _epitaph.TAPHONOMY

    def __repr__(meta, /):
        return f"<{type(meta).__name__}:{meta.__name__}>"


###############################################################################
###############################################################################
