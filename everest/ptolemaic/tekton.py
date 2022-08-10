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
        for kind in _field.Kind:
            yield kind.name, kind
        for signal in _field.Signal:
            yield signal.name, signal

    @classmethod
    def body_handle_anno(meta, body, name, hint, val, /):
        body[name] = _field.Field.from_annotation(hint, val)

    @property
    def arity(cls, /):
        try:
            return cls.__dict__['_clsarity']
        except KeyError:
            fields = cls.__fields__
            out = len(fields) - len(fields.degenerates)
            type.__setattr__(cls, '_clsarity', out)
            return out


class _TektonBase_(metaclass=Tekton):

    @classmethod
    def _get_returnanno(cls, /):
        try:
            return cls._construct_.__annotations__['return']
        except KeyError:
            return None

    @classmethod
    def __class_get_signature__(cls, /):
        fields = cls.__fields__
        parameters = (
            field.get_parameter(cls, name)
            for name, field in fields.items()
            if name not in fields.degenerates
            )
        retanno = cls._get_returnanno()
        return _inspect.Signature(parameters, return_annotation=retanno)

    @classmethod
    def _parameterise_(cls, /, *args, **kwargs):
        bound = cls.__signature__.bind(*args, **kwargs)
        bound.arguments = {
            key: val for key, val in bound.arguments.items()
            if val is not NotImplemented
            }
        bound.apply_defaults()
        return super()._parameterise_(**{
            **bound.arguments,
            **cls.__fields__.degenerates,
            })

    @classmethod
    def _post_parameterise_(cls, params, /):
        params = super()._post_parameterise_(params)
        if len(params) != cls.arity:
            raise ValueError(params)
        return params


###############################################################################
###############################################################################
