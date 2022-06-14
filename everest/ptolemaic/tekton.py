###############################################################################
''''''
###############################################################################


from collections import namedtuple as _namedtuple

from everest import ur as _ur

from .urgon import Urgon as _Urgon
from . import field as _field


class Tekton(_Urgon):

    @classmethod
    def _yield_smartattrtypes(meta, /):
        yield from super()._yield_smartattrtypes()
        yield _field.Field

    @classmethod
    def _process_bodyanno(meta, body, name, hint, val, /):
        return name, _field.Field.from_annotation(hint, val)


class _TektonBase_(metaclass=Tekton):

    @classmethod
    def _get_signature(cls, /):
        return cls.__fields__.signature

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        Params = cls.Params = _namedtuple(
            f"Params_{cls.__name__}", cls.__fields__
            )
        cls.arity = len(Params._fields)

    @classmethod
    def parameterise(cls, /, *args, **kwargs):
        bound = cls.__signature__.bind(*args, **kwargs)
        bound.apply_defaults()
        return super().parameterise(**bound.arguments)


###############################################################################
###############################################################################
