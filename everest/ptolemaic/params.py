###############################################################################
''''''
###############################################################################


import inspect as _inspect

from everest.ptolemaic.compound import Compound as _Compound
from everest.ptolemaic.collections import DictLike as _DictLike
from everest.ptolemaic.inherence import Inherence as _Inherence
from everest.ptolemaic.eidos import Eidos as _Eidos
from everest.ptolemaic.proxy import Proxy as _Proxy


KINDS = dict(zip(
    ('Pos', 'PosKw', 'Args', 'Kw', 'Kwargs'),
    _inspect._ParameterKind,
    ))


class ParamMeta(_Inherence):

    for kind in KINDS:
        exec('\n'.join((
            '@property',
            f'def {kind}(cls, /):'
            f"    return cls(kind='{kind}')"
            )))


class Param(_Compound, metaclass=ParamMeta):

    _req_slots__ = ('name', 'value', 'kind', 'hint', 'parameter', 'inps')

    @classmethod
    def _check_hint(cls, hint, /):
        return hint

    def __init__(self, /,
            name='anon',
            hint=_Eidos,
            value=NotImplemented,
            kind='PosKw',
            ):
        if not kind in KINDS:
            raise ValueError(kind)
        hint = self._check_hint(hint)
        self.kind, self.hint = kind, hint
        if kind in {'Args', 'Kwargs'}:
            if value is not NotImplemented:
                raise TypeError
        self.name, self.value = name, value
        default = (
            _inspect.Parameter.empty if value is NotImplemented
            else value
            )
        self.parameter = _inspect.Parameter(
            name, KINDS[kind], default=default, annotation=hint,
            )
        self.inps = dict(
            name=self.name, hint=self.hint, kind=self.kind, value=self.value
            )
        super().__init__()

    def __call__(self, **kwargs):
        return type(self).construct(**(self.inps | kwargs))

    @classmethod
    def __class_getitem__(cls, arg, /):
        return cls.construct()[arg]

    def __getitem__(self, arg, /):
        if isinstance(arg, Param):
            return self(**{**arg.inps, 'hint': self.hint[arg.hint]})
        return self(hint=self.hint[arg])

    def __repr__(self, /):
        return (
            f"Param.{self.kind}[{repr(self.hint)}]"
            f"({self.name}={self.value})"
            )

    def __get__(self, instance, /, owner=None):
        return instance.params[self.name]


class Sig(_DictLike, _Compound):

    _req_slots__ = ('parameters', 'signature', 'paramdict')

    @staticmethod
    def sort_params(params, /):
        params = sorted(
            params,
            key=(lambda x: x.parameter.default is not _inspect._empty)
            )
        params = sorted(
            params,
            key=(lambda x: x.parameter.kind)
            )
        return params

    def __init__(self, *parameters):
        parameters = self.parameters = tuple(self.sort_params(parameters))
        self.signature = _inspect.Signature(
            param.parameter for param in parameters
            )
        dct = self.paramdict = {param.name: param for param in parameters}
        super().__init__(dct)

    def __call__(self, /, *args, **kwargs):
        bound = self.signature.bind(*args, **kwargs)
        bound.apply_defaults()
        return Params(bound.args, bound.kwargs, bound.arguments)


class Params(_DictLike, _Compound):

    _req_slots__ = ('args', 'kwargs', 'arguments')

    def __init__(self, args, kwargs, arguments, /):
        self.args, self.kwargs, self.arguments = args, kwargs, arguments
        super().__init__(arguments)


###############################################################################
###############################################################################
