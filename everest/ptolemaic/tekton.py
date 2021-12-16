###############################################################################
''''''
###############################################################################


import abc as _abc
import inspect as _inspect
import itertools as _itertools
import weakref as _weakref
import functools as _functools
from collections import abc as _collabc

from everest.utilities import caching as _caching, FrozenMap as _FrozenMap

from everest.ptolemaic import chora as _chora
from everest.ptolemaic.essence import Essence as _Essence
from everest.ptolemaic.ptolemaic import Ptolemaic as _Ptolemaic
from everest.ptolemaic import exceptions as _exceptions
from everest.ptolemaic import utilities as _utilities


@_utilities.add_defer_meths('arguments', like=dict)
class CallSig(_Ptolemaic):

    __slots__ = (
        'args', 'kwargs', 'arguments',
        )

    @classmethod
    def signature_call(cls, signature, args, kwargs, /):
        bound = signature.bind(*args, **kwargs)
        bound.apply_defaults()
        return cls(bound.args, bound.kwargs, bound.arguments)

    def __init__(self, args, kwargs, arguments, /):
        super().__init__()
        self.args = args
        self.kwargs = _FrozenMap(kwargs)
        self.arguments = _FrozenMap(arguments)

    def get_epitaph(self, /):
        return (taph := self.taphonomy).custom_epitaph(
            *taph.posformat_callsig(
                type(self)._ptolemaic_class__,
                self.args, self.kwargs.content, self.arguments.content,
                )
            )

    def _repr(self, /):
        return ', '.join(map('='.join, zip(self, map(repr, self.values()))))


class BadParameters(_exceptions.ParameterisationException):

    def __init__(self, owner: type, bads: tuple, /):
        self.bads = bads
        super().__init__(owner)

    def message(self, /):
        yield from super().message()
        yield "when one or more parameters failed the prescribed check:"
        for param in self.bads:
            yield f"{repr(param)}, {repr(type(param))}"


class Registrar(_Ptolemaic):
    '''
    Handles parameterisation and type checking
    on behalf of its outer class.
    '''

    __slots__ = ('owner', 'args', 'kwargs', 'bads')

    def __init__(self, owner: type, /):
        self.owner, self.args, self.kwargs, self.bads = owner, [], {}, []

    ### Serialisation:

    def get_epitaph(self, /):
        return (taph := self.taphonomy).custom_epitaph(
            *taph.posformat_callsig(
                type(self)._ptolemaic_class__,
                self.owner,
                )
            )

    ### Basic functionality to check and process parameters:

    @property
    def process_param(self, /):
        return self.owner.process_param

    @property
    def check_param(self, /):
        return self.owner.check_param

    def __call__(self, /, *args, **kwargs):
        self.args.extend(map(self.process_param, args))
        self.kwargs.update(zip(
            map(str, kwargs),
            map(self.process_param, kwargs.values())
            ))

    def finalise(self, /):
        callsig = CallSig.signature_call(
            self.owner.__signature__,
            self.args,
            self.kwargs,
            )
        if bads := tuple(_itertools.filterfalse(
                self.check_param,
                callsig.values(),
                )):
            raise BadParameters(self.owner, bads)
        return callsig

    ### Basic object legibility:

    def _repr(self, /):
        argtup = ', '.join(map(repr, self.args))
        kwargtup = ', '.join(
            f"{key}: {repr(val)}"
            for key, val in self.kwargs.items()
            )
        return f"*({argtup}), **{{{kwargtup}}}"


class TektonChora(_chora.Sliceable):

    __slots__ = ('signature',)

    def __init__(self, signature: _inspect.Signature, /):
        self.signature = signature
        super().__init__()

    def _retrieve_contains_(self, incisor: CallSig, /) -> CallSig:
        try:
            return CallSig.signature_call(
                self.signature,
                incisor.args,
                incisor.kwargs,
                )
        except TypeError as exc:
            raise KeyError from exc


class Tekton(_Essence):

    @property
    @_caching.soft_cache('_cls_softcache')
    def __signature__(cls, /):
        return cls.get_signature()

    @_abc.abstractmethod
    def method(cls, /):
        raise NotImplementedError

    def get_signature(cls, /):
        return _inspect.signature(cls.method)

    @property
    @_caching.soft_cache('_cls_softcache')
    def premade(cls, /):
        return {}

    def construct(cls, callsig: CallSig, /) -> _collabc.Hashable:
        return cls.method(*callsig.args, **callsig.kwargs)

    def __class_getitem__(cls, callsig: CallSig, /):
        if (hexcode := callsig.hexcode) in (pre := cls.premade):
            out = pre[hexcode]
            if isinstance(out, _weakref.ref):
                out = out()
                if out is not None:
                    return out
            return out
        out = cls.construct(callsig)
        ref = _weakref.ref(out) if type(out).__weakrefoffset__ else out
        pre[hexcode] = ref
        return out

    def get_callsig(cls, /, *args, **kwargs):
        register = Registrar(cls)
        cls.parameterise(register, *args, **kwargs)
        return register.finalise()

    def __class_call__(cls, /, *args, **kwargs):
        return cls[cls.get_callsig(*args, **kwargs)]


class TektonBase(metaclass=Tekton):

    @classmethod
    def process_param(cls, arg, /):
        return arg

    @classmethod
    def check_param(cls, arg, /):
        return True

    @classmethod
    def parameterise(cls, register, /, *args, **kwargs):
        register(*args, **kwargs)


###############################################################################
###############################################################################
