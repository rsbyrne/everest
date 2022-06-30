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
        yield '__fields__', dict, _ptolemaic.PtolDict

    @classmethod
    def body_handle_anno(meta, body, name, hint, val, /):
        body['__fields__'][name] = (hint, val)
        body[name] = hint


class _SpriteBase_(metaclass=Sprite):

    ### Class setup:

    @classmethod
    def _yield_slots(cls, /):
        yield from super()._yield_slots()
        for name, (hint, default) in cls.__fields__.items():
            yield name, hint

    @classmethod
    def _get_signature(cls, /):
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
    def parameterise(cls, /, *args, **kwargs):
        bound = cls.__signature__.bind(*args, **kwargs)
        bound.apply_defaults()
        return _SimpleNamespace(**bound.arguments)

    ### Storage:

    def __getattr__(self, name, /):
        try:
            val = dict(zip(self.__fields__, self.params))[name]
        except KeyError as exc:
            raise AttributeError from exc
        object.__setattr__(self, name, val)
        return val

    ### Representations:

    def _content_repr(self, /):
        return ', '.join(map(repr, self.params))

    def _repr_pretty_(self, p, cycle, root=None):
        if root is None:
            root = self.rootrepr
        _pretty.pretty_kwargs(
            dict(zip(self.__fields__, self.params)), p, cycle, root=root
            )


###############################################################################
###############################################################################
