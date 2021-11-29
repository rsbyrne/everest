###############################################################################
''''''
###############################################################################


import pickle as _pickle

from everest import epitaph as _epitaph
from everest.primitive import Primitive as _Primitive


class Pleroma(type):

    def _pleroma_contains__(meta, arg, /):
        if isinstance(arg, meta):
            return True
        return arg in _Primitive.PRIMITIVETYPES

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
        super().__init__(*args, **kwargs)
        meta._pleroma_init__()

    def __class_init__(meta, /):
        pass

    def _pleroma_construct(meta, /, *args, **kwargs):
        cls = super().__call__(*args)
        cls.__class_init__(**kwargs)
        return cls

    def __call__(meta, /, *args, **kwargs):
        return meta._pleroma_construct(*args, **kwargs)

    def get_basetyp(meta, /):
        return object

    @property
    def BaseTyp(meta, /):
        return meta.get_basetyp()

    @property
    def taphonomy(meta, /):
        return _epitaph.TAPHONOMY

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
###############################################################################\
