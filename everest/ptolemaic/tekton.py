###############################################################################
''''''
###############################################################################


import inspect as _inspect

from .urgon import Urgon as _Urgon
from .eidos import Eidos as _Eidos
from . import field as _field
from .ousia import Ousia as _Ousia
from . import ptolemaic as _ptolemaic


class Tekton(_Eidos, _Urgon):

    @classmethod
    def _yield_smartattrtypes(meta, /):
        yield from super()._yield_smartattrtypes()
        yield _field.Field

    @classmethod
    def _yield_bodymeths(meta, body, /):
        yield from super()._yield_bodymeths(body)
        for kind in _field.Kinds:
            yield kind.name, kind
        for signal in _field.Signals:
            yield signal.name, signal

    @classmethod
    def body_handle_anno(meta, body, name, hint, val, /):
        if not isinstance(hint, _ptolemaic.Ptolemaic):
            hint = str(hint)
        body[name] = _field.Field.from_annotation(hint, val)

    @property
    def arity(cls, /):
        try:
            return cls._clsarity
        except AttributeError:
            fields = cls.__fields__
            out = len(fields) - len(fields.degenerates)
            with cls.mutable:
                cls._clsarity = out
            return out


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
    def __parameterise__(cls, /, *args, **kwargs):
        bound = cls.__signature__.bind(*args, **kwargs)
        bound.arguments = {
            key: val for key, val in bound.arguments.items()
            if val is not NotImplemented
            }
        bound.apply_defaults()
        return super().__parameterise__(**{
            **bound.arguments,
            **cls.__fields__.degenerates,
            })


###############################################################################
###############################################################################
