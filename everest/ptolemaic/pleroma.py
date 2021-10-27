###############################################################################
''''''
###############################################################################


from .primitive import Primitive as _Primitive


class Pleroma(type):

    def _pleroma_contains__(cls, arg, /):
        if isinstance(arg, cls):
            return True
        return arg in _Primitive.PRIMITIVETYPES

    def __contains__(cls, arg, /):
        return cls._pleroma_contains__(arg)

    def _pleroma_getitem__(cls, arg, /):
        if isinstance(arg, type):
            if issubclass(arg, cls):
                return arg
        if arg in cls:
            return arg
        raise KeyError(arg)

    def __getitem__(cls, arg, /):
        return cls._pleroma_getitem__(arg)

    def __meta_init__(meta, /):
        pass

    def __init__(meta, /, *args, **kwargs):
        super().__init__(*args, **kwargs)
        meta.__meta_init__()


###############################################################################
###############################################################################\
