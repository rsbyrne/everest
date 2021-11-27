###############################################################################
''''''
###############################################################################


from everest.ptolemaic.primitive import Primitive as _Primitive


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

    def _get_basetyp(meta, /):
        return object

    @property
    def BaseTyp(meta, /):
        return meta._get_basetyp()


###############################################################################
###############################################################################\
