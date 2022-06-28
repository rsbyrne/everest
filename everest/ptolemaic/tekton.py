###############################################################################
''''''
###############################################################################


import inspect as _inspect

from .urgon import Urgon as _Urgon
from .eidos import Eidos as _Eidos
from .field import Field as _Field
from .ousia import Ousia as _Ousia


class Tekton(_Eidos, _Urgon):

    @classmethod
    def _yield_smartattrtypes(meta, /):
        yield from super()._yield_smartattrtypes()
        yield _Field

    @classmethod
    def body_handle_anno(meta, body, name, hint, val, /):
        body[name] = _Field.from_annotation(hint, val)


class _TektonBase_(metaclass=Tekton):

    @classmethod
    def _get_returnanno(cls, /):
        try:
            return cls._construct_.__annotations__['return']
        except KeyError:
            return None

    @classmethod
    def _get_signature(cls, /):
        fields = cls.__fields__
        parameters = (
            field.get_parameter(name)
            for name, field in fields.items()
            if name not in fields.degenerates
            )
        retanno = cls._get_returnanno()
        return _inspect.Signature(parameters, return_annotation=retanno)

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        fields = cls.__fields__
        cls.arity = len(fields) - len(fields.degenerates)

    @classmethod
    def parameterise(cls, /, *args, **kwargs):
        bound = cls.__signature__.bind(*args, **kwargs)
        bound.apply_defaults()
        return super().parameterise(**{
            **bound.arguments,
            **cls.__fields__.degenerates,
            })


###############################################################################
###############################################################################
