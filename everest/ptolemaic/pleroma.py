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

from .utilities import Switch as _Switch


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
        type.__setattr__(meta, '_metamutable', _Switch(True))
        meta._meta_softcache = {}
        super().__init__(*args, **kwargs)
        meta.__meta_init__()
        meta.mutable = False

    @property
    def mutable(meta, /):
        return meta.__dict__['_metamutable']

    @mutable.setter
    def mutable(meta, val, /):
        meta.mutable.toggle(val)

    def __setattr__(meta, name, val, /):
        if meta.mutable:
            super().__setattr__(name, val)
        else:
            raise AttributeError(
                "Cannot alter class attribute while immutable."
                )

    def __delattr__(meta, name, /):
        if meta.mutable:
            super().__delattr__(name)
        else:
            raise AttributeError(
                "Cannot alter class attribute while immutable."
                )

    def __meta_call__(meta, /, *_, **__):
        raise NotImplementedError

    @property
    def __call__(meta, /):
        return meta.__meta_call__

    @property
    def basetypname(meta, /):
        metaname = meta.__name__
        if metaname.endswith(suffix := 'Meta'):
            return metaname.removesuffix(suffix)
        return f"_{metaname}Base_"

    @property
    def BaseTyp(meta, /):
        try:
            return meta.__dict__['_BaseTyp']
        except KeyError:
            module = _getmodule(meta)
            try:
                basetyp = eval(meta.basetypname, {}, module.__dict__)
            except (NameError, SyntaxError):
                raise AttributeError('BaseTyp')
            else:
                type.__setattr__(meta, '_BaseTyp', basetyp)
                return basetyp

    @property
    def taphonomy(meta, /):
        return _epitaph.TAPHONOMY

    def __repr__(meta, /):
        return f"<{type(meta).__name__}:{meta.__name__}>"


###############################################################################
###############################################################################


#     @property
#     def pleromabases(meta, /):
#         return tuple(
#             base for base in meta.__mro__ if isinstance(base, Pleroma)
#             )

#     @property
#     def basetypname(meta, /):
#         metaname = meta.__name__
#         if metaname.endswith(suffix := 'Meta'):
#             return metaname.removesuffix(suffix)
#         return f"{metaname}Base"

#     def get_basetyp(meta, /):
#         module = _getmodule(meta)
#         try:
#             return eval(meta.basetypname, {}, module.__dict__)
#         except (NameError, SyntaxError):
#             bases = meta.pleromabases[1:]
#             if bases:
#                 return Pleroma.get_basetyp(bases[0])
#             return object

#     @property
#     def BaseTyp(meta, /):
#         return meta.get_basetyp()

#     def yield_basetypes(meta, /):
#         seen = set()
#         seen.add(typ := meta.BaseTyp)
#         yield typ
#         for pleromabase in meta.pleromabases:
#             basetyp = pleromabase.BaseTyp
#             if basetyp not in seen:
#                 seen.add(basetyp)
#                 yield basetyp

#     @property
#     def basetypes(meta, /):
#         return tuple(meta.yield_basetypes())
