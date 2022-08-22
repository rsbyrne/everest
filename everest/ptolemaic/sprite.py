###############################################################################
''''''
###############################################################################


import inspect as _inspect
from types import SimpleNamespace as _SimpleNamespace

from everest.utilities import pretty as _pretty

from . import ptolemaic as _ptolemaic
from .ousia import Ousia as _Ousia


_pkind = _inspect._ParameterKind


class Sprite(_Ousia):

    @classmethod
    def _yield_mergenames(meta, /):
        yield from super()._yield_mergenames()
        yield '__fields__', (dict, dict)

    @classmethod
    def body_handle_anno(meta, body, name, hint, default, /):
        if not isinstance(hint, _ptolemaic.Ptolemaic):
            hint = str(hint)
        body['__fields__'][name] = (hint, default)
        body[name] = hint


class _SpriteBase_(metaclass=Sprite):

    ### Class setup:

    @classmethod
    def _yield_slots(cls, /):
        yield from super()._yield_slots()
        for name, (hint, default) in cls.__fields__.items():
            yield name, hint

    @classmethod
    def __class_get_signature__(cls, /):
        parameters = (
            _inspect.Parameter(
                name, _pkind['POSITIONAL_OR_KEYWORD'],
                default=default, annotation=hint,
                )
            for name, (hint, default) in cls.__fields__.items()
            )
        return _inspect.Signature(parameters, return_annotation=cls)

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        cls.arity = len(cls.__fields__)

    ### Class instantiation:

    @classmethod
    def _parameterise_(cls, /, *args, **kwargs):
        bound = cls.__signature__.bind(*args, **kwargs)
        bound.arguments = {
            key: val for key, val in bound.arguments.items()
            if val is not NotImplemented
            }
        bound.apply_defaults()
        return _SimpleNamespace(**bound.arguments)

    ### Storage:

    def __getattr__(self, name, /):
        try:
            val = self.params[name]
        except KeyError as exc:
            raise AttributeError from exc
        if val is NotImplemented:
            raise AttributeError(name)
        object.__setattr__(self, name, val)
        return val

    ### Representations:

    def _pretty_repr_(self, p, cycle, root=None):
        if root is None:
            root = self.rootrepr
        _pretty.pretty_kwargs(
            dict(zip(self.__fields__, self.__params__)), p, cycle, root=root
            )


###############################################################################
###############################################################################
