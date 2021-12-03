###############################################################################
''''''
###############################################################################


import inspect as _inspect

from everest.utilities import FrozenMap as _FrozenMap
from everest.utilities.classtools import add_defer_meths as _add_defer_meths

from everest.ptolemaic.essence import Essence as _Essence
from everest.ptolemaic.ousia import Ousia as _Ousia


KINDS = dict(zip(
    ('Pos', 'PosKw', 'Args', 'Kw', 'Kwargs'),
    _inspect._ParameterKind,
    ))


class ParamMeta(_Ousia):

    for kind in KINDS:
        exec('\n'.join((
            '@property',
            f'def {kind}(cls, /):'
            f"    return cls(kind='{kind}')"
            )))

    def __getitem__(cls, arg, /):
        return cls.construct()[arg]


class Generic:

    def __class_getitem__(cls, arg, /):
        return arg


class Param(metaclass=ParamMeta):

    _req_slots__ = ('name', 'value', 'kind', 'hint', 'parameter', 'inps')

    @classmethod
    def _check_hint(cls, hint, /):
        return hint

    def __init__(self, /,
            name='anon',
            hint=Generic,
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


_DICTMETHS = (
    '__getitem__', '__len__', '__iter__' '__contains__', 'keys',
    'items', 'values', 'get', '__eq__', '__ne__',
    )


@_add_defer_meths('paramdict', _DICTMETHS)
class Sig(metaclass=_Ousia):

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
        self.paramdict = _FrozenMap((param.name, param) for param in parameters)
        super().__init__()

    def __call__(self, /, *args, **kwargs):
        bound = self.signature.bind(*args, **kwargs)
        bound.apply_defaults()
        return Params(**bound.arguments)


@_add_defer_meths('arguments', _DICTMETHS)
class Params(metaclass=_Ousia):

    _req_slots__ = ('arguments',)

    def __init__(self, /, **arguments):
        self.arguments = arguments
        super().__init__()


###############################################################################
###############################################################################
