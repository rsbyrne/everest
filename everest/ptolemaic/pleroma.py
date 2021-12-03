###############################################################################
''''''
###############################################################################


import pickle as _pickle
from inspect import getmodule as _getmodule

from everest.utilities import caching as _caching, switch as _switch
from everest import epitaph as _epitaph
from everest.primitive import Primitive as _Primitive


class Pleroma(type):

    def _pleroma_contains__(meta, arg, /):
        if isinstance(arg, meta):
            return True
        return arg in _Primitive.TYPS

    def __contains__(meta, arg, /):
        return meta._pleroma_contains__(arg)

    def _pleroma_getitem__(meta, arg, /):
        if isinstance(arg, type):
            if issubclass(arg, meta):
                return arg
        if arg in meta:
            return arg
        raise KeyError(arg)

    def __getitem__(meta, arg, /):
        return meta._pleroma_getitem__(arg)

    def _pleroma_init__(meta, /):
        pass

    def __init__(meta, /, *args, **kwargs):
        with meta.metamutable:
            meta._meta_softcache = {}
            super().__init__(*args, **kwargs)
            meta._pleroma_init__()

    @property
    def metafreezeattr(meta, /):
        try:
            return meta.__dict__['_metafreezeattr']
        except KeyError:
            super().__setattr__(
                '_metafreezeattr', switch := _switch.Switch(True)
                )
            return switch

    @property
    def metamutable(meta, /):
        return meta.metafreezeattr.as_(False)

    @metafreezeattr.setter
    def metafreezeattr(meta, val, /):
        meta._metafreezeattr.toggle(val)

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
    def taphonomy(meta, /):
        return _epitaph.TAPHONOMY

    def get_meta_epitaph(meta, /):
        return meta.taphonomy.auto_epitaph(meta)

    @property
    @_caching.soft_cache('_meta_softcache')
    def epitaph(meta, /):
        return meta.get_meta_epitaph()

#     def reduce(meta=None, arg=None, /, *, method=_pickle.dumps):
#         '''Serialises the metaclass.'''
#         if meta is None:
#             return None
#         return method((meta, type(meta).reduce(arg)))

#     @classmethod
#     def revive(pleroma, arg=None, /, *, method=_pickle.loads):
#         '''Unserialises a previously serialised metaclass.'''
#         arg, sub = _pickle.loads(arg)
#         if not sub is None:
#             arg = arg.revive(sub, method=method)
#         return arg


###############################################################################
###############################################################################
